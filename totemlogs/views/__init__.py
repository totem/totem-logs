from flask import render_template
from totemlogs.server import app

__author__ = 'sukrit'


@app.route('/')
def index():
    return render_template('index.html')
