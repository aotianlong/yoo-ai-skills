---
name: deploy
description: >-
  yoo-base 生产部署与发版：首次部署（Traefik、三环境 PostgreSQL 库名、./yoo deploy configure/--docker、Tunnel/Pangolin/DDNS/TLS）
  与已部署实例更新（rsync、重建镜像、prestart 迁移、按场景仅更前端/后端、回滚）。
  在用户说「部署到新服务器」「生产环境部署」「生产更新」「发版」「同步服务器」「上线新版本」时使用。
  Pangolin 内网穿透详见 pangolin-deploy 技能。
---

# yoo-base 生产部署与发版

**说明**：yoo-base 是上游模板仓库；实际部署的是**你的下游项目**（fork / 私有副本）。文中 `<deploy-slug>`、`DOMAIN`、`STACK_NAME` 等替换为你的值（与远程 `~/apps/<deploy-slug>` 及 `.env.production` 一致）。

---

## 何时使用

**首次部署**

- 将基于 yoo-base 的应用部署到全新 Linux 服务器
- 配置生产环境（Traefik + Docker + TLS）
- NAT / 无公网 IP，需 **Cloudflare Tunnel** 暴露
- 自定义 API 子域（如 `base-api.example.com` 而非 `api.<DOMAIN>`）
- 查看部署命令或配置文件结构

**生产发版 / 更新**

- 代码已合并，更新**已部署**的生产实例
- 只改前端、只改后端、或全量发版
- 执行/确认 **Alembic 迁移**（经 `prestart`）
- 改 `.env.production` 后需要生效

---

## CLI 部署（推荐）

仓库内首选 **`./yoo deploy`**，替代手工 rsync + 远端 compose。与 `scripts/bootstrap-server.sh` / `scripts/deploy.sh` 可并存，日常以 CLI 为准；生产 Traefik 栈以 **`docker-compose.prod.yml` + `.env.production`** 为准。

### 1. 生成本地 `.env.production`

```bash
./yoo deploy configure          # 交互式（域名、STACK_NAME、密钥、超管、可选 SMTP/DDNS）
# 等价：./yoo deploy --docker --init
```

写入项含：`DOMAIN`、`FRONTEND_HOST`、`BACKEND_HOST`、`BACKEND_API_HOST`、`STACK_NAME`、数据库与 `FIRST_SUPERUSER` 等。模板见 `.env.production.example`。

### 2. 配置远端连接（项目根 `.env.local`，gitignore）

| 变量 | 说明 |
|------|------|
| `YOO_DEPLOY_HOST` | SSH 主机（必填） |
| `YOO_DEPLOY_USER` | SSH 用户，默认 `root` |
| `YOO_DEPLOY_REMOTE_PATH` | 远端项目目录，如 `~/apps/my-app` |
| `YOO_DEPLOY_VITE_API_URL` | 本机 `pnpm build` 用的 API 根 URL（优先于 DOMAIN 推导） |
| `YOO_DEPLOY_COMPOSE_FILE` | 默认 `docker-compose.prod.yml` |
| `YOO_DEPLOY_ENV_FILE` | 远端 compose `--env-file`，默认 `.env.production` |
| `YOO_DEPLOY_DOCKER` | 默认 `sudo docker` |

**同机开发 + 生产（`--local`）**：`./yoo` 启动时会把根目录 `.env` 注入进程环境，Docker Compose 变量优先级为 **Shell 环境 > `--env-file` > 项目 `.env`**。若 `.env` 含 `STACK_NAME=yoo-base`、`BACKEND_PORT=8001` 等开发值，会覆盖 `.env.production`，导致 Traefik 路由名错误（404）或 backend 端口与 label 不一致（502）。请在 **`.env.local`**（后加载且 `override=True`）显式写入生产值：

```bash
STACK_NAME=yoo-official          # 与 .env.production 一致，勿用 dev 栈名
BACKEND_PORT=8000                # Traefik label 固定 8000；dev 常用 8001
YOO_DEPLOY_VITE_API_URL=https://api.<DOMAIN>
```

并将 `BACKEND_PORT=8000` 写入 `.env.production`（compose `environment` 段会引用）。

将 `.env.production` 同步到远端（`scp` 或 `./yoo deploy pull-env` 反向拉取备份）。

### 3. 首次部署 / 发版

```bash
./yoo deploy --docker -y
```

默认流程：**本机 `web/pnpm build`** → rsync 代码与 `./yoo` CLI → 远端 `docker compose up -d --build` → `settings.yml` 加载 → **首次**自动 `python -m app.fixtures`。

常用参数：

| 参数 | 用途 |
|------|------|
| `--skip-sync` | 仅远端 compose，不同步代码 |
| `--skip-web-build` | 跳过本机构建（需已有 `web/dist`） |
| `--no-build` | 不 `--build`，仅重建/启动容器 |
| `--frontend-only` / `--backend-only` | 缩小重建范围 |
| `--ddns` | 叠加 `docker-compose.prod.ddns.yml`（IPv6 AAAA，见「公网暴露与 DNS」） |
| `--local` | 本机 compose，不 SSH |
| `--skip-fixture-load` | 不加载 fixtures |

子命令：`./yoo deploy --docker stop|start|restart [服务名...]`（支持 `--local`、`--ddns`）。旧命令 `deploy compose` 仍可用但会提示弃用。

---

## 发版前检查（本地）

- 后端：`alembic heads` 无多个 head；若有则先在本地 `alembic merge` 再发版（见坑8）
- 依赖：`backend/pyproject.toml` / `uv.lock` 已包含新增依赖
- 前端：含冒号的 i18n YAML 值已加引号（见坑7）
- 若变更 **仅配置**：准备 `.env.production` 修改说明，避免漏改 `DOMAIN` / `STACK_NAME` / CORS 等

---

## 按场景发版

在**本地**项目根目录（已配置 `.env.local` 与 `.env.production`）：

| 场景 | 推荐命令 |
|------|----------|
| 全量发版 | `./yoo deploy --docker -y` |
| 仅前端 | `./yoo deploy --docker --frontend-only -y` |
| 仅后端 + Celery（含 prestart） | `./yoo deploy --docker --backend-only -y` |
| 仅改 `.env.production` | 同步 env 后 `./yoo deploy --docker --skip-sync --no-build -y`（必要时加 `--force-recreate`） |
| 代码已同步，只重建容器 | `./yoo deploy --docker --skip-sync --no-build -y` |
| 仅重启不重建 | `./yoo deploy --docker restart <服务名>` |
| NAT 栈已用 Tunnel | 更新 ingress/DNS 见「方案 B」，勿再开 `--ddns` |

健康检查：`https://<DOMAIN>` 与 `https://<BACKEND_API_HOST>/docs`（自定义 API 域时勿用 `api.<DOMAIN>`）。

**注意**：`prestart` 在 `backend` 的 `depends_on` 中为 `service_completed_successfully`；含**新迁移**的后端发版应走完整 `up` 流程，让 prestart 重新执行，不要跳过。

### 手工 rsync + compose（无 CLI 时）

**本地**（与 `bootstrap-server.sh` 同步规则对齐）：

```bash
rsync -avz --progress \
  --exclude 'node_modules' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.git' \
  --exclude 'web/node_modules' \
  --exclude 'mobile/node_modules' \
  ./ <ssh-user>@<server-ip>:~/apps/<deploy-slug>/
```

**服务器**（`~/apps/<deploy-slug>`）：

```bash
# 若改了密钥、数据库、域名等，先编辑 .env.production
sudo docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build   # 全量
# ... up -d --build frontend   # 仅前端
# ... restart backend          # 仅重启
```

查看状态与日志：

```bash
sudo docker compose -f docker-compose.prod.yml --env-file .env.production ps
sudo docker compose -f docker-compose.prod.yml --env-file .env.production logs -f backend
```

---

## 数据库与迁移

- 固定使用三环境库名：`{stack_slug}_development`、`{stack_slug}_production`、`{stack_slug}_test`；应用角色使用 `{stack_slug}`。
- `.env.local` 指向 development，`.env.production` 指向 production；pytest / `./yoo db test-prepare` 指向 test。禁止生成 `*_development_test`。
- `./yoo deploy configure` 生成的 `POSTGRES_DB` 必须带 `_production` 后缀；发版前检查已有裸库名的数据迁移与容器重建。
- 正常路径：镜像更新后的 `up -d --build` 会触发新的 **prestart** 容器执行 `scripts/prestart.sh`（内含 `alembic upgrade` 等，以仓库为准）。
- 若 prestart 失败，先看日志：
  ```bash
  sudo docker compose -f docker-compose.prod.yml --env-file .env.production logs prestart
  ```
- **大版本 / 高风险迁移**：先在低峰做 **PostgreSQL 备份**（`pg_dump` 或卷快照），再发版。

---

## 回滚（简要）

- **配置回滚**：恢复 `.env.production` 备份后 `up -d --force-recreate` 相关服务。
- **代码回滚**：同步上一发版的 Git 标签/提交对应的代码目录后，再次 `up -d --build`。
- **数据库**：若迁移已执行且不可逆，需用备份还原或编写向前修复迁移；发版前备份可降低风险。

---

## 部署架构

设主域名为 `<DOMAIN>`（例如 `app.example.com`），API Traefik 主机名为 `<BACKEND_API_HOST>`（默认 `api.<DOMAIN>`，可自定义如 `base-api.example.com`）：

```
Internet
   │
   ├─ [有公网 IP] DNS A/AAAA → 服务器
   └─ [NAT / 无公网] Cloudflare Tunnel → 127.0.0.1:443（见「公网暴露与 DNS」）
   │
   ▼
Traefik (全局，/opt/traefik/ 或 ~/.local/share/yoo/traefik)
   ├── <DOMAIN>                 → frontend 容器 (Nginx 静态 :80)
   ├── <BACKEND_API_HOST>       → backend 容器 (FastAPI :8000)
   ├── adminer.<DOMAIN>         → adminer (:8080)
   └── traefik.<基础域>         → Traefik Dashboard

每个应用栈（STACK_NAME 唯一）：
   └── db (PostgreSQL)
   └── redis
   └── celery-worker
   └── [可选] cloudflare-ddns（仅 IPv6 AAAA）
```

---

## 文件结构

```
scripts/
  yoo/commands/deploy.py       # ./yoo deploy configure / --docker / --pm2 / pull-env …
  yoo/utils/production_env.py  # 交互式 .env.production
  yoo/utils/cloudflare_ddns.py # --ddns 与 docker-compose.prod.ddns.yml
  bootstrap-server.sh          # 从本地一键完成：初始化 + Traefik + 部署
  server-init.sh               # 服务器初始化（创建用户 + SSH + Docker）
  setup-traefik.sh             # 安装并启动 Traefik（全局，仅需运行一次）
  deploy.sh                    # 应用部署/更新脚本（部分下游仍用）

docker-compose.prod.yml        # 生产 compose（BACKEND_API_HOST Traefik 路由）
docker-compose.prod.ddns.yml   # 可选 DDNS 叠加（./yoo deploy --docker --ddns）
.env.production.example        # 生产配置模板
web/nginx.conf                 # Nginx SPA 路由（web/Dockerfile 使用）
```

---

## 前端构建策略

支持两种策略，**服务器内 multi-stage 构建**为默认推荐：

### 策略一：服务器内 multi-stage 构建（推荐）

`web/Dockerfile` 使用 multi-stage build，Node 在容器内构建：

```dockerfile
FROM node:20-alpine AS build-stage
WORKDIR /app
RUN corepack enable
COPY .npmrc package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

ARG VITE_API_URL          # ← 必须声明，否则 build args 不生效
ENV VITE_API_URL=${VITE_API_URL}

COPY . .
RUN pnpm build

FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf   # ← 必须 COPY
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

`docker-compose.prod.yml` 通过 build args 传入 API 地址：
```yaml
frontend:
  build:
    context: ./web
    args:
      - VITE_API_URL=https://api.${DOMAIN}
```

### 策略二：本地编译后同步（服务器内存不足时使用）

```dockerfile
FROM nginx:stable-alpine
COPY dist /usr/share/nginx/html   # 直接复制本地编译好的 dist
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**注意**：`web/.dockerignore` 中**不能**排除 `dist`，否则构建上下文缺失。

---

## 快速开始（全新服务器）

### 方式一：一键脚本（推荐）

```bash
# 在本地机器上执行，自动完成所有步骤
bash scripts/bootstrap-server.sh <server-ip> \
  --user <ssh-user> \
  --email <letsencrypt@example.com> \
  --domain <你的主域名> \
  --project <部署标识>

# --project 默认 yoo-base：同步到 ~/apps/yoo-base，并写入 STACK_NAME / 镜像名前缀。
# 多应用同机部署时每个项目使用不同的 --project，避免 Traefik 路由冲突。
```

#### `bootstrap-server.sh`：何时会请你补充资料

| 情况 | 行为 |
|------|------|
| 主域名仍是模板占位 `app.example.com`（且未加 `--allow-placeholder-domain`） | **交互终端**：提示输入真实主域名。**非交互**：**直接退出**，并打印须使用 `--domain` 等说明 |
| 仍使用默认 Let's Encrypt 邮箱 `admin@yoo.im` | **交互终端**：询问是否改用其它邮箱（可直接回车保留）。**非交互**：仅打印一条提醒，不阻断 |
| Traefik Dashboard 根域 | 默认由主域名推导（如 `app.example.com` → `example.com`）。若与 DNS 不一致，请显式传 `--base-domain` |

演练/本地可传 `--allow-placeholder-domain`；管道或 CI 务必传真实 `--domain`（及建议 `--email`）。

### 方式二：分步执行

#### 第一步：初始化服务器（以 root 登录执行）

```bash
scp scripts/server-init.sh root@<server-ip>:/tmp/
ssh root@<server-ip>
bash /tmp/server-init.sh aotianlong "$(cat ~/.ssh/id_rsa.pub)"
```

#### 第二步：安装 Traefik（服务器上执行，全局仅一次）

```bash
scp scripts/setup-traefik.sh aotianlong@<server-ip>:/tmp/
ssh aotianlong@<server-ip>
sudo bash /tmp/setup-traefik.sh admin@yoo.im yoo.im admin mypassword
```

#### 第三步：推送代码并配置 .env.production

```bash
rsync -avz --exclude 'node_modules' --exclude '.venv' --exclude '__pycache__' \
  ./ <ssh-user>@<server-ip>:~/apps/<deploy-slug>/

ssh <ssh-user>@<server-ip>
cd ~/apps/<deploy-slug>
cp .env.production.example .env.production
vim .env.production   # 填写实际配置
```

#### 第四步：部署应用

```bash
cd ~/apps/<deploy-slug>
bash scripts/deploy.sh --build
```

---

## .env.production 关键配置

| 变量 | 说明 | 示例 |
|------|------|------|
| `DOMAIN` | 主域名 | `app.example.com` |
| `STACK_NAME` | Docker / Traefik 资源前缀（**同机多栈须唯一**） | `base-yoo`（勿与其它栈重复） |
| `FRONTEND_HOST` | 前端完整 URL | `https://<DOMAIN>` |
| `BACKEND_HOST` | 前端调用的 API 根 URL | `https://api.<DOMAIN>` 或 `https://base-api.example.com` |
| `BACKEND_API_HOST` | Traefik 路由用的 API 主机名（无协议） | `api.<DOMAIN>` 或与 `BACKEND_HOST` 主机一致 |
| `SECRET_KEY` | JWT 密钥（必须修改） | `openssl rand -hex 32` |
| `POSTGRES_PASSWORD` | 数据库密码 | 强密码 |
| `DOCKER_IMAGE_BACKEND` | 后端镜像名 | `<STACK_NAME>-backend` |
| `DOCKER_IMAGE_FRONTEND` | 前端镜像名 | `<STACK_NAME>-frontend` |
| `CLOUDFLARE_DDNS_*` | 可选；配合 `--ddns` 写 IPv6 AAAA | 见「Cloudflare DDNS」 |

**自定义 API 子域**：当 API 不是 `api.<DOMAIN>` 时，须同时设置 `BACKEND_HOST=https://<自定义>` 与 `BACKEND_API_HOST=<自定义主机>`，并在 `YOO_DEPLOY_VITE_API_URL` 中与 `BACKEND_HOST` 对齐。Traefik 规则在 `docker-compose.prod.yml` 中读取 `BACKEND_API_HOST`。

---

## 日常运维命令

**推荐（本地项目根目录）：**

```bash
./yoo deploy --docker -y              # 全量发版（build + rsync + compose）
./yoo deploy --docker --frontend-only -y
./yoo deploy --docker --backend-only -y
./yoo deploy --docker --skip-sync --no-build -y   # 仅远端重启/重建
./yoo deploy --docker restart backend
./yoo deploy pull-env                # 从远端拉取 .env.production 备份
```

**远端手动（SSH 到 `~/apps/<deploy-slug>`）：**

```bash
sudo docker compose -f docker-compose.prod.yml --env-file .env.production ps
sudo docker compose -f docker-compose.prod.yml --env-file .env.production logs -f

docker compose -f docker-compose.prod.yml --env-file .env.production \
  run --rm prestart bash scripts/prestart.sh

docker compose -f docker-compose.prod.yml --env-file .env.production \
  exec backend bash

docker compose -f docker-compose.prod.yml --env-file .env.production down
```

**`./yoo deploy --docker`**：compose 成功后默认会（1）`settings_yaml_loader`，（2）与 `reset_db` 相同：`python -m app.fixtures` 全量加载。仅用发版跳过种子数据：`--skip-fixture-load` 或 `.env.local` 中 `YOO_DEPLOY_LOAD_FIXTURES=0`。

**本机生产栈（`./yoo deploy --docker --local` 或 `./yoo docker start`）**：若使用 `docker-compose.prod.yml` 且本机尚无 Traefik，CLI 会自动在全局目录（默认 `/opt/traefik` 或 `~/.local/share/yoo/traefik`，可用 `YOO_TRAEFIK_DIR` 覆盖）创建 `traefik-public` 网络并启动 Traefik（模板 `docker-compose.traefik.yml`）。Dashboard 凭据可选 `YOO_TRAEFIK_EMAIL` / `YOO_TRAEFIK_USERNAME` / `YOO_TRAEFIK_PASSWORD`；未设密码时会随机生成并打印。

---

## 公网暴露与 DNS

按服务器网络情况**三选一**（不要对同一主机名混用冲突方案）：

### 方案 A：公网 IP + 端口转发（传统）

| 记录 | 类型 | 值 |
|------|------|-----|
| `<DOMAIN>` | A | `<server-ip>` |
| `<BACKEND_API_HOST>` | A | `<server-ip>` |
| Traefik Dashboard 基础域 | A | `<server-ip>` |

Traefik 经 Let's Encrypt 自动签发证书（DNS 须已生效）。

### 方案 B：Cloudflare Tunnel（NAT / 家宽 / 无公网 IP，**推荐**）

Cloudflare 边缘 → **cloudflared** → 本机 `https://127.0.0.1:443`（Traefik），按 `Host` 分流。

**步骤概要**：

1. 服务器已安装 Traefik，本机验证：`curl -skI https://127.0.0.1/ -H 'Host: <DOMAIN>'` 为 200。
2. 使用已有 tunnel 或 `./yoo tunnel create` 创建 tunnel；ingress 增加：
   - `hostname: <DOMAIN>` → `https://127.0.0.1:443`，`httpHostHeader: <DOMAIN>`，`noTLSVerify: true`
   - `hostname: <BACKEND_API_HOST>` → 同上
3. DNS 使用 **CNAME** 指向 `<tunnel-id>.cfargotunnel.com`（Cloudflare 代理开启）。可用：
   ```bash
   cloudflared tunnel route dns <tunnel-id> <DOMAIN> --overwrite-dns
   ```
   或通过 Cloudflare Zero Trust / API 更新 **远端托管** 的 tunnel ingress（本地 `config.yml` 可能被云端配置覆盖）。
4. **不要**再对该域名启用 DDNS AAAA 或手工 A 记录指向错误公网 IP。

TLS 在 Cloudflare 边缘终止；origin 可为 Traefik 自签或 LE（tunnel 侧 `noTLSVerify: true`）。

### 方案 C：Cloudflare DDNS（仅 IPv6 AAAA）

服务器有**稳定公网 IPv6**、且 DNS **不用 Tunnel CNAME** 时：

```bash
./yoo deploy --docker --ddns -y
# 或 ./yoo docker start --ddns
```

在 `.env.production` 配置 `CLOUDFLARE_DDNS_IPV6_DOMAINS`。**与 Tunnel 互斥**：同一主机名若已是 Tunnel CNAME，DDNS 写 AAAA 会失败；Tunnel 场景应停用 DDNS 并注释 `CLOUDFLARE_DDNS_IPV6_DOMAINS`。

### 方案 D：Pangolin（VPS 中继 + Newt，替代 Cloudflare Tunnel）

NAT 场景下，若**自备公网 VPS**且不想用 Cloudflare Tunnel，使用 Pangolin：

- 中继 VPS：`./yoo pangolin install server` → 交互式 `./installer` → `./yoo pangolin server deploy`
- NAT 侧 newt：`./yoo pangolin client deploy --remote`，或 `./yoo docker start --pangolin`
- DNS：**A 记录**指向 VPS 公网 IP（非 Tunnel CNAME）

**与 Tunnel 互斥**：`--tunnel` 与 `--pangolin` 不能同时使用。完整流程、环境变量与排错见 **`pangolin-deploy`** 技能（`.cursor/skills/pangolin-deploy/SKILL.md`）。

---

## Checklist

### 新项目首次部署

- [ ] `./yoo deploy configure` 生成 `.env.production`（含 `BACKEND_API_HOST`、唯一 `STACK_NAME`）
- [ ] 配置 `.env.local`（`YOO_DEPLOY_HOST`、`YOO_DEPLOY_REMOTE_PATH`、`YOO_DEPLOY_VITE_API_URL`）
- [ ] 将 `.env.production` 放到远端项目目录
- [ ] 服务器已装 Docker + Traefik（`setup-traefik.sh` 或 `./yoo deploy --docker --local` 自动拉起）
- [ ] 选定公网方案：**Tunnel（NAT）** 或 **A 记录（公网 IP）** 或 **--ddns（仅 IPv6）**，勿混用
- [ ] 检查 `web/Dockerfile`：`ARG VITE_API_URL`、`COPY nginx.conf`
- [ ] 检查 `backend/Dockerfile`：COPY 所有自定义模块；基础镜像 **Python 3.12**（与 `pyproject.toml` 一致）
- [ ] `alembic heads` 无分叉；i18n YAML 含冒号值加引号
- [ ] `./yoo deploy --docker -y`；浏览器验证 `https://<DOMAIN>` 与 `https://<BACKEND_API_HOST>/docs`

### 生产发版

- [ ] 本地迁移与依赖、前端构建前提已满足
- [ ] `.env.production` / `.env.local` 已按需更新（含 `BACKEND_API_HOST`、`YOO_DEPLOY_VITE_API_URL`）
- [ ] `./yoo deploy --docker -y` 成功，`prestart` 无报错
- [ ] 前端与 API 域名抽查通过（Tunnel 栈确认 CNAME 未被 DDNS 覆盖）

---

## 注意事项

1. **Traefik 全局唯一**：一台服务器只部署一个 Traefik，所有应用共用
2. **STACK_NAME 必须唯一**：重复会导致 Traefik router 名冲突、404
3. **PostgreSQL 独立**：每个应用有自己的 db/redis 容器，数据隔离
4. **traefik-public 网络**：所有需要对外暴露的服务必须连接此网络
5. **TLS**：公网 IP 方案靠 Traefik LE；Tunnel 方案靠 Cloudflare 边缘证书
6. **Worker 数量**：生产环境 backend 默认 `BACKEND_WORKERS=1`，小内存机器勿盲目加大
7. **Tunnel vs DDNS**：Tunnel 用 CNAME；DDNS 写 AAAA——同一主机名只能选一种
8. **fixtures**：`./yoo deploy --docker` 首次会全量加载 fixtures；重复部署自动跳过，可用 `--skip-fixture-load` 关闭

---

## Worker 数量配置

`backend/Dockerfile` 的 `CMD` 使用 `fastapi run --workers ${BACKEND_WORKERS:-1}`（未设置环境变量时默认为 **1**）。每个 worker 是独立 Python 进程，会各自完整加载应用及所有依赖，在内存有限的服务器上多开会造成浪费。

FastAPI 本身是异步框架（async/await），**1 个 worker 就能高效处理并发请求**，多 worker 只在有大量 CPU 密集型同步操作时才有价值。

**调大 worker**：在 `.env.production` 或 compose 的 `backend.environment` 中设置 `BACKEND_WORKERS=4`。

| Workers | 内存占用（3.8GB 服务器实测） |
|---------|------------------------------|
| 4 | ~1.3 GB |
| 1 | ~280 MB |

**选取规则**：workers 数 = min(CPU 核数, 可用内存 / 单进程内存)，4GB 以下服务器始终用 `--workers 1`。

> 不要在 Dockerfile 的 `CMD` 中直接改，应在 `docker-compose.prod.yml` 中覆盖，这样不需要重新构建镜像。

---

## 踩坑记录（必读）

### 坑1：Traefik 3.x 与 Docker daemon API 版本不兼容

**现象**：前端与 API 域名返回 `404 page not found`，没有 HTTPS，Traefik 日志报：
```
Error response from daemon: client version 1.24 is too old. Minimum supported API version is 1.40
```

**原因**：Traefik 容器内置的 Docker 客户端在做版本协商时发起 API 1.24 的请求，而 Docker daemon 要求最低 1.40，导致 Traefik 完全无法发现任何 Docker 服务，路由全部失效。升级 Docker daemon 版本无效（Docker 已经是最新版）；给 Traefik 设置 `DOCKER_API_VERSION=1.40` 环境变量也无效。

**正确解法**：使用 `tecnativa/docker-socket-proxy` 作为 Docker socket 代理，Traefik 通过 TCP 连接代理而非直接挂载 socket：

```yaml
services:
  socket-proxy:
    image: tecnativa/docker-socket-proxy
    restart: always
    environment:
      CONTAINERS: 1
      SERVICES: 1
      NETWORKS: 1
      TASKS: 1
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - socket-proxy

  traefik:
    image: traefik:v2.11   # 或 v3.x，都可配合代理使用
    command:
      - --providers.docker
      - --providers.docker.endpoint=tcp://socket-proxy:2375  # 关键：走代理
      - --providers.docker.exposedbydefault=false
      # ...其他配置
    networks:
      - traefik-public
      - socket-proxy   # 必须加入此网络

networks:
  traefik-public:
    external: true
  socket-proxy:
    internal: true   # 内部网络，不对外暴露
```

### 坑2：`traefik-public-certificates` volume 必须手动创建

**现象**：`docker compose up` 报 `external volume "traefik-public-certificates" not found`

**原因**：`docker-compose.yml` 中声明为 `external: true` 的 volume 不会自动创建。

**解决**：部署前手动创建：
```bash
sudo docker volume create traefik-public-certificates
```

### 坑3：后端容器因缺少本地模块启动失败

**现象**：`<stack-name>-backend-1`（Compose 项目前缀随 `STACK_NAME`）反复重启，日志报：
```
ModuleNotFoundError: No module named 'lib'
ModuleNotFoundError: No module named 'bots'
```

**原因**：`backend/Dockerfile` 的 `COPY` 指令只复制了 `app/`，没有包含项目特有的 `lib/` 和 `bots/` 目录。

**解决**：在 `backend/Dockerfile` 中添加：
```dockerfile
COPY ./lib /app/lib
COPY ./bots /app/bots
```

**教训**：每次新项目部署后，检查后端容器日志，确认所有自定义模块都被正确打包进镜像。

### 坑4：`web/.dockerignore` 排除了 `dist` 目录

**现象**：本地已编译好 `dist/`，`rsync` 到服务器，`docker build` 时报 `"/dist": not found`。

**原因**：`web/.dockerignore` 默认忽略了 `dist`，导致构建上下文中没有该目录。

**解决**：检查并从 `web/.dockerignore` 中移除 `dist` 行。

### 坑5：`yoo fixture load` 只能连本地数据库

**原因**：宿主机执行 `./yoo fixture …` 时读取本地 `.env`，连接的是本地 PostgreSQL，无法直接写入远端容器内的数据库。

**正确做法**：在后端容器工作目录执行官方入口（加载顺序见仓库 `backend/app/fixtures/manifest.py`）：

```bash
ssh user@server "sudo docker exec <backend容器名> python -m app.fixtures"
```

仅需补齐 RBAC / 首超管关联且**不清空表**时，在宿主机（仓库根目录、已配置 compose）可用：

```bash
./yoo fixture migrate --compose
```

或在与镜像一致的环境里执行：`python -m app.fixtures`（全量）或 `./yoo fixture migrate`（仅核心表）。

**注意**：已通过 `python -m app.fixtures` 等方式写入 region、user(superuser)、setting 等数据后，再次执行全量 `./yoo fixture load` 可能触发唯一键冲突，属于正常现象；按需跳过或使用 `-a` / `-t`。

### 坑6：前端 Dockerfile 缺少 ARG VITE_API_URL 声明

**现象**：前端构建成功，但 API 请求全部打到错误地址（未替换环境变量）。

**原因**：`docker-compose.prod.yml` 通过 build args 传入 `VITE_API_URL=https://api.${DOMAIN}`，但 `web/Dockerfile` 没有声明 `ARG`，导致变量在构建时不生效，Vite 使用默认值。

**解决**：在 `web/Dockerfile` 的 build-stage 中添加：
```dockerfile
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
```
必须在 `COPY . .` 和 `RUN pnpm build` 之前声明。

### 坑7：YAML i18n 文件中含冒号的字符串导致构建失败

**现象**：前端 `pnpm build` 失败，报错：
```
[vite-plugin-pwa:build] locales/en/common.yml: Nested mappings are not allowed in compact mappings
```

**原因**：YAML 中值包含冒号（`:`）且未加引号，被解析器误认为嵌套 mapping：
```yaml
# 错误
reportEntity: Report: {title}
# 正确
reportEntity: "Report: {title}"
```

**解决**：所有含冒号的字符串值必须用双引号包裹。

**定位**：错误信息中包含出错文件路径和行号，直接定位修复。

### 坑8：Alembic 多个 head 导致 prestart 失败

**现象**：`prestart` 容器 exit 255，日志报：
```
FAILED: Multiple head revisions are present for given argument 'head'
```

**原因**：多个功能分支各自创建了迁移文件，产生分叉，`alembic upgrade head` 不知道升级哪个。

**解决**：在本地合并后重新同步、重建后端镜像：
```bash
cd backend
alembic heads          # 查看当前所有 heads
alembic merge heads -m "merge_multiple_heads"   # 生成合并迁移
# 然后同步 app/alembic/versions/ 到服务器并重建后端镜像
```

### 坑9：后端依赖未在 pyproject.toml 中声明

**现象**：后端容器启动失败，日志报：
```
ModuleNotFoundError: No module named 'bleach'
```

**原因**：代码中 `import bleach` 但 `pyproject.toml` 未声明该依赖，本地开发时可能通过其他方式安装了，但 Docker 构建时从零安装只读 pyproject.toml。

**解决**：
```bash
cd backend
uv add bleach    # 自动更新 pyproject.toml 和 uv.lock
# 同步 pyproject.toml 和 uv.lock 到服务器，重新构建后端镜像
```

**教训**：每次 `import` 新包后立即 `uv add` 确保声明到 pyproject.toml，而不是依赖 `pip install`。

### 坑10：修改管理员密码需在容器内执行

**原因**：`yoo admin edit` 同样只连本地数据库。

**正确做法**：
```bash
sudo docker exec <backend容器名> python -c "
import sys
sys.path.insert(0, '/app')
from sqlmodel import Session, select
from app.core.db import engine
from app.models import User
from app.core.security import get_password_hash

with Session(engine) as session:
    user = session.exec(select(User).where(User.email == 'admin@yoo.im')).first()
    user.hashed_password = get_password_hash('新密码')
    session.add(user)
    session.commit()
    print('✅ 密码修改成功')
"
```

先查看超级管理员账号：
```bash
sudo docker exec <backend容器名> python -c "
import sys; sys.path.insert(0, '/app')
from sqlmodel import Session, select
from app.core.db import engine
from app.models import User
with Session(engine) as s:
    for u in s.exec(select(User).where(User.is_superuser==True)).all():
        print(u.email, u.full_name)
"
```

### 坑11：NAT 下 A 记录无效 / Tunnel 与 DDNS 冲突

**现象 A**：DNS 已指向公网 IP，但 `https://<DOMAIN>` TLS 失败或 404；本机 `curl -skI https://127.0.0.1/ -H 'Host: <DOMAIN>'` 却正常。

**原因**：服务器在 NAT 后，公网 IP 并非本机 Traefik；或 `STACK_NAME` 与其它栈重复导致 Traefik router 冲突。

**解决**：
- NAT 场景改用 **Cloudflare Tunnel** + CNAME（见「公网暴露与 DNS」方案 B）
- 同机多栈为每个项目设置唯一 `STACK_NAME` 后 `--force-recreate`

**现象 B**：启用 `--ddns` 后日志报 `A CNAME record with that host already exists`。

**原因**：Tunnel 已为该域名创建 CNAME，DDNS 无法再写 AAAA。

**解决**：Tunnel 场景注释 `CLOUDFLARE_DDNS_IPV6_DOMAINS` 并停止 ddns 容器；二选一，勿混用。

### 坑12：`.env` 开发变量覆盖 `.env.production`（`--local` / `./yoo deploy`）

**现象**：`.env.production` 已设 `STACK_NAME=yoo-official`、`DOMAIN=www.example.com`，但容器 Traefik label 仍为 `yoo-base-*`；或 `curl -H 'Host: api.example.com'` 经 Traefik 502，backend 实际监听 8001。

**原因**：`scripts/yoo/main.py` 先 `load_dotenv(.env)` 再 `load_dotenv(.env.local)`；`./yoo deploy --docker --local` 子进程继承 Shell 中的 `STACK_NAME` / `BACKEND_PORT`，优先于 `docker compose --env-file .env.production`。

**解决**：
- 在 **`.env.local`** 写入与生产一致的 `STACK_NAME`、`BACKEND_PORT=8000`（见上文「同机开发 + 生产」）
- 在 **`.env.production`** 增加 `BACKEND_PORT=8000`
- 验证：`docker inspect <stack>-frontend-1` 的 label 应为 `yoo-official-frontend-https` 而非 `yoo-base-*`
- 发版后勿单独 `--force-recreate db`（见坑13）

### 坑13：生产栈 `--force-recreate db` 导致 PostgreSQL 认证失败

**现象**：`prestart` / `backend` 报 `password authentication failed for user "<prod_user>"` 或 `role does not exist`；仅重建 db 容器、不删卷时也可能出现。

**原因**：Postgres 卷仅在首次初始化时写入用户/密码；反复 recreate db 或卷与当前 `POSTGRES_*` 不一致时会陷入半初始化状态。

**解决**：
- 调整 Traefik/backend 时用 `--no-deps --force-recreate frontend backend`，**不要** recreate `db`
- 若库已损坏且可接受清空：`docker compose … down -v` 后完整 `./yoo deploy --docker --local -y`
- 有数据时先 `pg_dump` 再重建
