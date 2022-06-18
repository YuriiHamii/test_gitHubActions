import sqlite3
from flask import url_for
from flask_login import UserMixin


class UserLogin(UserMixin):

    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def getName(self):
        return self.__user['name'] if self.__user else "No name"

    def getEmail(self):
        return self.__user['email'] if self.__user else "No email"

    def getAvatar(self, application):
        img = None
        if not self.__user['avatar']:
            try:
                with application.open_resource(application.root_path + url_for('static', filename='images/default.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Avatar not found by default: " + str(e))
        else:
            img = self.__user['avatar']

        return img

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext == "png" or ext == "PNG":
            return True
        return False


