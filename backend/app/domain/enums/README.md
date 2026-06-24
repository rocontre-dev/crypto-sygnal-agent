# Domain Enums

This folder contains enumeration types used throughout the domain model.

## Purpose

Enums provide type-safe constants for fixed sets of values that appear frequently in the domain. They improve code readability, prevent invalid values, and make the codebase more maintainable.

## What Goes Here

- Signal types (BUY, SELL, HOLD)
- Timeframes (1m, 5m, 15m, 1h, 4h, 1d, 1w)
- Indicator types (RSI, MACD, Bollinger Bands, etc.)
- Signal strength levels
- Any other fixed value sets

## Example Structure

```python
# enums/signal_type.py
from enum import Enum

class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

# enums/timeframe.py
from enum import Enum

class Timeframe(str, Enum):
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1d"
    WEEK_1 = "1w"