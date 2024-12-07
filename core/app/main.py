from fastapi import FastAPI
from sqladmin import Admin

from app.database import async_db

from app.views import UserView, FileTypeView, StorageFileView, GroupView

# Инициализация FastAPI-приложения
app = FastAPI()
# Инициализация админ-панели
admin = Admin(app, async_db.engine)


# Добавление вью с ORM-моделями в админ-панель
for model in [UserView, FileTypeView, StorageFileView, GroupView]:
    admin.add_view(model)
