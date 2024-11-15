import datetime
from datetime import timedelta
from operator import itemgetter
import os


import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from langchain.docstore.document import Document
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from fastapi import Query
from langchain_core.messages import HumanMessage
import json
from typing import Literal
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langfuse import Langfuse
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from contextlib import asynccontextmanager
import logging
from fastapi.security.api_key import APIKeyHeader
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN


load_dotenv()


API_KEY = os.getenv("API_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST")
DATABASE_URL = os.getenv("DATABASE_URL")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "chatusers"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    def verify_password(self, password: str):
        return bcrypt.checkpw(
            password.encode("utf-8"), self.hashed_password.encode("utf-8")
        )


class UserIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    username: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


embeddings = OllamaEmbeddings(base_url=OLLAMA_HOST, model="llama3.2")

store = PGVector(
    collection_name="mydatabase",
    connection_string=DATABASE_URL,
    embedding_function=embeddings,
)
store.add_documents(
    [Document(page_content="Menu Item 1: Pizza Margherita costs 5 dollars")]
)
store.add_documents([Document(page_content="Menu Item 2: Capuccino costs $322")])
store.add_documents([Document(page_content="Menu Item 3: Gellatto $12")])
retriever = store.as_retriever()

template = """
Answer the question based only on the following context:
{context}

Always speak to the user with his/her name: {name}. 
Never forget the user's name. Say Hello {name}
Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
model = ChatOllama(base_url=OLLAMA_HOST, model="llama3.2")

chain = (
    {
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question"),
        "name": itemgetter("name"),
    }
    | prompt
    | model
    | StrOutputParser()
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
SECRET_KEY = "your_jwt_secret_key"

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    logger.info(api_key_header)
    logger.info(API_KEY)
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API key"
        )


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(
        password.encode("utf-8"), user.hashed_password.encode("utf-8")
    ):
        return False
    return user


def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def get_langfuse():
    return Langfuse(
        host=LANGFUSE_HOST,
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
    )


# def get_trace_handler(
#     langfuse: Langfuse = Depends(get_langfuse), user=Depends(get_current_user)
# ):
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated"
def get_trace_handler(
    langfuse: Langfuse = Depends(get_langfuse),
    api_key: str = Depends(get_api_key),
):
    trace = langfuse.trace(user_id=api_key)
    return trace.get_langchain_handler()


@app.get("/")
async def read_root(api_key: str = Depends(get_api_key)):
    logger.info("Root endpoint accessed")
    return {"Hello": "World"}


@app.post("/register", response_model=UserOut)
def register(user_in: UserIn, db: Session = Depends(get_db)):
    logger.info("/register endpoint accessed")
    db_user = db.query(User).filter(User.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = bcrypt.hashpw(user_in.password.encode("utf-8"), bcrypt.gensalt())
    new_user = User(
        username=user_in.username, hashed_password=hashed_password.decode("utf-8")
    )
    db.add(new_user)
    db.commit()
    return UserOut(username=new_user.username)


@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(hours=1)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# @app.post("/chat/")
# async def quick_response(
#     question: str, user=Depends(get_current_user), handler=Depends(get_trace_handler)
# ):
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated"
#         )
#     query = {"question": question, "name": user.username}
#     result = await chain.ainvoke(query, config={"callbacks": [handler]})
#     return result


@app.post("/chat/")
async def quick_response(
    question: str,
    api_key: str = Depends(get_api_key),
    handler=Depends(get_trace_handler),
):
    # if user is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated"
    #     )
    # query = {"question": question, "name": user.username}
    query = {"question": question, "name": "Bruno"}
    result = await chain.ainvoke(query, config={"callbacks": [handler]})
    return result


# Define the ContentType
ContentType = Literal["event", "job", "codebase", "user"]


# Define the input model
class SpamCheckInput(BaseModel):
    type: ContentType
    text: str


@app.post("/spamcheck/")
async def spam_check(
    input_data: SpamCheckInput,
    api_key: str = Depends(get_api_key),
    handler=Depends(get_trace_handler),
):
    logger.info(f"Checking {input_data.type} with text {input_data.text}.")

    text = input_data.text[0:500]

    prompt = {
        "role": "human",
        "content": f"""Is this a spam submission for the {input_data.type} board on a website for computational modelling and agent based modelling in social and ecological studies: ```{text}```

Respond using JSON only with the following structure:
{{
    "is_spam": boolean,
    "spam_indicators": [list of indicators],
    "reasoning": "brief explanation",
    "confidence": float (0-1)
}}""",
    }

    chat_model = ChatOllama(base_url=OLLAMA_HOST, model="llama3.2", format="json")
    messages = [prompt]

    response = await chat_model.ainvoke(messages, config={"callbacks": [handler]})

    try:
        result = json.loads(response.content)
        if "is_spam" in result and "confidence" in result:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Response JSON does not contain required fields",
            )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to parse the spam check result as JSON",
        )
