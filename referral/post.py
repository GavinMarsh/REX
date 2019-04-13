from flask import current_app, Blueprint
from models import (User, Referral, Request, Tag,
                    Tags, Awarded, Comment)
from auth import login_required
from flask import (
    redirect, render_template,
    request, url_for, session, abort
)
from datetime import datetime

post = Blueprint('post', __name__, template_folder='templates')


@post.record
def record(state):
    db = state.app.config.get("db_session")

    if db is None:
        raise Exception("This blueprint expects you to provide "
                        "database access through db_session")


@post.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new post for the current user."""
    db_session = current_app.config["db_session"]
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
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


@post.route('/view/<int:id>', methods=['GET'])
@login_required
def view(id):
    """View a post"""
    db_session = current_app.config["db_session"]
    post = db_session.query(Referral).filter(Referral.id_ == id).first()
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
    if post is None:
        abort(404)

    post_user = db_session.query(User).filter(User.id_ == post.user_id).one()
    r_uids = [x.user_id for x in post.request]
    c_uids = [x.user_id for x in post.comment]

    has_requested = user.id_ in r_uids
    request_users = db_session.query(User).filter(User.id_.in_(r_uids)).all()
    comment_users = [db_session.query(User).filter(User.id_ == uid).one() for uid in c_uids]
    comments = [(post.comment[i], comment_users[i]) for i in range(len(post.comment))]

    tagged = post.tag[0] if len(post.tag) > 0 else None
    awarded = post.award[0] if len(post.award) > 0 else None
    tags = []

    if tagged:
        tagged = db_session.query(Tag).filter(Tag.id_ == tagged.tag_id).one()
    else:
        tags = db_session.query(Tag).all()

    if awarded:
        awarded = db_session.query(User).filter(User.id_ == awarded.user_id).one()

    return render_template('blog/post.html', post=post, user=user,
                           post_user=post_user, requests=request_users, tags=tags,
                           comments=comments, has_requested=has_requested, tagged=tagged,
                           awarded=awarded)


@post.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    """Update a post if the current user is the author."""
    db_session = current_app.config["db_session"]
    post = db_session.query(Referral).filter(Referral.id_ == id).first()
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
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


@post.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a post if current user is author."""
    db_session = current_app.config["db_session"]
    post = db_session.query(Referral).filter(Referral.id_ == id).first()
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
    if post is None:
        abort(404)
    if user.id_ != post.user_id:
        abort(405)

    db_session.delete(post)
    db_session.commit()
    return redirect(url_for('index'))


@post.route('/request_post/<int:post_id>', methods=['GET'])
@login_required
def request_post(post_id):
    """Update a post if the current user is the author."""
    db_session = current_app.config["db_session"]
    post = db_session.query(Referral).filter(Referral.id_ == post_id).first()
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
    if post is None:
        abort(404)
    if user.id_ == post.user_id:
        abort(405)

    req = Request(user.id_, post_id)
    db_session.add(req)
    db_session.commit()
    return redirect(url_for('post.view', id=post.id_))


@post.route('/unrequest_post/<int:post_id>', methods=['GET'])
@login_required
def unrequest_post(post_id):
    """Update a post if the current user is the author."""
    db_session = current_app.config["db_session"]
    post = db_session.query(Referral).filter(Referral.id_ == post_id).first()
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
    if post is None:
        abort(404)

    req = db_session.query(Request).filter(Request.post_id == post_id,
                                           Request.user_id == user.id_).first()
    if req is None:
        abort(405)

    db_session.delete(req)
    db_session.commit()
    return redirect(url_for('post.view', id=post.id_))


@post.route('/tag_post/<int:post_id>', methods=['POST'])
@login_required
def tag_post(post_id):
    """Update a post if the current user is the author."""
    db_session = current_app.config["db_session"]
    post = db_session.query(Referral).filter(Referral.id_ == post_id).first()
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
    if post is None:
        abort(404)
    if user.id_ != post.user_id:
        abort(405)

    tag_id = int(request.form["tag"])
    tag = db_session.query(Tag).filter(Tag.id_ == tag_id).first()
    if not tag:
        abort(405)

    tagged = db_session.query(Tags).filter(Tags.post_id == post_id).first()
    if tagged:
        abort(405)

    tagged = Tags(post_id, tag_id)
    db_session.add(tagged)
    db_session.commit()
    return redirect(url_for('post.view', id=post.id_))


@post.route('/untag_post/<int:post_id>', methods=['GET'])
@login_required
def untag_post(post_id):
    """Update a post if the current user is the author."""
    db_session = current_app.config["db_session"]
    post = db_session.query(Referral).filter(Referral.id_ == post_id).first()
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
    if post is None:
        abort(404)
    if user.id_ != post.user_id:
        abort(405)

    tagged = db_session.query(Tags).filter(Tags.post_id == post_id).first()
    if not tagged:
        abort(405)

    db_session.delete(tagged)
    db_session.commit()
    return redirect(url_for('post.view', id=post.id_))


@post.route('/award_post/<int:post_id>', methods=['POST'])
@login_required
def award_post(post_id):
    """Search: Filter post by user"""
    db_session = current_app.config["db_session"]
    post = db_session.query(Referral).filter(Referral.id_ == post_id).first()
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
    if post is None:
        abort(404)
    if user.id_ != post.user_id:
        abort(405)
    awarded = len(post.award) > 0
    if awarded:
        abort(405)

    user_id = int(request.form["award"])
    user = db_session.query(User).filter(User.id_ == user_id).first()
    if not user:
        abort(405)

    award = Awarded(user.id_, post_id)
    db_session.add(award)
    db_session.commit()
    return redirect(url_for('post.view', id=post.id_))


@post.route('/unaward_post/<int:post_id>', methods=['GET'])
@login_required
def unaward_post(post_id):
    """Search: Filter post by user"""
    db_session = current_app.config["db_session"]
    post = db_session.query(Referral).filter(Referral.id_ == post_id).first()
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
    if post is None:
        abort(404)
    if user.id_ != post.user_id:
        abort(405)
    awarded = len(post.award) > 0
    if not awarded:
        abort(405)

    award = post.award[0]
    db_session.delete(award)
    db_session.commit()
    return redirect(url_for('post.view', id=post.id_))


@post.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    """Search: Filter post by user"""
    db_session = current_app.config["db_session"]
    post = db_session.query(Referral).filter(Referral.id_ == post_id).first()
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
    if post is None:
        abort(404)

    comment = request.form["comment"]
    comment = Comment(user.id_, post.id_, comment)
    db_session.add(comment)
    db_session.commit()
    return redirect(url_for('post.view', id=post.id_))


@post.route('/delete_comment/<int:comment_id>/<int:post_id>', methods=['GET'])
@login_required
def delete_comment(comment_id, post_id):
    """Search: Filter post by user"""
    db_session = current_app.config["db_session"]
    user = db_session.query(User).filter(User.id_ == session.get("user_id")).first()
    comment = db_session.query(Comment).filter(Comment.id_ == comment_id).first()
    if comment is None:
        abort(404)
    if user.id_ != comment.user_id:
        abort(405)

    db_session.delete(comment)
    db_session.commit()
    return redirect(url_for('post.view', id=post_id))
