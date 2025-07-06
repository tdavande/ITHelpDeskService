import unittest
from flask import Flask
from app import create_app, db # Assuming create_app and db are in app/__init__.py
from app.forms import LoginForm, RegistrationForm, TicketForm, CommentForm
from app.models import User
from config import Config # Import your Config class

# Define a test configuration for the application
class TestConfig(Config):
    TESTING = True # Enable testing mode
    # Use an in-memory SQLite database for fast, isolated tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Disable CSRF protection during tests for easier form submission
    # In real apps, you'd test CSRF separately if needed, but for unit forms, it simplifies.
    WTF_CSRF_ENABLED = False
    # Ensure SECRET_KEY is set for Flask-WTF forms
    SECRET_KEY = 'a-test-secret-key-for-forms'


class FormTests(unittest.TestCase):
    def setUp(self):
        # Create a test Flask application context
        self.app = create_app()
        self.app.config.from_object(TestConfig) # Apply the test configuration
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all() # Create database tables for the test

        # Create a test client for simulating requests if needed, though forms primarily tested directly
        self.client = self.app.test_client()

    def tearDown(self):
        # Clean up after each test
        db.session.remove()
        db.drop_all() # Drop all tables
        self.app_context.pop() # Pop the application context

    # --- LoginForm Tests ---
    def test_login_form_valid_data(self):
        form = LoginForm(username='testuser', password='password123')
        # Simulate form submission data (WTForms takes data as keyword args or via request context)
        # We can directly set the data for simple form validation tests
        form.username.data = 'testuser'
        form.password.data = 'password123'
        self.assertTrue(form.validate()) # Should be valid

    def test_login_form_missing_username(self):
        form = LoginForm(password='password123')
        form.password.data = 'password123' # Explicitly set data
        form.username.data = '' # Explicitly set empty username
        self.assertFalse(form.validate())
        self.assertIn('This field is required.', form.username.errors)

    def test_login_form_missing_password(self):
        form = LoginForm(username='testuser')
        form.username.data = 'testuser'
        form.password.data = '' # Explicitly set empty password
        self.assertFalse(form.validate())
        self.assertIn('This field is required.', form.password.errors)

    # --- RegistrationForm Tests ---
    def test_registration_form_valid_data(self):
        form = RegistrationForm(username='newuser', email='new@example.com',
                                password='password123', password2='password123')
        # Manually set data for direct validation test
        form.username.data = 'newuser'
        form.email.data = 'new@example.com'
        form.password.data = 'password123'
        form.password2.data = 'password123'
        self.assertTrue(form.validate())

    def test_registration_form_username_already_exists(self):
        # Create a user with an existing username
        user = User(username='existinguser', email='existing@example.com', role='user')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        form = RegistrationForm(username='existinguser', email='another@example.com',
                                password='password123', password2='password123')
        form.username.data = 'existinguser'
        form.email.data = 'another@example.com'
        form.password.data = 'password123'
        form.password2.data = 'password123'
        self.assertFalse(form.validate())
        self.assertIn('Please use a different username.', form.username.errors)

    def test_registration_form_email_already_exists(self):
        # Create a user with an existing email
        user = User(username='anotheruser', email='existing@example.com', role='user')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        form = RegistrationForm(username='newuser2', email='existing@example.com',
                                password='password123', password2='password123')
        form.username.data = 'newuser2'
        form.email.data = 'existing@example.com'
        form.password.data = 'password123'
        form.password2.data = 'password123'
        self.assertFalse(form.validate())
        self.assertIn('Please use a different email address.', form.email.errors)

    def test_registration_form_passwords_do_not_match(self):
        form = RegistrationForm(username='testuser', email='test@example.com',
                                password='password123', password2='different_password')
        form.username.data = 'testuser'
        form.email.data = 'test@example.com'
        form.password.data = 'password123'
        form.password2.data = 'different_password'
        self.assertFalse(form.validate())
        self.assertIn('Field must be equal to password.', form.password2.errors)

    def test_registration_form_invalid_email_format(self):
        form = RegistrationForm(username='testuser', email='invalid-email',
                                password='password123', password2='password123')
        form.username.data = 'testuser'
        form.email.data = 'invalid-email'
        form.password.data = 'password123'
        form.password2.data = 'password123'
        self.assertFalse(form.validate())
        self.assertIn('Invalid email address.', form.email.errors)


    # --- TicketForm Tests ---

    def test_ticket_form_valid_data(self):
        # Corrected: Ensure 'status' and 'priority' values match the 'choices' in forms.py
        form = TicketForm(title='Test Ticket Title',
                          description='This is a very detailed test description for the ticket.',
                          status='open',    # Use 'open' (lowercase) as per your forms.py choices
                          priority='low')   # Use 'low' (lowercase) as per your forms.py choices
        self.assertTrue(form.validate())

    def test_ticket_form_missing_title(self):
        form = TicketForm(description='...', status='Open', priority='Low')
        form.title.data = ''
        form.description.data = 'This is a test description.'
        form.status.data = 'Open'
        form.priority.data = 'Low'
        self.assertFalse(form.validate())
        self.assertIn('This field is required.', form.title.errors)

    def test_ticket_form_invalid_status_choice(self):
        form = TicketForm(title='Test', description='Test desc',
                          status='InvalidStatus', priority='Low')
        form.title.data = 'Test'
        form.description.data = 'Test desc'
        form.status.data = 'InvalidStatus' # Invalid choice
        form.priority.data = 'Low'
        self.assertFalse(form.validate())
        self.assertIn('Not a valid choice.', form.status.errors)

    def test_ticket_form_invalid_priority_choice(self):
        form = TicketForm(title='Test', description='Test desc',
                          status='Open', priority='Critical') # 'Critical' is not in your current choices
        form.title.data = 'Test'
        form.description.data = 'Test desc'
        form.status.data = 'Open'
        form.priority.data = 'Critical' # Invalid choice
        self.assertFalse(form.validate())
        self.assertIn('Not a valid choice.', form.priority.errors)


    # --- CommentForm Tests ---
    def test_comment_form_valid_data(self):
        form = CommentForm(content='This is a test comment.')
        form.content.data = 'This is a test comment.'
        self.assertTrue(form.validate())

    def test_comment_form_missing_content(self):
        form = CommentForm(content='')
        form.content.data = ''
        self.assertFalse(form.validate())
        self.assertIn('This field is required.', form.content.errors)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False) # Use exit=False for running in IDEs