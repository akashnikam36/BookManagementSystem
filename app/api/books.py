from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.api import bp
from app.models import Book, Review
from app.api.ai import generate_book_summary, get_book_recommendations

@bp.route('/books', methods=['POST'])
@jwt_required()
def create_book():
    data = request.get_json()
    
    if not data or 'title' not in data or 'author' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    book = Book(
        title=data['title'],
        author=data['author'],
        genre=data.get('genre'),
        year_published=data.get('year_published'),
        summary=data.get('summary')
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify(book.to_dict()), 201

@bp.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books])

@bp.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book.to_dict())

@bp.route('/books/<int:id>', methods=['PUT'])
@jwt_required()
def update_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    data = request.get_json()
    
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'genre' in data:
        book.genre = data['genre']
    if 'year_published' in data:
        book.year_published = data['year_published']
    if 'summary' in data:
        book.summary = data['summary']
    
    db.session.commit()
    return jsonify(book.to_dict())

@bp.route('/books/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    db.session.delete(book)
    db.session.commit()
    return '', 204

@bp.route('/books/<int:id>/reviews', methods=['GET'])
def get_book_reviews(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    reviews = Review.query.filter_by(book_id=id).all()
    return jsonify([review.to_dict() for review in reviews])

@bp.route('/books/<int:id>/summary', methods=['GET'])
def get_book_summary(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
        
    if not book.summary:
        book.summary = generate_book_summary(book)
        db.session.commit()
        
    return jsonify({
        'summary': book.summary,
        'average_rating': calculate_average_rating(book)
    })

def calculate_average_rating(book):
    reviews = Review.query.filter_by(book_id=book.id).all()
    if not reviews:
        return 0
    return sum(review.rating for review in reviews) / len(reviews)

@bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    try:
        recommendations = get_book_recommendations(user_id)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate recommendations',
            'message': str(e)
        }), 500 