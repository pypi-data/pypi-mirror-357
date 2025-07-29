# 🧼 cleanslay

**cleanslay** is a Python library that safely sanitizes complex objects into JSON-serializable structures.

It handles:

- Built-in types: `str`, `int`, `float`, `bool`, `None`
- Collections: `dict`, `list`, `tuple`, `set`
- Special types: `datetime`, `date`, `UUID`, `Decimal`
- Libraries:
  - ✅ Pydantic models
  - ✅ Dataclasses
  - ✅ NumPy arrays and scalars
  - ✅ Pandas Series and DataFrames
- Fallback for custom classes

---

## 🔧 Installation

```
pip install cleanslay
```

## For development

```
poetry install --extras "test"
or
pip3 install ".[test]"
```

## For testing

```
pytest tests --tb=short --disable-warnings
```
