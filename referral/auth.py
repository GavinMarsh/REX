from flask import current_app, Blueprint
from models import User
from flask import (
    flash, redirect, render_template,
    request, url_for, session
)
import functools

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.record
def record(state):
    db = state.app.config.get("db_session")

    if db is None:
        raise Exception("This blueprint expects you to provide "
                        "database access through db_session")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for('auth.login'))

        db_session = current_app.config["db_session"]
        user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
        if user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    db_session = current_app.config["db_session"]
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        user = db_session.query(User).filter(User.username == username).first()
        if user is not None:
            error = 'User {0} is already registered.'.format(username)

        if error is None:
            user = User(username, password, email)
            db_session.add(user)
            db_session.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a registered user by adding the user id to the session."""
    db_session = current_app.config["db_session"]
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = db_session.query(User).filter(User.username == username).first()

        if user is None:
            error = 'Incorrect username.'
        else:
            if not user.validate_password(password):
                error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['user_id'] = user.id_
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for('index'))
