"""
Domain events for the identity bounded context.
Implements event-driven architecture patterns for loose coupling.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID


class DomainEvent(Protocol):
    """Protocol for domain events."""

    occurred_at: datetime
    aggregate_id: UUID


@dataclass(frozen=True)
class UserRegistered:
    """Event fired when a new user registers."""

    aggregate_id: UUID
    email: str
    full_name: str
    occurred_at: datetime = datetime.now(UTC)


@dataclass(frozen=True)
class UserEmailVerified:
    """Event fired when user verifies their email."""

    aggregate_id: UUID
    email: str
    occurred_at: datetime = datetime.now(UTC)


@dataclass(frozen=True)
class UserLoggedIn:
    """Event fired when user successfully logs in."""

    aggregate_id: UUID
    email: str
    ip_address: str | None
    occurred_at: datetime = datetime.now(UTC)


@dataclass(frozen=True)
class UserPasswordChanged:
    """Event fired when user changes password."""

    aggregate_id: UUID
    email: str
    occurred_at: datetime = datetime.now(UTC)


class DomainEventDispatcher:
    """Dispatcher for domain events."""

    def __init__(self) -> None:
        self._handlers: dict[
            type[DomainEvent], list[Callable[[DomainEvent], None]]
        ] = {}

    def register(
        self, event_type: type[DomainEvent], handler: Callable[[DomainEvent], None]
    ) -> None:
        """Register event handler."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def dispatch(self, event: DomainEvent) -> None:
        """Dispatch event to registered handlers."""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)


event_dispatcher = DomainEventDispatcher()
