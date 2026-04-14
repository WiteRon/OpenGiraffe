# Travelbook 部署说明

这份说明对应当前这套单服务结构：

- `main.py` 提供主 FastAPI
- `/admin` 录入旅行记录
- `/mobile` 展示 3D 地球
- MySQL 存储 `entries` 数据

## 1. 服务器准备

```bash
sudo dnf install -y python3 python3-pip
cd /你的项目目录
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 2. 写 `.env`

在项目根目录创建 `.env`：

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=traveluser
DB_PASSWORD=你的数据库密码
DB_NAME=travelbook

# 还没接 AI 可以先留空
API_KEY=
BASE_URL=https://ark.cn-beijing.volces.com/api/coding/v3
MODEL=minimax-m2.5
```

## 3. 启动服务

前台测试：

```bash
cd /你的项目目录
source .venv/bin/activate
./scripts/run_api.sh
```

看到服务启动后，访问：

- `http://你的服务器IP:8000/health`
- `http://你的服务器IP:8000/admin`
- `http://你的服务器IP:8000/mobile`

说明：线上部署当前不需要 `gradio` 和 `openai`。如果以后要单独运行 `app.py` 或接 AI，再额外安装对应依赖即可。

## 4. 后台常驻

```bash
cd /你的项目目录
source .venv/bin/activate
nohup ./scripts/run_api.sh > uvicorn.log 2>&1 &
echo $!
```

查看日志：

```bash
tail -f uvicorn.log
```

停止服务：

```bash
pkill -f "uvicorn main:app"
```

## 5. 首次验证建议

1. 打开 `/admin` 新增一条中文记录
2. 打开 `/mobile` 检查地球上是否出现地点
3. 点击地点，验证详情、编辑、删除是否正常

## 6. 常见问题

- `/mobile` 白屏：检查 `/static/earth.jpg` 和 `/static/js/globe.gl.min.js` 是否 200
- `/locations` 为空：说明数据库里还没有带 `lat/lng` 的记录
- 中文乱码：确认 `.env` 和数据库连接都保持 `utf8mb4`
