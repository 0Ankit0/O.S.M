from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


AnalyticsProperties = dict[str, Any]


@dataclass(slots=True)
class AnalyticsProviderConfig:
    provider: str
    api_key: str = ""
    host: str = ""
    extra: dict[str, Any] = field(default_factory=dict)
