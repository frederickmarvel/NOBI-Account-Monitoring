import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Import the Flask app from backend
from backend import app as flask_app

# Export for Vercel WSGI
app = flask_app
