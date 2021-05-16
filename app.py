import os

from flask import Flask
from flask import render_template, url_for
from flask import redirect
from flask import session

from centagoj import eo_vortoj
from hillary.views import clickup_blueprint
from hillary.views import hillary_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

app.register_blueprint(clickup_blueprint, url_prefix="/login")
app.register_blueprint(hillary_blueprint, url_prefix='/hillary')


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/")
def index():
    print(app.url_map)
    return render_template('welcome.html')


@app.route('/hazarda-vorto')
def hazarda_vorto():
    word_def = eo_vortoj.get_word()
    return render_template('hazarda-vorto.html', word_def=word_def)
