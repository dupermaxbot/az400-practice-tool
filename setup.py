#!/usr/bin/env python
"""
Setup script to initialize the database and load questions.
Run this once before starting the app.
"""

from database import init_db, load_questions_from_json
import os
import sys

def main():
    print("🗄️  Initializing AZ-400 Practice Tool database...")
    
    # Initialize database
    init_db()
    print("✓ Database schema created")
    
    # Load questions from JSON
    # Try multiple paths
    possible_paths = [
        '../az400_questions.json',  # Parent directory
        './az400_questions.json',   # Current directory
        '/home/duper/clawd/az400_questions.json'  # Absolute path
    ]
    
    json_file = None
    for path in possible_paths:
        if os.path.exists(path):
            json_file = path
            break
    
    if not json_file:
        print(f"\n⚠️  Warning: az400_questions.json not found")
        print("Searched in:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\nDatabase created, but no questions loaded.")
        print("Copy az400_questions.json to the tool directory and run setup.py again")
        return
    
    try:
        load_questions_from_json(json_file)
        print(f"✓ Loaded questions from {json_file}")
    except Exception as e:
        import traceback
        print(f"✗ Error loading questions: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    print("\n✓ Setup complete! Run 'python app.py' to start the server")
    print("  Access at: http://localhost:5000")

if __name__ == '__main__':
    main()
