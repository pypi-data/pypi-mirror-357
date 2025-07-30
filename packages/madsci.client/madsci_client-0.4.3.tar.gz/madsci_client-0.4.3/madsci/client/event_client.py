"""MADSci Event Handling."""

import contextlib
import inspect
import json
import logging
import queue
import time
import warnings
from collections import OrderedDict
from pathlib import Path
from threading import Lock, Thread
from typing import Any, Optional, Union

import requests
from madsci.common.types.context_types import MadsciContext
from madsci.common.types.event_types import (
    Event,
    EventClientConfig,
    EventType,
)
from madsci.common.utils import threaded_task
from pydantic import BaseModel, ValidationError
from rich import print


class EventClient:
    """A logger and event handler for MADSci system components."""

    config: Optional[EventClientConfig] = None
    _event_buffer = queue.Queue()
    _buffer_lock = Lock()
    _retry_thread = None
    _retrying = False

    def __init__(
        self,
        config: Optional[EventClientConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the event logger. If no config is provided, use the default config.

        Keyword Arguments are used to override the values of the passed in/default config.
        """
        if kwargs:
            self.config = (
                EventClientConfig(**kwargs) if not config else config.__init__(**kwargs)
            )
        else:
            self.config = config or EventClientConfig()
        if self.config.name:
            self.name = self.config.name
        else:
            # * See if there's a calling module we can name after
            stack = inspect.stack()
            parent = stack[1][0]
            if calling_module := parent.f_globals.get("__name__"):
                self.name = calling_module
            else:
                # * No luck, name after EventClient
                self.name = __name__
        self.name = str(self.name)
        self.logger = logging.getLogger(self.name)
        self.log_dir = Path(self.config.log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logfile = self.log_dir / f"{self.name}.log"
        self.logger.setLevel(self.config.log_level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler) and handler.baseFilename == str(
                self.logfile
            ):
                self.logger.removeHandler(handler)
        file_handler = logging.FileHandler(filename=str(self.logfile), mode="a+")
        self.logger.addHandler(file_handler)
        self.event_server = (
            self.config.event_server_url or MadsciContext().event_server_url
        )
        self.log_debug(
            "Event logger {self.name} initialized.",
        )
        self.log_debug(self.config)

    def get_log(self) -> dict[str, Event]:
        """Read the log"""
        events = {}
        with self.logfile.open() as log:
            for line in log.readlines():
                try:
                    event = Event.model_validate_json(line)
                except ValidationError:
                    event = Event(event_type=EventType.UNKNOWN, event_data=line)
                events[event.event_id] = event
        return events

    def get_events(self, number: int = 100, level: int = -1) -> dict[str, Event]:
        """Query the event server for a certain number of recent events. If no event server is configured, query the log file instead."""
        if level == -1:
            level = self.logger.getEffectiveLevel()
        events = OrderedDict()
        if self.event_server:
            response = requests.get(
                str(self.event_server) + "/events",
                timeout=10,
                params={"number": number, "level": level},
            )
            if not response.ok:
                response.raise_for_status()
            print(response.json())
            for key, value in response.json().items():
                events[key] = Event.model_validate(value)
            return dict(events)
        events = self.get_log()
        selected_events = {}
        for event in reversed(list(events.values())):
            selected_events[event.event_id] = event
            if len(selected_events) >= number:
                break
        return selected_events

    def query_events(self, selector: dict) -> dict[str, Event]:
        """Query the event server for events based on a selector. Requires an event server be configured."""
        events = OrderedDict()
        if self.event_server:
            response = requests.get(
                str(self.event_server) + "/events",
                timeout=10,
                params={"selector": selector},
            )
            if not response.ok:
                response.raise_for_status()
            for key, value in response.json().items():
                events[key] = Event.model_validate(value)
            return dict(events)
        raise ValueError("No event server configured, cannot query events.")

    def log(
        self,
        event: Union[Event, Any],
        level: Optional[int] = None,
        alert: Optional[bool] = None,
        warning_category: Optional[Warning] = None,
    ) -> None:
        """Log an event."""

        # * If we've got a string or dict, check if it's a serialized event
        if isinstance(event, str):
            with contextlib.suppress(ValidationError):
                event = Event.model_validate_json(event)
        if isinstance(event, dict):
            with contextlib.suppress(ValidationError):
                event = Event.model_validate(event)
        if isinstance(event, Exception):
            import traceback

            event = Event(
                event_type=EventType.LOG_ERROR,
                event_data=traceback.format_exc(),
            )
        if not isinstance(event, Event):
            event = self._new_event_for_log(event, level)
        event.log_level = level if level else event.log_level
        event.alert = alert if alert is not None else event.alert
        if warning_category:
            warnings.warn(
                event.model_dump_json(),
                category=warning_category,
                stacklevel=3,
            )
        self.logger.log(event.log_level, event.model_dump_json())
        # * Log the event to the event server if configured
        # * Only log if the event is at the same level or higher than the logger
        if self.logger.getEffectiveLevel() <= event.log_level:
            print(f"{event.event_timestamp} ({event.event_type}): {event.event_data}")
            if self.event_server:
                self._send_event_to_event_server_task(event)

    def log_debug(self, event: Union[Event, str]) -> None:
        """Log an event at the debug level."""
        self.log(event, logging.DEBUG)

    debug = log_debug

    def log_info(self, event: Union[Event, str]) -> None:
        """Log an event at the info level."""
        self.log(event, logging.INFO)

    info = log_info

    def log_warning(
        self, event: Union[Event, str], warning_category: Warning = UserWarning
    ) -> None:
        """Log an event at the warning level."""
        self.log(event, logging.WARNING, warning_category=warning_category)

    warning = log_warning
    warn = log_warning

    def log_error(self, event: Union[Event, str]) -> None:
        """Log an event at the error level."""
        self.log(event, logging.ERROR)

    error = log_error

    def log_critical(self, event: Union[Event, str]) -> None:
        """Log an event at the critical level."""
        self.log(event, logging.CRITICAL)

    critical = log_critical

    def log_alert(self, event: Union[Event, str]) -> None:
        """Log an event at the alert level."""
        self.log(event, alert=True)

    alert = log_alert

    def _start_retry_thread(self) -> None:
        with self._buffer_lock:
            if not self._retrying:
                self._retrying = True
                self._retry_thread = Thread(
                    target=self._retry_buffered_events, daemon=True
                )
                self._retry_thread.start()

    def _retry_buffered_events(self) -> None:
        backoff = 2
        max_backoff = 60
        while not self._event_buffer.empty():
            try:
                event = self._event_buffer.get()
                self._send_event_to_event_server(event, retrying=True)
                backoff = 2  # Reset backoff on success
            except Exception:
                time.sleep(backoff)
                backoff = min(backoff * 2, max_backoff)
                self._event_buffer.put(event)  # Re-add the event to the buffer
        with self._buffer_lock:
            self._retrying = False

    @threaded_task
    def _send_event_to_event_server_task(
        self, event: Event, retrying: bool = False
    ) -> None:
        """Send an event to the event manager. Buffer on failure."""
        self._send_event_to_event_server(event, retrying=retrying)

    def _send_event_to_event_server(self, event: Event, retrying: bool = False) -> None:
        """Send an event to the event manager. Buffer on failure."""
        try:
            response = requests.post(
                url=self.event_server + "/event",
                json=event.model_dump(mode="json"),
                timeout=10,
            )
            if not response.ok:
                response.raise_for_status()
        except Exception:
            if not retrying:
                self._event_buffer.put(event)
                self._start_retry_thread()
            else:
                # If already retrying, just re-raise to trigger backoff
                raise

    def _new_event_for_log(self, event_data: Any, level: int) -> Event:
        """Create a new log event from arbitrary data"""
        event_type = EventType.LOG
        if level == logging.DEBUG:
            event_type = EventType.LOG_DEBUG
        elif level == logging.INFO:
            event_type = EventType.LOG_INFO
        elif level == logging.WARNING:
            event_type = EventType.LOG_WARNING
        elif level == logging.ERROR:
            event_type = EventType.LOG_ERROR
        elif level == logging.CRITICAL:
            event_type = EventType.LOG_CRITICAL
        if isinstance(event_data, BaseModel):
            event_data = event_data.model_dump(mode="json")
        else:
            try:
                event_data = json.dumps(event_data, default=str)
            except Exception:
                try:
                    event_data = str(event_data)
                except Exception:
                    event_data = {
                        "error": "Error during logging. Unable to serialize event data."
                    }
        return Event(
            event_type=event_type,
            event_data=event_data,
        )
