from __future__ import print_function
import sys
from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user
from flask_login.utils import login_required
from config import Config

from app import db
from app.Model.models import Post, Field, postFields, User, Application
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
    if current_user.type == 2:
        return redirect(url_for('routes.index'))

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




@bp_routes.route('/opportunities', methods=['GET','POST'])
@login_required
def opportunities():

    sForm = SortForm()

    if sForm.validate_on_submit():

        if sForm.sortbyrecommendedposts.data == True:
            #if sForm.sort.data == "Title":      # Title
            #     posts = Post.query.filter_by(Post.fields in current_user.get_fields()).order_by(Post.title.asc())
            # elif sForm.sort.data == "Start Date":      # Start Date
            #     posts = Post.query.order_by(Post.startdate.asc())
            # else:                           # Date / Default
            #     posts = Post.query.order_by(Post.id.asc())

            #for 

            posts = Post.query.order_by(Post.title.asc())
            flash('Only sorting by title, sort by recommended not working yet!')
            return render_template('opportunities.html', title="Research Opportunities", user = current_user, posts = posts.all(), form=sForm)
        else:
            if sForm.sort.data == "Title":      # Title
                posts = Post.query.order_by(Post.title.asc())
            elif sForm.sort.data == "Start Date":      # Start Date
                posts = Post.query.order_by(Post.startdate.asc())
            else:                           # Date / Default
                posts = Post.query.order_by(Post.id.asc())
            return render_template('opportunities.html', title='Research Opportunities', user = current_user, posts = posts.all(), form=sForm)


    posts = Post.query.order_by(Post.id.asc())
    return render_template('opportunities.html', title='Research Opportunities', user = current_user, posts = posts.all(), form=sForm)






@bp_routes.route('/myapplications', methods=['GET'])
@login_required
def myapplications():
    if current_user.type == 1:      #if user is faculty and tries through URL, returns them back to index
        return redirect(url_for('routes.index'))

    return render_template('myapplications.html', title='My Applications', user=current_user)

@bp_routes.route('/view_post/<postid>', methods=['GET'])
@login_required
def view_post(postid):
    thepost = Post.query.filter_by(id = postid).first()
    return render_template('view_post.html', title="View Post", user = current_user, post = thepost)

@bp_routes.route('/apply/<postid>', methods=['POST'])
@login_required
def apply(postid):
    thepost = Post.query.filter_by(id = postid).first()
    if thepost is None:
        flash('Post with id "{}" not found'.format(postid))
        return redirect(url_for('routes.opportunities'))
    current_user.apply(thepost)
    db.session.commit()
    flash('You have successfully applied for the post {}'.format(thepost.title))
    return redirect(url_for('routes.opportunities'))

@bp_routes.route('/unapply/<postid>', methods=['POST'])
@login_required
def unapply(postid):
    thepost = Post.query.filter_by(id = postid).first()
    if thepost is None:
        flash('Post with id "{}" not found'.format(postid))
        return redirect(url_for('routes.opportunities'))
    current_user.unapply(thepost)
    db.session.commit()
    flash('You have successfully unapplied from the post {}'.format(thepost.title))
    return redirect(url_for('routes.opportunities'))