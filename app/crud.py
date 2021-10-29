from sqlalchemy.orm import Session

import datetime as _dt

import database, schemas


def create_database():
    """Create database files in api folder"""
    return database.Base.metadata.create_all(bind=database.engine)


def get_db():
    """Create connection to database"""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create some client functions
def create_client(db: Session, client: schemas.ClientCreate):
    """Add new client to database

    Parameters:
        -> db: establish conversation with database
        -> client: get scheme of client create function

    Returns:
        -> dictionary that contain client information : first name, last name, mail and phone

    """
    db_user = database.Client(first_name=client.first_name, last_name=client.last_name, mail=client.mail,
                            phone=client.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_clients(db: Session, skip: int, limit: int):
    """Get list of all clients stored in database

    Parameters:
        -> db: establish conversation with database
        -> skip (int): number of element to skip from 0
        -> limit (int): maximum number of element to return

    Returns:
        -> list of dictionary that display information about all clients stored in database

    """
    return db.query(database.Client).offset(skip).limit(limit).all()


def delete_client(db: Session, id: int):
    """Delete existing client from database

    Parameters:
        -> db: establish conversation with database
        -> id (int): client id

    """
    db.query(database.Client).filter(database.Client.id == id).delete()
    db.commit()


def get_client(db: Session, id: int):
    """Get information about a client

    Parameters:
        -> db: establish conversation with database
        -> id (int): id of client

    Returns:
        -> Information about client that match with id

    """
    return db.query(database.Client).filter(database.Client.id == id).first()


def update_client(db: Session, id: int, client: schemas.ClientBase):
    """Update information about a client stored in the database

    Parameters:
        -> db: establish conversation with database
        -> id (int): id of client
        -> client (class): information about a client

    Returns:
        -> Information updated about a specified client

    """
    db_client = get_client(db=db, id=id)
    db_client.last_name = client.last_name
    db_client.first_name = client.first_name
    db_client.mail = client.mail
    db_client.phone = client.phone
    db.commit()
    db.refresh(db_client)
    return db_client


# Create some post functions
def get_post(db: Session, user_id: int):
    """Get all posts written by clients.

    Parameters:
        -> db: establish conversation with database
        -> skip (int): number of element to skip from 0
        -> limit (int): maximum number of element to return

    Returns:
        -> Last post created by client

    """
    return db.query(database.Post).filter(database.Post.id_client == user_id).order_by(
        database.Post.date_last_updated.desc()).first()


def get_all_posts(db: Session, skip: int, limit: int):
    """Get list of all clients stored in database

    Parameters:
        -> db: establish conversation with database
        -> skip (int): number of element to skip from 0
        -> limit (int): maximum number of element to return

    Returns:
        -> list of dictionary that display information about all clients stored in database

    """
    return db.query(database.Post).offset(skip).limit(limit).all()


def create_post(db: Session, post: schemas.PostCreate, user_id: int, sentiment: str, positive: float,
                neutral: float, negative: float):
    """Add new post to database

    Parameters:

        -> db: establish conversation with database
        -> id_client (int): if of client
        -> post (class): information about a post

    Returns:
        -> Class instance of post

    """
    db_post = database.Post(text=post.text, id_client=user_id, sentiment=sentiment, positive=positive,
                          neutral=neutral, negative=negative)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_posts(db: Session, id_client: int):
    """Get all post written by a single client

    Parameters:
        -> db: establish conversation with database
        -> id_post (int): id of post

    Returns:
        -> All post filtered that match with specified id client

    """
    return db.query(database.Post).filter(database.Post.id_client == id_client).all()


def update_post(db: Session, post: schemas.PostCreate, user_id: int, sentiment: str, positive: float,
                neutral: float, negative: float):
    """Update post

    Parameters:
        -> db: establish conversation with database
        -> user_id (int): id of user
        -> post (class): information about a posts

    Returns:
        -> Class instance of post

    """
    db_post = get_post(db=db, user_id=user_id)
    db_post.text = post.text
    db_post.sentiment = sentiment
    db_post.positive = positive
    db_post.neutral = neutral
    db_post.negative = negative
    db_post.date_last_updated = _dt.datetime.utcnow()
    db.commit()
    db.refresh(db_post)
    return db_post
