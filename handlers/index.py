import os
import functools
from uuid import uuid4
from utils.local_cache import cache
from handlers import RestHandler
from handlers import authenticated
from utils.parse_config import ConfigOperator
from base import BASE_PATH
from base import SYSTEM_CONFIG_FILE


def cookie_authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        token = self.get_cookie("admin_authentication")
        if token:
            user = cache.get(token)
            if user is None:
                self.redirect(url="/login")
                return
        return method(self, *args, **kwargs)

    return wrapper


class IndexHandler(RestHandler):

    def get(self):
        self.render(template_name="index.html")

    def post(self, *args, **kwargs):
        params = self.request_body
        username = params.get("username")
        password = params.get("password")
        if username == "hc" and password == "123":
            data = {
                "username": username,
                "password": password
            }
            self.set_secure_cookie(name="user_info", value="", expires_days=1)
            return self.render("admin.html", user=username, message="管理员")
        return self.render("login.html")


class AdminHandler(RestHandler):

    def get_all_client_config(self):
        SYS_CONF = os.path.join(BASE_PATH, SYSTEM_CONFIG_FILE)
        sys_conf = ConfigOperator(SYS_CONF)
        frp_ini_path = sys_conf.get(section="frpc", key="config_file_path")
        try:
            client_config = ConfigOperator(frp_ini_path)
            data = client_config.get_all()
            # arr = [{"name": k, "data": data[k]} for k in data]
            arr = [(k, [(key, v[key]) for key in v],) for k, v in data.items()]
            return arr
        except Exception as e:
            return []

    def get(self):
        token = self.get_cookie("admin_authentication")
        if token:
            user = cache.get(token)
            if user:
                return self.render(template_name="admin.html", user=user, message="管理员",
                                   arr=self.get_all_client_config())
        return self.redirect(url="/login")


class LoginHandler(RestHandler):

    def validation(self, u, p):
        config_path = os.path.join(BASE_PATH, SYSTEM_CONFIG_FILE)
        config = ConfigOperator(config_path)
        username = config.get(section="admin", key="username")
        password = config.get(section="admin", key="password")
        if username == u and password == p:
            return True
        return False

    def get(self):
        return self.render("login.html", message=None)

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        if self.validation(username, password):
            token = str(uuid4()).replace("-", '')
            self.set_cookie(name="admin_authentication", value=token)
            cache.set(token, "admin", 500)
            return self.redirect(url="admin")
        return self.render("login.html", message="用户名密码错误")


class FrpConfigHandler(RestHandler):

    def config_data(self):
        try:
            SYS_CONF = os.path.join(BASE_PATH, SYSTEM_CONFIG_FILE)
            sys_conf = ConfigOperator(SYS_CONF)
            frp_ini_path = sys_conf.get(section="frpc", key="config_file_path")
            client_config = ConfigOperator(frp_ini_path)
            return client_config
        except Exception as e:
            pass

    def post(self):
        section = self.get_argument("section")
        all_args = self.request.body_arguments
        data = {k: all_args[k][0].decode("utf8") if isinstance(all_args[k], list) and len(all_args[k]) > 0 else None for
                k in all_args if k != "section"}
        data = {k: v for k, v in data.items() if v is not None}
        config = self.config_data()
        for k, v in data.items():
            config.update(section, k, v)
        config.overwrite()
        return self.redirect(url="admin")
