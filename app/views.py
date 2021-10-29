import sys

from app.config import ENDPOINT
sys.path.append("..")
from typing import List

from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from config import ENDPOINT, KEY
    
import crud
import schemas

from ml.text_prediction import ml_model, text_cleaning, enc

app = FastAPI()


text_analytics_client = TextAnalyticsClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
    
if __name__ == "__main__":
    crud.create_database()


# ----- CREATE COACH REQUESTS ----- #
@app.post("/clients/")
def create_client(client: schemas.ClientCreate, db: Session = Depends(crud.get_db)):
    """Add new client to database

    Parameters:
        -> client (class) : information required to create new client :
            -> first_name (str)
            -> last_name (str)
            -> mail (str)
            -> phone (str)
        -> db: create connection to SQL database

    Returns:
        -> dic that summarize all information about the new client

    """
    return crud.create_client(db=db, client=client)


@app.delete("/clients/")
def delete_client(id: int, db: Session = Depends(crud.get_db)):
    """Delete existing client from database

    Parameters:
        -> id (int): client id
        -> db: create connection to SQL database

    Returns:
        -> String confirming that client has been successfully removed
    """
    client = crud.get_client(db=db, id=id)
    if client is None:
        raise HTTPException(
            status_code=404, detail="sorry this client does not exist"
        )
    else:
        crud.delete_client(db=db, id=id)
        return f"User with id {id} has been successfully deleted"


@app.get("/clients/", response_model=List[schemas.Client])
def read_clients(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(crud.get_db),
):
    """Get list of client stored in database

    Parameters:
        -> skip (int): number of client to skip from 0
        -> limit (int): max number of client information to display
        -> db: create connection to SQL database

    Returns:
        -> List of dictionaries with information about clients for range specified
    """
    clients = crud.get_clients(db=db, skip=skip, limit=limit)
    return clients


@app.get("/clients/{id}")
def read_client(
        id: int,
        db: Session = Depends(crud.get_db),
):
    """Get information about a single client.

    Parameters:
        -> id (int): client id
        -> db: create connection to SQL database

    Returns:
        -> dictionary with information about a client
    """
    client = crud.get_client(db=db, id=id)
    return client


@app.put("/clients/{client_id}")
def update_client(
        client_id: int,
        client: schemas.ClientBase,
        db: Session = Depends(crud.get_db),
):
    """Update client information in client table.

    Parameters:
        -> client_id (int): id of client
        -> client (class): information about a client
        -> db: create connection to SQL database

    Returns:
        -> dictionary with client information updated
    """
    is_in_list = crud.get_client(db=db, id=client_id)
    if is_in_list is None:
        raise HTTPException(
            status_code=404, detail="sorry this client does not exist"
        )
    else:
        return crud.update_client(db=db, id=client_id, client=client)


# ----- CREATE POST REQUESTS ----- #
@app.post("/clients/{user_id}/post/")
def create_post(post: schemas.PostCreate,
                user_id: int,
                db: Session = Depends(crud.get_db),
                ):
    """Add new post to Post table and make sentiment prediction.

    Parameters:
        -> post (class): information about a post
        -> user_id (int) : client id
        -> db: create connection to SQL database

    Returns:
        -> dictionary with post created and sentiment prediction
    """
    # clean the review
    cleaned_post = text_cleaning(post.text)
    enc_text = enc.transform([cleaned_post])

    # perform prediction
    prediction = ml_model.predict(enc_text)
    output = int(prediction[0])
    probas = ml_model.predict_proba(enc_text)
    
    result = text_analytics_client.analyze_sentiment(post.text, show_opinion_mining=True)
    
    # output dictionary
    sentiments = {0: "negative", 1: "neutral", 2: "positive"}

    # show results
    return crud.create_post(db=db, post=post, user_id=user_id, sentiment=result.sentiment,
                            negative=probas[0][0], neutral=probas[0][1],
                            positive=probas[0][2])


@app.put("/clients/{user_id}/post/")
def update_post(post: schemas.PostCreate,
                user_id: int,
                db: Session = Depends(crud.get_db)):
    """Update most recent post written by a client.

    Parameters:
        -> post (class): information about a post
        -> user_id (int) : id of user
        -> db: create connection to SQL database

    Returns:
        -> dictionary with message updated
    """
    is_in_list = crud.get_posts(db=db, id_client=user_id)
    if is_in_list is None:
        raise HTTPException(
            status_code=404, detail="sorry, you are looking for post that does not exist"
        )
    else:
        # clean the review
        cleaned_post = text_cleaning(post.text)
        enc_text = enc.transform([cleaned_post])

        # perform prediction
        prediction = ml_model.predict(enc_text)
        output = int(prediction[0])
        probas = ml_model.predict_proba(enc_text)

        # output dictionary
        sentiments = {0: "negative", 1: "neutral", 2: "positive"}

        # show results
        return crud.update_post(db=db, post=post, user_id=user_id, sentiment=sentiments[output],
                                negative=probas[0][0], neutral=probas[0][1],
                                positive=probas[0][2])


@app.get("/clients/{user_id}/post/", response_model=List[schemas.PostPrediction])
def read_post(
        user_id: int,
        db: Session = Depends(crud.get_db),
):
    """Read all from message posted by a user.

    Parameters:
        -> user_id (int): id of user
        -> db: create connection to SQL database

    Returns:
        -> list of posts written by client with id specified
    """
    posts = crud.get_posts(db=db, id_client=user_id)
    return posts


@app.get("/clients/posts/", response_model=List[schemas.PostPrediction])
def read_posts(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(crud.get_db),
):
    """Read all posts written by clients

    Parameters:
        -> skip (int): number of posts to skip from 0
        -> limit (int): max number of posts to display
        -> db: create connection to SQL database

    Returns:
        -> List of dictionaries with all posts written by clients and their prediction
    """
    posts = crud.get_all_posts(db=db, skip=skip, limit=limit)
    return posts
