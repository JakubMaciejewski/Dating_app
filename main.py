from flask import Flask, render_template, redirect, request, url_for, session, flash, jsonify
from models.alchemy_models import db, Users, Genders, Photos, Sexualities, Invitations, Pairs
from utility.alchemy_utils import init_db_file, save_uploaded_photos, date_conversion
from utility.parsing import parse_nickname, parse_edit_gender, parse_edit_sexuality, parse_edit_age
from dataclasses_json import dataclass_json
from werkzeug.utils import secure_filename
from datetime import date,datetime


app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///C:/Users/kuba/PycharmProjects/pythonProject1/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
init_db_file(app)


@app.route("/")
def index():
    if 'logged in' in session:
        print(session)
        return redirect(url_for('loggedIn'))
    else:
        return redirect(url_for('start'))


@app.route("/logout")
def logout():
    session.clear()
    flash('You were successfully logged out ', 'info')
    for item in session.items():
        print(f'{item}   ::   {type(item)}')
    return redirect(url_for('start'))


@app.route("/start", methods=['GET', 'POST'])
def start():

    if request.method == 'GET':
        if 'logged in' in session:
            return redirect(url_for('loggedIn'))
        else:
            return render_template("start.html")
    else:
        email = request.form["start_email_textfield"]
        nick = request.form["start_nick_textfield"]
        user = Users.get_user_by_nick_email(nick, email)
        if user:
            session['user'] = user
            session['logged in'] = True
            return redirect(url_for('loggedIn'))
        else:
            flash("incorrect nickname or email")
            flash("please try again")
        # check if data from post correct
        return render_template("start.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:

        email = request.form["email_textfield"]
        nick = parse_nickname(request.form['nick_textfield'])

        if nick is None:
            flash("incorrect data", 'info')
            return render_template("register.html")
        else:
            new_user = Users(nick=nick, email=email)
            db.session.add(new_user)
            db.session.commit()

            user = Users.get_user_by_nick_email(nick, email)
            session['user'] = user
            session['logged in'] = True
            flash("account has been created!", 'info')
            flash("now you have full access to our services", 'info')
            flash("Remember to fill out all our personal data in settings tab", 'info')

            return redirect(url_for('loggedIn'))


@app.route("/loggedIn", methods=['GET', 'POST'])
def loggedIn():

    if 'logged in' in session:

        user_data = session.get('user')

        # print(type(user_data))
        # print(user_data)
        if 'gender' in user_data:
            if user_data['gender'] is not None:
                user_data['gender'] = Genders(**user_data['gender']) #TO DO SEXUALITIES rework
        user = Users(**user_data)

        if request.method == "GET":

            invitations = Invitations.get_all_active_for_user(user.id)  # show invitations logic
            session['invitations'] = invitations  # save to session memory - don't need to ask database
            # print(f" invitations in session: {session.get('invitations')} type : {type(session.get('invitations'))}")
            ids = [invitation.sender.id for invitation in invitations]
            users_photo_dict = dict()
            photos = Photos.get_main_photos_for_users(ids)
            for invitation in invitations:
                for photo in photos:
                    if invitation.sender.id == photo.user_id:
                        users_photo_dict[invitation.sender.id] = photo  # get photo for all invitation users
            # print(users_photo_dict)

            paired_users = Pairs.get_all_paired_users(Pairs.find_all_for_user(user.id), user.id)
            paired_users_photos_dic = dict()
            paired_ids = [user.id for user in paired_users]
            paired_user_photos = Photos.get_main_photos_for_users(paired_ids)

            for user in paired_users:
                for photo in paired_user_photos:
                    if user.id == photo.user_id:
                        paired_users_photos_dic[user.id] = photo  # get photo for all paired users

            #print(f" users paired: {paired_users} type of users: {type(paired_users)}")

            return render_template("logged_in.html", user=user, invitations=invitations, photos=users_photo_dict,\
                                   paired_users=paired_users, paired_user_photos=paired_users_photos_dic)

        if request.method == 'POST':
            invitations = Invitations.get_all_active_for_user(user.id)  # show invitations logic

            if 'profile_to_view' in request.form:
                data = request.form['profile_to_view']
                data = int(data)
                user_to_show = Users.get_user_by_id(data)
                session['user_to_show'] = user_to_show

                return redirect(url_for('view_profile'))

            elif 'accept' in request.form:
                id = request.form['accept']
                id = int(id)
                for invitation in invitations:
                    if invitation.id == id:
                        invitation.accept_invitation()
                        invitations.remove(invitation)

            elif 'reject' in request.form:
                id = request.form['reject']
                id = int(id)

                for invitation in invitations:
                    if invitation.id == id:
                        invitation.reject_invitation()
                        invitations.remove(invitation)

            session['invitations'] = invitations  # save to session memory - don't need to ask database
            #print(f" invitations in session: {session.get('invitations')} type : {type(session.get('invitations'))}")
            ids = [invitation.sender.id for invitation in invitations]
            users_photo_dict = dict()
            photos = Photos.get_main_photos_for_users(ids)
            for invitation in invitations:
                for photo in photos:
                    if invitation.sender.id == photo.user_id:
                        users_photo_dict[invitation.sender.id] = photo  # get photo for all invitationg users
            # print(users_photo_dict)
            paired_users = Pairs.get_all_paired_users(Pairs.find_all_for_user(user.id), user.id)
            paired_users_photos_dic = dict()
            paired_ids = [user.id for user in paired_users]
            paired_user_photos = Photos.get_main_photos_for_users(paired_ids)

            for user in paired_users:
                for photo in paired_user_photos:
                    if user.id == photo.user_id:
                        paired_users_photos_dic[user.id] = photo  # get photo for all paired users

            #print(f" users paired: {paired_users} type of users: {type(paired_users)}")

            return render_template("logged_in.html", user=user, invitations=invitations, photos=users_photo_dict,\
                                   paired_users=paired_users, paired_user_photos=paired_users_photos_dic)
    else:
        return redirect(url_for('start'))


@app.route("/settings/view",methods=['GET', 'POST'])
def settings_view():

    if 'logged in' in session:
        user = session['user']
        photos = Photos.get_all_for_user(session['user']['id'])

        return render_template("view_settings.html", user=user, photos=photos)
    else:
        return redirect(url_for('start'))


@app.route("/find_new", methods=['GET', 'POST'])
def find_new():
    if request.method == 'GET':
        users = Users.get_number_of_random_users(5)
        user_id_list = [user.id for user in users]
        print(f'user id list: {user_id_list}')
        photos = Photos.get_main_photos_for_users(user_id_list)
        users_photo_dict = dict()
        for user in users:
            for photo in photos:
                if user.id ==photo.user_id:
                    users_photo_dict[user.id] = photo
        print(users_photo_dict)
        return render_template("find_new.html", users=users, photos=users_photo_dict)

    if request.method == 'POST':

        print(request.form)
        print(type(request.form))
        if 'data' in request.form:
            data = request.form['data']
            data = int(data)
            user_to_show = Users.get_user_by_id(data)
            session['user_to_show'] = user_to_show

            return redirect(url_for('view_profile'))

        elif 'invitation' in request.form:
            user_data = session.get('user')
            print(user_data)
            print(type(user_data))
            if 'gender' in user_data:
                if user_data['gender'] is not None:
                    user_data['gender'] = Genders(**user_data['gender']) #TO DO SEXUALITIES
            user = Users(**user_data)
            print(user)
            print(type(user))
            target_id = request.form['invitation']
            target_id = int(target_id)

            new_invitation = Invitations(sender_id=user.id, target_id=target_id)
            db.session.add(new_invitation)
            db.session.commit()
            return redirect(url_for('find_new'))


@app.route("/view_profile",methods=['GET', 'POST'])
def view_profile():
    user_to_show = session['user_to_show']
    photos = Photos.get_all_for_user(session['user_to_show']['id'])
    session.pop('user_to_show')
    return render_template("view_profile.html", user=user_to_show, photos=photos)


@app.route("/settings/edit",methods=['GET', 'POST'])
def settings_edit():

    if 'logged in' in session:

        user_info = session['user']
        photos = Photos.get_all_for_user(session['user']['id'])

        if request.method == 'GET':
            genders = Genders.get_all()
            sexualities = Sexualities.get_all()

            return render_template("edit_settings.html", user=user_info, genders=genders, sexualities=sexualities, photos=photos)

        else:

            if 'uploaded_photo' in request.files:
                file = request.files['uploaded_photo']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    print(type(file))
                    print(filename)

                    save_uploaded_photos(file, session['user']['id'])
                    photos = Photos.get_all_for_user(session['user']['id'])

                    return render_template("view_settings.html", user=user_info, photos=photos)

            elif 'gender_select' and 'sex_select' and 'age_select' in request.form:

                gender_id = parse_edit_gender(request.form['gender_select'])
                sex_id = parse_edit_sexuality(request.form['sex_select'])
                age = parse_edit_age(request.form['age_select'])
                print(f" gender passed {gender_id}")
                print(f" sex passed {request.form['sex_select']}")
                print(f"age passed {request.form['age_select']}")
                nick = session['user']['nick']
                email = session['user']['email']
                user = Users.get_user_by_nick_email(nick, email)
                user.update_user(gender_id=gender_id, sex_id=sex_id, age=age)
                db.session.commit()
                session['user'] = user
                user1 = Users.get_user_by_nick_email(nick, email)

                print(f' after update user form session: {user}')
                print(f'  after update user_from_db: {user1}')

                return redirect(url_for('settings_view'))

            else:
                print('bad post request')

            return redirect(url_for('settings_view'))
    else:
        return redirect(url_for('start'))


if __name__ == "__main__":
    app.run(debug=True)
