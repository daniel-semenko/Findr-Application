from datetime import datetime
from enum import unique
from sqlalchemy.orm import backref, session
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms.validators import Length
from app import db
from flask_login import UserMixin
from app import login

@login.user_loader
def load_user(id):
      return User.query.get(int(id))

userLanguages = db.Table('userLanguages',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('language_id', db.Integer, db.ForeignKey('language.id'))
)

postFields = db.Table('postFields',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('field_id', db.Integer, db.ForeignKey('field.id'))
)

userFields = db.Table('userFields',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('field_id', db.Integer, db.ForeignKey('field.id'))
)

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentid = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(20))

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coursenum = db.Column(db.String(3))
    title = db.Column(db.String(150))
    roster = db.relationship('Electives', back_populates="classtaken")
    def __repr__(self):
        return '<Class id: {} - coursenum: {}, title: {}, major: {}>'.format(self.id,self.coursenum,self.title)
    def getTitle(self):
        return self.title

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    goals = db.Column(db.String(300))
    startdate = db.Column(db.String(20))
    enddate = db.Column(db.String(20))
    commitment = db.Column(db.String(300))
    qualifications = db.Column(db.String(300))

    view_post = db.relationship('Application', back_populates='postapplied')
    
    fields = db.relationship(
        'Field',
        secondary=postFields,
        primaryjoin=(postFields.c.post_id == id),
        backref=db.backref('postFields', lazy='dynamic'),
        lazy='dynamic')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def get_tags(self):
        return self.fields

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentid = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(30))
    def __repr__(self):
        return '<Tag id : {} - Tag name: {}>'.format(self.id,self.name)




class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wsuid = db.Column(db.String(9), unique=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(120), unique=True)
    phone = db.Column(db.Integer, unique=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref="writer", lazy='dynamic')
    type = db.Column(db.Integer, default = 2)

    major = db.Column(db.String(120))
    gpa = db.Column(db.String(10))
    graddate = db.Column(db.String(120))
    prior_experience = db.Column(db.String(1500))
    classes = db.relationship('Electives', back_populates="studentenrolled")
    fields = db.relationship('Fields', back_populates="studentenrolled")
    languages = db.relationship('Languages', back_populates="studentenrolled")

    applications = db.relationship('Application', back_populates='studentapplied')

    def get_fields(self):
        return self.fields

    def __repr__(self):
        return '<User {} - {} {};>'.format(self.id, self.wsuid, self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_user_posts(self):
        return self.posts

    def enroll(self, newclass):
        if not self.has_taken(newclass):
            newElective = Electives(classtaken = newclass)
            self.classes.append(newElective)
            db.session.commit()

    def deleteclass(self, oldclass):
        if self.has_taken(oldclass):
            elective = Electives.query.filter_by(studentid=self.id).filter_by(classid=oldclass.id).first()
            db.session.delete(elective)
            db.session.commit()

    def has_taken(self, newclass):
        return (Electives.query.filter_by(studentid=self.id).filter_by(classid=newclass.id).count() > 0)

    def all_taken(self):
        return self.classes

    def getEnrollmentDate(self, theclass):
        if self.has_taken(theclass):
            return Electives.query.filter_by(studentid=self.id).filter_by(classid=theclass.id).first().datetaken
        else:
            return None

        

    def apply(self, newpost):
        if not self.is_applied(newpost):
            newApplication = Application(postapplied = newpost)
            self.applications.append(newApplication)
            db.session.commit()

    def unapply(self, oldpost):
        if self.is_applied(oldpost):
            curApplication = Application.query.filter_by(studentid=self.id).filter_by(postid=oldpost.id).first()
            db.session.delete(curApplication)
            db.session.commit()

    def is_applied(self, newpost):
        return (Application.query.filter_by(studentid=self.id).filter_by(postid=newpost.id).count() > 0)

    def appliedPosts(self):
        return self.applications


class Electives(db.Model):
    studentid = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    classid = db.Column(db.Integer, db.ForeignKey('class.id'), primary_key=True)
    datetaken = db.Column(db.String(120))
    studentenrolled = db.relationship('User')
    classtaken = db.relationship('Class')

class Application(db.Model):
    studentid = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    postid = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    studentapplied = db.relationship('User')
    postapplied = db.relationship('Post')

    def __repr__(self):
        return '<Application post: {} student: {}>'.format(self.postapplied, self.studentapplied)    

class Fields(db.Model):
    studentid = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    fieldid = db.Column(db.Integer, db.ForeignKey('field.id'), primary_key=True)
    studentenrolled = db.relationship('User')
    fieldpicked = db.relationship('Field')

class Languages(db.Model):
    studentid = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    languageid = db.Column(db.Integer, db.ForeignKey('language.id'), primary_key=True)
    studentenrolled = db.relationship('User')
    languagepicked = db.relationship('Language')
