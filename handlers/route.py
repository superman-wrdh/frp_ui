from tornado.web import url
from handlers.index import IndexHandler
from handlers.index import LoginHandler
from handlers.index import AdminHandler
from handlers.index import FrpConfigHandler

handlers = [

    url(r"/index", IndexHandler, name='index'),
    url(r"/login", LoginHandler, name='login'),
    url(r"/admin", AdminHandler, name='admin'),
    url(r"/update_config", FrpConfigHandler, name='admin'),
]
