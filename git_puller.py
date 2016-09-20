from flask import Flask
from flask import request, abort,jsonify, render_template, redirect
import subprocess
import yaml
import os, re
from gitter import git_pull
from rq import Queue
from redis import Redis

application = Flask(__name__)

from tinydb import TinyDB, Query
with open('config.yml','r') as f:
        config = yaml.load(f)

db = TinyDB(config['db_dir'])
Log = Query()

@application.route("/")
def index():
	return "this is route service"

@application.route("/log")
def log():
    logs = db.all()
    return render_template('log_list.html',logs=logs)

@application.route("/log/clear")
def clear_log():
    db.purge()
    return redirect('/log')

@application.route("/projects")
def list():
    with open('config.yml','r') as f:
        config = yaml.load(f)

    return render_template("project_list.html")

@application.route("/project/<string:project>/pull", methods=["GET","POST"])
def pull(project):
    with open('config.yml','r') as f:
        config = yaml.load(f)

    if project not in config:
        return abort(404)

    key = request.args.get('key','')
    if key != config[project]['key']:
        return abort(403)

    payload = request.json
    pattern = re.search('(?<=\/)[\w\-]+$', payload['ref'])
    branch = pattern.group(0)

    branch_cfg = config[project]['branches'][branch]

    # redis_conn = Redis()
    # q = Queue(connection=redis_conn)

    # job = q.enqueue_call(func=git_pull,args=(config[project]['docroot'],config[project]['branch']))

    git_pull(branch_cfg['docroot'],branch_cfg['name'], config)

    # repo = Repo(config[project]['docroot'])
    # origin = repo.remotes.origin
    # origin.fetch()
    # repo.git.reset('--hard','origin/master')


    
    return jsonify(message="OK")

@application.errorhandler(404)
def no_result(e):
    return jsonify(exception="Resource not found")

@application.errorhandler(403)
def forbidden(e):
    return jsonify(exception="Request forbidden")

@application.errorhandler(422)
def wrong_params(e):
    return jsonify(exception="Parameter not satisfied")

if __name__ == "__main__":
  application.run(host='0.0.0.0')
