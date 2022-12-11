import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import flask_excel as excel
from ensembles import RandomForestMSE, GradientBoostingMSE
import plotly
import plotly.graph_objs as go
import plotly.express as px


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
models_directory = os.path.join(os.path.dirname(__file__), "instance/models")
excel.init_excel(app)


def build_plot(hist):
    fig = go.Figure()
    iters = np.arange(len(hist['train-loss']), dtype=int)
    fig.add_trace(go.Scatter(x=iters, y=hist['train-loss'],
                             mode="lines+markers", name="MSE на обучающей выборке"))
    if 'val-loss' in hist:
        fig.add_trace(go.Scatter(x=iters, y=hist['val-loss'],
                                 mode="lines+markers", name="MSE на валидационной выборке"))
    fig.update_layout(
                      showlegend=True,
                      legend=dict(x=.5, xanchor="center"),
                      title={
                          'text': "Процесс обучения модели",
                          'x': 0.5,
                          'xanchor': 'center',
                          'font': {'size': 22}
                      },
                      xaxis_title={
                          'text': "Номер итерации",
                          'font': {'size': 18}
                      },
                      yaxis_title={
                          'text': "MSE",
                          'font': {'size': 18}
                      },
                      margin=dict(l=0, r=0, t=30, b=0))
    fig.update_traces(hoverinfo="all", hovertemplate="Итерация: %{x}<br> MSE: %{y}")
    return fig.to_json()


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

    def predict(self, X):
        with open(os.path.join(models_directory, self.filename), "rb") as f:
            data = pickle.load(f)
            preds = data["model"].predict(X)
        return preds

    def get_information(self):
        result = {
            'name': self.name,
            'model_type': self.model_type,
            'descr': self.description,
            'is_fitted': self.is_fitted,
            'data_descr': self.data_descr
        }
        with open(os.path.join(models_directory, self.filename), "rb") as f:
            data = pickle.load(f)
            if self.is_fitted:
                result['plot'] = build_plot(data['hist'])
            result['params'] = data['model'].get_params(deep=False)
        return result


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
            if data["model_est"] <= 0:
                return ["Error", "Число моделей должно быть положительным числом!"]
        if not data["model_depth"]:
            data["model_depth"] = None
        else:
            data["model_depth"] = int(data["model_depth"])
            if data["model_depth"] <= 0:
                return ["Error", "Глубина деревьев должна быть положительным числом!"]
        if not data["model_features"]:
            data["model_features"] = None
        else:
            data["model_features"] = float(data["model_features"])
            if data["model_features"] > 1 or data["model_features"] <= 0:
                return ["Error", "Размерность признаков не может быть больше 1 или меньше или равной 0!"]
        if not data["model_lr"]:
            data["model_lr"] = 0.1
        else:
            data["model_lr"] = float(data["model_lr"])
            if data["model_lr"] <= 0:
                return ["Error", "Learning rate должен быть положительным числом!"]
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
    try:
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
            return ["Error", f"Колонка {target} с таргетом отсутствует в обучающей выборке"]
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
    except Exception:
        return ["Error", "Не удалось обучить модель. Проверьте корректность введенных данных"]


@app.route("/predict", methods=["POST"])
def predict():
    try:
        try:
            data = pd.read_csv(request.files.get('test'))
            X_test = np.array(data)
        except ValueError:
            return ["Error", "Добавьте данные для предсказания!"]
        if 'model' not in request.form:
            return ["Error", "Выберете модель, с помощью которой хотите получить предсказания!"]
        if 'column_name' not in request.form:
            return ["Error", "Укажите название колонки!"]
        model = Model.query.filter(Model.name == request.form['model']).first()
        if not model:
            return ["Error", "Такой модели не существует!"]
        if not model.is_fitted:
            return ["Error", "Модель еще не обучена!"]
        try:
            preds = model.predict(X_test)
        except Exception:
            return ["Error",
                    "Неправильный формат данных, убедитесь, что они соответствуют данным, на которых обучалась модель "]
        filename = request.form['model'] + "_predictions.csv"
        data = {request.form['column_name']: list(preds)}
        return excel.make_response_from_dict(data, file_type="csv", file_name=filename)
    except Exception:
        return ["Error", "Не удалось получить предсказания. Проверьте корректность введенных данных"]


@app.route("/get_info_about_model", methods=["GET"])
def get_info_about_model():
    try:
        name = request.args.get('model_name')
        model = Model.query.filter(Model.name == name).first()
        if not model:
            return ["Error", "Модели с таким именем не существует!"]
        data = model.get_information()
        return ["OK", data]
    except Exception:
        return ["Error", "Некорректный запрос на получение информации о модели!"]
