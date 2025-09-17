"""
Message bus abstraction and implementations.
"""
from .db_outbox import DbOutboxBus

__all__ = ["DbOutboxBus"]
