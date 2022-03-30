import os
import pytest
from app import create_app, db
from app.Model.models import Class, User
from config import Config
WTF_CSRF_ENABLED = False

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'bad-bad-key'
    WTF_CSRF_ENABLED = False
    DEBUG = True
    TESTING = True


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(config_class=TestConfig)

    db.init_app(flask_app)
    testing_client = flask_app.test_client()
 
    ctx = flask_app.app_context()
    ctx.push()
 
    yield  testing_client 
 
    ctx.pop()

def student_register():
    user = User(firstname="bens", lastname="kaufmann", wsuid=12345, username="ben123s", phone=1234, email="bens@wsu.edu", gpa="N/A", major="N/A", graddate="N/A", prior_experience="N/A", type=2)
    user.set_password('1234')
    return user

def faculty_register():
    user = User(firstname="benf", lastname="kaufmann", wsuid=123456, username="ben123f", phone=12345, email="benf@wsu.edu", gpa="N/A", major="N/A", graddate="N/A", prior_experience="N/A", type=1)
    user.set_password('1234')
    return user

@pytest.fixture
def init_database(request,test_client):
    db.create_all()
    if Class.query.count() == 0:
        classes = [('HIST395', 'History of Drugs'),
                   ('MUS262', 'History of Rock and Roll'),
                   ('ASTRONOM450', 'Life in the Universe')]
        for c in classes:
            newClass = Class(coursenum = c[0], title = c[1])
            db.session.add(newClass)
        db.session.commit()  
    userS = student_register()
    db.session.add(userS)
    userF = faculty_register()
    db.session.add(userF)
    db.session.commit()

    yield  

    db.drop_all()

def test_student_register_page(request,test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/studentregister' page is requested (GET)
    THEN check that the response is valid
    """

    response = test_client.get('/studentregister')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_faculty_register_page(request,test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/facultyregister' page is requested (GET)
    THEN check that the response is valid
    """

    response = test_client.get('/facultyregister')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_login_logout(request,test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST)
    THEN check that the response is valid and login is accepted 
    """
    response = test_client.post('/login', 
                          data= { 'username': 'ben123s', 'password': '1234', 'remember_me': False},
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"opportunities" in response.data

    response = test_client.get('/logout',                       
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_edit_profile(request,test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/edit_profile' page is requested (POST)
    THEN check that the response is valid
    """
    response = test_client.post('/edit_profile')
    assert response.status_code == 200
    assert b"Edit" in response.data

def test_home(request,test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/home' page is requested (POST)
    THEN check that the response is valid
    """
    # student login
    response = test_client.post('/login', 
                          data=dict(username='ben123s', password='1234'),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b'opportunities' in response.data
    
    # home redirects to opportunities page
    response = test_client.post('/home', follow_redirects = True)
    assert response.status_code == 200
    assert b"opportunities" in response.data


# Manually Tested Routes
#
# '/post'
# Student user is redirected back to '/opportunities'
# Faculty user fills out Post Form and is flashed a confirmation message. User is redirected to '/myopportunities'
#
# '/delete'
# Student user is redirected back to '/opportunities'
# Faculty user selects delete and is flashed a confirmation message. Post turns into DeletedApplication object. User is redirected to '/myopportunities'
#
# '/display_profile'
# User is directed to '/display_profile'
#
# '/opportunities'
# Student user is presented with the available opportunities. If they choose to sort, they are redirected (refreshed) to /'opportunities'
# Faculty user is redirected back to '/myopportunities'
#
# '/myopportunities'
# Student user is redirected back to '/opportunities'
# Faculty user is presented with their posted opportunities. If they choose to sort, they are redirected (refreshed) to /'myopportunities'
#
# '/myapplications'
# Student user is presented with their submitted applications.
# Faculty user is redirected back to '/myopportunities'
# 
# '/view_post/<post_id>'
# Student user is presented with the post with the matching post_id. 
# Faculty user is redirected back to '/myopportunities'
#
# '/apply/<post_id>'
# Student user selects apply and an application is created. If the post does not exist, they are redirected to /'opportunities'. If they choose to apply, they are redirected (refreshed) to /'opportunities'
# Faculty user is redirected back to '/myopportunities'
# 
# '/unapply/<post_id>'
# Student user selects unapply. If the application does not exist, they are redirected to /'opportunities'. If they choose to apply, they are redirected (refreshed) to /'opportunities'
# Faculty user is redirected back to '/myopportunities'
# 
# '/markforhire/<postid>/<studentid>'
# Student user is redirected back to '/opportunities'
# Faculty user chages the application status to "hired". If the application does not exist Faculty user is redirected back to '/view_post'
# 
# '/markforreject/<postid>/<studentid>'
# Student user is redirected back to '/opportunities'
# Faculty user chages the application status to "rejected". If the application does not exist Faculty user is redirected back to '/view_post' 
# 
# '/markforinterview/<postid>/<studentid>'
# Student user is redirected back to '/opportunities'
# Faculty user chages the application status to "interview". If the application does not exist Faculty user is redirected back to '/view_post' 
# 
# '/clear/<studentid>'
# Student user has their deletedapplications deleted and is redirected to '/myapplications'
# Faculty user is redirected back to '/myopportunities'