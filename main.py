from datetime import datetime, date
from flask import render_template, Flask, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, PasswordField
from wtforms.validators import Length, DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'LATER'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


class TaskModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=False)
    text = db.Column(db.String(1000), unique=False)
    date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.now)


class UserModel(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30), unique=False)
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

    date = DateField(
        'Закончить до',
        format="%Y-%m-%d",
        validators=[DataRequired(message="Поле 'Закончить до' не должно быть пустым")]
    )
    submit = SubmitField('Добавить')


class RegisterForm(FlaskForm):
    login = StringField(
        'Логин',
        validators=[DataRequired(message="Поле не 'Логин' должно быть пустым"),
                    Length(max=30, message='Введите логин длиной до 30 символов')]
    )

    password = PasswordField(
        'Пароль',
        validators=[DataRequired(message="Поле не 'Пароль' должно быть пустым"),
                    Length(max=30, min=6, message='Введите Пароль от 6 до 30 символов')])

    submit = SubmitField('Продолжить')


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(user_id)


@app.route("/")
@login_required
def index():
    task_list = TaskModel.query.all()
    return render_template("index.html", tasks=task_list)


@app.route("/task/<int:id>")
@login_required
def task_info(id):
    task = TaskModel.query.get(id)
    return render_template("task_info.html", task=task, date=date)


@app.route("/task/<int:id>/del")
@login_required
def task_delete(id):
    task = TaskModel.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect("/")
    except:
        return redirect("/")


@app.route("/add_task", methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = TaskModel()
        task.name = form.name.data
        task.text = form.text.data
        task.date = form.date.data
        db.session.add(task)
        db.session.commit()
        return render_template(
            "task_info.html",
            task=task, date=date
        )

    return render_template('add_task.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = RegisterForm()
    if form.validate_on_submit():
        user = UserModel.query.filter_by(login=form.login.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                return redirect("/")
        flash("Логин/пароль неправильные")

    return render_template("autorization.html", form=form)


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = UserModel()
            user.login = form.login.data
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            return redirect("/")
        except:
            flash(message="Такой логин уже есть")

    return render_template('registration.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
