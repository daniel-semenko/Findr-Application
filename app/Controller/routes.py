from __future__ import print_function
import sys
from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user
from flask_login.utils import login_required
from config import Config

from app import db
from app.Model.models import DeletedApplication, Post, Field, postFields, User, Application
from app.Controller.forms import PostForm, SortForm
from app.Controller.auth_forms import EditForm, ApplicationForm

bp_routes = Blueprint('routes', __name__)
bp_routes.template_folder = Config.TEMPLATE_FOLDER #'..\\View\\templates'


@bp_routes.route('/', methods=['GET', 'POST'])

@bp_routes.route('/home', methods=['GET', 'POST'])
@login_required
def home():
   if current_user.type == 1:
       return redirect(url_for('routes.myopportunities'))
   if current_user.type == 2:
       return redirect(url_for('routes.opportunities'))

@bp_routes.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    if current_user.type == 2:
        return redirect(url_for('routes.opportunities'))

    postForm = PostForm()
    if postForm.validate_on_submit():
        post = Post(title=postForm.title.data, goals=postForm.goals.data, commitment=postForm.commitment.data, startdate=postForm.startdate.data, enddate=postForm.enddate.data, qualifications=postForm.qualifications.data, user_id=current_user.id)
        for t in postForm.fields.data:
            post.fields.append(t)
        db.session.add(post)
        db.session.commit()
        flash('Your research post has been created.')
        return redirect(url_for('routes.myopportunities'))
    return render_template('create.html', title="Post Research Opportunity", form=postForm)

@bp_routes.route('/delete/<post_id>', methods=['DELETE', 'POST'])
@login_required
def delete(post_id):
    if current_user.type == 2:
        return redirect(url_for('routes.opportunities'))

    deletepost = Post.query.filter_by(id=post_id).first()
    for t in deletepost.fields:
       deletepost.fields.remove(t)

    for a in deletepost.view_post:
       da = DeletedApplication(studentid = a.studentid, studentapplied = a.studentapplied, title = deletepost.title, status = 5)
       db.session.add(da)
       
    db.session.commit()
    db.session.delete(deletepost)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('routes.myopportunities'))



@bp_routes.route('/display_profile', methods=['GET'])
@login_required
def display_profile():
   user_id = request.args.get('user_id')
   user = current_user
   if user_id:
      user = User.query.filter_by(id = user_id).first()
   return render_template('display_profile.html', title='Display Profile', user=user)

@bp_routes.route('/opportunities', methods=['GET','POST'])
@login_required
def opportunities():
    if current_user.type == 1:
        return redirect(url_for('routes.myopportunities'))

    sForm = SortForm()

    if sForm.validate_on_submit():

        if sForm.sortbyrecommendedposts.data == True:

            s = []
            for l in current_user.fields:
                s.append(l.fieldpicked.name)

            p = []
            for j in Post.query.all():

                for t in j.get_tags().all():

                    if t.name in s:
                        p.append(j.title)
                        break

            if sForm.sort.data == "Title":
                posts = Post.query.filter(Post.title.in_(p)).order_by(Post.title.asc())
            elif sForm.sort.data == "Start Date":
                posts = Post.query.filter(Post.title.in_(p)).order_by(Post.startdate.asc())
            else:
                posts = Post.query.filter(Post.title.in_(p)).order_by(Post.id.asc())

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

@bp_routes.route('/myopportunities', methods=['GET','POST'])
@login_required
def myopportunities():

    if current_user.type == 2:
        return redirect(url_for('routes.opportunities'))

    sForm = SortForm()

    if sForm.validate_on_submit():
        if sForm.sort.data == "Title":      # Title
            posts = (current_user.get_user_posts()).order_by(Post.title.asc())
        elif sForm.sort.data == "Start Date":      # Start Date
            posts = (current_user.get_user_posts()).order_by(Post.startdate.asc())
        else:                           # Date / Default
            posts = (current_user.get_user_posts()).order_by(Post.id.asc())
        return render_template('myopportunities.html', title='Research Opportunities', user = current_user, posts = posts.all(), form=sForm)


    posts = Post.query.order_by(Post.id.asc())
    return render_template('myopportunities.html', title='Research Opportunities', user = current_user, posts = posts.all(), form=sForm)




@bp_routes.route('/myapplications', methods=['GET'])
@login_required
def myapplications():
    if current_user.type == 1:      #if user is faculty and tries through URL, returns them back to index
        return redirect(url_for('routes.myopportunities'))

    return render_template('myapplications.html', title='My Applications', user=current_user)

@bp_routes.route('/view_post/<postid>', methods=['GET'])
@login_required
def view_post(postid):
    thepost = Post.query.filter_by(id = postid).first()
    return render_template('view_post.html', title="View Post", user = current_user, post = thepost)

@bp_routes.route('/apply/<postid>', methods=['POST'])
@login_required
def apply(postid):
    if current_user.type == 1:      #if user is faculty and tries through URL, returns them back to index
        return redirect(url_for('routes.myopportunities'))
    thepost = Post.query.filter_by(id = postid).first()
    if thepost is None:
        flash('Post with id "{}" not found'.format(postid))
        return redirect(url_for('routes.opportunities'))
    form = ApplicationForm()
    if form.validate_on_submit():
        current_user.apply(thepost,form.name.data,form.email.data,form.statement.data)
    db.session.commit()
    flash('You have successfully applied for the post {}'.format(thepost.title))
    return redirect(url_for('routes.opportunities'))

@bp_routes.route('/unapply/<postid>', methods=['POST'])
@login_required
def unapply(postid):
    if current_user.type == 1:      #if user is faculty and tries through URL, returns them back to index
        return redirect(url_for('routes.myopportunities'))
    thepost = Post.query.filter_by(id = postid).first()
    if thepost is None:
        flash('Post with id "{}" not found'.format(postid))
        return redirect(url_for('routes.opportunities'))
    current_user.unapply(thepost)
    db.session.commit()
    flash('You have successfully unapplied from the post {}'.format(thepost.title))
    return redirect(url_for('routes.opportunities'))

@bp_routes.route('/tryapply/<postid>', methods=['GET','POST'])
@login_required
def tryapply(postid):
    if current_user.type == 1: #if user is faculty and tries through URL, returns them back to index
        return redirect(url_for('routes.myopportunities'))
    form = ApplicationForm()
    if form.validate_on_submit():
        thepost = Post.query.filter_by(id = postid).first()
        current_user.apply(thepost,form.name.data,form.email.data,form.statement.data)
        return redirect(url_for('routes.opportunities'))
    return render_template('apply.html', title='Apply', user = current_user, form=form)
#applied = 1, interview = 2, hired = 3, rejected = 4, not available = 5

@bp_routes.route('/markforhire/<postid>/<studentid>', methods=['POST'])
@login_required
def markforhire(postid, studentid):
    if current_user.type == 2:
        return redirect(url_for('routes.opportunities'))
    theapp = Application.query.filter_by(postid = postid).filter_by(studentid = studentid).first()


    if theapp is None:
        flash('Application by student with id "{}" not found'.format(studentid))
        return redirect(url_for('routes.view_post', user = current_user, postid = theapp.postapplied.id, studentid = theapp.studentapplied.id))
    
    theapp.markHired()
    flash('User has been marked as hired!')
    db.session.commit()
    return redirect(url_for('routes.view_post', user = current_user, postid = theapp.postapplied.id, studentid = theapp.studentapplied.id))

@bp_routes.route('/markforreject/<postid>/<studentid>', methods=['POST'])
@login_required
def markforreject(postid, studentid):
    if current_user.type == 2:
        return redirect(url_for('routes.opportunities'))
    theapp = Application.query.filter_by(postid = postid).filter_by(studentid = studentid).first()


    if theapp is None:
        flash('Application by student with id "{}" not found'.format(studentid))
        return redirect(url_for('routes.view_post', user = current_user, postid = theapp.postapplied.id, studentid = theapp.studentapplied.id))
    
    theapp.markRejected()
    flash('User has been marked as rejected.')
    db.session.commit()
    return redirect(url_for('routes.view_post', user = current_user, postid = theapp.postapplied.id, studentid = theapp.studentapplied.id))

@bp_routes.route('/markforinterview/<postid>/<studentid>', methods=['POST'])
@login_required
def markforinterview(postid, studentid):
    if current_user.type == 2:
        return redirect(url_for('routes.opportunities'))
    theapp = Application.query.filter_by(postid = postid).filter_by(studentid = studentid).first()


    if theapp is None:
        flash('Application by student with id "{}" not found'.format(studentid))
        return redirect(url_for('routes.view_post', user = current_user, postid = theapp.postapplied.id, studentid = theapp.studentapplied.id))
    
    theapp.markInterview()
    flash('User has been marked for Interview!')
    db.session.commit()
    return redirect(url_for('routes.view_post', user = current_user, postid = theapp.postapplied.id, studentid = theapp.studentapplied.id))

@bp_routes.route('/clear/<studentid>', methods=['GET','POST'])
@login_required
def clear(studentid):
    if current_user.type == 1:
        return redirect(url_for('routes.myopportunities'))
    student = User.query.filter_by(id = studentid).first()
    for da in student.deletedapplications:
        db.session.delete(da)
    db.session.commit()
    return redirect(url_for('routes.myapplications'))
