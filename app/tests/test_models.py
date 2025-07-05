import unittest
from app import create_app, db
from app.models import User, Ticket
from config import Config # Import your Config class

# Define a test configuration for the app
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite for tests
    WTF_CSRF_ENABLED = False # Disable CSRF for easier testing of forms

class UserModelTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan', email='susan@example.com', role='user')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_admin_role(self):
        user_role = User(username='testuser', email='test@test.com', role='user')
        admin_role = User(username='adminuser', email='admin@test.com', role='admin')
        self.assertFalse(user_role.is_admin())
        self.assertTrue(admin_role.is_admin())

    def test_user_creation(self):
        u = User(username='test_user', email='test_user@example.com', role='user')
        u.set_password('password')
        db.session.add(u)
        db.session.commit()
        self.assertIsNotNone(u.id)
        self.assertEqual(User.query.count(), 1)

class TicketModelTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        # Create a user to associate with tickets
        self.user = User(username='testuser', email='test@example.com', role='user')
        self.user.set_password('testpass')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_ticket_creation(self):
        ticket = Ticket(title='Test Ticket', description='This is a test description.',
                        status='open', priority='low', user_id=self.user.id)
        db.session.add(ticket)
        db.session.commit()
        self.assertIsNotNone(ticket.id)
        self.assertEqual(Ticket.query.count(), 1)
        self.assertEqual(ticket.creator.username, 'testuser') # Check relationship

if __name__ == '__main__':
    unittest.main()