import sqlite3
from flask import current_app, g
import os

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()




def init_db():
    db = get_db()
    print("Initializing database...")
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# Flask CLI command
import click
from flask import Flask

def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

@click.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
