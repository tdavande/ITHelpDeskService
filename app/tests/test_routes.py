import unittest
from app import create_app, db
from app.models import User
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier testing


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()  # Ensures a clean database for each test
        self.client = self.app.test_client()  # Flask test client

        # Create a test user for login (username: 'testuser', password: 'testpass')
        user = User(username='testuser', email='test@example.com', role='user')
        user.set_password('testpass')
        db.session.add(user)

        # Create an admin user (username: 'adminuser', password: 'adminpass')
        admin_user = User(username='adminuser', email='admin@example.com', role='admin')
        admin_user.set_password('adminpass')
        db.session.add(admin_user)

        db.session.commit()  # Commit both users to the database
        self.user_id = user.id
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
        # FIX: Use the correct username and password from setUp
        rv = self.login('testuser', 'testpass')
        self.assertIn(b'Home', rv.data)  # Check if 'Home' content is present after login
        self.assertIn(b'Logout', rv.data)  # Check if logout link is present

    def test_login_invalid_credentials(self):
        rv = self.login('testuser', 'wrongpass')
        self.assertIn(b'Invalid username or password', rv.data)

    def test_index_redirects_if_not_logged_in(self):
        with self.app.test_client() as client:
            rv = client.get('/')
            self.assertIn('/login', rv.headers['Location'])

    def test_admin_panel_access_denied_for_regular_user(self):
        with self.app.test_client() as client:
            # FIX: Use the correct username and password for testuser
            self.login('testuser', 'testpass')
            rv = client.get('/admin')
            # This assertion is now correct (403 Forbidden for regular user)
            self.assertEqual(rv.status_code, 403)

    def test_admin_panel_access_for_admin_user(self):
        with self.app.test_client() as client:
            # FIX: Use the correct username and password for adminuser
            self.login('adminuser', 'adminpass')
            rv = client.get('/admin')
            # This assertion is now correct (200 OK for admin user)
            self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()