from os import path
from datetime import datetime
from dataclasses import dataclass
from models.alchemy_models import db, Photos
from dataclasses import fields
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import werkzeug
from datetime import datetime
from random import choice


def init_db_file(app: Flask):
    ''' checks if file exist if not create database file with all necessary tables \n
    needs app object for app.app_context() method'''

    if not path.exists('C:/Users/kuba/PycharmProjects/pythonProject1/database.db'):
        with app.app_context():
            db.create_all()

            print(f"database file created on {datetime.now()}")


def save_uploaded_photos(file: werkzeug.datastructures.file_storage.FileStorage, user_id):
    now = datetime.now()
    date_time = now.strftime("%m_%d_%Y_%H_%M_%S")
    filepath = f'/user_images/{user_id}{date_time}'

    file.save('C:/Users/kuba/PycharmProjects/pythonProject1/Static' + filepath) #hardcoded ... to change in future
    print(f' photo {filepath} saved on server')
    if not Photos.get_all_for_user(user_id):
        photo = Photos(user_id=user_id, path=filepath, main_photo=1)
    else:
        photo = Photos(user_id=user_id, path=filepath)
    db.session.add(photo)
    db.session.commit()
    print(f'photo {filepath} saved in database')


def date_conversion(date_str:str) -> str:

    parts = date_str.split()

    month_mapping = {
        'Jan': '1',
        'Feb': '2',
        'Mar': '3',
        'Apr': '4',
        'May': '5',
        'Jun': '6',
        'Jul': '7',
        'Aug': '8',
        'Sep': '9',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12',
    }
    formatted_date_str = f"datetime.date({parts[3]}, {month_mapping[parts[2]]}, {parts[1]})"
    return formatted_date_str
