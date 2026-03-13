# Foodgram API

Backend service for a recipe sharing platform.

The service allows users to publish recipes, subscribe to authors, add recipes to favorites, and generate shopping lists.

---

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Nginx
- Gunicorn
- GitHub Actions (CI/CD)

---

## Features

- User authentication
- Recipe publishing
- Subscriptions to authors
- Favorites
- Shopping list generation
- Filtering and pagination for recipes

---

## Architecture

The application follows a typical web service architecture.

Client → REST API → Database

- Client interacts with the API using HTTP requests
- Django REST Framework handles request processing
- PostgreSQL stores application data

---

## API Examples

### Create a recipe

POST `/api/recipes/`

Request example:

```json
{
  "name": "Pasta",
  "ingredients": [
    {"id": 1, "amount": 200}
  ],
  "cooking_time": 20
}
