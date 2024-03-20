import uuid
from flask import jsonify, render_template, redirect, request, url_for, session
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm
from apps.authentication.models import User, login_manager

from apps.authentication.util import hash_pass, verify_pass

from apps.config import db

import json

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        email  = request.form['username'] # we can have here username OR email
        password = request.form['password']

        # Locate user
        user_db = db.users.find_one({'email':email})
        if user_db is  not None:
            user_data={
                "_id": user_db['_id'],
                "name": user_db['name'],
                "email": user_db['email'],
                "password": user_db['password'],
                "role": user_db['role']
            }
            user=User(user_data)

        if not user:
            return render_template( 'accounts/login.html',
                                msg='Unknown User or Email',
                                form=login_form)

        # Check the password
        if verify_pass(password, user.get_pass()):
            login_user(user)
            print(session['_user_id'])
            if(user_data["role"] == "user"):
                return redirect(url_for('home_blueprint.user'))
            else:
                return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # Create the user object
    user = {
        "_id": uuid.uuid4().hex,
        "name": str(request.form.get('name')),
        "email": str(request.form.get('email')),
        "password": request.form.get('password'),
        "role": request.form.get('admin')
    }

    # Encrypt the password
    user['password'] = hash_pass(str(user['password']))

    if (user["role"] == "on"):
        user["role"] = "admin"
    else:
        user["role"] = "user"

    # Check for existing email address
    if db.users.find_one({"email": user['email']}):
        return jsonify({"error": "Email address already in use"}), 400

    if db.users.insert_one(user):
        return jsonify({"error": "Account added"}), 200

    return jsonify({"error": "Signup failed"}), 400


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login')) 

# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
