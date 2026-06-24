# Domain Interfaces

This folder contains abstract base classes and interfaces that define contracts for domain services and repositories.

## Purpose

Interfaces provide abstraction layers that enable:

- **Loose coupling**: Components depend on abstractions, not concrete implementations
- **Testability**: Easy to mock dependencies for unit testing
- **Flexibility**: Multiple implementations can satisfy the same contract
- **Clear contracts**: Well-defined expectations for behavior

## What Goes Here

- `RepositoryInterface` - Base repository contract
- `ServiceInterface` - Base service contract
- `SignalServiceInterface` - Signal generation contract
- `MarketDataServiceInterface` - Market data contract
- `IndicatorServiceInterface` - Technical indicators contract
- Any other domain service contracts

## Example Structure

```python
# interfaces/repository_interface.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class RepositoryInterface(ABC, Generic[T]):
    """Base interface for all repositories."""
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass

# interfaces/signal_service_interface.py
class SignalServiceInterface(ABC):
    """Interface for signal generation service."""
    
    @abstractmethod
    async def generate_signal(self, symbol: str, timeframe: str) -> Signal:
        pass
    
    @abstractmethod
    async def get_signals(self, symbol: str, limit: int = 10) -> list[Signal]:
        pass