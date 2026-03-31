# 部署到服务器（手机可访问）

本项目的移动端页依赖 **FastAPI**：必须同时提供 `/mobile` 与 `/static/`，不能只上传单个 HTML。

**只想上传最少文件（不含 frontend、不含桌面版）**：见 **[MINIMAL-DEPLOY.md](./MINIMAL-DEPLOY.md)**，使用 `backend/server_mobile_minimal.py` 与 `scripts/pack-minimal-deploy.sh`。

---

## 你需要准备

- 一台 Linux 云服务器（如阿里云 ECS），已能 **SSH 登录**
- 服务器上 **Python 3.9+**（`python3 --version`）
- 本机代码已包含：`mini-trip-mobile.html`、`static/`（含 `js/globe.gl.min.js`、`earth.jpg`）、`backend/`

---

## 第一步：把代码弄到服务器上

任选一种方式。

### 方式 A：用 Git（推荐）

**在你自己的电脑上**（项目根目录）先提交并推送：

```bash
cd /Users/albert/Code/SSSVP/SSSSVP-YANG-master
git add .
git status
git commit -m "deploy: mobile globe + static"
git push origin master
```

**在服务器上**：

```bash
cd /opt   # 或你喜欢的目录，如 /home/yourname
sudo git clone https://github.com/你的用户名/你的仓库名.git SSSSVP-YANG
cd SSSSVP-YANG
```

若仓库是私有的，需配置 SSH 密钥或 HTTPS 凭据。

### 方式 B：不用 Git，用 scp 打包上传

**在你自己的电脑上**：

```bash
cd /Users/albert/Code/SSSVP
tar czf trip-deploy.tgz SSSSVP-YANG-master
scp trip-deploy.tgz root@你的服务器公网IP:/root/
```

**在服务器上**：

```bash
cd /root
tar xzf trip-deploy.tgz
cd SSSSVP-YANG-master
```

---

## 第二步：服务器上安装依赖

```bash
cd /opt/SSSSVP-YANG   # 或你的实际路径，例如 /root/SSSSVP-YANG-master
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r backend/requirements.txt
```

---

## 第三步：放行端口（阿里云安全组）

1. 登录 **阿里云控制台** → ECS → 你的实例 → **安全组**
2. **入方向** 添加规则：**TCP**，端口 **8000**，源 **0.0.0.0/0**（或仅你的 IP，更安全）

（若以后用 Nginx 反代到 80，再改规则即可。）

---

## 第四步：启动服务（先测试）

仍在项目根目录、且已 `source .venv/bin/activate`：

```bash
cd /opt/SSSSVP-YANG   # 换成你的实际路径
source .venv/bin/activate
uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

不要关 SSH 窗口。用手机浏览器打开：

```text
http://你的服务器公网IP:8000/mobile
```

桌面版：

```text
http://你的服务器公网IP:8000/
```

健康检查：

```text
http://你的服务器公网IP:8000/api/health
```

应返回：`{"status":"ok"}`

---

## 第五步：后台常驻（SSH 断开后仍运行）

按 `Ctrl+C` 停掉前台 uvicorn，然后：

```bash
cd /opt/SSSSVP-YANG
source .venv/bin/activate
nohup uvicorn backend.server:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
echo $!
```

记下进程号；查看日志：`tail -f uvicorn.log`

**停止服务**（需要时）：

```bash
pkill -f "uvicorn backend.server:app"
```

---

## 常见问题

| 现象 | 处理 |
|------|------|
| 手机打不开 | 检查安全组是否放行 **8000**；服务器防火墙 `firewalld`/`ufw` 是否放行 |
| 页面白屏 / 地球不显示 | 手机用 **http://IP:8000/mobile**，不要用 `file://`；浏览器里看 Network 是否 **200** 加载 `/static/js/globe.gl.min.js` 和 `/static/earth.jpg` |
| 端口被占用 | 换端口：`--port 8001`，访问时改成 `:8001` |

---

## 以后更新网页

用 Git 的服务器上：

```bash
cd /opt/SSSSVP-YANG
git pull
# 若已 nohup 运行，建议重启：
pkill -f "uvicorn backend.server:app"
source .venv/bin/activate
nohup uvicorn backend.server:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
```

用 scp 的：重新打包上传覆盖对应文件后，同样重启 uvicorn。
