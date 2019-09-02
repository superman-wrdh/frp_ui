import os
import signal
import time
import logging
import socket
import gc
from tornado.web import url
import tornado.options
import tornado.ioloop
import tornado.httpserver
from tornado.options import define
from tornado.options import options
import logging.handlers
from handlers import RestHandler
import tornado.httpclient
import tornado.netutil
import tornado.web

define("port", default=9800, help="run on the given port", type=int)
define("debug", default=True, help="debug mode", type=bool)
define("autoreload", default=True, help="autoreload on", type=bool)
define("process", default=1, help="process count", type=int)


class Global:
    pass


# options.log_to_stderr = True
class HelloReqHandler(RestHandler):
    def get(self):
        self.render("index.html")


MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 30


def sig_handler(sig, frame):
    logging.warning('Caught signal: %s', sig)
    tornado.ioloop.IOLoop.instance().add_callback_from_signal(shutdown)


def shutdown():
    logging.info('Stopping http server')
    # server.stop() # 不接收新的 HTTP 请求.f
    logging.info('Will shutdown in %s seconds ...', MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = tornado.ioloop.IOLoop.instance()
    now = time.time()
    io_loop.add_timeout(now + 15, server.stop)  # 不接收新的 HTTP 请求

    deadline = now + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN
    global Global
    Global.is_in_stop = True

    def stop_loop():

        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 2, stop_loop)
        else:
            io_loop.stop()  # 处理完现有的 callback 和 timeout 后，可以跳出 io_loop.start() 里的循环
            # save_all()  # 保存日志
            logging.info('Shutdown')

    stop_loop()


class Application(tornado.web.Application):
    def __init__(self):
        root_urls = [
            url(r"/", HelloReqHandler, name='index'),
        ]
        from handlers.route import handlers
        from handlers import NotFoundHandler
        handlers.extend(root_urls)
        command_setting = dict()
        command_setting['port'] = options.port
        command_setting['debug'] = options.debug
        command_setting['autoreload'] = options.autoreload
        settings = command_setting

        template_setting = {
            'template_path': os.path.join(os.path.dirname(__file__), "templates"),
            'static_path': os.path.join(os.path.dirname(__file__), 'templates', 'static'),
            'default_handler_class': NotFoundHandler
        }
        settings["debug"] = False
        settings.update(template_setting)
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    gc.set_threshold(5000)

    tornado.options.parse_command_line()

    app = Application()
    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    if options.process:
        server.bind(options.port, family=socket.AF_INET, reuse_port=True)
        server.start(options.process)
    else:
        sockets = tornado.netutil.bind_sockets(options.port, family=socket.AF_INET)
        server.add_sockets(sockets)

    logging.info('app server start listen 0.0.0.0:{} ...'.format(options.port))
    tornado.ioloop.IOLoop.instance().start()
