from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from typing import Any

class JsonSanitizer:
    def __init__(self):
        try:
            import numpy as np
            self.np = np
        except ImportError:
            self.np = None

        try:
            import pandas as pd
            self.pd = pd
        except ImportError:
            self.pd = None

        try:
            from pydantic import BaseModel
            self.pydantic_model = BaseModel
        except ImportError:
            self.pydantic_model = None

        try:
            from dataclasses import is_dataclass, asdict
            self.is_dataclass = is_dataclass
            self.asdict = asdict
        except ImportError:
            self.is_dataclass = None
            self.asdict = None

    def sanitize(self, obj: Any) -> Any:
        try:
            if isinstance(obj, (str, int, float, bool)) or obj is None:
                return obj

            if isinstance(obj, dict):
                return {str(k): self.sanitize(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple, set)):
                return [self.sanitize(i) for i in obj]

            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            if isinstance(obj, Decimal):
                return float(obj)
            if isinstance(obj, UUID):
                return str(obj)

            if self.np:
                if isinstance(obj, (self.np.integer, self.np.floating)):
                    return obj.item()
                if isinstance(obj, self.np.ndarray):
                    return self.sanitize(obj.tolist())

            if self.pd:
                if isinstance(obj, self.pd.Series):
                    return self.sanitize(obj.to_dict())
                if isinstance(obj, self.pd.DataFrame):
                    return self.sanitize(obj.to_dict(orient="records"))

            if self.pydantic_model and isinstance(obj, self.pydantic_model):
                return self.sanitize(obj.model_dump())

            if self.is_dataclass and self.is_dataclass(obj):
                return self.sanitize(self.asdict(obj))

            for method_name in ("to_dict", "as_dict"):
                method = getattr(obj, method_name, None)
                if callable(method):
                    return self.sanitize(method())

            if hasattr(obj, "__dict__"):
                obj_dict = vars(obj)
                if obj_dict:
                    return self.sanitize(obj_dict)
                else:
                    return str(obj)

            return str(obj)

        except Exception:
            return str(obj)
