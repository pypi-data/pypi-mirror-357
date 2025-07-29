import json
import os
import threading

import bottle
import webview
from webview import is_app, is_local_url, abspath
from webview.http import BottleServer, logger, _get_random_port, SSLWSGIRefServer, ThreadedAdapter
from idepy.core import settings

from jinja2 import Environment, FileSystemLoader


# 兼容方式导入importlib_metadata
try:
    from importlib import metadata as importlib_metadata
except ImportError:
    import importlib_metadata

# 导入版本解析工具
from packaging.version import parse as parse_version

# 获取目标包的版本（这里以'requests'为例）
try:
    pkg_version = importlib_metadata.version('pywebview')
except importlib_metadata.PackageNotFoundError:
    raise RuntimeError("Package 'requests' is required but not installed.")




jinja2_env = Environment(
    loader=FileSystemLoader(os.path.join(settings.PROJECT_PATH, './static/src')),
    variable_start_string='{{{',  # 更改变量开始符号
    variable_end_string='}}}',  # 更改变量结束符号
    block_start_string='{%',  # 更改控制结构开始符号
    block_end_string='%}',  # 更改控制结构结束符号
)
templates = jinja2_env.list_templates()
templates = list(filter(lambda x: str(x).endswith(".html"), templates))


class BottleCustom(BottleServer):

    @classmethod
    def start_server(
            cls, urls: list[str], http_port: int | None, keyfile: None = None, certfile: None = None
    ) -> tuple[str, str | None, BottleServer]:
        # 根据版本动态导入
        if parse_version(pkg_version) >= parse_version('5.4.0'):
            from webview import _state as start_config
        else:
            from webview import _settings as start_config


        from idepy.core.main import get_app



        apps = [u for u in urls if is_app(u)]
        server = cls()

        if len(apps) > 0:
            app = apps[0]
            common_path = '.'
        else:
            local_urls = [u for u in urls if is_local_url(u)]
            common_path = (
                os.path.dirname(os.path.commonpath(local_urls)) if len(local_urls) > 0 else None
            )
            server.root_path = abspath(common_path) if common_path is not None else None

            app = bottle.Bottle()


            @app.post(f'/js_api/{server.uid}')
            def js_api():
                bottle.response.headers['Access-Control-Allow-Origin'] = '*'
                bottle.response.headers[
                    'Access-Control-Allow-Methods'
                ] = 'PUT, GET, POST, DELETE, OPTIONS'
                bottle.response.headers[
                    'Access-Control-Allow-Headers'
                ] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

                body = json.loads(bottle.request.body.read().decode('utf-8'))
                if body['uid'] in server.js_callback:
                    return json.dumps(server.js_callback[body['uid']](body))
                else:
                    logger.error('JS callback function is not set for window %s' % body['uid'])

            # # 增加库读取
            # @app.route('/lib/<file:path>')
            # def idepy(file):
            #
            #     if not server.root_path:
            #         return ''
            #     bottle.response.headers['Access-Control-Allow-Origin'] = '*'
            #     bottle.response.headers[
            #         'Access-Control-Allow-Methods'
            #     ] = 'PUT, GET, POST, DELETE, OPTIONS'
            #     bottle.response.headers[
            #         'Access-Control-Allow-Headers'
            #     ] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
            #
            #     bottle.response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            #     bottle.response.set_header('Pragma', 'no-cache')
            #     bottle.response.set_header('Expires', 0)
            #
            #     return bottle.static_file(file, root=settings.PROJECT_STATIC_LIB_PATH)
            #
            #     # 增加窗口读取
            #
            # @app.route('/window_sys/<file:path>')
            # def window_sys(file):
            #     if not server.root_path:
            #         return ''
            #     bottle.response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            #     bottle.response.set_header('Pragma', 'no-cache')
            #     bottle.response.set_header('Expires', 0)
            #
            #
            #     return bottle.static_file(file, root=os.path.join(settings.PROJECT_STATIC_LIB_PATH, '../window_sys'))

            @app.route('/')
            @app.route('/<file:path>')
            def asset(file):
                bottle.response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                bottle.response.set_header('Pragma', 'no-cache')
                bottle.response.set_header('Expires', 0)

                # 获取单个查询参数
                jinjia_id = bottle.request.query.get('jinjia_id')
                idepy_app = get_app()

                # 使用渲染
                if file in templates or file[1:] in templates:

                    template = jinja2_env.get_template(file)
                    # 渲染模板（如果有变量的话）
                    if str(file).startswith("/"):
                        template_vars = idepy_app.get_jinjia_data(file)
                    else:
                        template_vars = idepy_app.get_jinjia_data("/" + file)
                    # 使用参数ID渲染
                    if jinjia_id:
                        template_vars = idepy_app.get_jinjia_data(jinjia_id)


                    rendered_html = template.render(template_vars)
                    return rendered_html

                # 服务器根目录
                root_path = os.path.join(settings.PROJECT_PATH, './static/src')
                return bottle.static_file(file, root=root_path)

        server.root_path = abspath(common_path) if common_path is not None else None
        server.port = http_port or _get_random_port()
        if keyfile and certfile:
            server_adapter = SSLWSGIRefServer()
            server_adapter.port = server.port
            setattr(server_adapter, 'pywebview_keyfile', keyfile)
            setattr(server_adapter, 'pywebview_certfile', certfile)
        else:
            server_adapter = ThreadedAdapter
        server.thread = threading.Thread(
            target=lambda: bottle.run(
                app=app, server=server_adapter, port=server.port, quiet=not start_config['debug']
            ),
            daemon=True,
        )
        server.thread.start()

        server.running = True
        protocol = 'https' if keyfile and certfile else 'http'
        server.address = f'{protocol}://127.0.0.1:{server.port}/'
        cls.common_path = common_path
        server.js_api_endpoint = f'{server.address}js_api/{server.uid}'

        return server.address, common_path, server
