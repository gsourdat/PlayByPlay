from flask import Blueprint, render_template

champions = Blueprint('champions', __name__)

@champions.route('/champions_list', methods=['GET'])
def champions_page():
    return render_template('champions.html')