import dataclasses
import typing as t


@dataclasses.dataclass
class Events:
    """Application events register."""

    startup: list[t.Callable[..., t.Coroutine[t.Any, t.Any, None]]] = dataclasses.field(default_factory=list)
    shutdown: list[t.Callable[..., t.Coroutine[t.Any, t.Any, None]]] = dataclasses.field(default_factory=list)

    def register(self, event: str, handler: t.Callable) -> None:
        """Register a new event.

        :param event: Event type.
        :param handler: Event handler.
        """
        assert event in {f.name for f in dataclasses.fields(self)}, f"Wrong event: {event}."
        getattr(self, event).append(handler)

    @classmethod
    def build(cls, **events: list[t.Callable[..., t.Coroutine[t.Any, t.Any, None]]]) -> "Events":
        """Build events register from dict.

        :param events: Events to register.
        :return: Events instance.
        """
        keys = set(events.keys()) - {f.name for f in dataclasses.fields(cls)}
        assert not keys, f"Wrong event{'s' if len(keys) > 1 else ''}: {', '.join(keys)}."
        return cls(**events)
