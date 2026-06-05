# Meeting Room Booking Service

Сервис бронирования переговорных комнат для коворкинга.

## Live Demo

API is deployed on Render:

https://meeting-room-booking-gyss.onrender.com/

Swagger documentation:

https://meeting-room-booking-gyss.onrender.com/docs

Demo users:

- employee / employee123
- admin / admin123

## Возможности

- JWT-аутентификация по логину и паролю.
- Роли пользователей: `employee` и `admin`.
- Просмотр списка переговорных комнат.
- Просмотр доступности всех комнат на выбранную дату.
- Создание бронирований сотрудниками.
- Отмена своих бронирований сотрудниками.
- Отмена любых бронирований администраторами.
- Защита от двойного бронирования одного активного слота.
- Хранение данных в PostgreSQL через SQLAlchemy.

## Стек

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Poetry
- Pytest
- Docker
- Docker Compose

## Запуск через Docker Compose

Собрать и запустить API вместе с PostgreSQL:

```bash
docker compose up --build
```

После запуска сервис доступен по адресу:

```text
http://localhost:8000
```

Демо-фронтенд:

```text
http://localhost:8000/
```

Документация OpenAPI:

```text
http://localhost:8000/docs
```

При старте контейнер API автоматически выполняет миграции Alembic и создаёт начальные данные.

Тестовые пользователи:

| Логин | Пароль | Роль |
| --- | --- | --- |
| `admin` | `admin123` | `admin` |
| `employee` | `employee123` | `employee` |
| `employee2` | `employee123` | `employee` |

## Запуск через Docker

Если PostgreSQL уже запущен и доступен по `DATABASE_URL`, можно запустить только контейнер API:

```bash
docker build -t meeting-room-booking .
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=postgresql://booking_user:booking_password@host.docker.internal:55432/booking_db \
  -e JWT_SECRET_KEY=change-this-secret-key \
  -e JWT_ALGORITHM=HS256 \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  meeting-room-booking
```

## Локальный запуск без Docker

Установить зависимости:

```bash
poetry install
```

Задать переменные окружения в `.env`:

```env
DATABASE_URL=postgresql://booking_user:booking_password@localhost:55432/booking_db
JWT_SECRET_KEY=change-this-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Применить миграции и создать начальные данные:

```bash
poetry run alembic upgrade head
poetry run python -m app.seed
```

Запустить API:

```bash
poetry run uvicorn app.main:app --reload
```

## Примеры запросов

Основные сценарии можно проверить через демо-фронтенд на `http://localhost:8000/`
или напрямую через API.

Получить JWT-токен:

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=employee&password=employee123"
```

Ответ:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

Посмотреть доступность комнат на дату:

```bash
curl "http://localhost:8000/rooms/availability?date=2030-01-01" \
  -H "Authorization: Bearer <jwt-token>"
```

Создать бронирование:

```bash
curl -X POST http://localhost:8000/bookings \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"room_id":1,"slot_id":1,"booking_date":"2030-01-01"}'
```

Посмотреть свои бронирования:

```bash
curl http://localhost:8000/bookings/my \
  -H "Authorization: Bearer <jwt-token>"
```

Отменить бронирование:

```bash
curl -X DELETE http://localhost:8000/bookings/1 \
  -H "Authorization: Bearer <jwt-token>"
```

## Тесты

Тесты написаны на `pytest` и используют базу данных из `DATABASE_URL`.

```bash
poetry run pytest
```
