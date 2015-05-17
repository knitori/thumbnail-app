
from contextlib import closing
import tempfile
import hashlib
import os

import requests
from PIL import Image
from flask import url_for, abort, render_template, redirect

from . import app, db, models

REDIRECT_CODE = 301  # moved permanently
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36',
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/thumbify/<int:width>x<int:height>/<path:url>')
def thumbify(width, height, url):
    if url.startswith('http:/') and not url.startswith('http://'):
        url = 'http://' + url[6:]
    elif url.startswith('https:/') and not url.startswith('https://'):
        url = 'https://' + url[7:]
    if width <= 0 or height <= 0:
        return abort(400, 'Invalid resolution')
    if width > 500 or height > 500:
        return abort(400, 'Resolution must not be bigger than 500x500')

    thumb_model = models.Thumbnail.query.filter_by(
        url=url, width=width, height=height).first()
    if thumb_model is not None:
        full_path = os.path.join('thumbnailer', 'static', thumb_model.path)
        if os.path.exists(full_path):
            return redirect(url_for('static', filename=thumb_model.path,
                                    _external=True)), REDIRECT_CODE
        else:
            # easiest way to continue, without causing integrity errors
            db.session.delete(thumb_model)

    with closing(requests.get(url, stream=True, headers=DEFAULT_HEADERS))\
            as response:
        if response.status_code != 200:
            return abort(400, 'Status Code was not 200')
        if not response.headers.get('content-type', '').startswith('image/'):
            return abort(400, 'Content-Type is not an image')
        fd = tempfile.NamedTemporaryFile('w+b')
        digest = hashlib.sha1()
        for chunk in response.iter_content(8 << 10):
            digest.update(chunk)
            fd.write(chunk)

    fd.seek(0)
    with closing(fd):
        file_hash = '{}x{}-{}.jpg'.format(width, height, digest.hexdigest())
        static_path = os.path.join('images', file_hash)
        thumbnail = os.path.join('thumbnailer', 'static', static_path)

        thumb_model = models.Thumbnail(
            url=url,
            path=static_path,
            width=width,
            height=height,
        )
        db.session.add(thumb_model)
        db.session.commit()

        fullurl = url_for('static', filename=static_path, _external=True)
        if os.path.exists(thumbnail):
            return redirect(fullurl), REDIRECT_CODE

        try:
            im = Image.open(fd)
        except:
            return abort(400, 'Provided URL might not be an image.')
        im.thumbnail((width, height))
        im.save(thumbnail, quality=90)

    return redirect(fullurl), REDIRECT_CODE
