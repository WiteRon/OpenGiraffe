# 最小可运行集合（仅移动端 3D 页）

不需要 `frontend/`、`mini-trip.html` 等，只要下面几项即可在服务器上跑起来。

## 目录结构（部署到服务器后应长这样）

```text
你的目录/                    ← 这里叫「项目根」，下面命令都在这一层执行
├── backend/
│   ├── server_mobile_minimal.py
│   └── requirements.txt
├── mini-trip-mobile.html
└── static/
    ├── earth.jpg
    └── js/
        └── globe.gl.min.js
```

## 体积大约

约 **2.5 MB**（主要是 `globe.gl.min.js` + `earth.jpg`），加上几 KB 的 Python 与 HTML。

## 方式一：本机打包后上传（推荐）

在 **Mac 上、项目根目录**执行：

```bash
cd /Users/albert/Code/SSSVP/SSSSVP-YANG-master
chmod +x scripts/pack-minimal-deploy.sh
./scripts/pack-minimal-deploy.sh
```

会生成 **`trip-mobile-minimal.tgz`**（在仓库根目录）。

上传到服务器：

```bash
scp trip-mobile-minimal.tgz root@你的服务器IP:/root/
```

服务器上解压并启动：

若出现 `tar: 忽略未知的扩展头关键字 'LIBARCHIVE.xattr...'`，是 Mac 打包带的苹果扩展属性，**可忽略**，不影响文件。

**路径说明**：压缩包顶层目录名为 `trip-mobile`。

- 在**家目录**执行 `tar xzf trip-mobile-minimal.tgz` → 项目根为 **`~/trip-mobile`**（`cd ~/trip-mobile`）。
- 若执行 `mkdir x && tar xzf ... -C x` → 项目根为 **`x/trip-mobile`**（多一层）。

```bash
ssh root@你的服务器IP
cd /root
mkdir -p trip-mobile && tar xzf trip-mobile-minimal.tgz -C trip-mobile
cd trip-mobile/trip-mobile
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.server_mobile_minimal:app --host 0.0.0.0 --port 8000
```

手机访问：`http://公网IP:8000/` 或 `http://公网IP:8000/mobile`

后台常驻：

```bash
nohup uvicorn backend.server_mobile_minimal:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
```

## 方式二：手动只拷贝这些路径

用 `rsync` / SFTP 只传：

- `backend/server_mobile_minimal.py`
- `backend/requirements.txt`
- `mini-trip-mobile.html`
- `static/`（整个目录）

保持与上面相同的目录结构即可。

## 与完整仓库的区别

| 完整 `git clone` | 最小集合 |
|------------------|----------|
| 含 `frontend/`、桌面版等 | 不含 |
| 用 `uvicorn backend.server:app` | 用 `uvicorn backend.server_mobile_minimal:app` |
| `/` 打开桌面地图 | `/` 与 `/mobile` 都是 3D 移动端 |

## 安全组

云厂商控制台放行 **TCP 8000**（或你改的端口）。
