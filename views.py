from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

mainBP = Blueprint('simple_page', __name__)

@mainBP.route('/')
def show():
    try:
        return render_template('index.html')
    except TemplateNotFound:
        abort(404)