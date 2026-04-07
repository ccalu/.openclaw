@echo off
rem OpenClaw Gateway (v2026.4.2)
set "GROQ_API_KEY=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"
set "TMPDIR=C:\Users\User-OEM\AppData\Local\Temp"
set "OPENCLAW_GATEWAY_PORT=18789"
set "OPENCLAW_SYSTEMD_UNIT=openclaw-gateway.service"
set "OPENCLAW_WINDOWS_TASK_NAME=OpenClaw Gateway"
set "OPENCLAW_SERVICE_MARKER=openclaw"
set "OPENCLAW_SERVICE_KIND=gateway"
set "OPENCLAW_SERVICE_VERSION=2026.4.2"
"C:\Program Files\nodejs\node.exe" C:\Users\User-OEM\AppData\Roaming\npm\node_modules\openclaw\dist\entry.js gateway --port 18789
