import os
import functools
import hashlib
from flask_cors import CORS
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Flask, jsonify
)
from flaskr.db import get_db

SHORT_URL_LENGTH = 8

# factory function
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    
    if test_config is None: 
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)
    addRoutes(app)

    CORS(app)  # Add this line to enable CORS for all routes
    return app

def getUniqueUrl(conn, original_url):
    short_url_generator = hashlib.sha256()
    IS_UNIQUE_URL = False
    while IS_UNIQUE_URL == False:
        short_url_generator.update(original_url.encode('UTF-8'))
        short_url = short_url_generator.hexdigest()[:SHORT_URL_LENGTH]
        result = conn.execute('''
                        SELECT *
                        FROM urls
                        WHERE short_url = ?
                        ''', (short_url,)
                        ).fetchone()
        if result == None:
            IS_UNIQUE_URL = True
    return short_url

def addRoutes(app):
    @app.route('/api/shorten', methods=['POST'])
    def shorten_url():
        conn = get_db()
        original_url = request.json.get('url')
        # check if the url does already exist in the db
        url_data = conn.execute('''
                                SELECT short_url
                                FROM urls
                                WHERE original_url = ?
                                ''', (original_url,)
                                ).fetchone()
        if url_data:
            short_url = url_data['short_url']
            print("existing mapping:", original_url, "->", short_url)
        else:
            # create the short one and insert into the db
            short_url = getUniqueUrl(conn, original_url)
            print("new mapping:", original_url, "->", short_url)

            conn.execute('''
                        INSERT INTO urls (original_url, short_url) 
                        VALUES (?, ?)
                        ''', (original_url, short_url))
            conn.commit()
            conn.close()


        return jsonify({'shortUrl': request.host_url + short_url})

    @app.route('/<short_url>', methods=['GET'])
    def redirect_to_long_url(short_url):
        conn = get_db()
        url_data = conn.execute('''
                                SELECT original_url 
                                FROM urls
                                WHERE short_url = ?
                                ''', (short_url,)
                                ).fetchone()
        if url_data:
            return redirect(url_data['original_url'])
        return jsonify({'error': 'Invalid short URL'})

