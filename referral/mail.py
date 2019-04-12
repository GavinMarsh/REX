from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os

from flask import Flask
from flask_mail import Mail, Message
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from models import Referral, Alert, User
from models import engine

app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "referraltestingemail@gmail.com",
    "MAIL_PASSWORD": "referral",
    "SITE_URL": "http://52.221.187.163:8088/"
}

app.config.update(mail_settings)
mail = Mail(app)
db_session = scoped_session(sessionmaker(bind=engine))


def get_user_emails():
    alert = db_session.query(Alert).all()
    user_ids = [x.user_id for x in alert]
    users = db_session.query(User).filter(User.id_.in_(user_ids)).all()
    user_emails = [u.email for u in users]
    return user_emails


def get_new_posts():
    posts = db_session.query(Referral).filter(Referral.processed == "False").all()
    return posts


def mark_posts(posts):
    for post in posts:
        post.processed = "True"
    db_session.commit()


def build_email(URL, posts):
    posts = [(os.path.join(URL, "view", str(x.id_)), x.title)
             for x in posts]
    subject = "{} New Referrals posted".format(len(posts))

    links = ["<li><a href={}>{}</a></li>".format(l, t)
             for l, t in posts]

    body = ["<h1>There have been {} new referrals posted </h1><br>".format(len(posts)),
            "<h4>Here are a list of referrals</h4><br>",
            "<ul>{}</ul>".format("\n".join(links))]
    body = "\n".join(body)

    return subject, body


def send_email():
    users = get_user_emails()
    posts = get_new_posts()
    if len(users) == 0 or len(posts) == 0:
        mark_posts(posts)
        return None

    with app.app_context():
        subject, body = build_email(app.config.get("SITE_URL"), posts)
        # subject, body = "Hello", "<h1>Testing processed {} </h1>".format(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))
        msg = Message(subject=subject,
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=users)
        msg.html = body
        mail.send(msg)
        print("Email sent to {} users".format(len(users)))

    mark_posts(posts)
    return None


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=send_email, trigger="interval", seconds=3600)
    scheduler.start()

    app.run(debug=False)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
