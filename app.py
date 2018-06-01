import hashlib
import os
from functools import wraps
from typing import List

from flask import Flask, render_template, abort, url_for, request, redirect, session, jsonify
from tinydb import TinyDB, Query
from tinydb.database import Table, Document

from json_serializable import JsonSerializable, from_json

app = Flask(__name__)

db: Table = TinyDB('projects.json').table()


class Project(JsonSerializable):
    name: str
    description: str
    link: str
    summary: str
    id: str

    def __init__(self, *, name: str = '', description: str = '', link: str = '', summary: str = '', id: str = ''):
        self.name = name
        self.id = id
        self.summary = summary
        self.liink = link
        self.description = description


def check_password(password) -> bool:
    return hashlib.sha256(bytes(os.environ['pepper'] + password, 'utf-8')).hexdigest() == os.environ['password_hash']


@app.context_processor
def inject():
    return {
        'projects': from_json(db.all(), List[Project]),
        'empty_project': Project(),
        'admin': session.get('logged_in', False)
    }


@app.route('/admin/login/', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/admin/login', methods=['POST'])
def check_login():
    if not check_password(request.form.get('pass')):
        return redirect(url_for('login'))
    session['logged_in'] = True
    return redirect('/')


@app.route('/admin/logout')
def logout():
    session['logged_in'] = False
    return redirect('/')


def require_admin(status: int = 401):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not session.get('logged_in'):
                abort(status)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def find_project(name) -> Document:
    Q = Query()
    matches = db.search(Q.id == name.lower())
    if len(matches) == 0:
        abort(404)
    return matches[0]


@app.route('/projects/new/')
@require_admin()
def new_project_form():
    return render_template('new.html')


@app.route('/projects/new/', methods=['POST'])
@require_admin()
def new_project():
    id = request.form.get('id')
    Q = Query()
    matches = db.search(Q.id == id.lower())
    if len(matches) != 0:
        abort(400)
    name = request.form.get('name')
    summary = request.form.get('summary')
    description = request.form.get('description')
    link = request.form.get('link')
    db.insert({
        'name': name,
        'id': id,
        'summary': summary,
        'description': description,
        'link': link,
    })
    return redirect(url_for('projects', project_name=id))


@app.route('/projects/<project_name>/edit/', methods=['GET'])
@require_admin()
def edit_project(project_name):
    return render_template('edit_project.html', project=find_project(project_name))


@app.route('/projects/<project_name>/edit/', methods=['POST'])
@require_admin()
def edit_project_data(project_name):
    project: Document = find_project(project_name)
    summary = request.form.get('summary')
    description = request.form.get('description')
    link = request.form.get('link')
    name = request.form.get('name')
    project['name'] = name
    project['link'] = link
    project['description'] = description
    project['summary'] = summary
    db.write_back([project])
    return jsonify({})


@app.route('/projects/<project_name>/')
def projects(project_name):
    return render_template('project.html', project=find_project(project_name))


@app.route('/projects/<project_name>/delete/', methods=['GET'])
@require_admin()
def delete_project(project_name):
    return render_template('delete.html', project=find_project(project_name))


@app.route('/projects/<project_name>/delete/', methods=['POST'])
@require_admin()
def delete_project_confirm(project_name):
    Q = Query()
    db.remove(Q.id == project_name.lower())
    return redirect('/')


@app.route('/')
def index():
    return render_template('index.html')


app.secret_key = os.environ.get('app_secret', '')

if __name__ == '__main__':
    app.run(port=80)
