#!/usr/bin/env bash
# backup_postgres.sh
# PostgreSQL 逻辑备份脚本

set -euo pipefail
IFS=$'\n\t'

# === 配置区，按需修改 ===
# Docker 容器名称，用于逻辑备份
CONTAINER_NAME="pgrepmgr"
# PostgreSQL 用户名和密码
PG_USER="postgres"
PG_PASSWORD="your_password_here"  # 请替换为实际密码
# 远端 BACKUP 服务器登录信息
BACKUP_USER="yms"
BACKUP_HOST="172.27.220.168"
# 远端基础备份目录
BACKUP_BASEDIR="/home/yms/postgres"
# 本地临时工作目录
TMPDIR="/tmp/pg_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TMPDIR"

# === 逻辑备份 ===
LOGIC_DUMP="${TMPDIR}/postgres_logical_$(date +%Y%m%d_%H%M%S).sql"
echo "[`date +'%F %T'`] 开始逻辑备份（pg_dumpall）到：$LOGIC_DUMP"
sudo docker exec -e PGPASSWORD="$PG_PASSWORD" "$CONTAINER_NAME" \
  pg_dumpall -U "$PG_USER" > "$LOGIC_DUMP"
echo "[`date +'%F %T'`] 逻辑备份完成，保存至：$LOGIC_DUMP"

# 上传逻辑备份到远端
echo "[`date +'%F %T'`] 上传逻辑备份到 ${BACKUP_HOST}:${BACKUP_BASEDIR}/logical/"
scp "$LOGIC_DUMP" "${BACKUP_USER}@${BACKUP_HOST}:$BACKUP_BASEDIR/logical/"
echo "[`date +'%F %T'`] 逻辑备份上传完成。"

# === 清理临时文件 ===
echo "[`date +'%F %T'`] 清理本地临时目录：$TMPDIR"
rm -rf "$TMPDIR"
echo "[`date +'%F %T'`] 备份脚本执行结束。"
