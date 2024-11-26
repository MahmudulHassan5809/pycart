import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class CustomJSONEncoder(Generic[T], json.JSONEncoder):
    def default(self, o: T) -> str | dict[str, Any]:
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, (Decimal, bool)):
            return str(o)
        if isinstance(o, BaseModel):
            return o.model_dump()
        return str(super().default(o))
