
from subprocess import Popen

from thumbnailer import app, db, models
from flask.ext.script import Manager

manager = Manager(app)


@manager.command
def run():
    app.run(host='0.0.0.0')


@manager.command
def init():
    # db.drop_all()
    db.create_all()


if __name__ == '__main__':
    manager.run()
