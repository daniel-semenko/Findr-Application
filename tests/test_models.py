import unittest
from app import db, create_app
from app.Model.models import User, Field, Post, Application, Class
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

# Unit Testing:
class TestModels(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        user = User(firstname="ben", lastname="kaufmann", wsuid=123456, username="ben123", phone=1234, email="ben@wsu.edu", gpa="N/A", major="N/A", graddate="N/A", prior_experience="N/A", type=2)
        user.set_password("123")
        self.assertTrue(user.get_password("123"))

    def test_enroll(self):
        user = User(firstname="ben", lastname="kaufmann", wsuid=123456, username="ben123", phone=1234, email="ben@wsu.edu", gpa="N/A", major="N/A", graddate="N/A", prior_experience="N/A", type=2)
        user.set_password("123")
        db.session.add(user)
        db.session.commit()
        self.assertEqual(user.classes, [])

        theclass = Class(id=123, coursenum=321, title="test")
        user.enroll(theclass)
        db.session.commit()
        self.assertEqual(len(user.classes), 1)
        self.assertEqual(user.classes[0].classtaken.id, theclass.id)

        # delete class
        user.deleteclass(theclass)
        db.session.commit()
        self.assertEqual(len(user.classes), 0)

    def test_apply(self):
        user = User(firstname="ben", lastname="kaufmann", wsuid=123456, username="ben123", phone=1234, email="ben@wsu.edu", gpa="N/A", major="N/A", graddate="N/A", prior_experience="N/A", type=2)
        user.set_password("123")
        db.session.add(user)
        db.session.commit()
        self.assertEqual(user.appliedPosts(), [])

        thepost = Post(id=123, title="test")
        user.apply(thepost, "ben", "ben@wsu.edu", "statement")
        db.session.commit()
        self.assertEqual(len(user.applications), 1)
        self.assertEqual(user.applications[0].postid, thepost.id)
        self.assertEqual(user.id, user.applications[0].studentapplied.id)

        # unapply test
        user.unapply(thepost)
        db.session.commit()
        self.assertEqual(len(user.applications), 0)



if __name__ == '__main__':
    unittest.main()
    
# Functional Testing:
# Use case checklist: (W = Working) (N = Not working)
# Student Sign Up | W
# Faculty Sign Up | W
# Student login | W
# Faculty login | W
# View open research positions | W
# Create undergraduate research positions | W
# View an individual position listing | W
# Apply to research position | W
# View submitted applications and check status | W
# Withdraw pending applications | W
# See applications submitted to their positions | W
# View qualifications of students who applied i.e. see student profiles | W
# Approve application for interview | W
# Update application with “Hired” or “Not hired” | W
# Delete research position | W

# UI Testing:
# (Browser) (Window size)
# Chrome large | W
# Chrome medium | W
# Chrome small | W
# Edge large | W
# Edge medium | W
# Edge small | W
# FireFox large | W
# FireFox medium | W
# FireFox small | W