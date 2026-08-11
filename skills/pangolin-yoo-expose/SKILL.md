---
name: pangolin-yoo-expose
description: >-
  Expose a local service on *.yoo.im via Pangolin (pig.rocks) + Newt + local Traefik,
  including DNS, TLS, and troubleshooting. Use when adding yoo.im subdomains through
  Pangolin, fixing certificate errors (TRAEFIK DEFAULT CERT), or wiring Docker services
  to traefik-public.
---

# Pangolin 暴露 yoo.im 服务

## 架构（三层 TLS/路由）

```
用户 → dify.yoo.im (A → 45.33.114.37)
     → Pangolin 边缘 Traefik（pig.rocks，终止 TLS，LE 证书）
     → WireGuard 隧道 internalPort（如 54013）
     → 本机 Newt → 127.0.0.1:443
     → 本机 Traefik → 服务 nginx/frontend
```

- **Pangolin 服务器**：SSH 别名 `pig.rocks`，配置在 `/opt/pangolin/`；用 `ssh -G pig.rocks` 确认实际用户，不要假定 `root`
- **本机 Newt**：`~/.config/pangolin/newt.json`，可能是系统级或用户级 `pangolin-newt.service`
- **本机 Traefik**：`~/.local/share/yoo/traefik/`，网络 `traefik-public`
- **Ubuntu siteId**：从 Pangolin DB 的 `sites` 表动态查询在线站点，禁止硬编码

## 完成定义（强制）

只有以下检查全部通过才算公网部署完成。不能用本机 `127.0.0.1` 返回 200 推断公网已可用。

1. 后端容器健康，本机 Traefik 按 Host 路由返回预期状态。
2. Pangolin 动态配置包含该域名及目标 service。
3. 公共 DNS 是预期 A 记录，且没有错误 CNAME。
4. 直连边缘 IP（`--resolve` 到 `45.33.114.37`）不是 404。
5. SNI 证书包含目标域名，签发者有效，绝不是 `TRAEFIK DEFAULT CERT`。
6. 不带 `--resolve` 的普通公网请求返回预期结果。

## 新增子域 checklist

```
- [ ] 1. 确认 SSH 身份、sudo 权限和实际 Newt unit
- [ ] 2. Pangolin 资源（动态查询 siteId，写 DB 前备份）
- [ ] 3. 本机 Traefik 路由与后端健康
- [ ] 4. 服务公网 URL（.env）
- [ ] 5. DNS（A 记录，禁止 CNAME 到 pig.rocks）
- [ ] 6. 重启 Newt + Pangolin/Gerbil
- [ ] 7. 逐层验证路由、HTTP 和公网证书
```

### 0. 预检实际运行环境

```bash
ssh -G pig.rocks | grep -E '^(hostname|user) '
ssh pig.rocks 'sudo -n true && echo sudo-ok'
systemctl is-active pangolin-newt.service || true
systemctl --user is-active pangolin-newt.service || true
```

以 active 的 unit 为准。系统级 unit active 时使用 `sudo systemctl`；只有用户级 unit active 时才使用 `systemctl --user`。用户级显示 inactive 不代表系统级 Newt 没运行。

### 1. Pangolin 资源

在 pig.rocks 上向 `resources` + `targets` 插入记录，或使用 `scripts/setup-pangolin-resource.sh`。

| 字段 | 典型值 |
|------|--------|
| `siteId` | 查询 `sites` 表所得的在线 `ubuntu` 站点 ID |
| `fullDomain` | `dify.yoo.im` |
| `internalPort` | 下一个空闲端口（查现有：`54001`–`54013` 等） |
| `target.ip` | `127.0.0.1` |
| `target.port` | `443` |
| `target.method` | `https` |
| `ssl` / `enabled` | `1` |

分配 internalPort：

```bash
ssh pig.rocks 'sudo sqlite3 /opt/pangolin/config/db/db.sqlite \
  "SELECT siteId,name,online FROM sites ORDER BY siteId; \
   SELECT r.fullDomain,t.siteId,t.internalPort FROM resources r JOIN targets t ON r.resourceId=t.resourceId WHERE r.enabled=1 ORDER BY t.internalPort;"'
```

选择 `name='ubuntu' AND online=1` 的站点；不得沿用旧文档里的固定 ID。写库前备份 SQLite，并检查域名和 internalPort 均未占用。优先使用 `scripts/setup-pangolin-resource.sh`。

重启 Pangolin 使边缘 Traefik 拉取新路由：

```bash
ssh pig.rocks 'cd /opt/pangolin && sudo docker compose restart gerbil pangolin'
```

确认动态配置已包含新域名：

```bash
ssh pig.rocks 'sudo docker exec traefik wget -qO- http://pangolin:3001/api/v1/traefik-config' \
  | grep -F 'Host(`你的域名`)'
```

### 2. 本机 Traefik 路由

为服务添加 `docker-compose.traefik.yml` overlay（**不要**覆盖掉原有 `default` 网络）：

```yaml
services:
  nginx:  # 或 frontend
    networks:
      - default
      - traefik-public
    labels:
      - traefik.enable=true
      - traefik.docker.network=traefik-public
      - traefik.http.services.SERVICE_NAME.loadbalancer.server.port=80
      - traefik.http.routers.SERVICE-http.rule=Host(`sub.yoo.im`)
      - traefik.http.routers.SERVICE-http.entrypoints=http
      - traefik.http.routers.SERVICE-http.middlewares=https-redirect
      - traefik.http.routers.SERVICE-http.service=SERVICE_NAME
      - traefik.http.routers.SERVICE-https.rule=Host(`sub.yoo.im`)
      - traefik.http.routers.SERVICE-https.entrypoints=https
      - traefik.http.routers.SERVICE-https.tls=true
      - traefik.http.routers.SERVICE-https.service=SERVICE_NAME

networks:
  traefik-public:
    external: true
```

部署：

```bash
docker compose -f docker-compose.yaml -f docker-compose.traefik.yml up -d
```

### 3. 服务公网 URL

按服务类型更新 `.env` 中的 URL（示例 Dify）：

```env
CONSOLE_API_URL=https://sub.yoo.im
CONSOLE_WEB_URL=https://sub.yoo.im
SERVICE_API_URL=https://sub.yoo.im
APP_API_URL=https://sub.yoo.im
APP_WEB_URL=https://sub.yoo.im
FILES_URL=https://sub.yoo.im
NEXT_PUBLIC_SOCKET_URL=wss://sub.yoo.im
ENDPOINT_URL_TEMPLATE=https://sub.yoo.im/e/{hook_id}
```

### 4. DNS（关键）

**必须用 A 记录指向 `45.33.114.37`，禁止 CNAME 到 `pig.rocks`。**

CNAME 到 `pig.rocks` 会导致 Cloudflare DNS-01 去找 `pig.rocks` zone，而 Traefik 的 `CF_DNS_API_TOKEN` 通常只有 `yoo.im` 权限，ACME 失败后会回退到 `TRAEFIK DEFAULT CERT`。

```bash
# 正确
dify.yoo.im  A  45.33.114.37

# 错误
dify.yoo.im  CNAME  pig.rocks
```

用 Cloudflare API 或面板 upsert A 记录后，用 Google DNS 验证：

```bash
curl -s "https://dns.google/resolve?name=sub.yoo.im&type=1" | python3 -m json.tool
# 应只有 type 1 → 45.33.114.37，无 CNAME
```

### 5. 重启 Newt

```bash
# 系统级（本机常见）
sudo systemctl restart pangolin-newt.service
systemctl is-active pangolin-newt.service

# 仅当预检确认是用户级时使用
systemctl --user restart pangolin-newt.service
```

### 6. 分层验证

```bash
# 本机路由：只证明本地成功
curl -skI --resolve sub.yoo.im:443:127.0.0.1 https://sub.yoo.im/

# 公共 DNS：本机 DNS 可能被 Clash fake-ip 污染
curl -s 'https://dns.google/resolve?name=sub.yoo.im&type=1' | python3 -m json.tool

# 绕过 DNS，直连 Pangolin 边缘；应为预期状态而非 404
curl -skI --resolve sub.yoo.im:443:45.33.114.37 https://sub.yoo.im/

# 检查边缘实际提供的证书
echo | openssl s_client -connect 45.33.114.37:443 -servername sub.yoo.im 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates

# 应看到 CN=sub.yoo.im, issuer=Let's Encrypt
# 若 subject=CN=TRAEFIK DEFAULT CERT → 见下方排障

# 最终普通公网请求
curl -sSIL https://sub.yoo.im/ | head
```

## 404 定位矩阵

| 结果 | 判断 | 下一步 |
|------|------|--------|
| 本机 Host 路由 200，公网 404 | Pangolin resource/target 缺失或未加载 | 查 DB 和 `traefik-config`，重启 Pangolin/Gerbil 与 Newt |
| 直连边缘 200，普通公网异常 | DNS、缓存或代理问题 | 用 Google DoH 查 A/CNAME，不信任 Clash fake-ip 结果 |
| 公网 HTTP 200，但浏览器报证书错误 | 边缘提供默认或错误证书 | 按下节修复；这不算部署成功 |
| 直连边缘也 404 | Pangolin 边缘没有匹配 Host 的 router | 确认 resource 启用、siteId 正确且动态配置已刷新 |

## 证书排障

| 现象 | 原因 | 处理 |
|------|------|------|
| `TRAEFIK DEFAULT CERT` | Pangolin 边缘 ACME 失败或没有匹配证书 | 查边缘 Traefik 日志和动态 router，不能只查本机 Traefik |
| `failed to find zone pig.rocks` | DNS CNAME 导致 ACME 找错 zone | 改为 A 记录 |
| 公网证书错误但 `127.0.0.1:443` 正常 | Pangolin 边缘未同步 | 重启 gerbil+pangolin；确认 traefik-config API 含该 Host |
| ACME 429 rate limit | 短时间内多次失败 | 等待 1h 或用手动 certbot + 静态证书 |

### 本机 Traefik 静态证书（ACME 失败时的兜底）

```bash
CF_TOKEN=$(grep '^CF_DNS_API_TOKEN=' ~/.local/share/yoo/traefik/.env | cut -d= -f2-)
mkdir -p /tmp/cert && printf 'dns_cloudflare_api_token = %s\n' "$CF_TOKEN" > /tmp/cert/cloudflare.ini
docker run --rm \
  -v /tmp/cert/cloudflare.ini:/cloudflare.ini:ro \
  -v /tmp/cert/letsencrypt:/etc/letsencrypt \
  certbot/dns-cloudflare certonly --non-interactive --agree-tos \
  --email admin@yoo.im --authenticator dns-cloudflare \
  --dns-cloudflare-credentials /cloudflare.ini -d sub.yoo.im

sudo mkdir -p ~/.local/share/yoo/traefik/certs/sub.yoo.im
sudo cp /tmp/cert/letsencrypt/live/sub.yoo.im/*.pem ~/.local/share/yoo/traefik/certs/sub.yoo.im/
```

Traefik 需挂载 certs + file provider（见 `~/.local/share/yoo/traefik/docker-compose.yml` 中 `certs/` 与 `dynamic/`）。路由 label **去掉** `tls.certresolver=le`，依赖静态证书 SNI 匹配。

Pangolin 边缘证书由 `/opt/pangolin/config/letsencrypt/acme.json` 自动管理。若日志持续出现 `failed to find zone pig.rocks`，仅改 A 记录后仍未恢复，可做单域名 HTTP-01 兜底：

1. 确认边缘 80 端口公网可达，且 Traefik 已配置 `le-http`（HTTP challenge 使用 `web` entrypoint）。
2. 从 `traefik-config` 读取 Pangolin 生成的真实 service 名，不要猜测。
3. 在 `/opt/pangolin/config/traefik/dynamic/<name>.yml` 添加优先级更高的同域名 router，复用该 service，并设置 `tls.certResolver: le-http`。
4. 重启边缘 Traefik，查看日志直到签发成功，再执行完整验收。

```yaml
http:
  routers:
    sub-http01:
      entryPoints: [websecure]
      rule: Host(`sub.yoo.im`)
      priority: 200
      service: RESOURCE_ID-NAME-service@http # 替换为动态配置真实值
      tls:
        certResolver: le-http
```

刚重启时 HTTP-01 可能短暂 `connection refused`。先确认边缘 80 已监听并检查日志，不要在尚未就绪时反复改配置或宣布成功。

## 常见陷阱

1. **traefik overlay 覆盖 networks**：只写 `traefik-public` 会导致 nginx 无法访问 api/web，必须同时保留 `default`。
2. **只配本机 Traefik 不配 Pangolin**：公网 443 由 Pangolin 边缘处理，DB 里必须有 resource + targets。
3. **local DNS 被 Clash fake-ip 干扰**：验证证书时用 `--resolve sub.yoo.im:443:45.33.114.37` 或 `127.0.0.1`。
4. **Dify 端口**：默认 `EXPOSE_NGINX_PORT=81`，Traefik 通过 Docker 网络连 nginx:80，不是宿主机 81。
5. **硬编码 siteId**：站点重建后 ID 会变化；从在线 `ubuntu` 站点动态查询。
6. **假定 SSH root**：使用 SSH 配置中的 `pig.rocks` 主机和用户，以 `sudo -n` 执行远端管理命令。
7. **检查错 Newt unit**：系统级 active 时用户级 inactive 是正常的；先识别 unit 再重启。
8. **把本机 200 当公网成功**：本机测试绕过 DNS、Pangolin router 和边缘证书，必须完成全部验收。

## 参考路径

| 用途 | 路径 |
|------|------|
| Newt 凭证 | `~/.config/pangolin/newt.json` |
| 本机 Traefik | `~/.local/share/yoo/traefik/` |
| Pangolin 脚本示例 | `~/workspace/pr-docker/poste/setup-pangolin-dify.sh` |
| Dify Traefik overlay | `~/apps/dify/docker/docker-compose.traefik.yml` |
| Pangolin DB | `ssh pig.rocks` → `/opt/pangolin/config/db/db.sqlite`（远端用 `sudo`） |

## 脚本

- `scripts/setup-pangolin-resource.sh`：在 pig.rocks 上添加 HTTP 资源的模板脚本
