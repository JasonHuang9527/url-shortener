import os
import functools
import hashlib
from flask_cors import CORS
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Flask, jsonify
)
from flaskr.db import get_db
import psycopg2
import psycopg2.extras

SHORT_URL_LENGTH = 8

# factory function
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )
    
    if test_config is None: 
        app.config.from_pyfile('/home/ec2-user/url-shortener/api/flaskr/config.py', silent=True)
        
    else:
        app.config.from_mapping(test_config)

    from . import db
    db.init_app(app)
    addRoutes(app)
    CORS(app) 
    return app

def getUniqueUrl(cursor, original_url):
    short_url_generator = hashlib.sha256()
    IS_UNIQUE_URL = False
    while IS_UNIQUE_URL == False:
        short_url_generator.update(original_url.encode('UTF-8'))
        short_url = short_url_generator.hexdigest()[:SHORT_URL_LENGTH]
        cursor.execute('''
                        SELECT *
                        FROM urls
                        WHERE short_url = %s
                        ''', (short_url,))
        result = cursor.fetchone()
        if result == None:
            IS_UNIQUE_URL = True
    return short_url

def addRoutes(app):
    @app.route('/api/shorten', methods=['POST'])
    def shorten_url():
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            original_url = request.json.get('url')
            # check if the url does already exist in the db
            cursor.execute('''
                            SELECT short_url
                            FROM urls
                            WHERE original_url = %s
                            ''', (original_url,))
            url_data =  cursor.fetchone()
            if url_data:
                short_url = url_data['short_url']
                print("existing mapping:", original_url, "->", short_url)
            else:
                # create the short one and insert into the db
                short_url = getUniqueUrl(cursor, original_url)
                print("new mapping:", original_url, "->", short_url)

                cursor.execute('''
                                INSERT INTO urls (original_url, short_url) 
                                VALUES (%s, %s)
                                ''', (original_url, short_url))



        return jsonify({'shortUrl': request.host_url + short_url})

    @app.route('/<short_url>', methods=['GET'])
    def redirect_to_long_url(short_url):
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute('''
                            SELECT original_url 
                            FROM urls
                            WHERE short_url = %s
                            ''', (short_url,))
            url_data = cursor.fetchone()
        if url_data:
            return redirect(url_data['original_url'])
        return jsonify({'error': 'Invalid short URL'})

