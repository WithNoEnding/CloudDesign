import os
import time
import redis
import requests  # 自选依赖包，用于满足任务书“加入至少1个自选Python包”的要求
from flask import Flask, jsonify, request

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
CPU_WORK = int(os.getenv("CPU_WORK", "0"))  # 用于HPA压测，可在K8s ConfigMap中调大


def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD if REDIS_PASSWORD else None,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3,
    )


def small_cpu_work():
    # 让 /api/ping 在K8s压测时产生一定CPU负载，便于HPA触发。
    # 本地默认 CPU_WORK=0，不影响普通联调。
    total = 0
    for i in range(CPU_WORK):
        total += (i * i) % 97
    return total


@app.route("/api/ping", methods=["GET"])
def ping():
    small_cpu_work()
    print("Received request: /api/ping", flush=True)
    return jsonify({"status": "ok"})


@app.route("/api/count", methods=["GET"])
def count():
    r = get_redis_client()
    value = r.incr("visit_count")
    print(f"Received request: /api/count, count={value}", flush=True)
    return jsonify({"count": value})


@app.route("/api/redis/set", methods=["POST", "GET"])
def redis_set():
    key = request.args.get("key", "testkey")
    value = request.args.get("value", "hello")
    r = get_redis_client()
    r.set(key, value)
    print(f"Redis SET {key}={value}", flush=True)
    return jsonify({"key": key, "value": value})


@app.route("/api/redis/get", methods=["GET"])
def redis_get():
    key = request.args.get("key", "testkey")
    r = get_redis_client()
    value = r.get(key)
    print(f"Redis GET {key}={value}", flush=True)
    return jsonify({"key": key, "value": value})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
