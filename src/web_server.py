import os
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pickle
import pandas as pd
import numpy as np
from ensembles import RandomForestMSE, GradientBoostingMSE

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)
models_directory = os.path.join(os.path.dirname(__file__), "instance/models")


class Model(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    filename = db.Column(db.String(85), primary_key=True)
    model_type = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(300))
    data_descr = db.Column(db.String(300))
    is_fitted = db.Column(db.Boolean(), default=False)

    def __init__(self, name, model_type='bt', description=''):
        self.name = name
        self.filename = name + '.pickle'
        self.model_type = model_type
        self.description = description
        self.data_descr = ''
        self.is_fitted = False

    def __repr__(self):
        return str((self.name, self.model_type))

    def fit(self, X_train, y_train, X_val, y_val, descr):
        self.data_descr = descr
        self.is_fitted = True
        data = None
        with open(os.path.join(models_directory, self.filename), "rb") as f:
            data = pickle.load(f)
        hist = data['model'].fit(X_train, y_train, X_val, y_val)
        with open(os.path.join(models_directory, self.filename), "wb") as f:
            pickle.dump({"model": data['model'], "hist": hist}, f)



@app.route("/")
def start_page():
    return render_template("index.html")


@app.route("/get_all_models", methods=["GET"])
def get_all_models():
    req = Model.query.all()
    result = []
    for md in req:
        result.append(tuple([md.name, md.model_type, md.description]))
    return result


@app.route("/add_model", methods=["POST"])
def add_model():
    try:
        data = eval(request.data)
        if not data["model_est"]:
            data["model_est"] = 100
        else:
            data["model_est"] = int(data["model_est"])
        if not data["model_depth"]:
            data["model_depth"] = None
        else:
            data["model_depth"] = int(data["model_depth"])
        if not data["model_features"]:
            data["model_features"] = None
        else:
            data["model_features"] = float(data["model_features"])
        if not data["model_lr"]:
            data["model_lr"] = 0.1
        else:
            data["model_lr"] = float(data["model_lr"])
        model = Model.query.filter(Model.name == data["model_name"]).first()
        if model:
            return ["Error", "Модель с таким именем уже существует!"]
        model = Model(data["model_name"], data["model_type"], data["model_descr"])
        md = None
        if data["model_type"] == 'bt':
            md = GradientBoostingMSE(data["model_est"], data["model_lr"],
                                     data["model_depth"], data["model_features"])
        elif data["model_type"] == 'rf':
            md = RandomForestMSE(data["model_est"], data["model_depth"], data["model_features"])
        if md:
            with open(os.path.join(models_directory, data["model_name"] + ".pickle"), "wb") as f:
                pickle.dump({"model": md, "hist": None}, f)
        else:
            return ["Error", "Проверьте корректность введенных данных!"]
        db.session.add(model)
        db.session.commit()
        return ["OK"]
    except Exception:
        return ["Error", "Проверьте корректность введенных данных!"]


@app.route("/delete_model", methods=["GET"])
def delete_model():
    try:
        name = request.args.get('model_name')
        model = Model.query.filter(Model.name == name).first()
        if not model:
            return ["Error", "Модели с таким именем не существует!"]
        os.remove(os.path.join(models_directory, model.filename))
        db.session.delete(model)
        db.session.commit()
        return ["OK"]
    except Exception:
        return ["Error", "Некорректный запрос на удаление!"]


@app.route("/fit_model", methods=["POST"])
def fit_model():
    if 'target' not in request.form:
        return ["Error", "Укажите целевую колонку!"]
    target = request.form['target']
    try:
        data = pd.read_csv(request.files.get('train'))
        y_train = np.array(data[target])
        X_train = np.array(data.drop(labels=[target], axis=1))
    except ValueError:
        return ["Error", "Добавьте обучающую выборку!"]
    except KeyError:
        return ["Error", f"Колонка {target} отсутствует в обучающей выборке"]
    X_val = None
    y_val = None
    if 'val' in request.files:
        try:
            val = pd.read_csv(request.files.get('val'))
            y_val = np.array(val[target])
            X_val = np.array(val.drop(labels=[target], axis=1))
        except ValueError:
            return ["Error", "Проверьте корректность валидационной выборки"]
        except KeyError:
            return ["Error", f"Колонка {target} отсутствует в вадидационной выборке"]
    if 'model' not in request.form:
        return ["Error", "Выберете модель, которую хотите обучить!"]
    model = Model.query.filter(Model.name == request.form['model']).first()
    if not model:
        return ["Error", "Такой модели не существует!"]
    model.fit(X_train, y_train, X_val, y_val, request.form['data_description'])
    db.session.add(model)
    db.session.commit()
    return ["OK"]
