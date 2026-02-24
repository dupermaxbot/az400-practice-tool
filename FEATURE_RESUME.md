# Feature: Resume & History

## Overview

Add ability to save quiz progress, resume incomplete quizzes, and view quiz history.

## Database Changes

### quiz_sessions Table Updates

Added columns:
- `status` (TEXT) - One of: `in_progress`, `completed`, `abandoned`
- `num_questions` (INTEGER) - Number of questions in the quiz

## API Endpoints

### 1. List User Sessions
```
GET /api/sessions
```

**Response:**
```json
{
  "sessions": [
    {
      "id": 1,
      "start_time": "2026-02-24T12:00:00",
      "end_time": "2026-02-24T12:30:00",
      "status": "completed",
      "total_score": 18,
      "num_questions": 25
    },
    {
      "id": 2,
      "start_time": "2026-02-24T13:00:00",
      "end_time": null,
      "status": "in_progress",
      "total_score": null,
      "num_questions": 25
    }
  ]
}
```

### 2. Resume a Quiz
```
GET /api/sessions/<session_id>/resume
```

**Response:**
```json
{
  "session_id": 2,
  "status": "in_progress",
  "total_questions": 25,
  "answered_count": 5,
  "remaining_questions": [
    {
      "id": 3,
      "scenario_text": "...",
      "text": "...",
      "explanation": "...",
      "difficulty": "medium",
      "answers": [...]
    }
  ]
}
```

### 3. Complete a Quiz
```
POST /api/sessions/<session_id>/complete
```

**Response:**
```json
{
  "session_id": 2,
  "final_score": 18,
  "status": "completed"
}
```

### 4. Abandon a Quiz
```
POST /api/sessions/<session_id>/abandon
```

**Response:**
```json
{
  "session_id": 2,
  "status": "abandoned"
}
```

## New Database Functions

### get_user_sessions(user_id)
- Returns list of all sessions for a user (completed, in_progress, abandoned)
- Sorted by start_time descending (newest first)

### resume_session(session_id, user_id)
- Gets unanswered questions from a session
- Returns session status + remaining questions
- Reconstructs questions from attempts table

### complete_session(session_id, user_id)
- Calculates final score
- Updates session status to 'completed'
- Sets end_time

### abandon_session(session_id, user_id)
- Updates session status to 'abandoned'
- Sets end_time

## UI Changes (Future)

- Home page: Show "Resume in progress quiz" button if one exists
- Session History: Display all sessions with status badges:
  - 🟢 Completed (with score)
  - 🟡 In Progress (with progress indicator)
  - 🔴 Abandoned
- Quiz flow: Add "Save & Exit" button to pause mid-quiz

## Implementation Status

✅ Database schema updated  
✅ New API endpoints  
✅ Backend functions  
⏳ UI integration (next step)

## Notes

- Sessions track `status` to distinguish between active, completed, and quit mid-quiz
- Resumed quizzes reconstruct questions from the attempts table
- Score is calculated at completion time, not during quiz
- Users can review any completed session (score + domain breakdown)
