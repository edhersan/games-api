import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Vercel Python expects the ASGI app as `handler` or `app`
handler = app