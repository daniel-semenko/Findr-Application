from __future__ import print_function
import sys
from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user
from flask_login.utils import login_required
from config import Config

from app import db
from app.Model.models import Post, Field, postFields, User
from app.Controller.forms import PostForm, SortForm
from app.Controller.auth_forms import EditForm

bp_routes = Blueprint('routes', __name__)
bp_routes.template_folder = Config.TEMPLATE_FOLDER #'..\\View\\templates'


@bp_routes.route('/', methods=['GET', 'POST'])

@bp_routes.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', title="Findr Home")

@bp_routes.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    if current_user.type == 2:
        return redirect(url_for('routes.index'))
    postForm = PostForm()
    if postForm.validate_on_submit():
        post = Post(title=postForm.title.data, goals=postForm.goals.data, commitment=postForm.commitment.data, startdate=postForm.startdate.data, enddate=postForm.enddate.data, qualifications=postForm.qualifications.data, user_id=current_user.id)
        for t in postForm.fields.data:
            post.fields.append(t)
        db.session.add(post)
        db.session.commit()
        flash('Your research post has been created.')
        return redirect(url_for('routes.index'))
    return render_template('create.html', title="Post Research Opportunity", form=postForm)

@bp_routes.route('/delete/<post_id>', methods=['DELETE', 'POST'])
@login_required
def delete(post_id):
    deletepost = Post.query.filter_by(id=post_id).first()
    for t in deletepost.fields:
        deletepost.fields.remove(t)
    db.session.commit()
    db.session.delete(deletepost)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('routes.index'))

@bp_routes.route('/display_profile', methods=['GET'])
@login_required
def display_profile():
    return render_template('display_profile.html', title='Display Profile', user = current_user)

@bp_routes.route('/opportunities', methods=['GET'])
@login_required
def opportunities():
    return render_template('opportunities.html', title='Research Opportunities', user = current_user)
