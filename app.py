import json
from typing import List

from flask import Flask, render_template, abort

from json_serializable import JsonSerializable, from_json

app = Flask(__name__)


class Project(JsonSerializable):
    name: str
    description: str
    link: str


with open('projects.json') as handle:
    project_data: List[Project] = from_json(json.load(handle), List[Project])


@app.route('/projects/<project_name>')
def projects(project_name):
    matches = [project for project in project_data if project.name.lower() == project_name.lower()]
    if len(matches) == 0:
        abort(404)
    if len(matches) > 1:
        abort(500)
    return render_template('project.html', project=matches[0])


@app.route('/')
def hello_world():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
