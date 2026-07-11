# Трекер задач сотрудников

## Описание проекта

Серверное приложение для работы с базой данных, представляющее собой трекер задач сотрудников.  
Приложение обеспечивает CRUD-операции для сотрудников и задач, а также предоставляет специальные эндпоинты для анализа загруженности сотрудников и поиска важных задач.

## Задание дипломного проекта

### Требования к базе данных

1. База данных реляционная.
2. Используется PostgreSQL.
3. Структура базы данных:
   - таблица сотрудников:
     - ФИО;
     - должность;
     - дополнительные поля;
   - таблица задач:
     - наименование;
     - описание;
     - ссылка на родительскую задачу;
     - исполнитель;
     - срок;
     - статус;
     - приоритет;
     - дополнительные поля.

### Функциональность

1. CRUD для сотрудников и задач.
2. Специальные эндпоинты:
   - **Занятые сотрудники** — список сотрудников и их активных задач, отсортированный по количеству активных задач.
   - **Важные задачи** — задачи, которые не взяты в работу, но от которых зависят другие задачи, находящиеся в работе. Для таких задач подбираются подходящие сотрудники:
     - наименее загруженный сотрудник;
     - сотрудник, выполняющий родительскую задачу, если его загрузка не превышает загрузку наименее загруженного сотрудника более чем на 2 задачи.

## Технические требования

1. Язык программирования: Python 3.12 и выше.
2. Фреймворк: Django + Django REST Framework.
3. База данных: PostgreSQL.
4. ORM: Django ORM.
5. Контейнеризация: Docker.
6. Валидация данных: через сериализаторы DRF.
7. Документация: README.md с описанием проекта, установки, запуска и API.
8. Качество кода: соблюдение PEP8.
9. Тестирование: покрытие тестами не менее 75%.
10. Автодокументация: Swagger / ReDoc.

## Структура проекта

```text
Employee_Task_Tracker_project/
├── config/                         # Настройки проекта
│   ├── settings.py                 # Общие настройки (PostgreSQL, DRF, SimpleJWT, drf-spectacular)
│   └── urls.py                     # Корневой роутинг (admin, API, схема, Swagger/Redoc)
│
├── users/                          # Приложение сотрудников
│   ├── models.py                   # Кастомная модель пользователя
│   ├── serializers.py              # Сериализаторы для чтения и создания пользователей
│   ├── views.py                    # UserViewSet, логика CRUD
│   ├── urls.py                     # DRF DefaultRouter для /api/users/
│   └── tests.py                    # Тесты
│
├── employee_tasks/                 # Приложение задач
│   ├── models.py                   # Модель Task
│   ├── serializers.py              # Сериализаторы задач и спецэндпоинтов
│   ├── views.py                    # TaskViewSet, BusyEmployeesView, ImportantTasksView
│   ├── urls.py                     # Роуты /api/tasks/, /api/busy-employees/, /api/important-tasks/
│   ├── tests.py                    # Тесты специальных эндпоинтов
│   └── tests_crud.py               # Тесты CRUD для задач
│
├── ui/                             # Веб-интерфейс на Django templates
│   ├── views.py                    # Dashboard, Users, Tasks, Analytics
│   ├── urls.py                     # Маршруты UI-страниц
│   └── templates/                  # Шаблоны страниц интерфейса
│
├── templates/                      # Общие шаблоны проекта
│   ├── base_ui.html                # Базовый шаблон UI
│   ├── dashboard.html              # Главная панель
│   ├── users_list.html             # Страница сотрудников
│   ├── tasks_list.html             # Страница задач
│   ├── analytics.html              # Страница аналитики
│   └── rest_framework/
│       └── api.html                # Шаблон оформления browsable API
│
├── static/                         # Статические файлы
│   └── css/
│       └── bootstrap.min.css       # Локальная копия Bootstrap 5
│
├── manage.py                       # Точка входа Django-проекта
├── .env-sample                     # Шаблон переменных окружения
├── pyproject.toml                  # Зависимости и настройки Poetry
└── requirements.txt                # Зависимости для pip
```

## Установка и запуск

Проект можно установить и запустить двумя способами: через Poetry или через pip с использованием `venv`.

### Требования

- Python 3.12 или выше;
- PostgreSQL;
- Git.

### Вариант 1. Установка через Poetry

1. Установите Poetry, если он ещё не установлен:

```bash
pip install poetry
```

2. Клонируйте репозиторий и перейдите в папку проекта:

```bash
git clone https://github.com/Nekrontir/Employee_Task_Tracker_project.git
cd Employee_Task_Tracker_project
```

3. Установите зависимости:

```bash
poetry install
```

4. Активируйте виртуальное окружение Poetry:

```bash
source "$(poetry env info --path)/bin/activate"
```

или:

```bash
eval "$(poetry env activate)"
```

5. Создайте файл `.env` на основе шаблона:

```bash
cp .env-sample .env
```

6. Заполните переменные подключения к PostgreSQL.

7. Примените миграции:

```bash
python manage.py migrate
```

8. Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

9. Запустите сервер:

```bash
python manage.py runserver
```

### Вариант 2. Установка через pip и venv

1. Клонируйте репозиторий и перейдите в папку проекта:

```bash
git clone https://github.com/Nekrontir/Employee_Task_Tracker_project.git
cd Employee_Task_Tracker_project
```

2. Создайте виртуальное окружение:

```bash
python3 -m venv .venv
```

или:

```bash
py -m venv .venv
```

3. Активируйте окружение:

- Linux / macOS:

```bash
source .venv/bin/activate
```

- Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

4. Установите зависимости:

```bash
pip install -r requirements.txt
```

5. Создайте файл `.env` на основе шаблона:

```bash
cp .env-sample .env
```

6. Заполните переменные подключения к PostgreSQL.

7. Примените миграции:

```bash
python manage.py migrate
```

8. Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

9. Запустите сервер:

```bash
python manage.py runserver
```

## Доступные адреса

- Админка: `http://127.0.0.1:8000/admin/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`

## Веб-интерфейс

В проекте реализован простой веб-интерфейс на Django templates с использованием Bootstrap 5.

### Страницы UI

- Главная панель: `/`
- Сотрудники: `/users/`
- Задачи: `/tasks/`
- Аналитика: `/analytics/`

### Назначение страниц

- **Главная панель** — навигация по основным разделам проекта.
- **Сотрудники** — список сотрудников.
- **Задачи** — список задач с фильтрацией по приоритету.
- **Аналитика** — информация о загруженности сотрудников и важных задачах.

## Описание API

### Авторизация

Используется `djangorestframework-simplejwt`.

#### Получение токена

```http
POST /api/token/
```

Тело запроса:

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

Ответ:

```json
{
  "access": "<ACCESS_TOKEN>",
  "refresh": "<REFRESH_TOKEN>"
}
```

#### Обновление токена

```http
POST /api/token/refresh/
```

### CRUD сотрудников

#### Список сотрудников

```http
GET /api/users/
```

#### Создание сотрудника

```http
POST /api/users/
```

#### Просмотр, обновление и удаление

```http
GET /api/users/{id}/
PUT /api/users/{id}/
PATCH /api/users/{id}/
DELETE /api/users/{id}/
```

### CRUD задач

#### Список задач

```http
GET /api/tasks/
```

#### Создание задачи

```http
POST /api/tasks/
```

#### Просмотр, обновление и удаление

```http
GET /api/tasks/{id}/
PUT /api/tasks/{id}/
PATCH /api/tasks/{id}/
DELETE /api/tasks/{id}/
```

### Специальные эндпоинты

#### Занятые сотрудники

```http
GET /api/busy-employees/
```

Пример ответа:

```json
[
  {
    "id": 3,
    "full_name": "Иванов Иван Иванович",
    "position": "Backend Developer",
    "active_tasks_count": 5
  }
]
```

#### Важные задачи

```http
GET /api/important-tasks/
```

Пример ответа:

```json
[
  {
    "important_task": "Настроить CI/CD",
    "deadline": "2026-07-20",
    "employees": [
      "Петров Петр Петрович",
      "Иванов Иван Иванович"
    ]
  }
]
```

Полная спецификация API доступна в Swagger и ReDoc.

## Тесты и покрытие

Запуск тестов:

```bash
python manage.py test
```

Проверка покрытия:

```bash
coverage run --source="." manage.py test
coverage report -m
```

Фактическое покрытие проекта превышает 75%.

## Статические файлы

Для оформления browsable API используется локальная копия Bootstrap 5:

- файл `bootstrap.min.css` находится в `static/css/`;
- в шаблоне `templates/rest_framework/api.html` он подключается через `{% static %}`;
- настройки статики указаны в `STATIC_URL` и `STATICFILES_DIRS`.

## Docker

Если в проекте настроены `Dockerfile` и `docker-compose.yml`, то запуск осуществляется так:

```bash
docker-compose up --build
```

После запуска:

- приложение доступно по `http://localhost:8000/`;
- база данных PostgreSQL запускается в отдельном контейнере.