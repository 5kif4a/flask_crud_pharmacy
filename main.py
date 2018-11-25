from flask import Flask, render_template, request, session, redirect, url_for, flash, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import pdfkit
import models as mdl
import config

app = Flask('Pharmacy', template_folder='templates', static_url_path='/static')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = config.URL
app.secret_key = config.KEY
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)  # get data from existing db


def check(model, login_name, password):  # authentication
    c = db.session.query(model).filter(model.login.in_([login_name]), model.password.in_([password])).first()
    db.session.commit()
    db.session.close()
    return c


def render_html(obj):  # для сохранения в pdf
    model = mdl.get_class_by_tablename(obj)
    columns = model.__table__.columns.keys()
    data = model.query.order_by(model.id).all()
    db.session.commit()
    db.session.close()
    return render_template('pdf_template.html', entity=obj, columns=columns, data=data)


@app.route('/')  # redirect to home page
def index():
    return redirect(url_for('home'))


@app.route('/home')  # home page
def home():
    if not session.get('logined'):
        return redirect(url_for('login'))
    else:
        return render_template('home.html', role=session['role'])


@app.route('/auth', methods=['GET', 'POST'])  # authorization
def login():
    if request.method == 'POST':
        login_name = request.form['login']
        password = request.form['password']
        admin = check(mdl.Admin, login_name, password)
        user = check(mdl.User, login_name, password)
        db.session.close()
        if admin:
            session['logined'] = True
            session['role'] = 'Administrator'
            return redirect(url_for('home'))
        elif user:
            session['logined'] = True
            session['role'] = 'User'
            return redirect(url_for('home'))
        else:
            flash('Admin or User with this login does not exist or wrong password')
            return render_template('auth.html')
    return render_template('auth.html')


@app.route('/logout')
def logout():
    session['logined'] = False
    return redirect(url_for('auth'))


@app.route('/tables', methods=['GET'])  # show all tables
def tables():
    if session.get('logined'):
        return render_template('tables.html', tables=sorted(mdl.tables), role=session['role'], table_selected=False)
    else:
        return redirect(url_for('login'))


@app.route('/tables/<tname>')  # select * from table
def table(tname):
    if session.get('logined'):
        try:
            model = mdl.get_class_by_tablename(tname)
            columns = model.__table__.columns.keys()
            data = model.query.order_by(model.id).all()
            db.session.commit()
            db.session.close()
            return render_template('tables.html', tname=tname, tables=sorted(mdl.tables), columns=columns, data=data,
                                   role=session['role'], table_selected=True)
        except Exception:
            abort(404)
    elif session['role'] == 'User' and (tname == 'Admins' or tname == 'Users'):
        flash('You don\'t have permission for this')
        return redirect(url_for('tables'))
    else:
        flash('You are not logged in')
        return redirect(url_for('login'))


@app.route('/tables/<table>/add', methods=['GET', 'POST'])  # insert
def add(table):
    if session.get('logined') and session.get('role') == 'Administrator':
        model = mdl.get_class_by_tablename(table)
        columns = model.__table__.columns.keys()
        try:
            if request.method == 'POST':
                row = [request.form[str(c)] for c in columns]
                obj = model(*row)
                db.session.add(obj)
                db.session.commit()
                db.session.close()
                flash('Row inserted', 'info')
        except Exception:
            flash('Error occured. Check the correctness of input data', 'error')
        return render_template('add.html', tname=table, columns=columns, role=session['role'])
    elif session.get('logined') and session.get('role') == 'User':
        flash('You don\'t have permission for this')
        return redirect(url_for('table'), tname=table, role=session['role'])
    else:
        flash('You are not logged in')
        return redirect(url_for('login'))


# redefine this func, very big and unreadable
@app.route('/tables/<table>/edit/<id>', methods=['GET', 'POST'])  # modify data in table row
def modify(table, id):
    if session.get('logined') and session.get('role') == 'Administrator':
        model = mdl.get_class_by_tablename(table)  # берем нужную модель по имени таблицы
        columns = model.__table__.columns.keys()  # столбцы
        sess = db.session  # сессия
        exists = db.session.query(db.session.query(model).filter_by(id=id).exists()
                                  ).scalar()  # проверка на существование поля с определенным id
        if exists:  # если поле существует
            obj = sess.query(model).filter_by(id=id).first()  # строка которую мы будем обновлять
            if request.method == 'POST':
                try:
                    rows = dict((c, request.form[c]) for c in columns)  # берем все значения полей с формы
                    upd = dict()  # словарь для обновления
                    for k in obj.__dict__.keys():
                        if k != '_sa_instance_state' and k != 'id':  # instance и id не берем, потому не нужны
                            upd[k] = rows[k]  # в словарь для обновления записываем значения с полей
                    sess.query(model).filter_by(id=id).update(upd)  # обновляем по строку id поля
                    sess.commit()
                    flash('Row updated', 'info')
                    return render_template('edit.html', tname=table, columns=columns, id=obj.id, row=obj,
                                           role=session['role'])
                except Exception as e:
                    flash('Error occured. Check the correctness of input data', 'error')
        else:  # поле не существует
            return abort(404)
        return render_template('edit.html', tname=table, columns=columns, id=obj.id, row=obj,
                               role=session['role'])
    elif session.get('logined') and session.get('role') == 'User':   # если зашел как юзер
        flash('You don\'t permission for this')  # юзеру нельзя редактировать информацию
        return redirect(url_for('table'), tname=table)
    else:
        flash('You are not logged')  # если не залогирован
        return redirect(url_for('login'))


@app.route('/tables/<table>/delete/<id>', methods=['GET'])  # delete row, тут опасян с параметром id
def delete(table, id):                                      # надо как то брать параметр id не из url
    if session.get('logined') and session.get('role') == 'Administrator':  # если зашел как админ
        model = mdl.get_class_by_tablename(table)
        if request.method == 'GET':
            try:
                db.session.query(model).filter_by(id=id).delete()  # удаляем по id
                db.session.commit()
                db.session.close()
                return redirect(url_for('table', tname=table))  # переходим на страницу с таблицой
            except Exception:
                abort(404)
    elif session.get('logined') and session.get('role') == 'User':  # если зашел как юзер
        flash('You don\'t have permission for this')  # юзеру нельзя удалять
        return redirect(url_for('table', tname=table))  # переходим на страницу с таблицой
    else:
        flash('You are not logged in')  # если не залогирован
        return redirect(url_for('login'))


@app.route('/views', methods=['GET'])  # показать все представления
def views():
    if session.get('logined'):
        return render_template('views.html', views=mdl.views, role=session['role'], view_selected=False)
    else:
        return redirect(url_for('login'))


@app.route('/views/<view>')  # представления
def get_view(view):
    if session.get('logined'):
        try:
            model = mdl.get_class_by_tablename(view)
            columns = model.__table__.columns.keys()
            data = model.query.order_by(model.id).all()
            return render_template('views.html', view=view, views=mdl.views, columns=columns,
                                   data=data, role=session['role'], view_selected=True)
        except Exception as e:
            print(e)
            abort(404)
    else:
        flash('You are not logged in')
        return redirect(url_for('login'))


@app.route('/<entity>/save/<obj>')  # сохранить в pdf формате
def save_as_pdf(entity, obj):
    if session.get('logined'):
        try:
            renderer = render_html(obj)
            cfg = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
            pdf = pdfkit.from_string(renderer, False, configuration=cfg)
            response = make_response(pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename={}.pdf'.format(obj)
            return response
        except Exception as e:
            print(e)
            abort(404)
    else:
        flash('You are not logged in')
        return redirect(url_for('login'))


@app.route('/queries')  # запросы на выборку
def query():
    pass


@app.route('/procedures')  # хранимые процедуры
def procedure():
    if session.get('logined'):
        try:
            db.session.query(func.myproc3(11)).all()
            # or db.session.execute('SELECT "myproc3"(11)')
            db.session.commit()
            return render_template('procedures.html', role=session['role'])
        except Exception as e:
            print(e)
            abort(404)
    else:
        flash('You are not logged in')
        return redirect(url_for('login'))


@app.errorhandler(404)  # 404 page
def page404(e):
    print(e)
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)