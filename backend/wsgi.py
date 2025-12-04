import os
from flask import redirect

try:
    # If the project provides a factory, use it so existing routes are preserved
    from app import create_app  # type: ignore
    app = create_app(os.getenv('FLASK_ENV') or 'default')
except Exception:
    # Fallback minimal app (useful if `app.create_app` is missing)
    from flask import Flask
    app = Flask(__name__)

# Ensure frontend URL is available in config
FRONTEND_URL = os.getenv('FRONTEND_URL') or app.config.get('FRONTEND_URL') or 'http://localhost:5173'
app.config['FRONTEND_URL'] = FRONTEND_URL


@app.route('/')
def index_redirect():
    """Redirect root requests to the frontend landing page."""
    return redirect(app.config['FRONTEND_URL'])


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', os.getenv('PORT', 5000)))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(host=host, port=port, debug=debug)
