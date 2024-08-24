from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from fastapi.testclient import TestClient
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