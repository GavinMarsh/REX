import sys

from flask import (
    Flask, redirect, render_template,
    request, url_for, abort, session
)
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from math import ceil
from models import (User, Referral, Request, Awarded)
from models import engine
from auth import auth, login_required
from post import post
from settings import (Key, post_limit)
import pdb


print("Setting up app...")
app = Flask(__name__)
app.secret_key = Key
print("Creating database link and session...")
db_session = scoped_session(sessionmaker(bind=engine))
app.config["db_session"] = db_session
app.register_blueprint(auth)
app.register_blueprint(post)


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


@app.route('/user/<int:id>', methods=['GET'])
@app.route('/user/<int:id>/<string:edit>', methods=['GET', 'POST'])
@login_required
def user(id, edit=""):
    """User page"""
    if edit not in ["", "edit"]:
        abort(405)
    user = get_user(session.get("user_id"), db_session)
    editable = id is user.id_
    edit = edit.strip() == "edit"

    if not editable and edit:
        abort(405)

    if request.method == "POST":
        desc = request.form["desc"]
        user.desc = desc
        db_session.commit()
        return redirect(url_for('user', id=id))

    requests = db_session.query(Request).filter(Request.user_id == user.id_).count()
    awards = db_session.query(Awarded).filter(Awarded.user_id == user.id_).count()
    referrals = db_session.query(Referral).filter(Referral.user_id == user.id_).count()

    return render_template('blog/user.html', user=user, requests=requests, referrals=referrals,
                           awards=awards, edit=edit, editable=editable)


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
