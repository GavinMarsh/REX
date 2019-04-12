from flask import current_app, Blueprint
from models import Referral, User
from flask import request
import os
from werkzeug.contrib.atom import AtomFeed

rss = Blueprint('rss', __name__, template_folder='templates')


@rss.record
def record(state):
    db = state.app.config.get("db_session")

    if db is None:
        raise Exception("This blueprint expects you to provide "
                        "database access through db_session")


@rss.route('/feed', methods=['GET'])
def feed():
    """Register a new user."""
    db_session = current_app.config["db_session"]
    rss_feed = AtomFeed('Recent Articles',
                        feed_url=request.url, url=request.url_root)
    posts = db_session.query(Referral).order_by(Referral.timestamp.desc())
    posts = posts.limit(10).all()

    for post in posts:
        user = db_session.query(User).filter(User.id_ == post.user_id).one()
        rss_feed.add(post.title, post.description,
                     content_type='html',
                     author=user.username,
                     url=os.path.join(request.url_root, "view", str(post.id_)),
                     updated=post.timestamp,
                     )
    return rss_feed.get_response()
