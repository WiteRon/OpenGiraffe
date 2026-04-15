# Trio_fullstack_<version1.0.1>

## 1. 本次版本目标

本次版本围绕 Travelbook 做了一次完整的全栈闭环整理，目标是：

- 让旅行记录可以通过网页录入，而不是手写 SQL
- 让 3D 地球页面直接读取数据库数据
- 让同一个 FastAPI 服务同时承载页面、静态资源和 API
- 让项目能在资源有限的服务器上稳定运行
- 解决“每次新增地点都要手查经纬度”的痛点

当前版本已经形成可运行的第一版全栈链路。

## 2. 当前功能总览

### 页面

- `/admin`
  用于录入旅行记录、查看最近记录

- `/mobile`
  用于展示 3D 地球、地点详情、地点下的记录内容

- `/health`
  用于健康检查

### API

- `GET /locations`
  返回地球仪标点需要的聚合地点数据

- `GET /entries`
  返回旅行记录列表

- `GET /entries/{id}`
  返回单条记录

- `POST /entries`
  新建旅行记录

- `PUT /entries/{id}`
  更新旅行记录

- `DELETE /entries/{id}`
  删除旅行记录

### 数据库

当前主业务仍然围绕一张表：

- `entries`

关键字段包括：

- `destination`
- `entry_date`
- `entry_type`
- `country`
- `city`
- `lat`
- `lng`
- `title`
- `content`

## 3. 本次核心改动

### 3.1 主服务整合

原本项目中存在多条后端路线。

本次调整后，主线统一为：

- `main.py`
- `src/api/server.py`
- `src/container.py`

由主 FastAPI 服务统一提供：

- 页面路由
- 静态资源
- MySQL CRUD
- 地球仪地点聚合接口

这样做的好处是：

- 部署更简单
- 服务更轻
- 页面和 API 不再分散在不同入口

### 3.2 新增 `/admin` 录入页

新增了轻量录入页面：

- `admin.html`

主要能力：

- 新增记录
- 查看最近记录
- 使用 `POST /entries` 写数据库

这个页面的定位是：

- 日常录入后台
- 测试数据入口
- 不依赖复杂前端框架

### 3.3 改造 `/mobile` 地球页

`mini-trip-mobile.html` 不再依赖前端硬编码的静态地点数据。

现在逻辑改为：

1. 页面加载后请求 `/locations`
2. 根据返回的地点数据生成地球标点
3. 点击地点后请求 `/entries`
4. 在右侧面板里展示该地点记录

并补充了：

- 地点记录编辑
- 地点记录删除
- 空数据时仍展示地球本体

### 3.4 MySQL 接入主后端

新增了数据库相关模块：

- `src/db/connection.py`
- `src/repositories/entry_repository.py`
- `src/domain/entry.py`

作用分别是：

- 建立 MySQL 连接
- 负责 `entries` 表读写
- 定义记录和地点响应模型

### 3.5 自动 geocoding 能力

这是本次版本的重点增强。

现在 `POST /entries` 的逻辑支持：

- 如果前端传了 `lat/lng`，直接保存
- 如果前端没有传 `lat/lng`，后端自动尝试 geocoding

新增模块：

- `src/services/geocode_service.py`

当前 geocoding 策略：

1. 先查数据库里已有同城坐标
2. 如果已有同城坐标，则直接复用
3. 如果没有，则调用外部 geocoding API
4. 获取到 `lat/lng` 后再保存 entry

当前默认 provider：

- `OpenCage`

对应配置：

- `GEOCODE_PROVIDER`
- `GEOCODE_API_KEY`
- `GEOCODE_TIMEOUT`

### 3.6 让老服务器环境可运行

本次还专门做了兼容性收敛，原因是线上环境较老。

处理包括：

- 把 `gradio` 改成可选依赖
- 把 `openai` 改成可选依赖
- 去掉对 `python-dotenv`、`pydantic-settings` 的强依赖
- 自己实现 `.env` 读取
- 将主启动链改为兼容服务器老 Python 环境

这样主站可以先跑起来，AI 和 Gradio 不再阻塞部署。

## 4. 当前运行方式

### 主服务入口

- `scripts/run_api.sh`

当前脚本能力：

- 自动进入项目根目录
- 自动加载 `.env`
- 自动激活 `.venv`（如果存在）
- 使用 `uvicorn main:app` 启动

### 当前运行端口

当前项目已经切换到：

- `4399`

对外主要地址：

- `http://112.126.58.252:4399/health`
- `http://112.126.58.252:4399/admin`
- `http://112.126.58.252:4399/mobile`

## 5. 当前数据流

### 新增记录

1. 用户在 `/admin` 填写记录
2. 前端调用 `POST /entries`
3. 后端检查是否已有 `lat/lng`
4. 如果缺少坐标，则触发 geocoding
5. 后端保存 entry 到 MySQL
6. 前端收到成功结果
7. `/mobile` 通过 `/locations` 获取地点并显示

### 查看地点

1. `/mobile` 请求 `/locations`
2. 地球生成标点
3. 用户点击某个地点
4. 前端请求 `/entries?destination=...&city=...`
5. 页面展示该地点下所有记录

### 编辑 / 删除记录

在 `/mobile` 中点击地点后：

- 可编辑单条记录
- 可删除单条记录
- 删除后会刷新地点聚合结果

## 6. 新增或重点修改的文件

### 新增

- `admin.html`
- `docs/DEVELOPMENT.md`
- `docs/TRAVELBOOK-DEPLOY.md`
- `src/db/__init__.py`
- `src/db/connection.py`
- `src/domain/entry.py`
- `src/repositories/__init__.py`
- `src/repositories/entry_repository.py`
- `src/services/__init__.py`
- `src/services/geocode_service.py`

### 重点修改

- `.gitignore`
- `.env.example`
- `mini-trip-mobile.html`
- `requirements.txt`
- `pyproject.toml`
- `scripts/run_api.sh`
- `src/api/server.py`
- `src/config/settings.py`
- `src/container.py`
- `src/domain/chat.py`
- `src/domain/message.py`

## 7. 当前已知限制

### 7.1 地球标点依赖坐标

`/locations` 只会返回满足以下条件的记录：

- `city` 不为空
- `lat` 不为空
- `lng` 不为空

如果 geocoding 失败或记录没有坐标，地球上不会出现点。

### 7.2 geocoding 依赖外部服务

自动查经纬度依赖：

- OpenCage API key

如果 key 缺失或外部 API 失败，`POST /entries` 会返回明确的错误提示。

### 7.3 `/mobile` 编辑体验仍是轻量实现

当前移动页编辑仍使用浏览器原生：

- `prompt`
- `confirm`

优点是实现轻、兼容老环境；
缺点是交互还不算最终形态。

## 8. 适合继续迭代的方向

下一步推荐优先级：

1. 把 `/admin` 做成更友好的表单校验
2. geocoding 增加缓存表，而不只复用已有 entry
3. `/mobile` 改成更好的编辑弹层
4. 给地点增加按 `destination` 的筛选
5. 把 AI 总结能力挂进地点详情页

## 9. 版本结论

`Trio_fullstack_<version1.0.1>` 可以视为 Travelbook 第一版真正可运行的全栈版本。

它已经完成：

- 页面
- API
- MySQL
- 3D 地球
- 录入
- 编辑
- 删除
- 自动 geocoding
- 服务器部署

虽然仍有体验优化空间，但主流程已经完整闭环。
