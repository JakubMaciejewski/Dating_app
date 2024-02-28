from flask_sqlalchemy import SQLAlchemy, session
from dataclasses import dataclass
from datetime import datetime
from random import randrange, choice, sample
from time import time
db = SQLAlchemy()


@dataclass
class Users(db.Model):
    __tablename__ = 'users'
    __allow_unmapped__ = True

    id: int
    nick: str
    email: str
    insert_data: str
    gender_id: int
    sexuality_id: int
    age: int
    account_desc: str
    list_of_interests: str

    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(50))
    email = db.Column(db.String(100))
    insert_data = db.Column(db.Date, default=datetime.utcnow())
    gender_id = db.Column(db.Integer, db.ForeignKey('genders.id'))
    gender: 'Genders' = db.relationship('Genders', primaryjoin=(
            f"Genders.id==Users.gender_id"),  backref=db.backref('user'))
    sexuality_id = db.Column(db.Integer, db.ForeignKey('sexualities.id'))
    sexuality: 'Sexualities' = db.relationship('Sexualities',primaryjoin=(
            f"Sexualities.id==Users.sexuality_id"),  backref=db.backref('user'))
    age = db.Column(db.Integer)
    account_desc = db.Column(db.String(200))
    list_of_interests = db.Column(db.String(300))

    '''
    def __setstate__(self, state):
        self.id = state['id']
        self.nick = state['name']
        self.email = state['email']
        self.insert_data = state['insert_data']
        self.gender_id = state['gender_id']
        self.sexuality_id = state['sexuality_id']
        self.age = state['age']
        self.account_desc = state['account_desc']
        self.list_of_interests = state['list_of_interests']
    '''

    @classmethod
    def get_user_by_nick_email(cls, nick: str, email: str):
        ''' checks if user with given nick and email exist in database and return it '''
        result = db.session.query(cls).filter(cls.nick == nick, cls.email == email).first()
        return result

    @classmethod
    def get_user_by_id(cls, id: int):
        '''returns user by given id'''
        result = db.session.query(cls).filter(cls.id == id).first()
        return result
    @classmethod
    def get_number_of_random_users(cls, number: int):
        '''find given number of users'''
        id_list = Users.get_list_of_random_id(number) # five for good start
        result = db.session.query(cls).filter(cls.id.in_(id_list)).all()
        return result
    @staticmethod
    def get_list_of_random_id(number: int):

        rows = db.session.query(Users).count()
        if rows < number:
            number = rows
        random_list = sample(range(1, rows), number)

        return random_list

    def update_user(self, age=None, gender_id=None, sex_id=None):

        print(f' arguments passed to update user: age {age} ,gender {gender_id},sex {sex_id}')
        if gender_id is not None:
            self.gender_id = gender_id
        if age is not None:
            self.age = age
        if sex_id is not None:
            self.sexuality_id = sex_id

        db.session.commit()


@dataclass
class Invitations(db.Model):
    __allow_unmapped__ = True
    id: int
    sender_id: int
    target_id: int
    active: int #1 - active # 0-refused # 2 -accepted
    insert_date: str
    update_date: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender: 'Users' = db.relationship('Users', primaryjoin=(
            f"Users.id==Invitations.sender_id"))

    target_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    target: 'Users' = db.relationship('Users', primaryjoin=(
            f"Users.id==Invitations.target_id"))

    active = db.Column(db.Integer, default=1)
    insert_date = db.Column(db.Date, default=datetime.utcnow())
    update_date = db.Column(db.Date, default=datetime.utcnow())

    @classmethod
    def get_all_active_for_user(cls, user_id: int) -> list:
        result = db.session.query(cls).filter(
            cls.target_id == user_id,
            cls.active == 1
        ).all()
        return result

    @classmethod
    def get_invitation_by_sender_target(cls, sender_id: int , target_id: int):
        result = db.session.query(cls).filter(
            cls.sender_id == sender_id,
            cls.target_id == target_id
        ).first()
        return result

    @classmethod
    def get_invitation_by_id(cls, id: int):
        result = db.session.query(cls).filter(
            cls.id == id
        ).first()
        if not isinstance(result, Invitations):
            raise ValueError("db object not found or not correct type")
        return result

    def reject_invitation(self):
        self.active = 0
        db.session.commit()

    def accept_invitation(self):
        new_pair = Pairs(user_one_id=self.sender_id, user_two_id=self.target_id)
        db.session.add(new_pair)
        self.active = 2
        db.session.commit()



@dataclass
class Pairs(db.Model):
    __allow_unmapped__ = True
    id: int
    user_one_id: int
    user_two_id: int
    insert_date: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_one_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_one: 'Users' = db.relationship('Users', primaryjoin=(
            f"Users.id==Pairs.user_one_id"))
    user_two_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_two: 'Users' = db.relationship('Users', primaryjoin=(
            f"Users.id==Pairs.user_two_id"))
    insert_date = db.Column(db.Date, default=datetime.utcnow())

    @classmethod
    def find_all_for_user(cls, id: int) -> list:
        result = db.session.query(cls).filter(
            (cls.user_one_id == id) |
            (cls.user_two_id == id)
        ).all()
        return result

    @classmethod
    def get_all_paired_users(cls, list_of_pairs: list, user_id: int) -> list:

        result = []

        if len(list_of_pairs) == 0:
            return result

        for pair in list_of_pairs:
            if pair.user_one_id != user_id:
                if pair.user_two_id == user_id:
                    result.append(pair.user_one)
                else:
                    pass
                    raise ValueError("given list of pairs is not correct. Check passed data")
            else:
                if pair.user_two_id != user_id:
                    result.append(pair.user_two)
                else:
                    raise ValueError("given list of pairs is not correct. Check passed data")

        return result
@dataclass
class Genders(db.Model):
    __tablename__ = 'genders'
    id: int
    name: str
    desc: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    desc = db.Column(db.String(100))
    '''
    def __init__(self,  dictionary=None):
        self.id = dictionary['id']
        self.name = dictionary['name']
        self.desc = dictionary['desc']
    '''
    @classmethod
    def get_all(cls):
        '''returning list of all genders'''
        result = db.session.query(cls).all()
        return result


@dataclass
class Photos(db.Model):
    id: int
    user_id: int
    path: str
    main_photo: int

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    path = db.Column(db.String(100))
    main_photo = db.Column(db.Integer, default=0)

    @classmethod
    def get_all_for_user(cls, user_id: int) -> list:
        '''returning list of photos of user '''
        result = db.session.query(cls).filter(cls.user_id == user_id).all()
        #print(f' result: {result}  type: {type(result)}')
        return result
    @classmethod
    def get_main_photos_for_users(cls, id_list: list) -> list:
        '''returning list of main photos for list of users by given ids'''
        result = db.session.query(cls).filter(
                cls.user_id.in_(id_list),
                cls.main_photo == 1).all()
        return result


@dataclass
class Sexualities(db.Model):
    id: int
    name: str
    desc: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    desc = db.Column(db.String(100))

    @classmethod
    def get_all(cls):
        '''returning list of all genders'''
        result = db.session.query(cls).all()
        return result
