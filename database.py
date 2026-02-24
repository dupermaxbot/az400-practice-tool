import sqlite3
import json
from datetime import datetime

DB_PATH = 'az400_practice.db'

def init_db():
    """Initialize the database with the finalized schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Domains table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')
    
    # Question types table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_types (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')
    
    # Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            scenario_text TEXT,
            text TEXT NOT NULL,
            explanation TEXT,
            question_type_id INTEGER,
            domain_id INTEGER,
            difficulty TEXT DEFAULT 'medium',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_type_id) REFERENCES question_types(id),
            FOREIGN KEY (domain_id) REFERENCES domains(id)
        )
    ''')
    
    # Answers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY,
            question_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            is_correct BOOLEAN DEFAULT FALSE,
            explanation TEXT,
            display_order INTEGER,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    ''')
    
    # Attempts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            quiz_session_id INTEGER,
            question_id INTEGER NOT NULL,
            selected_answer_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            time_spent_seconds INTEGER,
            correct BOOLEAN,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (quiz_session_id) REFERENCES quiz_sessions(id),
            FOREIGN KEY (question_id) REFERENCES questions(id),
            FOREIGN KEY (selected_answer_id) REFERENCES answers(id)
        )
    ''')
    
    # Quiz sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            total_score INTEGER,
            status TEXT DEFAULT 'in_progress',
            num_questions INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_domain ON questions(domain_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_active ON questions(is_active)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_answers_question ON answers(question_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_attempts_user_correct ON attempts(user_id, correct)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_attempts_session ON attempts(quiz_session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_attempts_question ON attempts(question_id)')
    
    # Insert default user if not exists
    cursor.execute('SELECT id FROM users WHERE username = ?', ('default_user',))
    if not cursor.fetchone():
        cursor.execute(
            'INSERT INTO users (username, email) VALUES (?, ?)',
            ('default_user', 'user@az400.local')
        )
    
    # Insert question types
    types = ['multiple_choice', 'code_snippet', 'scenario']
    for q_type in types:
        cursor.execute('INSERT OR IGNORE INTO question_types (name) VALUES (?)', (q_type,))
    
    # Insert domains
    domains = [
        'CI/CD Pipelines',
        'Build Automation',
        'Infrastructure as Code',
        'Release Management',
        'Artifact Management',
        'Testing',
        'Source Control',
        'Monitoring and Logging',
        'Security and Compliance',
        'Deployment Strategies'
    ]
    for domain in domains:
        cursor.execute('INSERT OR IGNORE INTO domains (name) VALUES (?)', (domain,))
    
    conn.commit()
    conn.close()

def load_questions_from_json(json_file):
    """Load questions from JSON file and insert into database."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for q in data['questions']:
        try:
            # Get domain_id
            cursor.execute('SELECT id FROM domains WHERE name = ?', (q['domain'],))
            domain = cursor.fetchone()
            domain_id = domain[0] if domain else None
            
            # Insert question
            cursor.execute('''
                INSERT INTO questions (scenario_text, text, explanation, question_type_id, domain_id, difficulty)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                q.get('scenario_text'),
                q['text'],
                None,  # Will be set from answer explanations
                1,  # multiple_choice
                domain_id,
                q['difficulty']
            ))
            
            question_id = cursor.lastrowid
            
            # Insert answers
            for i, answer in enumerate(q['answers']):
                cursor.execute('''
                    INSERT INTO answers (question_id, text, is_correct, explanation, display_order)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    question_id,
                    answer['text'],
                    answer['is_correct'],
                    answer['explanation'],
                    i
                ))
        except Exception as e:
            print(f"ERROR on question {idx+1}: {e}")
            raise
    
    conn.commit()
    conn.close()

def get_random_questions(count=25, user_id=1):
    """Get random active questions and create a quiz session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create quiz session
    cursor.execute('''
        INSERT INTO quiz_sessions (user_id, start_time, num_questions)
        VALUES (?, ?, ?)
    ''', (user_id, datetime.now(), count))
    
    session_id = cursor.lastrowid
    conn.commit()
    
    # Get random questions
    cursor.execute('''
        SELECT id FROM questions WHERE is_active = TRUE
        ORDER BY RANDOM() LIMIT ?
    ''', (count,))
    
    question_ids = [row[0] for row in cursor.fetchall()]
    questions = []
    
    for q_id in question_ids:
        cursor.execute('''
            SELECT id, scenario_text, text, explanation, difficulty
            FROM questions WHERE id = ?
        ''', (q_id,))
        q = cursor.fetchone()
        
        cursor.execute('''
            SELECT id, text FROM answers WHERE question_id = ?
            ORDER BY display_order
        ''', (q_id,))
        answers = cursor.fetchall()
        
        questions.append({
            'id': q[0],
            'scenario_text': q[1],
            'text': q[2],
            'explanation': q[3],
            'difficulty': q[4],
            'answers': [{'id': a[0], 'text': a[1]} for a in answers]
        })
    
    conn.close()
    return session_id, questions

def submit_answer(session_id, question_id, answer_id, user_id=1):
    """Submit an answer and check if it's correct."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get correct answer
    cursor.execute('''
        SELECT id FROM answers WHERE question_id = ? AND is_correct = TRUE
    ''', (question_id,))
    correct_answer = cursor.fetchone()
    correct_answer_id = correct_answer[0] if correct_answer else None
    
    is_correct = answer_id == correct_answer_id
    
    # Record attempt
    cursor.execute('''
        INSERT INTO attempts (user_id, quiz_session_id, question_id, selected_answer_id, correct)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, session_id, question_id, answer_id, is_correct))
    
    conn.commit()
    
    # Get answer details
    cursor.execute('''
        SELECT text, explanation FROM answers WHERE id = ?
    ''', (answer_id,))
    selected = cursor.fetchone()
    
    cursor.execute('''
        SELECT text, explanation FROM answers WHERE question_id = ? AND is_correct = TRUE
    ''', (question_id,))
    correct = cursor.fetchone()
    
    # Get general question explanation
    cursor.execute('''
        SELECT explanation FROM questions WHERE id = ?
    ''', (question_id,))
    q_explanation = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'is_correct': is_correct,
        'selected_answer': selected,
        'correct_answer': correct,
        'question_explanation': q_explanation
    }

def get_session_summary(session_id):
    """Get summary of a quiz session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT SUM(CASE WHEN correct = TRUE THEN 1 ELSE 0 END) as score,
               COUNT(*) as total
        FROM attempts
        WHERE quiz_session_id = ?
    ''', (session_id,))
    
    result = cursor.fetchone()
    score = result[0] or 0
    total = result[1] or 0
    
    # Get missed questions
    cursor.execute('''
        SELECT q.id, q.text, q.domain_id, a.text as selected_answer
        FROM attempts a
        JOIN questions q ON a.question_id = q.id
        WHERE a.quiz_session_id = ? AND a.correct = FALSE
    ''', (session_id,))
    
    missed = cursor.fetchall()
    conn.close()
    
    return {
        'score': score,
        'total': total,
        'percentage': (score / total * 100) if total > 0 else 0,
        'missed_count': len(missed),
        'missed_questions': missed
    }

def get_stats(user_id=1):
    """Get overall statistics for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total attempts
    cursor.execute('''
        SELECT SUM(CASE WHEN correct = TRUE THEN 1 ELSE 0 END) as total_correct,
               COUNT(*) as total_attempts
        FROM attempts
        WHERE user_id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    total_correct = result[0] or 0
    total_attempts = result[1] or 0
    
    # By domain
    cursor.execute('''
        SELECT d.name,
               SUM(CASE WHEN a.correct = TRUE THEN 1 ELSE 0 END) as correct,
               COUNT(*) as total
        FROM attempts a
        JOIN questions q ON a.question_id = q.id
        JOIN domains d ON q.domain_id = d.id
        WHERE a.user_id = ?
        GROUP BY d.id, d.name
    ''', (user_id,))
    
    by_domain = cursor.fetchall()
    conn.close()
    
    return {
        'total_correct': total_correct,
        'total_attempts': total_attempts,
        'accuracy': (total_correct / total_attempts * 100) if total_attempts > 0 else 0,
        'by_domain': [{'domain': row[0], 'correct': row[1], 'total': row[2]} for row in by_domain]
    }

def get_user_sessions(user_id):
    """Get all sessions for a user (both in-progress and completed)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, start_time, end_time, status, total_score, num_questions
        FROM quiz_sessions
        WHERE user_id = ?
        ORDER BY start_time DESC
    ''', (user_id,))
    
    sessions = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'start_time': row[1],
            'end_time': row[2],
            'status': row[3],
            'total_score': row[4],
            'num_questions': row[5]
        }
        for row in sessions
    ]

def get_session_progress(session_id, user_id):
    """Get progress for a session: which questions answered, which not."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get session info
    cursor.execute('''
        SELECT num_questions FROM quiz_sessions
        WHERE id = ? AND user_id = ?
    ''', (session_id, user_id))
    
    session = cursor.fetchone()
    if not session:
        conn.close()
        return None
    
    num_questions = session[0]
    
    # Get all questions in this session
    cursor.execute('''
        SELECT DISTINCT q.id FROM questions q
        JOIN attempts a ON q.id = a.question_id
        WHERE a.quiz_session_id = ?
        ORDER BY q.id
    ''', (session_id,))
    
    answered_question_ids = [row[0] for row in cursor.fetchall()]
    
    # Get all questions that were supposed to be in this session
    cursor.execute('''
        SELECT id FROM questions WHERE is_active = TRUE
        ORDER BY RANDOM() LIMIT ?
    ''', (num_questions,))
    
    all_question_ids = [row[0] for row in cursor.fetchall()]
    
    # Find unanswered questions
    unanswered = [q_id for q_id in all_question_ids if q_id not in answered_question_ids]
    
    conn.close()
    
    return {
        'session_id': session_id,
        'num_questions': num_questions,
        'answered_count': len(answered_question_ids),
        'unanswered_count': len(unanswered)
    }

def resume_session(session_id, user_id):
    """Get unanswered questions for a session to resume."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verify session exists and belongs to user
    cursor.execute('''
        SELECT status, num_questions FROM quiz_sessions
        WHERE id = ? AND user_id = ?
    ''', (session_id, user_id))
    
    session = cursor.fetchone()
    if not session:
        conn.close()
        return None
    
    status, num_questions = session
    
    # Get all questions that were in this session (from attempts)
    cursor.execute('''
        SELECT DISTINCT q.id FROM questions q
        JOIN attempts a ON q.id = a.question_id
        WHERE a.quiz_session_id = ?
    ''', (session_id,))
    
    session_questions = set(row[0] for row in cursor.fetchall())
    
    # Get questions already answered in this session
    cursor.execute('''
        SELECT DISTINCT question_id FROM attempts
        WHERE quiz_session_id = ?
    ''', (session_id,))
    
    answered_ids = set(row[0] for row in cursor.fetchall())
    
    # Unanswered questions are those in the session that haven't been answered
    unanswered_ids = session_questions - answered_ids
    
    questions = []
    for q_id in unanswered_ids:
        cursor.execute('''
            SELECT id, scenario_text, text, explanation, difficulty
            FROM questions WHERE id = ?
        ''', (q_id,))
        q = cursor.fetchone()
        
        if q:
            cursor.execute('''
                SELECT id, text FROM answers WHERE question_id = ?
                ORDER BY display_order
            ''', (q[0],))
            answers = cursor.fetchall()
            
            questions.append({
                'id': q[0],
                'scenario_text': q[1],
                'text': q[2],
                'explanation': q[3],
                'difficulty': q[4],
                'answers': [{'id': a[0], 'text': a[1]} for a in answers]
            })
    
    conn.close()
    
    return {
        'session_id': session_id,
        'status': status,
        'total_questions': num_questions,
        'answered_count': len(answered_ids),
        'remaining_questions': questions
    }

def complete_session(session_id, user_id):
    """Mark a session as completed and calculate final score."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calculate score
    cursor.execute('''
        SELECT SUM(CASE WHEN correct = TRUE THEN 1 ELSE 0 END)
        FROM attempts
        WHERE quiz_session_id = ? AND user_id = ?
    ''', (session_id, user_id))
    
    score = cursor.fetchone()[0] or 0
    
    # Update session
    cursor.execute('''
        UPDATE quiz_sessions
        SET status = 'completed', end_time = ?, total_score = ?
        WHERE id = ? AND user_id = ?
    ''', (datetime.now(), score, session_id, user_id))
    
    conn.commit()
    conn.close()
    
    return score

def abandon_session(session_id, user_id):
    """Mark a session as abandoned (user quit mid-quiz)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE quiz_sessions
        SET status = 'abandoned', end_time = ?
        WHERE id = ? AND user_id = ?
    ''', (datetime.now(), session_id, user_id))
    
    conn.commit()
    conn.close()
