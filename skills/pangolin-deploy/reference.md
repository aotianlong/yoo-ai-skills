# Pangolin 部署参考

## 相关文件

```
scripts/yoo/commands/pangolin.py   # ./yoo pangolin CLI
scripts/yoo/utils/pangolin.py      # 配置、SSH、systemd/LaunchAgent、Docker env
docker-compose.prod.newt.yml       # newt 容器叠加（host 网络）
.pangolin/meta.json                # 元数据（server、endpoint、newt 凭证）
.pangolin/newt.json                # newt 运行时配置（gitignore）
```

---

## CLI 命令树

```
./yoo pangolin
├── configure          # 交互式生成 .pangolin/，写入 .env.local
├── show               # 配置摘要
├── help               # 内置说明
├── install
│   ├── server         # VPS 下载 Pangolin installer
│   └── client [--remote] [-f]
├── server
│   ├── deploy         # docker compose up -d
│   ├── start|stop|restart|status
└── client
    ├── deploy [--remote]   # 推送 newt.json + systemd/LaunchAgent
    ├── run                 # 前台调试
    └── start|stop|restart|status [--remote]
```

---

## configure 参数

| 参数 | 说明 |
|------|------|
| `--server-host` | 中继 VPS 公网地址 |
| `--server-user` | SSH 用户 |
| `--endpoint` | 控制台 URL，如 `https://pangolin.example.com` |
| `--newt-id` / `--newt-secret` | Newt Site 凭证 |
| `--install-dir` | VPS 安装目录，默认 `/opt/pangolin` |
| `-y` / `--yes` | 非交互，使用已有默认值 |

未传 `--newt-id` 时可先留空，控制台创建 Site 后再执行一次 `configure`。

---

## newt 部署方式对比

| 方式 | 命令 | 配置路径 | 适用 |
|------|------|----------|------|
| 远端 systemd | `client deploy --remote` | `/etc/pangolin/newt.json` | NAT 生产机（`YOO_DEPLOY_HOST`） |
| 本机 systemd | `client deploy` | `/etc/pangolin/newt.json` | Linux 本机 |
| 本机 LaunchAgent | `client deploy` | `.pangolin/newt.json` | macOS 本机 |
| Docker 容器 | `./yoo docker start --pangolin` | bind mount `.pangolin/newt.json` | 与 prod compose 同机 |

Docker 方式使用 `fosrl/newt:latest`，`network_mode: host`，环境变量 `CONFIG_FILE=/etc/pangolin/newt.json`。

---

## Pangolin 控制台 Resource 示例

假设 `.env.production`：

```
DOMAIN=app.example.com
BACKEND_API_HOST=api.example.com
```

| Resource 主机名 | 目标 | 说明 |
|---------------|------|------|
| `app.example.com` | `127.0.0.1:443` | 前端（Traefik 按 Host 路由） |
| `api.example.com` | `127.0.0.1:443` | API（`BACKEND_API_HOST`） |

本地 Traefik 须已监听 `127.0.0.1:443` 且路由与 `docker-compose.prod.yml` 一致。

---

## 与 Cloudflare Tunnel 对比

| | Cloudflare Tunnel | Pangolin |
|---|-------------------|----------|
| 公网入口 | Cloudflare 边缘 | 自备 VPS |
| DNS | CNAME → `*.cfargotunnel.com` | A → VPS IP |
| NAT 客户端 | cloudflared 容器 | newt（systemd 或容器） |
| CLI | `./yoo tunnel …` / `--tunnel` | `./yoo pangolin …` / `--pangolin` |
| TLS | Cloudflare 边缘 | Pangolin/Traefik + LE |
| 互斥 | 与 `--pangolin` 不能同开 | 与 `--tunnel` 不能同开 |

---

## 排错

### `未配置 YOO_PANGOLIN_SERVER_HOST`

执行 `./yoo pangolin configure`，或于 `.env.local` 手动设置。

### `未找到 docker-compose.yml`（server deploy）

VPS 上尚未运行交互式 `./installer`。顺序：`install server` → SSH 运行 `sudo ./installer` → `server deploy`。

### `未配置 Newt ID/Secret`

在 Pangolin 控制台创建 Site 后重新 `./yoo pangolin configure`。

### newt 无法连接

1. VPS 防火墙是否放行 UDP 51820
2. `./yoo pangolin server status` 容器是否正常
3. `endpoint` 是否与控制台 URL 一致（含 `https://`）
4. 远端：`./yoo pangolin client status --remote` 或 `journalctl -u pangolin-newt.service`
5. **凭证为占位符**：`/etc/pangolin/newt.json` 若为 `test-id` / `test-secret`，日志报 `No newt found with that newtId`；从 Pangolin 控制台或已运行的 newt 容器环境变量复制真实 ID/Secret，执行 `./yoo pangolin configure` 后 `sudo cp .pangolin/newt.json /etc/pangolin/newt.json && sudo systemctl restart pangolin-newt`

### DNS 从 Tunnel 切到 Pangolin

```bash
CLOUDFLARE_API_TOKEN=... ./yoo pangolin dns point-vps \
  --hostname www.example.com --hostname api.example.com \
  --vps-ip <VPS_IP> --no-tunnel-ingress --dns-only
```

Token 可来自 `~/.local/share/yoo/traefik/.env` 的 `CF_DNS_API_TOKEN`（需 Zone DNS Edit）。`--dns-only` 为灰云；橙云用默认 `--proxied`。

### 域名 404 / TLS 失败

1. DNS A 记录是否指向 VPS（勿与 Tunnel CNAME 混用）
2. Pangolin 控制台 Resource 是否指向 `127.0.0.1:443`
3. 本地 Traefik：`curl -skI https://127.0.0.1/ -H 'Host: <DOMAIN>'` 应 200
4. `STACK_NAME` 是否与其它栈冲突（见 deploy 技能坑11）
5. **Traefik label 仍是 dev 栈名**（如 `yoo-base-*` 而非 `yoo-official-*`）：见 deploy 技能坑12，检查 `.env.local`
6. **API 502 但 frontend 200**：backend 监听端口与 Traefik `loadbalancer.server.port=8000` 不一致，查 `BACKEND_PORT` 是否被 `.env` 设为 8001

### yoo.im / pig.rocks 资源

在 VPS 上为 `www.yoo.im`、`api.yoo.im`、`yoo.im` 插入 Pangolin DB 资源（目标 `127.0.0.1:443`）可参考 `~/apps/pr-docker/poste/setup-pangolin-official.sh`。DNS 用 **A → VPS IP**，勿 CNAME 到 `pig.rocks`（否则 ACME / 边缘路由异常）。

### Docker newt 容器

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.prod.newt.yml \
  --env-file .env.production logs -f newt
```

需环境变量 `PANGOLIN_NEWT_CONFIG_FILE`（`docker start --pangolin` 自动注入）。

---

## dry-run

多数子命令支持 `--dry-run`，仅打印远端 SSH 脚本，不实际执行：

```bash
./yoo pangolin install server --dry-run
./yoo pangolin client deploy --remote --dry-run
```
