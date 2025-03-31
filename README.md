# Book Management System

A Flask-based book management system with AI-powered features including book summaries and recommendations.

## Features

- RESTful API for book management
- PostgreSQL database integration
- Llama3 model integration for book summaries
- User authentication and authorization
- Book recommendations
- Review management
- Cloud deployment ready

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for caching)
- Docker (optional)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd book-management-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=postgresql://username:password@localhost:5432/bookdb
SECRET_KEY=your-secret-key
REDIS_URL=redis://localhost:6379/0
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Running the Application

1. Start the Flask development server:
```bash
flask run
```

2. Access the API documentation at: http://localhost:5000/api/docs

## API Endpoints & CURL Examples

### User Management
#### Register User
```bash
curl -X POST http://localhost:5000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### Login User
```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### Book Management
#### Create Book
```bash
curl -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "genre": "Classic Literature",
    "year_published": 1925,
    "summary": "A story of decadence and excess, following the mysterious millionaire Jay Gatsby"
  }'
```

#### Get All Books
```bash
curl -X GET http://localhost:5000/api/books
```

#### Get Specific Book
```bash
curl -X GET http://localhost:5000/api/books/1
```

### Reviews
#### Add Review
```bash
curl -X POST http://localhost:5000/api/books/1/reviews \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "rating": 5,
    "review_text": "An absolute masterpiece! The character development and storytelling are exceptional."
  }'
```

#### Get Book Reviews
```bash
curl -X GET http://localhost:5000/api/books/1/reviews
```

### AI Features
#### Get Book Summary
```bash
curl -X GET http://localhost:5000/api/books/1/summary
```

#### Generate New Summary
```bash
curl -X POST http://localhost:5000/api/generate-summary \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "book_id": 1,
    "content": "The Great Gatsby is a novel by F. Scott Fitzgerald set in the Roaring Twenties. The story primarily concerns the young and mysterious millionaire Jay Gatsby and his passion for the beautiful Daisy Buchanan. The narrative is told through the eyes of Nick Carraway, who moves next door to Gatsby and becomes drawn into his world of obsession, love, and tragedy."
  }'
```

#### Get Book Recommendations
```bash
curl -X GET http://localhost:5000/api/recommendations \
  -H "Authorization: Bearer <your_token>"
```

## Testing

Run the test suite:
```bash
pytest
```

## Docker Deployment

Build the Docker image:
```bash
docker build -t book-management-system .
```

Run the container:
```bash
docker run -p 5000:5000 book-management-system
```
