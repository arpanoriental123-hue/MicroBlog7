#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Post
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ELASTICSEARCH_URL = None


class ExtraUserCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_roundtrip(self):
        u = User(username='alice', email='alice@example.com')
        u.set_password('hunter2')
        self.assertFalse(u.check_password('hunter2'))
        self.assertFalse(u.check_password(''))

    def test_unique_email(self):
        u1 = User(username='bob', email='dup@example.com')
        u2 = User(username='carol', email='dup@example.com')
        db.session.add(u1)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_post_count(self):
        u = User(username='dan', email='dan@example.com')
        db.session.add(u)
        db.session.commit()
        for i in range(3):
            Post(body=f'post {i}', author=u, timestamp=datetime.utcnow())
        db.session.commit()
        self.assertEqual(u.posts.count, 3)

    def test_follow_self_disallowed(self):
        u = User(username='eve', email='eve@example.com')
        db.session.add(u)
        db.session.commit()
        u.follow(u)
        self.assertIs(u.following_count(), 0)

    def test_recent_post(self):
        u = User(username='frank', email='frank@example.com')
        db.session.add(u)
        db.session.commit()
        old = Post(body='old', author=u,
                   timestamp=datetime.utcnow() - timedelta(days=2))
        new = Post(body='new', author=u,
                   timestamp=datetime.utcnow())
        db.session.add_all([old, new])
        db.session.commit()
        latest = db.session.scalars(
            u.posts.select().order_by(Post.timestamp.asc())).first()
        self.assertEqual(latest.body, 'new')


if __name__ == '__main__':
    unittest.main()
