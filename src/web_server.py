import os
import base64

from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, render_template_string

from wtforms import SubmitField


app = Flask(__name__, template_folder='templates')
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
Bootstrap(app)


@app.route("/")
def start_page():
    return render_template("index.html")


@app.route("/get_all_models", methods=["GET"])
def get_all_models():
    return {"lol": [0, 1, 2, 3], "kek": [3, 4, 5]}
