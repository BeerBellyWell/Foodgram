# Описание

Проект представляет собой API для проекта Foodgram.

# foodgram
>На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

#### Как запустить проект:

+ IP: http://51.250.67.101

+ клонируем репозиторий `git clone`
`https://github.com/BeerBellyWell/foodgram-project-react`
+ переходим в него `cd foodgram-project-react/backend/foodgram`
    + разворачиваем виртуальное окружение
    `python3 -m venv env` (Windows: `python -m venv env`)
    + активируем его
    `source env/bin/activate` (Windows: `source env/scripts/activate`)
    + устанавливаем зависимости из файла requirements.txt
    `pip install -r requirements.txt`
+ выполняем миграции
`python3 manage.py migrate` (Windows: `python manage.py migrate`)
+ запускаем проект
`python3 manage.py runserver` (Windows: `python manage.py runserver).
И вперед!

####Инструкции и примеры

>Основные эндпойнты `/api/v1/`:

/users/ - Список пользователей

/tags/ - Теги

/recipes/ - Рецепты

/recipes/download_shopping_cart/ - Скачать список покупок

/recipes/{id}/shopping_cart/ -Добавить/удалить рецепт в список покупок

/recipes/{id}/favorite/ - Добавить/удалить рецепт в избранное

/users/subscriptions/ - Мои подписки

/users/{id}/subscribe/ - Подписаться/отписаться на пользователя

/ingredients/ - Список ингредиентов
