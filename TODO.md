# AZ-400 Practice Tool - TODO

## ✅ Completed (In fix/security-and-validation branch)

- [x] Move hardcoded secret key to `.env` file
- [x] Fix bare `except` block with proper exception handling
- [x] Add input validation for API endpoints
- [x] Generate unique user IDs per session (UUID)
- [x] Add CSRF protection with Flask-WTF
- [x] Add logging for debugging
- [x] Secure session cookies (HTTPONLY, Secure, SameSite)
- [x] SSL/TLS support with self-signed certificate

---

## 🔄 In Progress / Backlog

### Database & ORM

- [ ] **Replace raw SQL with SQLAlchemy ORM**
  - Current: ~400 lines of raw SQL in `database.py`
  - Target: ~100 lines with SQLAlchemy
  - Benefit: Auto SQL injection prevention, cleaner code, easier Postgres migration
  - Priority: HIGH (reduces bugs, improves maintainability)

- [ ] **Switch from SQLite to PostgreSQL**
  - SQLite locks the entire DB on writes (concurrency bottleneck)
  - Target: PostgreSQL for production
  - Defer: After MVP is working well locally
  - Priority: MEDIUM (only needed if multiple users)

### Features & UX

- [ ] **User Authentication (Optional for MVP)**
  - Currently: UUID-based anonymous sessions
  - Consider: Simple email/password or OAuth
  - Defer: Until user tracking is needed
  - Priority: LOW (works fine for single-user testing)

- [ ] **Question Filtering by Domain & Difficulty**
  - UI: Add checkboxes on home page
  - API: `GET /api/questions?domain=CI/CD&difficulty=hard`
  - Priority: MEDIUM (nice to have, schema already supports it)

- [ ] **Time-Limited Quizzes**
  - Add `time_limit` parameter to `/api/quiz/start`
  - UI: Show countdown timer
  - DB: Store `time_spent_seconds` per attempt (already tracked)
  - Priority: MEDIUM (schema ready, just needs UI)

- [ ] **Retry/Review Mode**
  - Allow users to retake questions they missed
  - UI: "Review Missed" button shows failed questions only
  - API: `POST /api/quiz/retry?session_id=X`
  - Priority: LOW (nice feature for studying)

### Code Quality

- [ ] **API Request Validation Library (Pydantic)**
  - Replace manual `BadRequest` checks with Pydantic models
  - Benefits: Cleaner code, better error messages, auto-docs
  - Example:
    ```python
    class StartQuizRequest(BaseModel):
        count: int = Field(ge=1, le=50, default=25)
    ```
  - Priority: LOW (current manual validation works)

- [ ] **Add Unit & Integration Tests**
  - Current: No tests
  - Target: pytest with fixtures for DB
  - Coverage: Routes, DB functions, edge cases
  - Priority: MEDIUM (needed before production)

- [ ] **API Documentation (Swagger/OpenAPI)**
  - Add `flask-restx` or `flasgger` for auto-generated docs
  - Endpoint: `GET /api/docs`
  - Priority: LOW (internal tool, not critical)

### Deployment & Operations

- [ ] **Docker Support**
  - Create `Dockerfile` for containerization
  - Create `docker-compose.yml` for easy local dev
  - Priority: MEDIUM (helpful for sharing, deploying)

- [ ] **Production Server (Gunicorn/Nginx)**
  - Replace Flask dev server with Gunicorn for multi-process
  - Add Nginx reverse proxy for SSL/static files
  - Priority: HIGH (when moving out of dev)
  - Steps:
    ```bash
    pip install gunicorn
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
    ```

- [ ] **Error Logging & Monitoring**
  - Log to file or centralized service (e.g., Sentry)
  - Track: Errors, slow requests, user sessions
  - Priority: MEDIUM (useful for debugging)

- [ ] **Performance Monitoring**
  - Add timing stats to index page
  - Track: Average quiz time, slowest questions
  - DB query optimization (add missing indexes)
  - Priority: LOW (optimize when it matters)

### Question Bank

- [ ] **Add More Questions**
  - Current: 50 questions
  - Target: 100+ for better variety
  - Source: Microsoft Learn, practice exams
  - Priority: MEDIUM (improves study value)

- [ ] **Import Questions from CSV/JSON**
  - Create a CLI tool: `python manage.py import_questions questions.csv`
  - Priority: LOW (can do manually for now)

- [ ] **Question Analytics**
  - Track: Most commonly missed questions
  - Report: Questions with low accuracy across all users
  - UI: Show stats on admin dashboard
  - Priority: LOW (useful for tuning questions later)

---

## Release Checklist

Before "Production Ready":

- [ ] All critical issues fixed (security branch merged)
- [ ] SQLAlchemy ORM implemented
- [ ] PostgreSQL support added
- [ ] Unit tests passing (>80% coverage)
- [ ] API docs available
- [ ] Docker image builds successfully
- [ ] Load testing (handle 10+ concurrent users)
- [ ] Security audit completed
- [ ] SSL certificate signed by CA (not self-signed)

---

## Notes

- **MVP is NOW**: Single-user, SQLite, basic CRUD, SSL
- **Next Phase**: Multi-user, PostgreSQL, filtering, time limits
- **Far Future**: Mobile app, AI-assisted learning, leaderboards

---

Last updated: 2026-02-23
