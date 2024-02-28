from flask import Flask, render_template, redirect, request, url_for, session, flash, jsonify
from models.alchemy_models import db, Users, Genders, Photos, Sexualities
from utility.alchemy_utils import init_db_file
from utility.parsing import parse_nickname, parse_edit_gender, parse_edit_sexuality, parse_edit_age
from main import app
from models.alchemy_models import db, Users, Genders, Photos, Sexualities, Invitations, Pairs
import pytest
import time
import ast

def test_parse_gender():
    x = parse_edit_gender('some string')
    v = parse_edit_gender('2')
    z = parse_edit_gender(None)
    assert isinstance(x, int) or x is None
    assert isinstance(v, int) or v is None
    assert isinstance(z, int) or z is None


def test_parse_sexuality():
    x = parse_edit_sexuality('some string')
    v = parse_edit_sexuality('2')
    z = parse_edit_sexuality(None)
    assert isinstance(x, int) or x is None
    assert isinstance(v, int) or v is None
    assert isinstance(z, int) or z is None


def test_parse_age():
    x = parse_edit_age('some string')
    v = parse_edit_age('2')
    z = parse_edit_age(None)
    assert isinstance(x, int) or x is None
    assert isinstance(v, int) or v is None
    assert isinstance(z, int) or z is None


def test_users_query_time():
    with app.app_context():
        print("styartinnsdsssssss")
        start_time = time.time()
        rows = db.session.query(Users).count()
        end_time = time.time()
        print(f'time: {end_time - start_time}')
        start_time = time.time()
        rows = db.session.query(Users).all()
        end_time = time.time()
        print(f'time: {end_time - start_time}')


def test_get_list_of_random_id():
    with app.app_context():
        for i in range(10):
            print(Users.get_list_of_random_id(5))


def test_get_list_of_random_id():
    with app.app_context():
        start_time = time.time()
        for i in range(10):
            print(Users.get_number_of_random_users(5))
        end_time = time.time()
        print(f'time: {end_time - start_time}')


def test_get_main_photos_for_users():
    with app.app_context():
        start_time = time.time()
        tst_list = [1, 2, 3, 4, 7]
        data = Photos.get_main_photos_for_users(tst_list)
        end_time = time.time()
        assert len(data) <= len(tst_list)
        assert type(data) is list
        print(f'time: {end_time - start_time}')
        print(f'given list of photos: {data}')


def test_get_invitations_for_user():
    with app.app_context():
        start_time = time.time()
        invitations = Invitations.get_all_active_for_user(1)
        end_time = time.time()
        print(invitations)
        print(len(invitations))
        assert type(invitations) is list
        for invitation in invitations:
            assert isinstance(invitation,Invitations)


def test_get_pairs_for_user():
    with app.app_context():
        start_time = time.time()
        pairs = Pairs.find_all_for_user(1)
        end_time = time.time()
        print(pairs)
        print(len(pairs))
        assert type(pairs) is list
        if len(pairs) > 0:
            assert isinstance(pairs[0], Pairs)


def test_get_paired_users():
    with app.app_context():
        start_time = time.time()
        pairs = Pairs.find_all_for_user(1)
        #pairs = ['dfdfdf', 'sdsds']
        users = Pairs.get_all_paired_users(pairs, 1)
        end_time = time.time()
        print(users)
        print(len(users))
        assert isinstance(users, list)
        for user in users:
            assert isinstance(user, Users)

def test_get_invitation_by_id(id = 1):
    with app.app_context():
        invitation = Invitations.get_invitation_by_id(id)
        print(invitation)
        assert isinstance(invitation, Invitations)
