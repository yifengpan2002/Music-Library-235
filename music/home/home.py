from flask import Blueprint, render_template

home_blueprint = Blueprint(
    'home_bp', __name__)

@home_blueprint.route('/')
def home():
    # Use Jinja to customize a predefined html page rendering the layout for showing a single track.
    return render_template('home/home.html')