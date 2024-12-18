from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse
from app import db
from app.models import User, Ticket, Comment
from app.forms import LoginForm, RegistrationForm, TicketForm, CommentForm
from flask import Blueprint
from app.decorators import admin_required

bp = Blueprint('routes', __name__)

@bp.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        # Admin sees all tickets
        tickets = Ticket.query.all()
    else:
        # Regular user sees only their tickets
        tickets = Ticket.query.filter_by(user_id=current_user.id).all()

    return render_template('index.html', title='Home', tickets=tickets)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))  # Correctly prefixed
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('routes.login'))  # Correctly prefixed
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('routes.index')  # Correctly prefixed
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.index'))  # Correctly prefixed

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/create_ticket', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        # Create a new ticket and associate it with the logged-in user
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            priority=form.priority.data,
            user_id=current_user.id  # Associate ticket with the logged-in user
        )
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for('routes.index'))  # Redirect to the index page to view tickets
    return render_template('create_ticket.html', title='Create Ticket', form=form)

@bp.route('/ticket/<int:id>', methods=['GET', 'POST'])
@login_required
def ticket(id):
    ticket = Ticket.query.get_or_404(id)
    comments = Comment.query.filter_by(ticket_id=id).all()
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(content=form.content.data, ticket_id=id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added.')
        return redirect(url_for('routes.ticket', id=id))  # Correctly prefixed

    # Ensure this return statement is outside the if block
    return render_template('ticket.html', title=ticket.title, ticket=ticket, comments=comments, form=form)


@bp.route('/update_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    form = TicketForm(obj=ticket)
    if form.validate_on_submit():
        ticket.title = form.title.data
        ticket.description = form.description.data
        ticket.status = form.status.data
        ticket.priority = form.priority.data
        db.session.commit()
        flash('Ticket updated successfully!', 'success')
        return redirect(url_for('routes.index'))
    return render_template('edit_ticket.html', title='Edit Ticket', form=form, ticket=ticket)

@bp.route('/create_admin', methods=['POST'])
def create_admin():
    admin_user = User(username='admin', email='admin@example.com', role='admin')
    admin_user.set_password('adminpassword')
    db.session.add(admin_user)
    db.session.commit()
    return redirect(url_for('routes.admin_panel'))

@bp.route('/admin')
@login_required
@admin_required  # Protect this route with admin access control
def admin_panel():
    users = User.query.all()
    tickets = Ticket.query.all()
    comments = Comment.query.all()
    return render_template('admin_panel.html', users=users, tickets=tickets, comments=comments)

@bp.route('/admin/update_ticket_status/<int:ticket_id>', methods=['POST'])
@login_required
@admin_required
def update_ticket_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    new_status = request.form.get('status')
    if new_status:
        ticket.status = new_status
        db.session.commit()
        flash('Ticket status updated successfully!', 'success')
    else:
        flash('Invalid status selection', 'danger')
    return redirect(url_for('routes.admin_panel'))

@bp.route('/admin/delete_ticket/<int:id>')
@login_required
@admin_required  # Only admin can delete tickets
def delete_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket has been deleted.')
    return redirect(url_for('routes.admin_panel'))

@bp.route('/admin/delete_user/<int:id>')
@login_required
@admin_required  # Only admin can delete users
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted.')
    return redirect(url_for('routes.admin_panel'))

@bp.route('/admin/delete_comment/<int:id>')
@login_required
@admin_required  # Only admin can delete comments
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment has been deleted.')
    return redirect(url_for('routes.admin_panel'))
