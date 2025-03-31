import requests
from flask import current_app, jsonify, request
from app.models import Book, Review
from app import db
from app.api import bp
import redis
import json

def get_redis_client():
    """Get Redis client with current application context."""
    return redis.from_url(current_app.config['REDIS_URL'])

def generate_summary_with_ollama(text):
    """Generate a summary using Ollama's Llama2 model."""
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.1',
                'prompt': f"Please provide a concise summary of the following text:\n\n{text}\n\nSummary:",
                'stream': False
            }
        )
        response.raise_for_status()
        return response.json()['response']
    except Exception as e:
        current_app.logger.error(f"Error generating summary: {str(e)}")
        return "Summary generation failed."

@bp.route('/generate-summary', methods=['POST'])
def generate_summary():
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Missing content field'}), 400
    
    content = data['content']
    summary = generate_summary_with_ollama(content)
    
    if data.get('book_id'):
        # If book_id is provided, update the book's summary
        book = Book.query.get_or_404(data['book_id'])
        book.summary = summary
        db.session.commit()
    
    return jsonify({
        'summary': summary
    })

def generate_book_summary(book):
    """Generate a summary for a book using the Llama2 model."""
    prompt = f"Book Title: {book.title}\nAuthor: {book.author}\n"
    if book.genre:
        prompt += f"Genre: {book.genre}\n"
    if book.year_published:
        prompt += f"Published in: {book.year_published}\n"
    prompt += "\nPlease provide a concise summary of this book:"
    
    return generate_summary_with_ollama(prompt)

def get_book_recommendations(user_id, limit=5):
    """Get personalized book recommendations based on user preferences."""
    redis_client = get_redis_client()
    
    # Try to get recommendations from cache
    cache_key = f"recommendations:{user_id}"
    cached_recommendations = redis_client.get(cache_key)
    
    if cached_recommendations:
        return json.loads(cached_recommendations)
    
    # Get user's reviewed books and their ratings
    user_reviews = Review.query.filter_by(user_id=user_id).all()
    
    if not user_reviews:
        # If no reviews, return most popular books
        popular_books = Book.query.join(Review).group_by(Book.id).order_by(
            db.func.avg(Review.rating).desc()
        ).limit(limit).all()
        recommendations = [book.to_dict() for book in popular_books]
    else:
        # Get average ratings for each genre
        genre_ratings = {}
        for review in user_reviews:
            book = review.book
            if book.genre:
                if book.genre not in genre_ratings:
                    genre_ratings[book.genre] = []
                genre_ratings[book.genre].append(review.rating)
        
        # Calculate average rating for each genre
        genre_avg_ratings = {
            genre: sum(ratings) / len(ratings)
            for genre, ratings in genre_ratings.items()
        }
        
        # Get top genres
        top_genres = sorted(
            genre_avg_ratings.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Get books from top genres
        recommended_books = []
        for genre, _ in top_genres:
            books = Book.query.filter_by(genre=genre).limit(limit).all()
            recommended_books.extend(books)
        
        recommendations = [book.to_dict() for book in recommended_books[:limit]]
    
    # Cache recommendations for 1 hour
    redis_client.setex(
        cache_key,
        3600,
        json.dumps(recommendations)
    )
    
    return recommendations

def generate_review_summary(book_id):
    """Generate a summary of reviews for a book using the Llama2 model."""
    reviews = Review.query.filter_by(book_id=book_id).all()
    if not reviews:
        return "No reviews available."
    
    review_texts = [review.review_text for review in reviews if review.review_text]
    if not review_texts:
        return "No detailed reviews available."
    
    prompt = "Please summarize the following book reviews:\n\n"
    prompt += "\n".join([f"- {text}" for text in review_texts[:5]])  # Limit to first 5 reviews
    prompt += "\n\nSummary of reviews:"
    
    return generate_summary_with_ollama(prompt) 