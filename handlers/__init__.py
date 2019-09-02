import json
import traceback

import tornado.web

import functools
from tornado.web import HTTPError


def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            raise HTTPError(403)
        return method(self, *args, **kwargs)

    return wrapper


class MyAppException(tornado.web.HTTPError):
    pass


class RestHandler(tornado.web.RequestHandler):

    @property
    def request_body(self):
        try:
            json_body = json.loads(self.request.body)
            return json_body
        except Exception as e:
            return {}

    def render_json(self, data=None, code=0, message=''):
        result = {
            'data': data if data else {},
            'code': code,
            'message': message
        }
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(result, ensure_ascii=False))
        return

    def write_error(self, status_code, **kwargs):

        self.set_header('Content-Type', 'application/json')
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                    'traceback': lines,
                }
            }))
        else:
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                }
            }))


class NotFoundHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(404)
        self.write("This page <span style='color:red'>{}</span> is not Found".format(self.request.path))
