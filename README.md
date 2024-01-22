## API для проекта "Yamdb".

### Описание:

API проекта предназначен для взаимодействия бэкэнда "Yamdb" с различными ресурсами(фронтэнд, мобильные приложения и т.д.).
Для передачи данных используются файлы формата JSON.

### Использованные технологии

В этом проекте были использованы следующие технологии:

- Python - язык программирования, на котором написан проект. [Python документация](https://docs.python.org/3.9/)
- Django - веб-фреймворк для разработки веб-приложений. [Документация](https://docs.djangoproject.com/)
- Django REST framework - библиотека для создания RESTful API на основе Django. [Документация](https://www.django-rest-framework.org/)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/inferno681/api_yamdb
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### Импорт данных:

Для импорта данных необходимо выполнить следующую комманду в корневом каталоге проекта:

```
python csv_import
```

### Документация:

Документация и примеры доступны при развернутом и запущеном проекте по ссылке:

[Redoc](http://127.0.0.1:8000/redoc/)

Также документация находится по следующему адресу:
```
\api_yamdb\static\redoc.yaml
```

### Автор

- Kirill Konovalov, GitHub: [https://github.com/KeKcOn](https://github.com/KeKcOn)
- Vasilii Stakrotckii, GitHub: [https://github.com/inferno681](https://github.com/inferno681)
