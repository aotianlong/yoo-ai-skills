---
name: pangolin-deploy
description: >-
  yoo-base Pangolin 内网穿透部署：VPS 中继（Pangolin + Gerbil + Traefik）+ NAT 侧 Newt 客户端，
  替代 Cloudflare Tunnel。含 ./yoo pangolin configure/install/server/client、
  ./yoo docker start --pangolin 与 docker-compose.prod.newt.yml。
  在用户说「Pangolin 部署」「Newt 内网穿透」「替代 Cloudflare Tunnel」「VPS 中继穿透」时使用。
---

# Pangolin 内网穿透部署

**说明**：Pangolin 需自备**有公网 IP 的中继 VPS**。NAT 侧（家宽/内网）运行 **newt**，经 WireGuard 隧道连接 VPS 上的 Pangolin，将流量转发到本地 Traefik（`127.0.0.1:443`）。

与 `./yoo deploy` 配合：应用栈仍用 `docker-compose.prod.yml` + Traefik；公网暴露走 Pangolin 而非 Cloudflare Tunnel。

---

## 何时使用

- NAT / 无公网 IP，但**不想用 Cloudflare Tunnel**
- 需要 Pangolin 内置的零信任访问控制
- 已有 VPS，希望 TLS 由 Pangolin/Traefik + Let's Encrypt 处理

**勿与 Cloudflare Tunnel 混用**：`--tunnel` 与 `--pangolin` 互斥；同一域名勿同时配 Tunnel CNAME 与 Pangolin A 记录。

---

## 拓扑

```
Internet → DNS A 记录 → 中继 VPS（Pangolin + Gerbil + Traefik）
                              ↑ WireGuard (UDP 51820)
                         NAT 侧 newt → 127.0.0.1:443（本地 Traefik）
                              ↑
                    yoo-base 应用栈（frontend / backend / db …）
```

---

## 快速开始

### 1. 生成本地配置

```bash
./yoo deploy configure          # 若尚无 .env.production（DOMAIN、STACK_NAME 等）
./yoo pangolin configure        # 写入 .pangolin/ 与 .env.local 中的 YOO_PANGOLIN_*
```

`.pangolin/` 含 `newt.json`（含 secret），已在 `.gitignore`，勿提交。

### 2. 中继 VPS：安装并启动 Pangolin server

```bash
./yoo pangolin install server
ssh <user>@<vps> 'cd /opt/pangolin && sudo ./installer'   # 交互式，生成 docker-compose.yml
./yoo pangolin server deploy
./yoo pangolin server status
```

VPS 防火墙放行：**TCP 80、443** 与 **UDP 51820**（WireGuard）。

### 3. 控制台：创建 Newt Site

在 Pangolin 控制台完成初始化 → 创建 **Newt Site** → 复制 **ID / Secret**：

```bash
./yoo pangolin configure        # 填入 newt-id / newt-secret
./yoo pangolin show
```

### 4. NAT 侧：部署 newt client

**方式 A — systemd / LaunchAgent（推荐生产机）**

```bash
./yoo pangolin install client --remote    # 在 YOO_DEPLOY_HOST 安装二进制
./yoo pangolin client deploy --remote     # 推送配置并 systemd 自启
./yoo pangolin client status --remote
```

**方式 B — Docker 容器（与本机生产栈联用）**

```bash
./yoo pangolin configure                # 确保 .pangolin/newt.json 就绪
./yoo docker start --pangolin           # 叠加 docker-compose.prod.newt.yml
```

**方式 C — 本机调试**

```bash
./yoo pangolin install client
./yoo pangolin client run               # 前台运行
```

### 5. 控制台：添加 Resource + DNS

在 Pangolin 控制台为 `<DOMAIN>`、`<BACKEND_API_HOST>` 添加 Resource，目标 **`127.0.0.1:443`**（Host 由 Traefik 分流）。

DNS：**A 记录**指向中继 VPS 公网 IP（非 Cloudflare Tunnel CNAME）。

### 6. 部署应用

```bash
# .env.local 配置 YOO_DEPLOY_* 后
./yoo deploy --docker -y
```

健康检查：`https://<DOMAIN>`、`https://<BACKEND_API_HOST>/docs`。

---

## 环境变量（`.env.local`）

| 变量 | 说明 |
|------|------|
| `YOO_PANGOLIN_SERVER_HOST` | 中继 VPS 地址（必填） |
| `YOO_PANGOLIN_SERVER_USER` | SSH 用户，默认 `root` |
| `YOO_PANGOLIN_SERVER_PORT` | SSH 端口，默认 `22` |
| `YOO_PANGOLIN_SERVER_IDENTITY_FILE` | SSH 私钥 |
| `YOO_PANGOLIN_ENDPOINT` | Pangolin 控制台 URL |
| `YOO_PANGOLIN_INSTALL_DIR` | VPS 安装目录，默认 `/opt/pangolin` |
| `YOO_DEPLOY_*` | `client deploy --remote` 与 `./yoo deploy --docker` 共用 |

---

## 常用命令

```bash
./yoo pangolin help
./yoo pangolin show
./yoo pangolin server start|stop|restart|status
./yoo pangolin client start|stop|restart|status [--remote]
./yoo docker start --pangolin [--skip-web-build]
```

---

## 与 deploy / Tunnel / DDNS 的关系

| 方案 | CLI | 适用 |
|------|-----|------|
| Cloudflare Tunnel | `./yoo docker start --tunnel` | NAT，无需 VPS |
| **Pangolin** | `./yoo pangolin …` + `--pangolin` | NAT，自备 VPS，零信任 |
| 公网 IP + A 记录 | 无额外 CLI | 有公网 IP |
| Cloudflare DDNS | `./yoo deploy --docker --ddns` | 稳定 IPv6，不用 Tunnel |

完整发版、Traefik、迁移见 **`deploy`** 技能；Pangolin 命令细节与排错见 [reference.md](reference.md)。

---

## NAT 侧本机发版（部署机 = Newt 所在机器）

当应用与 Traefik 跑在 **NAT 内网机**（非 SSH 到公网域名）时：

```bash
./yoo deploy configure                    # 或手写 .env.production（www + api 子域）
./yoo pangolin configure                  # VPS、endpoint、Newt 凭证 → .pangolin/ + .env.local
# 若已有 systemd pangolin-newt 且凭证正确，可不再 --pangolin 叠 Docker newt
./yoo pangolin dns point-vps \            # Tunnel CNAME → VPS A 记录（需 Cloudflare Token）
  --hostname www.example.com --hostname api.example.com \
  --vps-ip <VPS_IP> --no-tunnel-ingress --dns-only
./yoo deploy --docker --local -y
```

要点：
- 使用 **`--local`**，勿把 `YOO_DEPLOY_HOST` 设为仅内网解析的域名（如 Clash fake-ip）
- **systemd newt** 与 **`--pangolin` Docker newt** 二选一；本机已有 `pangolin-newt.service` 且 `Websocket connected` 时，发版不必再加 `--pangolin`
- Pangolin 控制台 / VPS DB 须为 `DOMAIN`、`BACKEND_API_HOST` 配置 Resource → `127.0.0.1:443`
- 发版前 `cd backend && alembic heads` 仅一个 head（多 head 先 merge）
- **`.env.local`** 中覆盖生产 `STACK_NAME`、`BACKEND_PORT=8000`（见 **deploy** 技能坑12）

yoo.im 实示例：`setup-pangolin-official.sh`（pig.rocks 上添加 www/api/yoo.im Resource）、VPS `45.33.114.37`、DNS **A 记录**（禁止 CNAME 到 pig.rocks）。

---

## Checklist

### 首次 Pangolin 穿透

- [ ] `./yoo deploy configure` 已生成 `.env.production`（`DOMAIN`、`BACKEND_API_HOST`、`STACK_NAME`）
- [ ] **`.env.local` 已覆盖** `STACK_NAME`、`BACKEND_PORT=8000`（同机 dev `.env` 勿污染生产，见 deploy 坑12）
- [ ] `./yoo pangolin configure` 已写入 `.pangolin/` 与 `YOO_PANGOLIN_*`
- [ ] VPS 已运行 `./installer` 且 `./yoo pangolin server deploy` 成功
- [ ] 控制台已创建 Newt Site，凭证已写入 `./yoo pangolin configure`
- [ ] NAT 侧 newt 已运行（`client deploy --remote` 或 `docker start --pangolin`）
- [ ] 控制台 Resource 指向 `127.0.0.1:443`；DNS A 记录指向 VPS
- [ ] `./yoo deploy --docker -y` 后前后端域名可访问

### 日常发版

- [ ] 应用发版仍用 `./yoo deploy --docker`（Pangolin 层通常无需重建）
- [ ] 若更换 Newt 凭证：重新 `configure` → `client deploy --remote` 或重启 newt 容器
