#!/bin/bash
# 在 pig.rocks Pangolin 上添加 HTTP 资源
# 用法: ./setup-pangolin-resource.sh <name> <fullDomain> <subdomain> <internalPort>
# 示例: ./setup-pangolin-resource.sh dify dify.yoo.im dify 54013
set -euo pipefail

NAME="${1:?name}"
FULL_DOMAIN="${2:?fullDomain}"
SUBDOMAIN="${3:?subdomain}"
INTERNAL_PORT="${4:?internalPort}"

DB=/opt/pangolin/config/db/db.sqlite
SITE_ID=2
ORG_ID=yoo-baseyoo-base
DOMAIN_ID=domain1

sudo cp "$DB" "${DB}.bak-${NAME}-$(date +%Y%m%d%H%M%S)"

sudo python3 - "$DB" "$SITE_ID" "$ORG_ID" "$DOMAIN_ID" "$NAME" "$FULL_DOMAIN" "$SUBDOMAIN" "$INTERNAL_PORT" <<'PY'
import sqlite3, uuid, sys

db = sys.argv[1]
site_id = int(sys.argv[2])
org_id = sys.argv[3]
domain_id = sys.argv[4]
name, full_domain, subdomain, internal_port = sys.argv[5:9]

conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT 1 FROM resources WHERE fullDomain=?", (full_domain,))
if cur.fetchone():
    print(f"skip {full_domain} (already exists)")
    conn.close()
    raise SystemExit(0)

cur.execute("SELECT MAX(resourceId) FROM resources")
rid = (cur.fetchone()[0] or 0) + 1
guid = str(uuid.uuid4())
nice = f"{name}-{rid}"
sub = subdomain or None

cur.execute(
    """INSERT INTO resources (
        resourceId, resourceGuid, orgId, niceId, name, subdomain, fullDomain, domainId,
        ssl, blockAccess, sso, http, protocol, emailWhitelistEnabled,
        applyRules, enabled, stickySession, setHostHeader, enableProxy, proxyProtocol, wildcard
    ) VALUES (?,?,?,?,?,?,?,?,1,0,0,1,'tcp',0,0,1,0,?,1,0,0)""",
    (rid, guid, org_id, nice, name, sub, full_domain, domain_id, full_domain),
)
cur.execute(
    """INSERT INTO targets (resourceId, siteId, ip, method, port, internalPort, enabled, priority)
       VALUES (?,?,?,?,?,?,1,100)""",
    (rid, site_id, "127.0.0.1", "https", 443, int(internal_port)),
)
conn.commit()
conn.close()
print(f"added {full_domain} internalPort={internal_port}")
PY

cd /opt/pangolin && sudo docker compose restart gerbil pangolin
echo "Done. On ubuntu: systemctl --user restart pangolin-newt.service"
