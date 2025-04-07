from flask import Blueprint, render_template

match = Blueprint('match', __name__)

@match.route('/match/<int:match_id>')
def match_details(match_id):
    return render_template('match.html', match_id=match_id)


@match.route('/addMatch')
def add_match():
    return render_template('add_match.html')