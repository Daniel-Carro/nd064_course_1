import sqlite3

#DCR
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
import logging
from datetime import datetime
from flask import jsonify
import sys

db_connection_count = 0

# Configurar logging
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

# Desactivar que el logger propague al root (evita duplicados/confusión de niveles)
logger.propagate = False



# Handler para STDOUT (INFO y DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.addFilter(lambda record: record.levelno < logging.ERROR)  # Solo INFO y WARNING van aquí

# Handler para STDERR (ERROR y CRÍTICOS)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)

# Formato común
formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s, %(message)s')
stdout_handler.setFormatter(formatter)
stderr_handler.setFormatter(formatter)

# Agregar handlers al logger
logger.addHandler(stdout_handler)
logger.addHandler(stderr_handler)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    global db_connection_count
    db_connection_count += 1
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

    
@app.route("/healthz")
def healthcheck():
    return jsonify(result="OK - healthy"), 200

@app.route("/metrics")
def metrics():
    # Contar posts
    conn = get_db_connection()
    post_count = conn.execute("SELECT COUNT(*) FROM POSTS").fetchone()[0]
    conn.close()
    return jsonify(db_connection_count=db_connection_count, post_count=post_count), 200

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logger.error(f'Non-existing article accessed: ID {post_id}')
        return render_template('404.html'), 404
    else:
        logger.info(f'Article "{post["Title"]}" retrieved!')
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info('About page retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logger.info(f'New article created: "{title}"')

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
