# Foodgram — Продуктовый помощник

![Foodgram workflow](https://github.com/dmitrii23/foodgram/actions/workflows/main.yml/badge.svg)

**Foodgram** — это социальная сеть и сервис для обмена рецептами. Пользователи могут публиковать свои кулинарные открытия, подписываться на интересных авторов, добавлять рецепты в избранное и формировать список покупок для похода в магазин.

**Проект доступен по адресу:** [http://62.84.123.151](http://62.84.123.151)

---

## О проекте
Данный репозиторий содержит реализацию **Backend-составляющей** приложения и конфигурацию для его **развертывания**. Backend спроектирован с нуля с акцентом на производительность и безопасность. Frontend реализован на **React** и интегрирован с API.

### Ключевой функционал Backend:
- **Аутентификация**: Реализована на базе Token Authentication (Djoser).
- **Подписки**: Система фолловинга за авторами рецептов.
- **Избранное и Корзина**: Управление персональными списками рецептов.
- **Список покупок**: Агрегация необходимых ингредиентов из разных рецептов и экспорт в текстовый файл.
- **Короткие ссылки**: Генерация уникальных коротких URL для быстрого обмена рецептами.

---

## Технологический стек

### Backend & API:
- **Python 3.12** / **Django 5.2** — проектирование архитектуры и серверной логики.
- **Django REST Framework (DRF)** — построение RESTful API.
- **PostgreSQL** — надежное хранилище данных.
- **Django Filter** — гибкая система фильтрации (по тегам, автору, наличию в списках).
- **Optimization**: Использование `prefetch_related` для решения проблемы N+1 и `Exists`/`annotate` для эффективной выборки связанных данных.
- **Djoser**: Управление пользователями и аутентификацией.

### Infrastructure & DevOps:
- **Docker & Docker Compose** — оркестрация контейнеров для backend, db и nginx.
- **Nginx** — реверс-прокси, обработка статики и медиа, поддержка Redoc.
- **Gunicorn** — стабильный WSGI-сервер.
- **GitHub Actions** — автоматизированный CI/CD пайплайн (тесты, сборка образов, деплой на VPS).

### Frontend:
- **React** — клиентское SPA-приложение.

---

## Установка и запуск

### Локальный запуск (Docker)

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/dmitrii23/foodgram.git
   cd foodgram
   ```

2. Создайте файл `.env` в директории `infra/` по образцу:
   ```env
   POSTGRES_USER=django
   POSTGRES_PASSWORD=django
   POSTGRES_DB=django
   DB_HOST=db
   DB_PORT=5432
   SECRET_KEY=your_secret_key
   DEBUG=False
   ALLOWED_HOSTS=127.0.0.1, localhost, <your_ip>
   ```

3. Запустите контейнеры:
   ```bash
   docker compose -f infra/docker-compose.production.yml up -d
   ```

4. Выполните миграции и подготовьте статику:
   ```bash
   docker compose -f infra/docker-compose.production.yml exec backend python manage.py migrate
   docker compose -f infra/docker-compose.production.yml exec backend python manage.py collectstatic --no-input
   ```

5. Загрузите базу ингредиентов:
   ```bash
   docker compose -f infra/docker-compose.production.yml exec backend python manage.py load_ingredients data/ingredients.csv
   ```

---

## Документация API
Спецификация API в формате Redoc доступна после запуска проекта по адресу:
`http://localhost:8080/api/docs/` (или по IP вашего сервера).

---

## Автор
**Дмитрий**
- Backend разработка
- Проектирование архитектуры БД
- Настройка инфраструктуры и CI/CD деплоя
- [GitHub Profile](https://github.com/Dmtrii-Zverev)
