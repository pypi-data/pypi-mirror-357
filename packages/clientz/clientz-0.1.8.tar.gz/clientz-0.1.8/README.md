# clientz

# 正式启动
cd src; python -m clientz.server 8008

# 测试启动
cd src; uv run python -m clientz.server 8108 --log-level "debug"
基本只需要修改
core.py 
config.yaml