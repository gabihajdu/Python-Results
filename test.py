pip install flask
from flask import Flask, request, render_template_string, make_response
import logging
import sqlite3

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Database setup (Assuming SQLite for simplicity)
conn = sqlite3.connect('example.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS xss_storage (data TEXT)''')
conn.commit()

@app.route('/')
def index():
    # Tainted user input
    user_input = request.args.get('input', '')

    # Sink 1: Directly rendering user input in a template (XSS)
    rendered_template = render_template_string(f'<div>Hello, {user_input}!</div>')

    # Sink 2: Including user input in a response header (XSS)
    response = make_response(rendered_template)
    response.headers["X-Custom-Info"] = user_input

    # Sink 3: Direct reflection in HTTP response (XSS)
    response.data = f"User input was: {user_input}"

    # Sink 4: Logging the user input (potential log injection)
    logging.info(f"Received user input: {user_input}")

    # Sink 5: Storing user input in a database (persistent XSS)
    c.execute("INSERT INTO xss_storage (data) VALUES (?)", (user_input,))
    conn.commit()

    return response

if __name__ == '__main__':
    app.run(debug=True)