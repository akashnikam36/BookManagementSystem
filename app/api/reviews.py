from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.api import bp
from app.models import Book, Review

@bp.route('/books/<int:book_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    user_id = get_jwt_identity()
    
    if not data or 'rating' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not 1 <= data['rating'] <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    review = Review(
        book_id=book_id,
        user_id=user_id,
        review_text=data.get('review_text'),
        rating=data['rating']
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify(review.to_dict()), 201

@bp.route('/reviews/<int:id>', methods=['PUT'])
@jwt_required()
def update_review(id):
    review = db.session.get(Review, id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    user_id = get_jwt_identity()
    
    if review.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'rating' in data:
        if not 1 <= data['rating'] <= 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        review.rating = data['rating']
    
    if 'review_text' in data:
        review.review_text = data['review_text']
    
    db.session.commit()
    return jsonify(review.to_dict())

@bp.route('/reviews/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_review(id):
    review = db.session.get(Review, id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    user_id = get_jwt_identity()
    
    if review.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(review)
    db.session.commit()
    return '', 204 