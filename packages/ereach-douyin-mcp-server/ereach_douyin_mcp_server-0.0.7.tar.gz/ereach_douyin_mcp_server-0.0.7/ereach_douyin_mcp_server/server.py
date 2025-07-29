from flask import Flask, jsonify, request

import os
from flask_cors import CORS
from dotenv import load_dotenv
from lib.redis_cache import RedisCache
from douyin_proxy import douyin_search
load_dotenv()


app = Flask(__name__)

server_port = 8088

if 'server_port' in os.environ:
    server_port = int(os.environ['server_port'])

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
@app.route('/douyin/search',methods=['POST'])
def api_douyin_search():
    results = douyin_search(request.json['keyword'],request.json['count'])
    return jsonify(results)

if __name__ == '__main__':
    CORS(app,origins="*",supports_credentials=True)
    app.run(host="0.0.0.0",port=server_port,debug=True,use_reloader=True, use_debugger=False)