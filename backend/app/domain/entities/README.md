# Domain Entities

This folder contains the core business entities of the application.

## Purpose

Entities represent the fundamental business objects that encapsulate both state and behavior. They are:

- **Infrastructure-agnostic**: Independent of database, API, or framework concerns
- **Rich in business logic**: Contain the rules and operations that govern the domain
- **Identity-based**: Each entity has a unique identifier that persists across state changes

## What Goes Here

- Signal entities
- Market data entities
- User entities (future)
- Any other core business objects

## Example Structure

```python
# entities/signal.py
class Signal:
    def __init__(self, symbol: str, signal_type: SignalType, strength: float):
        self.id = None
        self.symbol = symbol
        self.signal_type = signal_type
        self.strength = strength
        self.created_at = datetime.utcnow()
    
    def is_strong(self) -> bool:
        return self.strength >= 80.0