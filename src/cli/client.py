"""
用来跟腾讯api交互的模块
"""
import os
import json
from abc import ABC, abstractmethod

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait


HEADERS = {
    'Referer': 'https://www.wegame.com.cn/middle/login/third_callback.html',
    'Accept': 'application/json',
    'Accept-Encoding': 'application/json, text/plain, gzip',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
}

NICK_API = "https://m.wegame.com.cn/api/mobile/lua/proxy/index/mwg_lol_proxy/query_by_nick"


def parse_cookies(_cookies):
    new_cookies = {}
    if not _cookies:
        return new_cookies
    for _cookie in _cookies:
        new_cookies[_cookie["name"]] = _cookie["value"]
    return new_cookies


class BaseClient(ABC):

    @abstractmethod
    def login(self):
        ...

    @abstractmethod
    def query_by_nick(self, nick):
        ...

    @abstractmethod
    def get_battle_list(self, offset, num):
        ...


class ClientSync(BaseClient, ABC):
    def __init__(self, qq, password):
        self.qq = qq
        self.password = password
        # 等待刷新的超时时间，根据网络调节
        self.load_time_out = 10

        self.session = requests.Session()
        # 设置请求头
        self.session.headers = HEADERS

    def login(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        prefs = {"profile.managed_default_content_settings.images": 2}

        caps = DesiredCapabilities().CHROME
        # caps["pageLoadStrategy"] = "normal"  #  Waits for full page load
        caps["pageLoadStrategy"] = "none"

        options.add_experimental_option("prefs", prefs)
        executable_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "lib", "chromedriver.exe")
        chrome_driver = webdriver.Chrome(
            executable_path=executable_path, options=options, desired_capabilities=caps)
        chrome_driver.get("https://www.wegame.com.cn/")
        WebDriverWait(chrome_driver, self.load_time_out).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'widget-header-login-btn')))
        chrome_driver.find_element_by_class_name("widget-header-login-btn").click()

        iframe = chrome_driver.find_elements_by_tag_name("iframe")[0]
        chrome_driver.switch_to.frame(iframe)

        WebDriverWait(chrome_driver, self.load_time_out).until(
            expected_conditions.presence_of_element_located((By.ID, 'switcher_plogin')))
        chrome_driver.implicitly_wait(1)
        chrome_driver.find_element(By.ID, "switcher_plogin").click()
        chrome_driver.find_element(By.ID, "u").send_keys(self.qq)
        # 输入密码
        chrome_driver.find_element(By.ID, "p").send_keys(self.password)
        # 发送登录请求
        chrome_driver.find_element(By.ID, "login_button").click()
        chrome_driver.switch_to.default_content()
        WebDriverWait(chrome_driver, self.load_time_out).until(
            expected_conditions.invisibility_of_element_located((By.ID, "login")))
        cookies = parse_cookies(chrome_driver.get_cookies())

        for key, value in cookies.items():
            self.session.cookies.set(key, value)
        # self.session.cookies.set("tgp_ticket", cookies.get("tgp_ticket"))
        # self.session.cookies.set("tgp_id", cookies.get("tgp_ticket"))

    def query_by_nick(self, nick):
        resp = self.session.post(NICK_API, json={
            "search_nick": nick
        })
        if resp.status_code != 200:
            return None
        context = resp.content.decode()
        try:
            json_body = json.loads(context)
            if json_body.get("code") != 0:
                return None
            return json_body.get("data")
        except Exception("load query_by_nick context error") as e:
            print(e)
            return None

    def get_battle_list(self, offset, num):
        ...

