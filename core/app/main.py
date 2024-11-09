from fastapi import FastAPI
from sqladmin import Admin

from app.database import async_db

from app.views import UserView, FileTypeView, StorageFileView

app = FastAPI()
admin = Admin(app, async_db.engine)


for model in [UserView, FileTypeView, StorageFileView]:
    admin.add_view(model)
