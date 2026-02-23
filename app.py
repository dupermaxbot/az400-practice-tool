from flask import Flask, render_template, request, jsonify, session
import random
from database import init_db, load_questions_from_json, get_random_questions, submit_answer, get_session_summary, get_stats

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
    stats = get_stats(user_id=1)
    return jsonify(stats)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
