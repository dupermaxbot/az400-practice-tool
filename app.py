from flask import Flask, render_template, request, jsonify, session
import random
from database import (
    init_db, load_questions_from_json, get_random_questions, submit_answer, 
    get_session_summary, get_stats, get_user_sessions, resume_session, 
    complete_session, abandon_session
)

app = Flask(__name__)
app.secret_key = 'az400-practice-secret-key'

# Initialize database on startup
try:
    init_db()
except:
    pass  # DB already initialized

@app.route('/')
def index():
    """Home page - show stats and start quiz button."""
    stats = get_stats(user_id=1)
    return render_template('index.html', stats=stats)

@app.route('/api/quiz/start', methods=['POST'])
def start_quiz():
    """Start a new quiz session."""
    count = request.json.get('count', 25)
    session_id, questions = get_random_questions(count=count, user_id=1)
    
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

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz_answer():
    """Submit answer to a question."""
    data = request.json
    session_id = data.get('session_id')
    question_id = data.get('question_id')
    answer_id = data.get('answer_id')
    
    result = submit_answer(session_id, question_id, answer_id, user_id=1)
    
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

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all quiz sessions for the user."""
    user_id = session.get('user_id')
    sessions = get_user_sessions(user_id=user_id)
    return jsonify({'sessions': sessions})

@app.route('/api/sessions/<int:session_id>/resume', methods=['GET'])
def resume_quiz(session_id):
    """Get unanswered questions to resume a quiz."""
    user_id = session.get('user_id')
    result = resume_session(session_id, user_id=user_id)
    
    if not result:
        return jsonify({'error': 'Session not found'}), 404
    
    # Shuffle answers
    for q in result['remaining_questions']:
        random.shuffle(q['answers'])
    
    session['current_session_id'] = session_id
    
    return jsonify(result)

@app.route('/api/sessions/<int:session_id>/complete', methods=['POST'])
@csrf.exempt
def complete_quiz(session_id):
    """Mark a quiz session as completed."""
    user_id = session.get('user_id')
    score = complete_session(session_id, user_id=user_id)
    
    return jsonify({
        'session_id': session_id,
        'final_score': score,
        'status': 'completed'
    })

@app.route('/api/sessions/<int:session_id>/abandon', methods=['POST'])
@csrf.exempt
def abandon_quiz(session_id):
    """Mark a quiz session as abandoned."""
    user_id = session.get('user_id')
    abandon_session(session_id, user_id=user_id)
    
    return jsonify({
        'session_id': session_id,
        'status': 'abandoned'
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
