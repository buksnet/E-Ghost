from datetime import datetime, date
from flask import render_template, Flask, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import Length, DataRequired
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'LATER'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'

db = SQLAlchemy(app)


class TaskModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=False)
    text = db.Column(db.String(1000), unique=False)
    compose_up = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.now)


class TaskForm(FlaskForm):
    name = StringField(
        'Название',
        validators=[DataRequired(message="Поле не 'Название' должно быть пустым"),
                    Length(max=255, message='Введите название задачи длиной до 255 символов')]
    )
    text = StringField(
        'Текст',
        validators=[DataRequired(message="Поле не 'Текст' должно быть пустым"),
                    Length(max=1000, message='Введите описание задачи длиной до 1000 символов')])

    compose_up = DateField(
        'Закончить до',
        format="%Y-%m-%d",
        validators=[DataRequired(message="Поле 'Закончить до' не должно быть пустым")]
    )
    submit = SubmitField('Добавить')


@app.route("/")
def index():
    task_list = TaskModel.query.all()
    return render_template("index.html", task_list=task_list)


@app.route("/task/<int:id>")
def task_info(id):
    task = TaskModel.query.get(id)
    return render_template("task_info.html", task=task, date=date.today())


@app.route("/task/<int:id>/del")
def task_delete(id):
    task = TaskModel.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect("/")
    except:
        return redirect("/")


@app.route("/add_task", methods=['GET', 'POST'])
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = TaskModel()
        task.name = form.name.data
        task.text = form.text.data
        task.compose_up = form.compose_up.data
        db.session.add(task)
        db.session.commit()
        return render_template(
            "task_info.html",
            task=task, date=date
        )

    return render_template('add_task.html', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
