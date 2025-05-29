#!/bin/sh

set -eu

USER=vagrant
SSH_KEY="/home/${USER}/.ssh/id_ed25519"
ME=$(hostname)
DATE=$(date +'%F')
TM=$(date +'%T')

TMP="/tmp/${ME}_${DATE}_${TM}.heartbeat"
echo "${ME},${DATE},${TM}" > "${TMP}"

for IP in 192.168.198.2 192.168.198.3 192.168.198.4; do
  [ "$(hostname -i)" = "$IP" ] && continue
  printf "[%s] Sending heartbeat to %s…\n" "$ME" "$IP"
  sudo -u "$USER" sftp -q -i "$SSH_KEY" \
    -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
    "${USER}@${IP}:incoming/" <<EOF || true
put $TMP
EOF

done

rm -f "$TMP"


API_URL="http://*.*.*.*:8000/add" #add your ip


send() {
  HOST="$1"
  D="$2"
  T="$3"
  curl -s -X POST "${API_URL}/${HOST}" \
    -H "Content-Type: application/json" \
    -d "{\"machine_name\":\"${ME}\",\"date\":\"${D}\",\"time\":\"${T}\"}"
}

send "$ME" "$DATE" "$TM"

for HB in /home/vagrant/incoming/*.heartbeat; do
  [ -e "$HB" ] || continue
  F=$(basename "$HB" .heartbeat)
  HOST="${F%%_*}"
  TS="${F#${HOST}_}"
  D="${TS%_*}"
  T="${TS#*_}"
  send "$HOST" "$D" "$T"
  rm -f "$HB"
done