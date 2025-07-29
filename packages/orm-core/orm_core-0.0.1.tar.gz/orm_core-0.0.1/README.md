# ORM Manager Factory

<!-- [![PyPI Version](https://img.shields.io/pypi/v/orm-manager-factory.svg)](https://pypi.org/project/orm-manager-factory/) -->
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Универсальная фабрика для создания менеджеров работы с SQLAlchemy ORM, поддерживающая:
- Базовые CRUD-операции
- Автоматическую валидацию через Pydantic схемы
- Генерацию FastAPI роутеров

## 📦 Установка

```bash
pip install orm_core
```

## 🚀 Возможности

### 1. Базовый ORM менеджер
Работа с моделями SQLAlchemy без дополнительных схем.

### 2. Менеджер с Pydantic схемами
Автоматическая валидация входных/выходных данных.

### 3. Менеджер с автогенерацией FastAPI роутеров
Полноценное CRUD API из коробки.

## 🔧 Использование

### 1. Базовый ORM менеджер

```python
from orm_manager import ClientDB, create_orm_manager

class YourClientDB(ClientDB):
    def __init__(self, async_url: str):
        super().__init__(async_url)
        self.user = create_orm_manager(User)

db = YourClientDB("postgresql+asyncpg://user:pass@localhost:5432/db")

# Использование
await db.user.add(...)
await db.user.get_all(...)
await db.user.delete(...)
```

### 2. С Pydantic схемами

```python
class YourClientDB(ClientDB):
    def __init__(self, async_url: str):
        super().__init__(async_url)
        self.user = create_orm_manager(
            User,
            UserCreateSchema,
            UserUpdateSchema,
            UserOutSchema
        )

# Автоматическая валидация данных
await db.user.add(create_schema_instance)
```

### 3. С генерацией FastAPI роутеров

```python
class YourClientDB(ClientDB):
    def __init__(self, async_url: str):
        super().__init__(async_url)
        self.user = create_orm_manager(
            User,
            UserCreateSchema,
            UserUpdateSchema,
            UserOutSchema,
            session_factory=self.session_factory,
            api=True,
            tags=["Users"]
        )

app = FastAPI()
app.include_router(db.user.router)
```

## 📄 Лицензия

MIT License. См. файл [LICENSE](LICENSE).

## 🧑‍💻 Об авторе

Соловьёв Эрик - [GitHub](https://github.com/ErJokeCode)

