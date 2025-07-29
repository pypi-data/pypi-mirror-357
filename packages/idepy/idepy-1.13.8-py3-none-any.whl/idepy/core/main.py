import logging
import os
import random
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox

import webview
from idepy.core import settings, utils
from idepy.core.boot_start import BootStartedManage
from idepy.core.config import SoftConfig
from idepy.core.file import select_folder_path, select_file_path, select_file_save_path
import idepy.core.pywebview_file as pywebview_file
from idepy.core.hotkeys import Hotkeys
from idepy.core.server import BottleCustom
from idepy.core.soft_server import SoftServer
from idepy.core.tray_menu import TrayMenu


class IDEPY:

    def __init__(self, app_name, main_window_config, create_tk_thread=True, create_main_window_now=True):
        """
        :param app_name: 应用名称，程序开机自启使用的文件名，如idepy，则自启使用idepy.exe
        :param main_window_config: 创建主窗口的配置信息
        :param create_tk_thread: 创建tkinter相关线程，用于弹窗、文件选择等，默认为True
        :param create_main_window_now: 立即创建主窗口，默认为True
        """
        super().__init__()
        settings.app = self
        settings.PROJECT_PATH = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.getcwd()

        settings.PROJECT_STATIC_LIB_PATH = os.path.join(settings.PROJECT_PATH, r'./static/src/lib')

        # 避免端口共用
        webview.DEFAULT_HTTP_PORT = None

        self.app_name = app_name
        self.app_started = False

        # 创建主窗口
        self.main_window = None

        # 主窗口配置内容
        self.main_window_config = main_window_config
        if create_main_window_now:
            self.main_window = self._create_main_window()

        # 开启全局热键监听循环
        Hotkeys.start()

        # 托盘菜单
        self.tray_menu = None

        # 配置项
        self.config = SoftConfig()

        # 软件服务
        self.soft = SoftServer()



        # tkinter组件
        self.tk = None

        def start_tkinter():
            self.tk = tk.Tk()
            self.tk.withdraw()
            self.tk.mainloop()  # 运行 tkinter 的主事件循环

        # 启动 tkinter 在单独的线程中，如果其他应用有tk线程，那么则无需创建
        if create_tk_thread:
            tkinter_thread = threading.Thread(target=start_tkinter, daemon=True)
            tkinter_thread.start()

        # 主窗口配置内容
        self.main_window_config = main_window_config

    def init_main_window(self):
        """初始化主窗口"""
        self.main_window = self._create_main_window()

    def create_window(self, *args, **kwargs, ):

        window = webview.create_window(*args, **kwargs)







        js_api = kwargs.get('js_api')
        settings.WINDOW_INDEX += 1
        if js_api:
            # 设置window对象映射
            js_api._set_window(settings.WINDOW_INDEX)

            settings.WINDOW_MAPPER[settings.WINDOW_INDEX] = window

        def window_loaded():
            window.evaluate_js("""
            
            
            
/// 获取 pywebview.api 中所有的属性和方法
const api = pywebview.api;

// 创建两个对象：一个存储剔除前缀后的函数，另一个存储剩余的函数
const iglobalFunctions = {};
const remainingFunctions = {};

// 遍历 api 对象的所有键
Object.keys(api).forEach(key => {
  if (key.startsWith('iglobal_') && typeof api[key] === 'function') {
    // 剔除 'iglobal' 前缀并将函数存入 iglobalFunctions
    const newKey = key.replace(/^iglobal_/, '');
    iglobalFunctions[newKey] = api[key];
  } else if (typeof api[key] === 'function') {
    // 其余函数存入 remainingFunctions
    remainingFunctions[key] = api[key];
  }
});

// 将剔除前缀后的函数赋值给 window.idepy
window.idepy = iglobalFunctions;

// 将剩余的函数赋值给 window.api
window.api = remainingFunctions;

console.log("[IDEPY]初始化功能接口成功");


           
            """)

        window.events.loaded += window_loaded



        # 控制本地网站加载逻辑
        def before_window_show():
            # print("显示前", window.original_url,  window.real_url, webview.http.global_server.address)
            if window.original_url.startswith('/window'):
                new_url = webview.http.global_server.address + str(window.original_url)
                window.load_url(new_url)

        window.events.shown += before_window_show


        return window

    def _create_main_window(self):

        if self.main_window:
            raise Exception("仅允许创建一个主窗口")
        mwc = {
            "title": "启动窗口（启动）",
            "url": f"/windows/main/index.html",
            **self.main_window_config
        }

        main_window = self.create_window(**mwc)

        def on_close_window():
            while len(webview.windows) > 0:
                for w in webview.windows:
                    w.destroy()


        main_window.events.closed += on_close_window
        return main_window

    def is_env_support_gui(self):
        pass

    def start(self, *args, **kwargs):
        """
        启动应用主线程
        :param args:
        :param kwargs:
        :return:
        """



        def func():
            self.app_started = True

        default = {
            "gui": 'edgechromium',
            "server": BottleCustom,
            "private_mode": False,
            "func": func,
            "ssl": True,
        }


        final_args = {
            **default,
            **kwargs
        }

        webview.start(
            *args,
            **final_args
        )


    def set_auto_start(self, enabled=True):
        """设置应用开机自动启动"""
        bsm = BootStartedManage(self.app_name)
        if enabled:
            bsm.register()
        else:
            bsm.unregister()

    def is_enabled_auto_start(self):
        """
        检查程序是否开机启动

        :return: bool
        """
        bsm = BootStartedManage(self.app_name)
        return bsm.is_added_to_startup_folder()

    def hotkeys_reg(self, key, oncall, suppress=False):
        """
        注册全局热键

        :param key:按键，组合键为：alt+ctrl+h、单按键为：h
        :param oncall: 热键触发函数
        :param suppress: 当本程序触发热键时，其他项目不触发热键
        :return:
        """
        Hotkeys.reg(key, oncall, suppress)

    def hotkeys_list(self):
        """
        获取组成的热键
        :return: list 注册的热键列表
        """
        return Hotkeys.registered_keys

    def tray_start(self, name, icon_path, menu_list):

        # 主窗口隐藏/显示
        def show_main_window():
            if self.main_window:
                self.main_window.restore()
                self.main_window.show()
                self.main_window.on_top = True
                self.main_window.on_top = False

        self.tray_menu = TrayMenu(name, icon_path)
        self.tray_menu.add_menu('显示', show_main_window, visible=False, default=True)
        for menu in menu_list:
            self.tray_menu.add_menu(**menu)
        self.tray_menu.mount()

    def tray_stop(self):
        self.tray_menu.stop()

    def show_notify(self, title, msg, duration=5):
        """
        显示系统通知
        :param title: 标题
        :param msg:  信息
        :param duration: 持续时间默认10s
        :return:
        """
        from plyer import notification

        # 显示一个桌面通知
        notification.notify(title, msg, timeout=duration)

    def config_get(self, key_path, default=""):
        """
        获取程序配置项
        :param key_path: 配置项的键
        :param default: 返回默认值
        :return:
        """
        return self.config.get(key_path, default)

    def config_data(self):
        """
        获取程序配置项
        :return:
        """
        return self.config.load()

    def config_update(self, key_path, value):
        """
        更新程序配置项
        :param key_path: 配置项键，如base.time
        :param value: 对应项的值
        :return:
        """
        self.config.update(key_path, value)
        self.config.save()

    def file_select_folder_path(self, **kwargs):
        """
        弹出对话框，让用户选择一个文件夹地址
        :param kwargs:
        :return: 文件夹路径
        """
        return select_folder_path(**kwargs)

    def file_select_file_path(self, **kwargs):
        """
        弹出对话框，让用户选择一个文件地址
        :param kwargs:
        :return: 文件夹路径
        """
        return select_file_path(**kwargs)

    def file_select_file_save_path(self, **kwargs):
        """
        弹出对话框，让用户选择一个保存地址
        :param kwargs:
        :return: 文件夹路径
        """
        return select_file_save_path(**kwargs)

    def pywebview_file_select_folder_path(self, **kwargs):
        """
        弹出对话框，让用户选择一个文件夹地址
        :param kwargs:
        :return: 文件夹路径
        """
        return pywebview_file.select_folder_save_path(**kwargs)

    def pywebview_file_select_file_path(self, **kwargs):
        """
        弹出对话框，让用户选择一个文件地址
        :param kwargs:
        :return: 文件夹路径
        """
        return pywebview_file.select_file_path(**kwargs)

    def pywebview_file_select_file_save_path(self, **kwargs):
        """
        弹出对话框，让用户选择一个保存地址
        :param kwargs:
        :return: 文件夹路径
        """
        return pywebview_file.select_file_save_path(**kwargs)



    def _show_message(self, message, title="提示", height=200, width=400):
        wd = None

        class MessageAPI:

            def get_data(self):
                return {
                    "title": title,
                    "message": message,
                }

            def close(self):
                wd.destroy()

        wd = webview.create_window(
            title, url='/window_sys/message/index.html',

            js_api=MessageAPI(),
            width=width,
            height=height,
            on_top=True,
            frameless=True,
            focus=True,

        )

        return wd

    def show_message_box_draw(self, message, title="提示", height=200, width=400, block=False):
        """
        显示消息框，使用单独窗口绘制
        :param message: 提示消息
        :param title: 提示标题
        :param height: 高度
        :param width: 宽度
        :param block: 是否阻塞，等待用户关闭后执行操作
        :return:
        """
        if not self.app_started:
            logging.warning("请在IDEPY主应用启动后调用本函数")
            return

        wd = self._show_message(message, title, height, width)

        while block and wd in webview.windows:
            time.sleep(0.3)


    def check_support_and_update_edgechromium(self):
        """
        检查是否支持edgechromium，并提示更新，强制退出程序
        :return: bool
        """
        from webview.platforms.winforms import _is_chromium
        if not _is_chromium():
            messagebox.showinfo('提示', '当前Edge版本过旧，请升级后使用本程序。')
            utils.open_url("https://www.microsoft.com/zh-cn/edge/?form=MA13FJ")
            exit()
        return True

    def set_jinjia_data(self, template_path_or_jinjia_id, data):
        """设置jinjia模板的数据，需要页面刷新后才生效
        :param template_path_or_jinjia_id 输入模板文件的目录，如：/windows/window1/index.html，开头和连接符使用/，且相对于static/src目录的路径，或jinjia模板id。
        :param data 设置的数据值
        """
        settings.jinjia_data[template_path_or_jinjia_id] = data
        # print(idepy_next.jinjia_data)

    def get_jinjia_data(self, template_path_or_jinjia_id):
        """获取jinjia模板的数据
        :param template_path_or_jinjia_id 输入模板文件的目录，如：/windows/window1/index.html，使用反斜杠，且相对于static/src目录的路径，或jinjia模板id。
        """
        return settings.jinjia_data.get(template_path_or_jinjia_id, {})

    def remove_jinjia_data(self, template_path_or_jinjia_id):
        """移除jinjia模板的数据
        :param template_path_or_jinjia_id 输入模板文件的目录，如：/windows/window1/index.html，使用反斜杠，且相对于static/src目录的路径，或jinjia模板id。
        """
        settings.jinjia_data.pop(template_path_or_jinjia_id)

    def _show_message_by_js(self, message, title="提示", height=200, width=400):
        wd = None
        app = get_app()

        class MessageAPI:

            def get_data(self):
                return {
                    "title": title,
                    "message": message,
                }

            def close(self):
                app.remove_jinjia_data(jinjia_id)
                wd.destroy()

        jinjia_id = "MSG_" + str(random.randint(0,99999))
        app.set_jinjia_data(jinjia_id, {
            "title":title,
            "message": message
        })

        wd = webview.create_window(
            title, url= f'/window_sys/message_js/index.html?jinjia_id={jinjia_id}',
            js_api=MessageAPI(),
            width=width,
            height=height,
            on_top=True,
            frameless=True,
            focus=True,

        )


        return wd


    def show_message_box_draw_by_js(self, message, title="提示", height=200, width=400, block=False):
        """
        显示消息框，使用单独窗口绘制，纯原生+Jinjia2实现，执行效率比show_message_box_draw更高。
        如果旧项目没有相关内容，可以到idepy/templates/base_project/static/src/window_sys/message_js复制。
        :param message: 提示消息
        :param title: 提示标题
        :param height: 高度
        :param width: 宽度
        :param block: 是否阻塞，等待用户关闭后执行操作
        :return:
        """

        wd = self._show_message_by_js(message, title, height, width)

        while block and wd in webview.windows:
            time.sleep(0.3)





def get_app() -> IDEPY:
    return settings.app
