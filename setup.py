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
    json_file = '../az400_questions.json'  # Path from clawd directory
    
    if not os.path.exists(json_file):
        print(f"\n⚠️  Warning: {json_file} not found")
        print("To load questions, copy az400_questions.json to the tool directory")
        print("Then run: python setup.py")
        return
    
    try:
        load_questions_from_json(json_file)
        print(f"✓ Loaded questions from {json_file}")
    except Exception as e:
        print(f"✗ Error loading questions: {e}")
        sys.exit(1)
    
    print("\n✓ Setup complete! Run 'python app.py' to start the server")
    print("  Access at: http://localhost:5000")

if __name__ == '__main__':
    main()
