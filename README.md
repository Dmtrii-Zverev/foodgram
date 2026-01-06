### проект foodgram размещен на виртуальном удаленном сервере и доступен по IP 62.84.123.151
# Foodgram — сайт, на котором пользователи могут публиковать собственные рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Foodgram — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создать список продуктов, которые нужно купить для приготовления выбранных блюд. Это полностью рабочий проект, который состоит из бэкенда в виде REST API сервиса на Django и фронтенда - одностраничного SPA-приложение, написанное на фреймворке React.

## Используемые технологии

*   Python 3.12: Основной язык разработки.
*   Django: версия 5.2.8
*   Django REST Framework 3.16.1
*   Docker версия 28.5.1.
*   PostgreSql версия 16-alpine
*   nginx версия 1.25.4-alpine.
*   gunicorn версия 20.1.0
*   React версия 17.0.1


## Установка через Docker на локальную машину.

Для локального запуска следуйте этим инструкциям:

1. Клонирование репозитория.
В командной строке:
- git clone https://github.com/Dmtrii-Zverev/foodgram.git

2. Запустите Docker Compose, находясь в корневой директории проекта.
Перейти в папку проекта:
- cd infra/
Запустите Docker Compose:
- docker compose up -d

3. Выполните команду сборки статики.
Собрать статику Django:
- docker compose exec backend python manage.py collectstatic
копируем статику в /backend_static/static/:
- docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
4. Применение миграций базы данных.
- docker compose exec backend python manage.py migrate

5. Создание суперпользователя и заргузка ингредиентов в бд для корректной работы приложения:
- docker compose exec -it backend bash
- python manage.py createsuperuser
- python manage.py load_ingredients apps/recipes/ingredients.csv

## Примеры запросов
#### Путь для авторизации:
http://localhost/signin/
#### Путь для регистрации:
http://localhost/signup/
#### Путь для добавления рецептов:
http://localhost/recipes/create/
#### Путь для получения списка рецептов:
http://localhost/
#### путь для получения экземпляра рецепта:
http://localhost/recipes/id/


## Авторы 
Дмитрий Зверев: 
https://github.com/Dmitrii-Zverev

Яндекс практикум: 
https://github.com/yandex-praktikum 
 
