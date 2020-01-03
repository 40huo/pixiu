import multiprocessing

# Web后端接口默认开到这个地址
bind = "unix:/run/gunicorn/pixiu.socket"
pid = "/run/gunicorn/pid"

# workers
# debug模式下只开启1个worker
workers = multiprocessing.cpu_count() * 2 + 1

# worker class
# worker进程的类型，你可能需要手动安装：pip install gunicorn[gevent]
worker_class = "gevent"

# max_requests
# 当worker进程每处理max_requests个请求后，会自动重启，如果为0，则表示永不重启
max_requests = 1024

# worker重启前处理后事的时间
graceful_timeout = 3

# remoteIP - 请求时间 请求行 状态码 返回值长度 "referer" "UA"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(t)s %(r)s %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = "info"
