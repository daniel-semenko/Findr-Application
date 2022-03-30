from __future__ import print_function
import sys
from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_sqlalchemy import sqlalchemy
from flask_login import current_user
from config import Config

from app import db
from app.Controller.auth_forms import FacultyRegistrationForm, StudentRegistrationForm, LoginForm, EditForm
from app.Model.models import User, Class, Electives, Fields, Languages, Field, Language, Application
from flask_login import current_user, login_user, logout_user, login_required

bp_auth = Blueprint('auth', __name__)
bp_auth.template_folder = Config.TEMPLATE_FOLDER

@bp_auth.route('/studentregister', methods=['GET', 'POST'])
def studentregister():
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, wsuid=form.wsuid.data, username=form.username.data, phone=form.phone.data, email=form.email.data, gpa="N/A", major="N/A", graddate="N/A", prior_experience="N/A", type=2)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered as a student, please login to continue!')
        return redirect(url_for('auth.login'))
    return render_template('studentregister.html', form = form)

@bp_auth.route('/facultyregister', methods=['GET', 'POST'])
def facultyregister():
    form = FacultyRegistrationForm()
    if form.validate_on_submit():
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, wsuid=form.wsuid.data, username=form.username.data, phone=form.phone.data, email=form.email.data, type=1)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered as a faculty member, please login to continue!')
        return redirect(url_for('auth.login'))
    return render_template('facultyregister.html', form = form)

@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.type == 1:
        return redirect(url_for('routes.myopportunities'))
    if current_user.is_authenticated and current_user.type == 2:
        return redirect(url_for('routes.opportunities'))
    lform = LoginForm()
    if lform.validate_on_submit():
        user = User.query.filter_by(username = lform.username.data).first()
        if (user is None) or (user.get_password(lform.password.data) == False):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember = lform.remember_me.data)
        if current_user.type == 1:
            return redirect(url_for('routes.myopportunities'))
        if current_user.type == 2:
            return redirect(url_for('routes.opportunities'))
    return render_template('login.html', title='Sign In', form=lform)

@bp_auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp_auth.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    eform = EditForm()
    if request.method == 'POST':
        if eform.validate_on_submit():
            current_user.username = eform.username.data
            current_user.firstname = eform.firstname.data
            current_user.lastname = eform.lastname.data
            current_user.wsuid = eform.wsuid.data
            current_user.email = eform.email.data
            current_user.major = eform.major.data
            current_user.gpa = eform.gpa.data
            current_user.graddate = eform.graddate.data
            current_user.phone = eform.phone.data
            current_user.prior_experience = eform.prior_experience.data
            current_user.set_password(eform.password.data)

            for l in Electives.query.filter_by(studentid=current_user.id).all():
                db.session.delete(l)
                db.session.commit()
            for l in Fields.query.filter_by(studentid=current_user.id).all():
                db.session.delete(l)
                db.session.commit()
            for l in Languages.query.filter_by(studentid=current_user.id).all():
                db.session.delete(l)
                db.session.commit()

            for l in eform.languages.data:
                newLang = Languages(languagepicked = l)
                current_user.languages.append(newLang)
                db.session.commit()
            for l in eform.fields.data:
                newField = Fields(fieldpicked = l)
                current_user.fields.append(newField)
                db.session.commit()
            for l in eform.electives.data:
                newElective = Electives(classtaken = l)
                current_user.classes.append(newElective)
                db.session.commit()

            db.session.add(current_user)
            db.session.commit()
            flash("Profile changes saved.")
            return redirect(url_for('routes.display_profile'))
    elif request.method == 'GET':
        eform.username.data = current_user.username
        eform.firstname.data = current_user.firstname
        eform.lastname.data = current_user.lastname
        eform.wsuid.data = current_user.wsuid
        eform.gpa.data = current_user.gpa
        eform.graddate.data = current_user.graddate
        eform.email.data = current_user.email
        eform.phone.data = current_user.phone
        eform.major.data = current_user.major
        eform.languages.data = list(map(lambda x: x.languagepicked, current_user.languages))
        eform.fields.data = list(map(lambda x: x.fieldpicked, current_user.fields))
        eform.electives.data = list(map(lambda x: x.classtaken, current_user.classes))
        eform.prior_experience.data = current_user.prior_experience
    else:
        pass
    return render_template('edit_profile.html', title='Edit Profile', form = eform)
