import sqlite3

import click

from flask import current_app, g

import psycopg2
import psycopg2.extras
def get_db():
    if 'db' not in g:
        conn_string = "host=%s port=%s dbname=%s user=%s password=%s"%(
                current_app.config['PG_END_POINT'],
                current_app.config['PG_PORT'],
                current_app.config['PG_DB_NAME'],
                current_app.config['PG_USER_NAME'],
                current_app.config['PG_PASSWORD'])
        g.db = psycopg2.connect(conn_string)
        g.db.autocommit = True
    return g.db

def close_db(e=None):
    conn = g.pop('db', None)
    if conn:
        conn.close()


def init_db():
    conn = get_db()
    with current_app.open_resource('schema.sql') as f:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(f.read().decode('utf8'))
            

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)