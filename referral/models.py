"""Models for Hydra Classes."""
import pdb
from settings import DB_URL
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from passlib.hash import bcrypt
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date

Base = declarative_base()
engine = create_engine(DB_URL)


class User(Base):
    """Model for Users.

    Each user has a username and password that matches with their ubuntu login IDs.
    """

    __tablename__ = "users"

    id_ = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True)
    password = Column(String(20))
    desc = Column(String(100))

    def __init__(self, username, password):
        """Create new instance."""
        self.username = username
        self.password = bcrypt.encrypt(password)
        self.desc = ""

    def validate_password(self, password):
        """Check encrypted password."""
        return bcrypt.verify(password, self.password)

    def __repr__(self):
        """Verbose object name."""
        return "<id='%s', username='%s'>" % (self.id_, self.username)


class Referral(Base):
    """Model prefered songs of a user."""

    __tablename__ = "referral"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"), unique=False)
    title = Column(String(200))
    turnover = Column(String(50))
    project_date = Column(Date)
    enum = Column(String(100))
    timestamp = Column(Date)
    budget = Column(String(50))
    description = Column(String(2500))

    request = relationship("Request", cascade="all,delete", backref="request")
    tag = relationship("Tag", cascade="all,delete", backref="tag")
    comment = relationship("Comment", cascade="all,delete", backref="comment")

    def __init__(self, user_id, title, turnover, budget, project_date, description, enum):
        """Create new instance."""
        self.user_id = user_id
        self.title = title
        self.turnover = turnover
        self.budget = budget
        self.enum = enum
        if type(project_date) is date:
            self.project_date = project_date
        self.description = description
        self.timestamp = date.today()

    def update(self, title=None, turnover=None, budget=None, project_date=None, description=None, enum=None):
        """Create new instance."""
        if title:
            self.title = title
        if enum:
            self.enum = enum
        if turnover:
            self.turnover = turnover
        if budget:
            self.budget = budget
        if project_date:
            if type(project_date) is date:
                self.project_date = project_date
        if description:
            self.description = description
        self.timestamp = date.today()

    def __repr__(self):
        """Verbose object name."""
        return "<postid='%s', userid='%s', title='%s'>" % (self.id_, self.user_id, self.title)


class Request(Base):
    """Model for Genre Profile."""

    __tablename__ = "request"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"))
    post_id = Column(Integer, ForeignKey("referral.id_", ondelete='CASCADE'))

    def __init__(self, user_id, post_id):
        """Create new instance."""
        self.user_id = user_id
        self.post_id = post_id

    def __repr__(self):
        """Verbose object name."""
        return "<userid='%s', postid='%s'>" % (self.user_id, self.post_id)


class Tag(Base):
    """Model for Genre Profile."""

    __tablename__ = "tag"

    id_ = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("referral.id_", ondelete='CASCADE'))
    tag_name = Column(String(100), unique=True)

    def __init__(self, post_id, tag_name):
        """Create new instance."""
        self.post_id = post_id
        self.tag_name = tag_name

    def __repr__(self):
        """Verbose object name."""
        return "<tag='%s', postid='%s'>" % (self.tag_name, self.post_id)


class Comment(Base):
    """Model for Genre Profile."""

    __tablename__ = "comment"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"))
    post_id = Column(Integer, ForeignKey("referral.id_", ondelete='CASCADE'))
    content = Column(String(500))

    def __init__(self, user_id, post_id, content):
        """Create new instance."""
        self.user_id = user_id
        self.post_id = post_id
        self.content = content

    def __repr__(self):
        """Verbose object name."""
        return "<userid='%s', postid='%s', content='%s'>" % (self.user_id, self.post_id, self.content)


class Alert(Base):
    """Model for Genre Profile."""

    __tablename__ = "alert"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"))

    def __init__(self, user_id):
        """Create new instance."""
        self.user_id = user_id

    def __repr__(self):
        """Verbose object name."""
        return "<userid='%s'>" % (self.user_id)


class Awarded(Base):
    """Model for Genre Profile."""

    __tablename__ = "award"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"))
    post_id = Column(Integer, ForeignKey("referral.id_"))

    def __init__(self, user_id, post_id):
        """Create new instance."""
        self.user_id = user_id
        self.post_id = post_id

    def __repr__(self):
        """Verbose object name."""
        return "<userid='%s', postid='%s'>" % (self.user_id, self.post_id)


def get_debug_session(DB_URL):
    """Get a DB session for debugging."""
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def setup(DB_URL):
    """Setup."""
    # Create database tables
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Add test
    adminuser = User("test", "test")
    session.add(adminuser)
    session.commit()
    return session


if __name__ == "__main__":
    session = setup(DB_URL)
    session = get_debug_session(DB_URL)

    # Adding some fake data to test
    d = date.today()
    for i in range(30):
        adminuser = User("test"+str(i), "test")
        session.add(adminuser)
    session.commit()
    for i in range(1, 31):
        adminuser = Referral(i, "Testing", "40000", "40000", d, "Testing project", "224RDF")
        session.add(adminuser)
    session.commit()
    pdb.set_trace()
