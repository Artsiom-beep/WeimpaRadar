#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE_DIR="$ROOT_DIR/runs/_semrush_profile"
DISPLAY_NUM=":99"
VNC_PORT="5901"
NOVNC_PORT="6080"

PID_DIR="/tmp/weimpa_semrush_login_web"
mkdir -p "$PID_DIR"

log() { printf "[%s] %s\n" "$(date +'%F %T')" "$*"; }

kill_if_running() {
  local pidfile="$1"
  if [[ -f "$pidfile" ]]; then
    local pid
    pid="$(cat "$pidfile" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
    rm -f "$pidfile" || true
  fi
}

cleanup() {
  log "Stopping..."
  kill_if_running "$PID_DIR/novnc.pid"
  kill_if_running "$PID_DIR/x11vnc.pid"
  kill_if_running "$PID_DIR/chrome.pid"
  kill_if_running "$PID_DIR/xvfb.pid"
  rm -rf "$PID_DIR" 2>/dev/null || true
  log "Done."
}
trap cleanup EXIT

mkdir -p "$PROFILE_DIR"

kill_if_running "$PID_DIR/novnc.pid"
kill_if_running "$PID_DIR/x11vnc.pid"
kill_if_running "$PID_DIR/chrome.pid"
kill_if_running "$PID_DIR/xvfb.pid"

log "ROOT_DIR=$ROOT_DIR"
log "PROFILE_DIR=$PROFILE_DIR"

log "Starting Xvfb on $DISPLAY_NUM ..."
Xvfb "$DISPLAY_NUM" -screen 0 1440x900x24 -ac +extension GLX +render -noreset >/tmp/xvfb_semrush.log 2>&1 &
echo $! > "$PID_DIR/xvfb.pid"
sleep 0.5

CHROME_BIN="/home/ubuntu/.cache/ms-playwright/chromium-1200/chrome-linux64/chrome"
# if command -v chromium >/dev/null 2>&1; then CHROME_BIN="chromium"; fi
# if [[ -z "$CHROME_BIN" ]] && command -v chromium-browser >/dev/null 2>&1; then CHROME_BIN="chromium-browser"; fi
# if [[ -z "$CHROME_BIN" ]] && command -v google-chrome >/dev/null 2>&1; then CHROME_BIN="google-chrome"; fi

if [[ -z "$CHROME_BIN" ]]; then
  PW_CHROME="$(python3 - <<'PY'
import os, glob
base=os.path.expanduser("~/.cache/ms-playwright")
paths=sorted(glob.glob(base+"/chromium-*/chrome-linux*/chrome"))
print(paths[-1] if paths else "")
PY
)"
  if [[ -n "$PW_CHROME" ]]; then CHROME_BIN="$PW_CHROME"; fi
fi

if [[ -z "$CHROME_BIN" ]]; then
  log "ERROR: Chromium binary not found (chromium/google-chrome/playwright)."
  exit 1
fi

log "Starting browser: $CHROME_BIN"
export DISPLAY="$DISPLAY_NUM"
"$CHROME_BIN" \
  --user-data-dir="$PROFILE_DIR" \
  --no-first-run \
  --no-default-browser-check \
  --disable-dev-shm-usage \
  --disable-features=TranslateUI \
  --window-size=1440,900 \
  "https://www.semrush.com/" \
  >/tmp/chrome_semrush.log 2>&1 &
echo $! > "$PID_DIR/chrome.pid"
sleep 0.8

log "Starting x11vnc on port $VNC_PORT (localhost only) ..."
x11vnc -display "$DISPLAY_NUM" -rfbport "$VNC_PORT" -localhost -shared -forever -nopw \
  >/tmp/x11vnc_semrush.log 2>&1 &
echo $! > "$PID_DIR/x11vnc.pid"
sleep 0.4

log "Starting noVNC on port $NOVNC_PORT (localhost only) ..."
if command -v novnc_proxy >/dev/null 2>&1; then
  novnc_proxy --vnc "localhost:$VNC_PORT" --listen "127.0.0.1:$NOVNC_PORT" \
    >/tmp/novnc_semrush.log 2>&1 &
  echo $! > "$PID_DIR/novnc.pid"
else
  WEBDIR="/usr/share/novnc"
  websockify --web "$WEBDIR" "127.0.0.1:$NOVNC_PORT" "localhost:$VNC_PORT" \
    >/tmp/novnc_semrush.log 2>&1 &
  echo $! > "$PID_DIR/novnc.pid"
fi

log "READY"
log "noVNC: http://127.0.0.1:$NOVNC_PORT/vnc.html?autoconnect=1&resize=remote"
log "Keep this running while you log in. Stop with Ctrl+C."
wait
