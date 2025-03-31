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

## API Endpoints

- POST /api/books - Add a new book
- GET /api/books - Get all books
- GET /api/books/<id> - Get a specific book
- PUT /api/books/<id> - Update a book
- DELETE /api/books/<id> - Delete a book
- POST /api/books/<id>/reviews - Add a review
- GET /api/books/<id>/reviews - Get book reviews
- GET /api/books/<id>/summary - Get book summary
- GET /api/recommendations - Get book recommendations
- POST /api/generate-summary - Generate book summary

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

## Cloud Deployment

The application is configured for deployment on AWS. Follow these steps:

1. Set up an AWS account
2. Configure AWS CLI
3. Deploy using the provided CloudFormation template
4. Set up CI/CD pipeline using GitHub Actions

## Security

- JWT-based authentication
- Password hashing using bcrypt
- CORS enabled
- Rate limiting
- Input validation 