# _# kat-transform_
Kittie's attempt to declaratively transform Python objects into serializable dictionaries.
Minimal, composable, Pydantic-free. Just fields, dataclasses, and a pinch of magic.

Features
- Declarative schema definition
- Field-level transformation
- Nested schemas
- Dependency-injected getters via FunDI
- No runtime overhead, no metaclasses, no opinionated data modeling
- Multiple getters(with fallback: `"created_at"` -> `"created"`)
- Custom field metadata and schema metadata

## Basic Usage:
```python
from dataclasses import dataclass
from datetime import datetime

from kat_transform import schema, field

user_schema = schema(
    "User",
    field(str, "username"),
    field(int, "id")
)

@dataclass
class User:
    username: str,
    id: int

user = User("Kuyugama", -1)

raw = user_schema.get(user)
transformed = user_schema.transform(raw)

assert transformed == {"username": "Kuyugama", "id": -1}

print(transformed)
```

## Deep dive

### Transform on the Fly
```python
from dataclasses import dataclass
from datetime import datetime

from kat_transform import schema, field

user_schema = schema(
    "User",
    field(str, "username", transform=lambda x: x.lower()),
    field(int, "created", transform=lambda x: int(x.timestamp()), getter=("created_at", "created")),
    field(int, "id")
)

@dataclass
class User:
    username: str,
    created_at: datetime
    id: int

user = User("Kuyugama", datetime(day=17, month=3, year=2026), -1)

raw = user_schema.get(user)
transformed = user_schema.transform(raw)

assert transformed == {"username": "kuyugama", "created": 1773612000, "id": -1}

print(transformed)
```

### DI-based getters (aka fields from the void)
```python
from dataclasses import dataclass
from datetime import datetime

from kat_transform import schema, field, resolve_fields

error_schema = schema(
    "Error",
    field(str, "message"),
    field(str, "category"),
    field(str, "code"),
    field(str, "cat", transform=lambda x: f"https://http.cat/{x}", getter=lambda response: response["status_code"])
)

@dataclass
class Error:
    message: str
    category: str
    code: str

error = Error("User not found", "users", "not-found")

raw = error_schema.get(error)

resolved = resolve_fields({"response": {"status_code": 404}}, raw)

transformed = error_schema.transform(resolved)

assert transformed == {"message": "User not found", "category": "users", "code": "not-found", "cat": "https://http.cat/404"}

print(transformed)
```
> ``resolve_fields`` uses FunDI dependency injection under the hood.
> All ``getter`` functions should be valid FunDI dependencies.

### Nested schemas? Awww, gotcha!

```python
from dataclasses import dataclass
from datetime import datetime

from kat_transform import schema, field, resolve_fields

user_schema = schema(
    "User",
    field(str, "username", transform=lambda x: x.lower()),
    field(int, "id"),
)

content_schema = schema(
    "Content",
    field(user_schema, "owner"),
    field(str, "title", transform=lambda x: x.title()),
)


@dataclass
class User:
    username: str
    id: int


@dataclass
class Content:
  owner: User
  title: str


user = User("Kuyugama", 1)

content = Content(user, "Clever flower")

raw = content_schema.get(content)

transformed = content_schema.transform(raw)

assert transformed == {"owner": {"username": "kuyugama", "id": 1}, "title": "Clever Flower"}

print(transformed)
```
