import pytest
from app import create_app, db
from app.models import User, Book, Review
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from datetime import datetime, UTC

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session

@pytest.fixture
def test_user(app, session):
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('password123')
    )
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def test_book(app, session):
    book = Book(
        title='Test Book',
        author='Test Author',
        genre='Test Genre',
        year_published=2024,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    session.add(book)
    session.commit()
    return book

@pytest.fixture
def auth_headers(app, session, test_user):
    with app.app_context():
        # Refresh the user from the database
        user = session.get(User, test_user.id)
        access_token = create_access_token(identity=str(user.id))
        return {'Authorization': f'Bearer {access_token}'}

def test_register(client):
    response = client.post('/api/users/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['username'] == 'newuser'
    assert data['email'] == 'new@example.com'

def test_login(client, test_user):
    response = client.post('/api/users/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['user']['username'] == 'testuser'

def test_create_book(client, auth_headers):
    response = client.post('/api/books', json={
        'title': 'New Book',
        'author': 'New Author',
        'genre': 'New Genre',
        'year_published': 2024
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'New Book'
    assert data['author'] == 'New Author'

def test_get_books(client, test_book):
    response = client.get('/api/books')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['title'] == 'Test Book'

def test_create_review(client, session, test_book, auth_headers):
    response = client.post(f'/api/books/{test_book.id}/reviews', json={
        'rating': 5,
        'review_text': 'Great book!'
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data['rating'] == 5
    assert data['review_text'] == 'Great book!'

def test_get_book_reviews(client, session, test_book, test_user):
    book = session.get(Book, test_book.id)
    user = session.get(User, test_user.id)
    
    review = Review(
        book_id=book.id,
        user_id=user.id,
        rating=5,
        review_text='Great book!',
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    session.add(review)
    session.commit()
    
    response = client.get(f'/api/books/{book.id}/reviews')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['rating'] == 5 