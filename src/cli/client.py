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

from src.cache.redis_cli import save_cookie, load_cookie, delete_cookie


HEADERS = {
    'Referer': 'https://www.wegame.com.cn/middle/login/third_callback.html',
    'Accept': 'application/json',
    'Accept-Encoding': 'application/json, text/plain, gzip',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
}

NICK_API = "https://m.wegame.com.cn/api/mobile/lua/proxy/index/mwg_lol_proxy/query_by_nick"
BATTLE_API = "https://m.wegame.com.cn/api/mobile/lua/proxy/index/mwg_lol_proxy/get_battle_list"


def parse_cookies(_cookies):
    new_cookies = {}
    if not _cookies:
        return new_cookies
    for _cookie in _cookies:
        new_cookies[_cookie["name"]] = _cookie["value"]
    return new_cookies


class Player:
    slol_id = ""
    area_id = 0
    isMe = False
    game_id = 26
    game_nick = ""
    icon_url = ""
    rank_title = ""


class Battle:
    def __str__(self):
        return "battle_id: {}, {}-{}, {}".format(self.battle_id, self.kill_num, self.death_num, self.ext_tag_desc)
    battle_id = 0
    game_score = 0
    battle_time = 0
    kill_num = 0
    death_num = 0
    ext_tag_desc = ""


class BaseClient(ABC):

    @abstractmethod
    def login(self):
        ...

    @abstractmethod
    def query_by_nick(self, nick):
        ...

    @abstractmethod
    def get_battle_list(self, player, b_type, offset, limit):
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
        _cookie = load_cookie()
        if _cookie:
            for key, value in _cookie.items():
                self.session.cookies.set(key, value)
            return
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        prefs = {"profile.managed_default_content_settings.images": 2}

        caps = DesiredCapabilities().CHROME
        # caps["pageLoadStrategy"] = "normal"
        #  Waits for full page load
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

        save_cookie(cookies)
        for key, value in cookies.items():
            self.session.cookies.set(key, value)

    def query_by_nick(self, nick):
        resp = self.session.post(NICK_API, json={
            "search_nick": nick
        })
        if resp.status_code != 200:
            return None
        try:
            players = []
            json_body = resp.json()
            if not json_body:
                return None
            data = json_body.get("data")
            if data.get("result") != 0:
                delete_cookie()
                return None
            for player in data.get("player_list"):
                p = Player()
                p.game_nick = player.get("game_nick")
                p.area_id = player.get("area_id")
                p.slol_id = player.get("slol_id")
                p.icon_url = player.get("icon_url")
                p.rank_title = player.get("rank_title")

                players.append(p)
            return players
        except Exception("query_by_nick error") as e:
            delete_cookie()
            print(e)

    def get_battle_list(self, player, b_type=0, offset=0, limit=10):
        resp = self.session.post(BATTLE_API, json={
            "offset": 0,
            "limit": 10,
            "filter_type": b_type,  # 查询类型 0:无筛选 1:匹配 2:排位 3:云顶
            "game_id": 26,
            "slol_id": player.slol_id,
            "area_id": player.area_id,
        }, verify=False)
        if resp.status_code != 200:
            return None
        try:
            player_battle_brief_list = []
            json_body = resp.json()
            data = json_body.get("data")
            if data.get("result") != 0:
                delete_cookie()
                return None
            for battle in data.get("player_battle_brief_list"):
                b = Battle()
                b.battle_id = battle.get("battle_id")
                b.game_score = battle.get("game_score")
                b.battle_time = battle.get("battle_time")
                b.kill_num = battle.get("kill_num")
                b.death_num = battle.get("death_num")
                b.ext_tag_desc = battle.get("ext_tag_desc")
                player_battle_brief_list.append(b)
            return player_battle_brief_list

        except Exception("query_by_nick error") as e:
            delete_cookie()
            print(e)

