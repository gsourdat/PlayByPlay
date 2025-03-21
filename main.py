from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('app.html')


@main.route('/champions_list', methods=['GET'])
def champions_page():
    return render_template('champions.html')


@main.route('/match/<int:match_id>')
def match_details(match_id):
    return render_template('match.html', match_id=match_id)


@main.route('/app')
def appMain():
    return render_template('app.html')


@main.route('/addMatch')
def addMatch():
    return render_template('add_match.html')
