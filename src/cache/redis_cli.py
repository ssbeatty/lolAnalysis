import json

import redis

from src.cache.redis_pool import POOL

COOKIE_KEY = "cookie"


def save_cookie(cookies):
    conn = redis.Redis(connection_pool=POOL)
    if isinstance(cookies, str) or isinstance(cookies, bytes):
        context = cookies
    elif isinstance(cookies, dict):
        context = json.dumps(cookies)
    else:
        return

    conn.setex(COOKIE_KEY, 3600, context)


def load_cookie():
    conn = redis.Redis(connection_pool=POOL)
    result = conn.get(COOKIE_KEY)
    if result:
        try:
            res = json.loads(result.decode())
            return res
        except Exception as e:
            print(e)
            return None
    else:
        return None


def delete_cookie():
    conn = redis.Redis(connection_pool=POOL)
    return conn.delete(COOKIE_KEY)


if __name__ == '__main__':
    save_cookie({"tgp_user_type": "0", "tgp_env": "online", "tgp_ticket": "C255003EDA272C56C63B57B855239A4E2F8CD0E5F3853AC7C18D7633CA6B5595FF4F8272261F072A9FD80857B4B717E903C73E8984E59AC4373812D1186347B455FEA5DB5BEB3A0437F22580DADA09397A4360DDD51CB161B8754F52F62BA1E95B74E60D15AEC3FDCA486BAB471224D86C6495B77DBB944E9AF941BB402C0265", "tgp_id": "43109330", "p_skey": "1FlfL3K0Hgr4i4fg5Faj9QgxCDh9RFtxgaS5J4fSaMk_", "p_uin": "o0918562230", "skey": "@U6jGYg3wK", "uin": "o0918562230", "pgv_pvid": "1272040817", "ssr": "0", "ts_uid": "1282140444", "ts_last": "www.wegame.com.cn/", "pt4_token": "FBE*f4fCOMIxl0Lbba6gQwEPExw7HqcIDFk5Fj5wmgE_", "pgv_info": "ssid=s5890389328"})
