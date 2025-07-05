import unittest
from app import create_app, db
from app.models import User
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False # Disable CSRF for easier testing

class RouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client() # Flask test client

        # Create a test user for login
        user = User(username='testuser', email='test@example.com', role='user')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

        # Create an admin user
        admin_user = User(username='adminuser', email='admin@example.com', role='admin')
        admin_user.set_password('adminpass')
        db.session.add(admin_user)
        db.session.commit()
        self.admin_user_id = admin_user.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_login(self):
        rv = self.login('testuser', 'testpass')
        self.assertIn(b'Home', rv.data) # Check if 'Home' content is present after login
        self.assertIn(b'Logout', rv.data) # Check if logout link is present

    def test_login_invalid_credentials(self):
        rv = self.login('testuser', 'wrongpass')
        self.assertIn(b'Invalid username or password', rv.data)

    def test_index_redirects_if_not_logged_in(self):
        self.logout() # Ensure logged out
        rv = self.client.get('/', follow_redirects=False)
        self.assertEqual(rv.status_code, 302) # Should redirect
        self.assertIn(b'/login', rv.headers['Location']) # Should redirect to login

    def test_admin_panel_access_denied_for_regular_user(self):
        self.login('testuser', 'testpass')
        rv = self.client.get('/admin_panel')
        self.assertEqual(rv.status_code, 403) # Should be forbidden

    def test_admin_panel_access_for_admin_user(self):
        self.login('adminuser', 'adminpass')
        rv = self.client.get('/admin_panel')
        self.assertEqual(rv.status_code, 200) # Should be successful

if __name__ == '__main__':
    unittest.main()