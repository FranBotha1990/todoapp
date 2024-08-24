from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from ..routers.todos import get_db, get_current_user
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from ..models import Todos

# Set SQLite test DB URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

# Create engine to connect to the test DB
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args = {"check_same_thread": False},
    poolclass = StaticPool,
)

# Create a testing session, separate from production, tied to engine above
TestingSessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

# Create all the database tables that are defined in Base
Base.metadata.create_all(bind = engine)

# Dependency override for the get_db function, returning a test database session
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override get_current_user with hardcoded mock user object
def override_get_current_user():
    return {'username': 'codingwithrobytest', 'id': 1, 'user_role': 'admin'}

# Override dependency functions to ensure testing environment and session database is used
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# Create a testing client in FastAPI, allowing HTTPS requests to the endpoints
client = TestClient(app)


# Create pytest fixture for Todo, add and commit todo before returning it, then deleting it from the DB
@pytest.fixture
def test_todo():
    todo = Todos(
        title = "Learn to code!",
        description = "Need to learn everyday!",
        priority = 5,
        complete = False,
        owner_id = 1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


# Test reading mock todo while authenticated
def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 
                                'title': 'Learn to code!', 
                                'description': 'Need to learn everyday!', 
                                'id': 1, 
                                'priority': 5, 
                                'owner_id':1}]


# Test reading one todo while authenticated
def test_read_one_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False, 
                                'title': 'Learn to code!', 
                                'description': 'Need to learn everyday!', 
                                'id': 1, 
                                'priority': 5, 
                                'owner_id':1}


# Test non-existent todo while authenticated
def test_read_one_authenticated_not_found():
    response = client.get("/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


# Test creating a new todo
def test_create_todo(test_todo):
    request_data = {
        'title': 'New Todo!',
        'description': 'New Todo description.',
        'priority': 5,
        'complete': False,
    }

    response = client.post('/todo/', json = request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')

