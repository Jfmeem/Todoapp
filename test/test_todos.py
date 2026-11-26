from test.test_main import client
from main import app
from fastapi import status
from router.auth import get_current_user
from models import Todo, User 
from database import SessionLocal


def override_get_current_user():
    return {
        "user_id": 1, 
        "username": "testuser"
    }


app.dependency_overrides[get_current_user] = override_get_current_user


def test_todo():
    db = SessionLocal()
    # remove old test data if it exists
    db.query(Todo).filter(Todo.id == 99).delete()
    db.commit()

    user = db.query(User).filter(User.id == 1).first()
    if not user:
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            firstname="Test",
            lastname="User",
            hash_password="x",
            is_active=True,
        )
        db.add(user)
        db.commit()

    todo = Todo(
        id=99,
        title="Testing",
        description="Testing",
        priority=5,
        completed=True,
        owner_id=1,         
    )
    db.add(todo)
    db.commit()
    db.close()


def test_read_todos():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK


def test_read_specific_todos():
    response = client.get("/todos/99")
    assert response.status_code == status.HTTP_200_OK
    
    
def test_create_todos():
    db = SessionLocal()
    db.query(Todo).filter(Todo.id == 0).delete()
    db.commit()      
    db.close()
    request_data = {
        "id": 0,
        "title": "string",
        "description": "string",
        "priority": 1,
        "completed": True

    }
    response = client.post("/create/", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "To do created successfully"}