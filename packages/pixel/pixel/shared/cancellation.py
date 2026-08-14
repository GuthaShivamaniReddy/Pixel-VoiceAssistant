from dataclasses import dataclass, field
from threading import Event


@dataclass
class CancellationFlag:
    _event: Event = field(default_factory=Event)

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()


class CancelledError(Exception):
    """Provider work stopped because the turn was cancelled."""
