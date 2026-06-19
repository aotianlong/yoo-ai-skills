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

- **Pangolin 服务器**：`root@pig.rocks`，配置在 `/opt/pangolin/`
- **本机 Newt**：`~/.config/pangolin/newt.json`，systemd `pangolin-newt.service`
- **本机 Traefik**：`~/.local/share/yoo/traefik/`，网络 `traefik-public`
- **Ubuntu siteId**：`2`（Pangolin DB `sites` 表）

## 新增子域 checklist

```
- [ ] 1. Pangolin 资源（pig.rocks DB）
- [ ] 2. 本机 Traefik 路由（docker labels）
- [ ] 3. 服务公网 URL（.env）
- [ ] 4. DNS（A 记录，禁止 CNAME 到 pig.rocks）
- [ ] 5. 重启 newt + pangolin/gerbil
- [ ] 6. 验证证书与 HTTP
```

### 1. Pangolin 资源

在 pig.rocks 上向 `resources` + `targets` 插入记录，或使用 `scripts/setup-pangolin-resource.sh`。

| 字段 | 典型值 |
|------|--------|
| `siteId` | `2`（ubuntu） |
| `fullDomain` | `dify.yoo.im` |
| `internalPort` | 下一个空闲端口（查现有：`54001`–`54013` 等） |
| `target.ip` | `127.0.0.1` |
| `target.port` | `443` |
| `target.method` | `https` |
| `ssl` / `enabled` | `1` |

分配 internalPort：

```bash
ssh root@pig.rocks 'sqlite3 /opt/pangolin/config/db/db.sqlite \
  "SELECT r.fullDomain, t.internalPort FROM resources r JOIN targets t ON r.resourceId=t.resourceId WHERE r.enabled=1 ORDER BY t.internalPort;"'
```

重启 Pangolin 使边缘 Traefik 拉取新路由：

```bash
ssh root@pig.rocks 'cd /opt/pangolin && docker compose restart gerbil pangolin'
```

确认动态配置已包含新域名：

```bash
ssh root@pig.rocks 'docker exec traefik wget -qO- http://pangolin:3001/api/v1/traefik-config | grep -o "Host(\`你的域名\`)"'
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
systemctl --user restart pangolin-newt.service
```

### 6. 验证

```bash
# 证书（公网）
echo | openssl s_client -connect sub.yoo.im:443 -servername sub.yoo.im 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates

# 应看到 CN=sub.yoo.im, issuer=Let's Encrypt
# 若 subject=CN=TRAEFIK DEFAULT CERT → 见下方排障

# HTTP
curl -sI https://sub.yoo.im/ | head -5
```

## 证书排障

| 现象 | 原因 | 处理 |
|------|------|------|
| `TRAEFIK DEFAULT CERT` | 本机 Traefik ACME 失败 | 查 DNS 是否 CNAME 到 pig.rocks；查 traefik 日志 `Unable to obtain ACME` |
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

Pangolin 边缘证书由 `/opt/pangolin/config/letsencrypt/acme.json` 自动管理，一般无需手动处理。

## 常见陷阱

1. **traefik overlay 覆盖 networks**：只写 `traefik-public` 会导致 nginx 无法访问 api/web，必须同时保留 `default`。
2. **只配本机 Traefik 不配 Pangolin**：公网 443 由 Pangolin 边缘处理，DB 里必须有 resource + targets。
3. **local DNS 被 Clash fake-ip 干扰**：验证证书时用 `--resolve sub.yoo.im:443:45.33.114.37` 或 `127.0.0.1`。
4. **Dify 端口**：默认 `EXPOSE_NGINX_PORT=81`，Traefik 通过 Docker 网络连 nginx:80，不是宿主机 81。

## 参考路径

| 用途 | 路径 |
|------|------|
| Newt 凭证 | `~/.config/pangolin/newt.json` |
| 本机 Traefik | `~/.local/share/yoo/traefik/` |
| Pangolin 脚本示例 | `~/workspace/pr-docker/poste/setup-pangolin-dify.sh` |
| Dify Traefik overlay | `~/apps/dify/docker/docker-compose.traefik.yml` |
| Pangolin DB | `ssh root@pig.rocks` → `/opt/pangolin/config/db/db.sqlite` |

## 脚本

- `scripts/setup-pangolin-resource.sh`：在 pig.rocks 上添加 HTTP 资源的模板脚本
