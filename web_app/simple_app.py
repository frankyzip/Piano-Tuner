"""
Simplified Piano Tuner - Test Version
"""

from flask import Flask, render_template
import webbrowser
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def open_browser():
    """Open browser after server starts"""
    import time
    time.sleep(1.5)
    webbrowser.open('http://localhost:5555')

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Simple Test Server...")
    print("URL: http://localhost:5555")
    print("=" * 60)
    
    # Open browser in background
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server
    app.run(host='127.0.0.1', port=5555, debug=False)
