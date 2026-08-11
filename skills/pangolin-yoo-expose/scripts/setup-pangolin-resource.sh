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
ORG_ID=yoo-baseyoo-base
DOMAIN_ID=domain1

sudo cp "$DB" "${DB}.bak-${NAME}-$(date +%Y%m%d%H%M%S)"

sudo python3 - "$DB" "$ORG_ID" "$DOMAIN_ID" "$NAME" "$FULL_DOMAIN" "$SUBDOMAIN" "$INTERNAL_PORT" <<'PY'
import sqlite3, uuid, sys

db = sys.argv[1]
org_id = sys.argv[2]
domain_id = sys.argv[3]
name, full_domain, subdomain, internal_port = sys.argv[4:8]
internal_port = int(internal_port)

conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT siteId FROM sites WHERE name='ubuntu' AND online=1 ORDER BY siteId DESC LIMIT 1")
row = cur.fetchone()
if not row:
    raise SystemExit("no online site named 'ubuntu'; aborting")
site_id = int(row[0])

cur.execute("SELECT 1 FROM resources WHERE fullDomain=?", (full_domain,))
if cur.fetchone():
    print(f"skip {full_domain} (already exists)")
    conn.close()
    raise SystemExit(0)

cur.execute("SELECT 1 FROM targets WHERE internalPort=? AND enabled=1", (internal_port,))
if cur.fetchone():
    raise SystemExit(f"internalPort {internal_port} is already in use; aborting")

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
    (rid, site_id, "127.0.0.1", "https", 443, internal_port),
)
conn.commit()
conn.close()
print(f"added {full_domain} siteId={site_id} internalPort={internal_port}")
PY

cd /opt/pangolin && sudo docker compose restart gerbil pangolin
echo "Done. Identify the active Newt unit before restarting:"
echo "  systemctl is-active pangolin-newt.service || systemctl --user is-active pangolin-newt.service"
