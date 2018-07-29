from flask import Blueprint
from flask import render_template

news_blueprint=Blueprint('new',__name__)
@news_blueprint.route('/')
def index():
    return render_template('news/index.html')