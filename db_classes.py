from peewee import *
from gunluk import db


class BaseModel(Model):
    class Meta:
        database = db


class UsersDiary(BaseModel):
    id = IntegerField()
    password = CharField()
    username = CharField()
    email = CharField()
    key = CharField()

    @staticmethod
    def check_username_exists(input_username):
        return UsersDiary.select().where(UsersDiary.username == input_username).exists()

    @staticmethod
    def get_password_of_user(input_username):
        return UsersDiary.get(UsersDiary.username == input_username).password

    @staticmethod
    def get_key_of_user(username):
        return UsersDiary.get(UsersDiary.username == username).key


class Articles(BaseModel):
    id = IntegerField()
    author = CharField()
    name = CharField()
    content = CharField()
    last_edited = CharField()

    @staticmethod
    def articles_of_user(username):
        return Articles.select().where(Articles.author == username)

    @staticmethod
    def delete_article(article_id):
        Articles.delete().where(Articles.id == article_id).execute()
        return "OK"

    @staticmethod
    def get_article(article_id):
        return Articles.get(Articles.id == article_id)

    @staticmethod
    def id_exists(name):
        return Articles.select().where(Articles.name == name).exists()
