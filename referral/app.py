import sys

from flask import (
    Flask, redirect, render_template,
    request, url_for, abort, session
)
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

from math import ceil
from models import (User, Referral, Request, Awarded,
                    Tag, Tags, Alert)
from models import engine
from auth import auth, login_required
from post import post
from rss import rss
from settings import (Key, post_limit)


print("Creating app...")
app = Flask(__name__)
print("Creating database link and session...")
db_session = scoped_session(sessionmaker(bind=engine))
print("Configuring app...")
app.secret_key = Key
app.config["db_session"] = db_session
app.register_blueprint(auth)
app.register_blueprint(post)
app.register_blueprint(rss)


def get_user(user_id, db_session):
    user = db_session.query(User).filter(User.id_ == user_id).first()
    return user


def get_all_posts(pagenum, db_session):
    posts = db_session.query(Referral).order_by(desc(Referral.timestamp))
    posts = posts.offset((pagenum-1) * post_limit).limit(post_limit).all()
    users_posts = []
    for p in posts:
        up = (p, db_session.query(User.username).filter(User.id_ == p.user_id).one()[0])
        users_posts.append(up)

    total_pages = ceil(db_session.query(Referral).count() / float(post_limit))
    return users_posts, total_pages


def get_all_tagged_posts(pagenum, db_session, post_ids):
    posts_all = db_session.query(Referral).filter(Referral.id_.in_(post_ids))
    posts_tagged = posts_all.offset((pagenum-1) * post_limit).limit(post_limit).all()
    users_posts = []
    for p in posts_tagged:
        up = (p, db_session.query(User.username).filter(User.id_ == p.user_id).one()[0])
        users_posts.append(up)

    total_pages = ceil(posts_all.count() / float(post_limit))
    return users_posts, total_pages


def get_all_user_posts(pagenum, db_session, user_id):
    posts_all = db_session.query(Referral).filter(Referral.user_id == user_id)
    posts_tagged = posts_all.offset((pagenum-1) * post_limit).limit(post_limit).all()
    users_posts = []
    for p in posts_tagged:
        up = (p, db_session.query(User.username).filter(User.id_ == p.user_id).one()[0])
        users_posts.append(up)

    total_pages = ceil(posts_all.count() / float(post_limit))
    return users_posts, total_pages


@app.route('/', methods=["GET"])
@app.route('/<int:pagenum>', methods=["GET"])
def index(pagenum=1):
    """Show all the posts, most recent first."""
    user = get_user(session.get("user_id"), db_session)
    posts, total_pages = get_all_posts(pagenum, db_session)

    if pagenum > total_pages and total_pages != 0:
        abort(404)

    return render_template('blog/index.html', user=user, posts=posts,
                           pagenum=pagenum, total_pages=total_pages)


@app.route('/search', methods=['GET'])
@app.route('/search/<int:pagenum>', methods=['GET'])
def search(pagenum=1):
    """Search: Filter post by user"""
    user = get_user(session.get("user_id"), db_session)
    query = request.args["search"].strip()
    query_user = db_session.query(User).filter(User.username == query).first()

    if query_user is None:
        return render_template('blog/search.html', no_user=True, query=query, user=user)

    posts, total_pages = get_all_user_posts(pagenum, db_session, query_user.id_)

    if pagenum > total_pages and total_pages != 0:
        abort(404)

    no_posts = len(posts) > 0

    return render_template('blog/search.html', user=user, posts=posts,
                           pagenum=pagenum, total_pages=total_pages,
                           no_posts=no_posts, query=query)


@app.route('/tag_search/<int:tag_id>', methods=['GET'])
@app.route('/tag_search/<int:tag_id>/<int:pagenum>', methods=["GET"])
@login_required
def tag_search(tag_id, pagenum=1):
    """Search: Filter post by user"""
    user = get_user(session.get("user_id"), db_session)
    tag = db_session.query(Tag).filter(Tag.id_ == tag_id).one()
    if not tag:
        abort(405)
    tagged_posts = db_session.query(Tags).filter(Tags.tag_id == tag_id).all()
    tagged_posts = [post.post_id for post in tagged_posts]
    posts, total_pages = get_all_tagged_posts(pagenum, db_session, tagged_posts)

    if pagenum > total_pages and total_pages != 0:
        abort(404)

    no_posts = len(posts) > 0

    return render_template('blog/tagged.html', user=user, posts=posts,
                           pagenum=pagenum, total_pages=total_pages, tag=tag,
                           no_posts=no_posts)


@app.route('/user/<int:id>', methods=['GET'])
@app.route('/user/<int:id>/<string:edit>', methods=['GET', 'POST'])
@login_required
def user(id, edit=""):
    """User page"""
    if edit not in ["", "edit"]:
        abort(405)
    user = get_user(id, db_session)
    editable = id is session.get("user_id")
    edit = edit.strip() == "edit"

    if not editable and edit:
        abort(405)

    if request.method == "POST":
        desc = request.form["desc"]
        email = request.form["email"]
        user.desc = desc
        user.email = email
        db_session.commit()
        return redirect(url_for('user', id=id))

    requests = db_session.query(Request).filter(Request.user_id == user.id_).count()
    awards = db_session.query(Awarded).filter(Awarded.user_id == user.id_).count()
    referrals = db_session.query(Referral).filter(Referral.user_id == user.id_).count()

    alert = db_session.query(Alert).filter(Alert.user_id == user.id_).first()

    return render_template('blog/user.html', user=user, requests=requests, referrals=referrals,
                           awards=awards, edit=edit, editable=editable, alert=alert)


@app.route('/subscribe/<string:argument>', methods=['GET'])
@login_required
def subscribe(argument):
    """Search: Filter post by user"""
    if argument not in ["S", "U"]:
        abort(405)
    user = get_user(session.get("user_id"), db_session)
    sub = db_session.query(Alert).filter(Alert.user_id == user.id_).first()

    if argument == "S":
        if sub is None:
            sub = Alert(user.id_)
            db_session.add(sub)
            db_session.commit()
    elif argument == "U":
        if sub is not None:
            db_session.delete(sub)
            db_session.commit()

    return redirect(url_for('user', id=user.id_))


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage:\n\tpython app.py [host address] [port]\n")
        sys.exit(0)

    IP_addr = sys.argv[1]
    port = sys.argv[2]
    try:
        print("Running server...")
        app.run(host=IP_addr, debug=True, port=int(port))

    except KeyboardInterrupt:
        print("Exiting server")
        sys.exit(0)
