from .lib.redis_cache import RedisCache
from .lib.douyin import Douyin
import os
from dotenv import load_dotenv

load_dotenv()

index = 0

redis_host = os.environ['redis_host']
redis_port = os.environ['redis_port']
redis_password = os.environ['redis_password']
redis_db = int(os.environ['redis_db'])

cache = RedisCache({
    'host': redis_host,
    'db':redis_db,
    'port': redis_port,
    'password': redis_password,
    'max_connections':20,
    'socket_timeout':5,        # 套接字操作超时（秒）
    'socket_connect_timeout':5, # 连接建立超时（秒）
    'retry_on_timeout':True,
    })

def douyin_search(keyword,count = 20):
    global index
    cookies = cache.get_all('douyin-cookies')
    cookie = ''
    local_index = 0
    for key in cookies:
        curr = index % len(cookies)
        if curr == local_index:
            cookie = str(cookies[key])
            break
        local_index += 1
    type = 'search'
    url = f'https://www.douyin.com/root/search/{keyword}?type=general'
    a = Douyin(url, count, type, '下载', cookie)
    results = a.run()
    index+=1
    return results