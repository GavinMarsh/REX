import functools
import sys
from datetime import datetime

from flask import (
    Flask, flash, redirect, render_template,
    request, url_for, abort, session
)
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from math import ceil
from models import (User, Referral)
from settings import (Key, DB_URL, post_limit)


print("Setting up app...")
app = Flask(__name__)
app.secret_key = Key
print("Creating database link and session...")
engine = create_engine(DB_URL)
db_session = scoped_session(sessionmaker(bind=engine))


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for('login'))
        return view(**kwargs)

    return wrapped_view


def get_user(user_id, db_session):
    user = db_session.query(User).filter(User.id_ == user_id).one()
    return user


def get_all_posts(pagenum, db_session):
    posts = db_session.query(Referral).offset((pagenum-1) * post_limit).limit(post_limit).all()
    users_posts = []
    for p in posts:
        up = (p, db_session.query(User.username).filter(User.id_ == p.user_id).one()[0])
        users_posts.append(up)

    total_pages = ceil(db_session.query(Referral).count() / float(post_limit))
    return users_posts, total_pages


@app.route('/', methods=["GET"])
@app.route('/<int:pagenum>', methods=["GET"])
@login_required
def index(pagenum=1):
    """Show all the posts, most recent first."""
    user = get_user(session.get("user_id"), db_session)
    posts, total_pages = get_all_posts(pagenum, db_session)

    if pagenum > total_pages and total_pages != 0:
        abort(404)
    context = {"posts": posts,
               "pagenum": pagenum,
               "total_pages": total_pages}

    return render_template('blog/index.html', user=user, **context)


@app.route('/search', methods=['GET'])
@login_required
def search():
    """Search: Filter post by user"""
    # Implement search that filters by users
    pass


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new post for the current user."""
    user = get_user(session.get("user_id"), db_session)
    if request.method == 'POST':
        content = {}
        content["user_id"] = user.id_
        content["title"] = request.form['title']
        content["enum"] = request.form['enum']
        content["turnover"] = request.form['turnover']
        pdate = request.form['project_date']
        content["project_date"] = datetime.strptime(pdate, "%Y-%m-%d").date()
        content["budget"] = request.form['budget']
        content["description"] = request.form['desc']

        referral = Referral(**content)
        db_session.add(referral)
        db_session.commit()
        return redirect(url_for('index'))

    return render_template('blog/create.html', user=user)


@app.route('/view/<int:id>', methods=['GET'])
@login_required
def view(id):
    """View a post"""
    post = db_session.query(Referral).filter(Referral.id_ == id).first()
    user = get_user(session.get("user_id"), db_session)
    if post is None:
        abort(404)
    post_user = get_user(post.user_id, db_session)

    return render_template('blog/post.html', post=post, user=user, post_user=post_user)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = db_session.query(Referral).filter(Referral.id_ == id).first()
    user = get_user(session.get("user_id"), db_session)
    if post is None:
        abort(404)
    if user.id_ != post.user_id:
        abort(405)

    if request.method == 'POST':
        content = {}
        content["title"] = request.form['title']
        content["enum"] = request.form['enum']
        content["turnover"] = request.form['turnover']
        pdate = request.form['project_date']
        content["project_date"] = datetime.strptime(pdate, "%Y-%m-%d").date()
        content["budget"] = request.form['budget']
        content["description"] = request.form['desc']

        post.update(**content)
        db_session.commit()
        return redirect(url_for('index'))

    return render_template('blog/update.html', post=post, user=user)


@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a post if current user is author."""
    post = db_session.query(Referral).filter(Referral.id_ == id).first()
    user = get_user(session.get("user_id"), db_session)
    if post is None:
        abort(404)
    if user.id_ != post.user_id:
        abort(405)

    db_session.delete(post)
    db_session.commit()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        user = db_session.query(User).filter(User.username == username).first()
        if user is not None:
            error = 'User {0} is already registered.'.format(username)

        if error is None:
            user = User(username, password)
            db_session.add(user)
            db_session.commit()
            return redirect(url_for('login'))

        flash(error)

    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = db_session.query(User).filter(User.username == username).first()

        if user is None:
            error = 'Incorrect username.'
        else:
            user = user[0]
            if not user.validate_password(password):
                error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['user_id'] = user.id_
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage:\n\tpython app.py [host address] [port]\n")
        sys.exit(0)

    IP_addr = sys.argv[1]
    port = sys.argv[2]
    try:
        print("Running server...")
        app.run(host=IP_addr, debug=True, port=int(port))

    # http_server = WSGIServer((IP_addr, int(port)), app)
    # print("Server running on http://{}:{}".format(IP_addr, port))
    # try:
    #     http_server.serve_forever()
    except KeyboardInterrupt:
        print("Exiting server")
        sys.exit(0)
