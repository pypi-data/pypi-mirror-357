import pytest
import numpy as np
import pandas as pd
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, date
from cleanslay import JsonSanitizer

try:
    from pydantic import BaseModel

    class User(BaseModel):
        id: str
        name: str
        created: datetime
except ImportError:
    User = None

@pytest.fixture
def sanitizer():
    return JsonSanitizer()

def test_basic_types(sanitizer):
    assert sanitizer.sanitize("hello") == "hello"
    assert sanitizer.sanitize(123) == 123
    assert sanitizer.sanitize(True) is True
    assert sanitizer.sanitize(None) is None

def test_datetime_uuid_decimal(sanitizer):
    now = datetime.utcnow()
    assert sanitizer.sanitize(now) == now.isoformat()
    assert sanitizer.sanitize(date(2023, 1, 1)) == "2023-01-01"
    assert sanitizer.sanitize(Decimal("12.34")) == 12.34
    uid = uuid4()
    assert sanitizer.sanitize(uid) == str(uid)

def test_collections(sanitizer):
    assert sanitizer.sanitize({"a": 1, "b": 2}) == {"a": 1, "b": 2}
    assert sanitizer.sanitize([1, 2, 3]) == [1, 2, 3]
    assert sanitizer.sanitize((4, 5)) == [4, 5]
    assert sanitizer.sanitize({6, 7}) == [6, 7]

def test_numpy(sanitizer):
    arr = np.array([1, 2, 3])
    assert sanitizer.sanitize(arr) == [1, 2, 3]
    assert sanitizer.sanitize(np.int64(5)) == 5
    assert sanitizer.sanitize(np.float32(3.14)) == pytest.approx(3.14)

def test_pandas(sanitizer):
    s = pd.Series([1, 2], index=["a", "b"])
    assert sanitizer.sanitize(s) == {"a": 1, "b": 2}
    df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    assert sanitizer.sanitize(df) == [{"x": 1, "y": 3}, {"x": 2, "y": 4}]

@pytest.mark.skipif(User is None, reason="Pydantic not installed")
def test_pydantic_model(sanitizer):
    user = User(id="abc", name="Alice", created=datetime(2020, 1, 1))
    result = sanitizer.sanitize(user)
    assert result["id"] == "abc"
    assert result["name"] == "Alice"
    assert result["created"] == "2020-01-01T00:00:00"

def test_unknown_object(sanitizer):
    class Thing:
        def __str__(self):
            return "custom thing"
    t = Thing()
    assert sanitizer.sanitize(t) == "custom thing"
