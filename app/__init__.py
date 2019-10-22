from os import environ
from secrets import token_hex

from flask import Flask, make_response, request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, InternalServerError

from .sheets import post_report


# Initialize application
app = Flask(__name__)
app.config.from_mapping(
    DEBUG=True,
    SECRET_KEY=environ.get("FLASK_SECRET_KEY", token_hex(64)),
)
CORS(app)


def _validate_request():
    """
    Verify the 'Host', 'Origin' and 'Referer' of the request.
    """
    origin = request.headers.get("Origin")
    referer = request.headers.get("Referer")
    if origin != 'https://viendochileencontexto.github.io':
        return False
    elif referer != 'https://viendochileencontexto.github.io/mapa-denuncias-abuso-policial/new_report.html':
        return False
    else:
        return True


@app.route('/report', methods=['POST'])
def report():
    """
    Handle POSTS in /report.
    """
    if not (app.debug or _validate_request()):
        return make_response("Bad Credentials", 401)
    if not request.is_json:
        return make_response("Bad Request", 400)

    try:
        return post_report(app, request)
    except (BadRequest, TypeError):
        return make_response("Bad Request", 400)
    except InternalServerError as e:
        return make_response(e.description, 500)


if __name__ == '__main__':
    app.run(debug=True)
