from flask import Flask, render_template, request, jsonify, session
from werkzeug.exceptions import BadRequest
from flask_wtf.csrf import CSRFProtect
import random
import uuid
import os
import logging
from dotenv import load_dotenv
from database import init_db, load_questions_from_json, get_random_questions, submit_answer, get_session_summary, get_stats

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-change-this-in-production')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Enable CSRF protection
csrf = CSRFProtect(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database on startup
try:
    init_db()
    logger.info("Database initialized successfully")
except FileNotFoundError as e:
    logger.error(f"Database initialization failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error during database initialization: {e}")
    raise

@app.before_request
def ensure_user():
    """Ensure user has a unique session ID."""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        logger.info(f"Created new session: {session['user_id']}")

@app.route('/')
def index():
    """Home page - show stats and start quiz button."""
    user_id = session.get('user_id')
    stats = get_stats(user_id=user_id)
    return render_template('index.html', stats=stats)

@app.route('/api/quiz/start', methods=['POST'])
@csrf.exempt  # API endpoint, not form-based
def start_quiz():
    """Start a new quiz session."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('Request must be JSON')
        
        count = data.get('count', 25)
        
        # Validate count
        if not isinstance(count, int):
            raise BadRequest('count must be an integer')
        if count < 1 or count > 50:
            raise BadRequest('count must be between 1 and 50')
        
        user_id = session.get('user_id')
        session_id, questions = get_random_questions(count=count, user_id=user_id)
    
    # Shuffle answers for each question
    for q in questions:
        random.shuffle(q['answers'])
    
        session['current_session_id'] = session_id
        session['current_question_index'] = 0
        
        return jsonify({
            'session_id': session_id,
            'questions': questions,
            'total': len(questions)
        })
    except BadRequest as e:
        logger.warning(f"Bad request: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error starting quiz: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/quiz/submit', methods=['POST'])
@csrf.exempt  # API endpoint, not form-based
def submit_quiz_answer():
    """Submit answer to a question."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('Request must be JSON')
        
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')
        
        # Validate inputs
        if not session_id or not isinstance(session_id, int):
            raise BadRequest('session_id is required and must be an integer')
        if not question_id or not isinstance(question_id, int):
            raise BadRequest('question_id is required and must be an integer')
        if not answer_id or not isinstance(answer_id, int):
            raise BadRequest('answer_id is required and must be an integer')
        
        user_id = session.get('user_id')
        result = submit_answer(session_id, question_id, answer_id, user_id=user_id)
    
        return jsonify({
            'correct': result['is_correct'],
            'selected_answer': {
                'text': result['selected_answer'][0] if result['selected_answer'] else None,
                'explanation': result['selected_answer'][1] if result['selected_answer'] else None
            },
            'correct_answer': {
                'text': result['correct_answer'][0] if result['correct_answer'] else None,
                'explanation': result['correct_answer'][1] if result['correct_answer'] else None
            },
            'question_explanation': result['question_explanation']
        })
    except BadRequest as e:
        logger.warning(f"Bad request: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/quiz/summary/<int:session_id>', methods=['GET'])
def get_quiz_summary(session_id):
    """Get summary of completed quiz."""
    summary = get_session_summary(session_id)
    return jsonify(summary)

@app.route('/api/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics."""
    user_id = session.get('user_id')
    stats = get_stats(user_id=user_id)
    return jsonify(stats)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(
        debug=debug,
        host=host,
        port=port,
        ssl_context=('cert.pem', 'key.pem')  # Self-signed SSL certificate
    )
