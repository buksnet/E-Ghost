from datetime import datetime

from flask import render_template, Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LATER'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'

db = SQLAlchemy(app)


class TaskModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=False)
    text = db.Column(db.String(1000), unique=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


@app.route("/")
def index():
    task_list = TaskModel.query.all()
    return render_template(
        "base.html",
        task_list=task_list
    )


@app.route("/task/<int:id>")
def task():
    task = TaskModel.query.get(id)
    return render_template(
        "base.html",
        task=task
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
