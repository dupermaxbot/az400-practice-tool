# AZ-400 Practice Tool

A Flask-based web application for practicing AZ-400 (Azure DevOps Engineer Expert) exam questions.

## Features

- 🎯 **Question Bank**: 50+ AZ-400 exam questions with detailed explanations
- 📊 **Progress Tracking**: See your accuracy by domain and overall stats
- 🔀 **Shuffled Answers**: Questions show randomized answer choices
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 💾 **Persistent Storage**: SQLite database tracks all attempts and sessions
- ⚡ **Fast Feedback**: Instant grading with detailed explanations

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database & Load Questions

```bash
python setup.py
```

This creates the SQLite database and loads the question bank.

### 3. Configure Environment (Optional)

Copy the example `.env` file and customize it:

```bash
cp .env.example .env
# Edit .env with your settings (SECRET_KEY, HOST, PORT, etc.)
```

### 4. Run the Application

**Option A: Flask Development Server** (not recommended for production)

```bash
python app.py
```

**Option B: Gunicorn (Recommended)** ⭐

```bash
# Using config file (recommended)
gunicorn -c gunicorn_config.py app:app

# Or with inline options
gunicorn -w 4 -b 0.0.0.0:5000 --certfile=cert.pem --keyfile=key.pem app:app
```

Gunicorn provides:
- ✅ Multiple worker processes (handle more concurrent users)
- ✅ Better error handling (doesn't crash on exceptions)
- ✅ Built-in SSL/TLS support
- ✅ Access logging
- ✅ Graceful restarts

The app will be available at `https://localhost:5000` (note: HTTPS)

## Database Schema

### Tables

- **users**: User accounts (single-user MVP)
- **domains**: AZ-400 exam domains
- **question_types**: Question type classification
- **questions**: Exam questions with scenario/explanation
- **answers**: Multiple choice options
- **attempts**: User answers and correctness
- **quiz_sessions**: Quiz session tracking

### Features (Deferred)

The schema supports:
- User accounts and authentication
- Multiple question types (code snippets, scenarios)
- Time limits on quizzes
- Difficulty-based filtering
- Domain-based filtering
- Export/analytics of historical data

No schema changes needed to add these features!

## API Endpoints

### Quiz Management

- `POST /api/quiz/start` - Start a new quiz session
  - Body: `{ "count": 25 }`
  - Returns: `{ "session_id", "questions", "total" }`

- `POST /api/quiz/submit` - Submit an answer
  - Body: `{ "session_id", "question_id", "answer_id" }`
  - Returns: `{ "correct", "selected_answer", "correct_answer", "question_explanation" }`

- `GET /api/quiz/summary/<session_id>` - Get quiz results
  - Returns: `{ "score", "total", "percentage", "missed_count", "missed_questions" }`

### Statistics

- `GET /api/stats` - Get user statistics
  - Returns: `{ "total_correct", "total_attempts", "accuracy", "by_domain" }`

- `GET /health` - Health check
  - Returns: `{ "status": "ok" }`

## File Structure

```
az400-practice-tool/
├── app.py                 # Main Flask application
├── database.py           # SQLite schema and utilities
├── requirements.txt      # Python dependencies
├── setup.py             # Database initialization
├── README.md            # This file
├── .gitignore
├── templates/
│   ├── base.html        # Base template with CSS
│   └── index.html       # Quiz interface
└── static/
    └── (CSS/JS assets)
```

## Running on a Web Server

The Flask development server is suitable for local testing. For production or accessing from other machines:

### Option 1: Simple HTTP Server (No Additional Setup)

The app is a standard Flask app and runs on `http://0.0.0.0:5000` by default.

Access from other machines: `http://<your-machine-ip>:5000`

### Option 2: Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

```bash
docker build -t az400-tool .
docker run -p 5000:5000 az400-tool
```

### Option 3: Gunicorn (Production)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option 4: Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }
}
```

## Future Enhancements

- [ ] User authentication and profiles
- [ ] Time limits on quizzes
- [ ] Question filtering by domain/difficulty
- [ ] Code snippet and scenario questions
- [ ] Email notifications for weak areas
- [ ] Integration with Discord for reminders
- [ ] Admin panel for managing questions

## Contributing

To add more questions:

1. Edit `az400_questions.json`
2. Run `python setup.py` to reload
3. Start quizzing!

## License

MIT
