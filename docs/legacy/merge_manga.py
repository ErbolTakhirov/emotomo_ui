import re
import os

with open('templates/manga.html', 'r', encoding='utf-8') as f:
    old_manga = f.read()

# Extract PixiJS deps
pixi_match = re.search(r'<script src="https://unpkg\.com/pixi\.js@7.*?</script>\s*<script src="https://cubism\.live2d\.com.*?</script>\s*<script src="https://unpkg\.com/pixi-live2d-display.*?</script>', old_manga, re.DOTALL)
pixi_scripts = pixi_match.group(0) if pixi_match else ""

# Extract Three.js/Model-Viewer deps
vrm_match = re.search(r'<!-- Three.js & VRM Dependencies -->\s*<!-- Google Model-Viewer -->\s*<script type="module" src="https://ajax.*?</script>', old_manga, re.DOTALL)
vrm_scripts = vrm_match.group(0) if vrm_match else ""

# Extract the core Javascript from the bottom (Live2D + Chat logic)
core_js_match = re.search(r'(<!-- ===== Live2D \+ Chat bootstrap ===== -->.*?)</body>', old_manga, re.DOTALL)
core_js = core_js_match.group(1) if core_js_match else ""

# The core JS currently references old DOM IDs... let's replace them carefully!
# 1. old: $('#input') -> new: document.getElementById('user-input')
core_js = core_js.replace("const messages = $('#messages'), input = $('#input'), sendBtn = $('#send');",
                          "const messages = document.getElementById('messages'), input = document.getElementById('user-input'), sendBtn = document.getElementById('sendBtnCustom') || {addEventListener:()=>{}};") # Fake sendBtn so EventListener doesn't break, the user HTML handles send via onclick="sendMessage()"

# 2. Add dependencies like makeSimpleMouth that reside outside the bootstrap block:
make_mouth_match = re.search(r'(function makeSimpleMouth.*?\n    })', old_manga, re.DOTALL)
make_mouth_logic = make_mouth_match.group(1) if make_mouth_match else ""

# We need the user's provided HTML
user_html = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>EmoTomo</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

{PIXI}
{VRM}

<style>
/* ─── RESET & BASE ─── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --pink:        #FF2D78;
  --pink-dim:    rgba(255,45,120,0.15);
  --pink-border: rgba(255,45,120,0.3);
  --purple:      #7B5CF0;
  --purple-dim:  rgba(123,92,240,0.2);
  --bg:          #0e0f16;
  --surface:     rgba(18,20,32,0.92);
  --surface2:    rgba(26,28,44,0.9);
  --border:      rgba(255,255,255,0.07);
  --border2:     rgba(255,255,255,0.12);
  --text:        #ffffff;
  --muted:       rgba(255,255,255,0.45);
  --muted2:      rgba(255,255,255,0.22);
  --red:         #E5484D;
  --red-dim:     rgba(229,72,77,0.15);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-top:    env(safe-area-inset-top, 0px);
}

html, body {
  height: 100%; width: 100%;
  overflow: hidden;
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  touch-action: none;
}

/* ─── STAGE (Live2D canvas) ─── */
#stage {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: radial-gradient(ellipse at 50% 60%, #1a1228 0%, #0e0f16 70%);
  cursor: crosshair;
}

/* ─── TOP BAR ─── */
.top-bar {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: calc(12px + var(--safe-top)) 16px 12px;
  pointer-events: none;
}
.top-bar > * { pointer-events: auto; }

/* Hamburger */
.hamb {
  width: 42px; height: 42px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border2);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: var(--text);
  transition: background 0.15s, border-color 0.15s, transform 0.15s;
}
.hamb:hover { background: var(--surface2); border-color: rgba(255,255,255,0.2); }
.hamb:active { transform: scale(0.94); }
.hamb svg { width: 18px; height: 18px; }

/* Character name chip (center) */
.char-chip {
  display: flex; align-items: center; gap: 8px;
  background: var(--surface);
  border: 1px solid var(--border2);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 50px;
  padding: 8px 16px;
  font-size: 13px; font-weight: 600;
  letter-spacing: 0.01em;
  pointer-events: none;
}
.char-chip-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34,197,94,0.7);
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%,100% { opacity:1; transform:scale(1); }
  50% { opacity:0.6; transform:scale(0.8); }
}

/* End session button */
.end-btn {
  display: flex; align-items: center; gap: 7px;
  background: var(--red-dim);
  border: 1px solid rgba(229,72,77,0.35);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 10px;
  padding: 10px 16px;
  color: #ff6b6e;
  font-family: 'Inter', sans-serif;
  font-size: 13px; font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, transform 0.15s;
}
.end-btn:hover { background: rgba(229,72,77,0.25); border-color: rgba(229,72,77,0.5); }
.end-btn:active { transform: scale(0.95); }
.end-btn svg { width: 14px; height: 14px; }

/* ─── SIDEBAR MENU ─── */
.sidebar {
  position: fixed;
  top: 0; left: 0; bottom: 0;
  width: 280px;
  z-index: 40;
  background: rgba(14,15,22,0.97);
  border-right: 1px solid var(--border2);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  transform: translateX(-100%);
  transition: transform 0.3s cubic-bezier(0.4,0,0.2,1);
  display: flex; flex-direction: column;
  padding: calc(20px + var(--safe-top)) 0 calc(20px + var(--safe-bottom));
  overflow-y: auto;
}
.sidebar.open { transform: translateX(0); }

.sidebar-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px 20px;
  border-bottom: 1px solid var(--border);
}
.sidebar-title { font-size: 16px; font-weight: 700; }
.sidebar-close {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--surface2); border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: var(--muted); font-size: 18px;
  transition: color 0.15s, background 0.15s;
}
.sidebar-close:hover { color: var(--text); background: rgba(255,255,255,0.08); }

.sidebar-body { padding: 20px; display: flex; flex-direction: column; gap: 6px; }

.sidebar-label {
  font-size: 10px; font-weight: 600; color: var(--muted);
  letter-spacing: 0.1em; text-transform: uppercase;
  padding: 4px 0; margin-top: 8px;
}
.sidebar-label:first-child { margin-top: 0; }

.s-select {
  width: 100%;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border2);
  border-radius: 10px;
  color: var(--text);
  font-family: 'Inter', sans-serif;
  font-size: 13px; font-weight: 500;
  padding: 10px 14px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' fill='none'%3E%3Cpath d='M1 1.5l5 5 5-5' stroke='rgba(255,255,255,.4)' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  cursor: pointer;
  transition: border-color 0.15s;
}
.s-select:focus { outline: none; border-color: var(--pink-border); }

.s-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border-radius: 10px;
  transition: background 0.15s; cursor: pointer;
}
.s-row:hover { background: rgba(255,255,255,0.04); }
.s-row-left { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.s-row-left svg { color: var(--muted); flex-shrink: 0; }
.s-row-icon {
  width: 28px; height: 28px; border-radius: 7px;
  background: rgba(255,255,255,0.06);
  display: flex; align-items: center; justify-content: center; font-size: 14px;
}

.sw {
  width: 36px; height: 20px;
  background: rgba(255,255,255,0.08);
  border: 1px solid var(--border);
  border-radius: 10px; position: relative; cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
.sw.on { background: rgba(255,45,120,0.2); border-color: var(--pink); }
.sw::after {
  content: ''; position: absolute;
  width: 14px; height: 14px;
  background: rgba(255,255,255,0.3); border-radius: 50%;
  top: 2px; left: 2px; transition: transform 0.2s, background 0.2s;
}
.sw.on::after { transform: translateX(16px); background: var(--pink); box-shadow: 0 0 6px rgba(255,45,120,0.5); }

.sidebar-divider { height: 1px; background: var(--border); margin: 8px 0; }

.sidebar-btn {
  display: flex; align-items: center; gap: 10px;
  width: 100%; padding: 11px 14px; border-radius: 10px;
  background: transparent; border: 1px solid var(--border);
  color: var(--text); font-family: 'Inter', sans-serif;
  font-size: 13px; font-weight: 500; cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  text-align: left;
}
.sidebar-btn:hover { background: rgba(255,255,255,0.05); border-color: var(--border2); }
.sidebar-btn.pink { color: var(--pink); border-color: var(--pink-border); }
.sidebar-btn.pink:hover { background: var(--pink-dim); }

/* Auth info in sidebar */
.sidebar-user {
  margin: 0 20px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
  display: flex; align-items: center; gap: 10px;
}
.sidebar-user-av {
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(255,45,120,0.15);
  border: 1.5px solid var(--pink);
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 700; color: var(--pink); flex-shrink: 0;
}
.sidebar-user-name { font-size: 13px; font-weight: 600; }
.sidebar-user-sub  { font-size: 11px; color: var(--muted); }

/* Overlay */
.overlay {
  position: fixed; inset: 0; z-index: 35;
  background: rgba(0,0,0,0.5);
  opacity: 0; pointer-events: none;
  transition: opacity 0.3s;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}
.overlay.show { opacity: 1; pointer-events: auto; }

/* ─── CHAT UI ─── */
#chat-ui {
  position: fixed;
  left: 0; right: 0; bottom: 0;
  z-index: 10;
  display: flex; flex-direction: column;
  max-height: 70vh;
  pointer-events: none;
  transform: translateY(0);
  transition: transform 0.35s cubic-bezier(0.4,0,0.2,1);
}
#chat-ui.collapsed { transform: translateY(calc(100% - 80px - var(--safe-bottom))); }

/* Messages area */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 16px 8px;
  display: flex; flex-direction: column; gap: 12px;
  pointer-events: auto;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
  scroll-behavior: smooth;
  mask-image: linear-gradient(transparent, black 40px);
  -webkit-mask-image: linear-gradient(transparent, black 40px);
}
.messages::-webkit-scrollbar { width: 3px; }
.messages::-webkit-scrollbar-track { background: transparent; }
.messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 2px; }

/* Message bubbles */
.msg {
  display: flex; gap: 8px; align-items: flex-end;
  animation: msg-in 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
@keyframes msg-in {
  from { opacity:0; transform: translateY(12px) scale(0.95); }
  to   { opacity:1; transform: translateY(0) scale(1); }
}

.msg.user { flex-direction: row-reverse; }

.msg-bubble {
  max-width: min(72%, 340px);
  padding: 10px 14px;
  font-size: 14px; line-height: 1.5;
  word-break: break-word;
}
.msg.ai .msg-bubble {
  background: var(--surface);
  border: 1px solid var(--border2);
  border-bottom-left-radius: 4px;
  border-radius: 16px 16px 16px 4px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.msg.user .msg-bubble {
  background: var(--purple);
  border-radius: 16px 16px 4px 16px;
  color: #fff;
}

.msg-avatar {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  background: rgba(255,45,120,0.15);
  border: 1.5px solid rgba(255,45,120,0.4);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: var(--pink);
  margin-bottom: 2px;
}

.msg-time {
  font-size: 10px; color: var(--muted2);
  margin: 0 4px 2px; flex-shrink: 0; align-self: flex-end;
}

/* Typing indicator */
.typing-indicator {
  display: flex; gap: 4px; align-items: center;
  padding: 12px 14px;
}
.typing-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--muted);
  animation: typing 1.4s ease-in-out infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
  0%,80%,100% { transform: scale(0.7); opacity:0.4; }
  40% { transform: scale(1); opacity:1; }
}

/* Retry btn */
.retry-btn {
  margin-top: 6px; font-size: 11px;
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--border); border-radius: 6px;
  color: var(--muted); padding: 4px 10px; cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background 0.15s, color 0.15s;
}
.retry-btn:hover { background: rgba(255,255,255,0.1); color: var(--text); }

/* Quick chips */
.quick {
  display: flex; gap: 8px; padding: 0 16px 8px;
  overflow-x: auto; pointer-events: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.quick::-webkit-scrollbar { display: none; }
.chip {
  flex-shrink: 0;
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 50px; padding: 8px 14px;
  font-size: 12px; font-weight: 500;
  color: rgba(255,255,255,0.8);
  cursor: pointer; white-space: nowrap;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: background 0.15s, border-color 0.15s, transform 0.1s;
}
.chip:hover { background: var(--surface2); border-color: var(--border2); }
.chip:active { transform: scale(0.96); }

/* ─── INPUT BAR ─── */
.input-bar {
  display: flex; align-items: flex-end; gap: 8px;
  padding: 12px 16px calc(12px + var(--safe-bottom));
  background: var(--surface);
  border-top: 1px solid var(--border2);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  pointer-events: auto;
}

/* Drag handle for mobile collapse */
.drag-handle {
  position: absolute;
  top: -14px; left: 50%; transform: translateX(-50%);
  width: 36px; height: 4px;
  background: rgba(255,255,255,0.2);
  border-radius: 2px;
  cursor: grab;
  display: none;
}

.chat-input-wrap {
  flex: 1;
  display: flex; align-items: flex-end;
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--border2);
  border-radius: 14px;
  padding: 10px 14px;
  gap: 8px;
  transition: border-color 0.15s;
  min-height: 48px;
}
.chat-input-wrap:focus-within { border-color: rgba(255,255,255,0.2); }

#user-input {
  flex: 1; background: transparent; border: none; outline: none;
  color: var(--text); font-family: 'Inter', sans-serif;
  font-size: 14px; line-height: 1.4;
  resize: none; max-height: 120px;
  overflow-y: auto; align-self: center;
}
#user-input::placeholder { color: var(--muted); }
#user-input::-webkit-scrollbar { width: 3px; }
#user-input::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); }

.input-icon-btn {
  width: 32px; height: 32px; border-radius: 8px;
  background: transparent; border: none;
  color: var(--muted); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; align-self: flex-end;
  transition: color 0.15s, background 0.15s;
}
.input-icon-btn:hover { color: var(--text); background: rgba(255,255,255,0.06); }
.input-icon-btn svg { width: 18px; height: 18px; }
.input-icon-btn.active { color: var(--pink); }
.input-icon-btn.recording { color: var(--red); animation: rec-pulse 1s ease-in-out infinite; }
@keyframes rec-pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* Send button */
#send {
  width: 48px; height: 48px; border-radius: 14px;
  background: var(--purple); border: none;
  color: #fff; cursor: pointer; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s, transform 0.15s;
  box-shadow: 0 4px 20px rgba(123,92,240,0.4);
}
#send:hover { background: #8f6ff5; }
#send:active { transform: scale(0.94); }
#send svg { width: 18px; height: 18px; }

/* ─── CHAT TOGGLE (mobile FAB) ─── */
#chat-toggle {
  position: fixed;
  right: 16px;
  bottom: calc(96px + var(--safe-bottom));
  z-index: 15;
  width: 48px; height: 48px; border-radius: 50%;
  background: rgba(30,32,52,0.9);
  border: 1.5px solid rgba(123,92,240,0.5);
  color: var(--purple); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  transition: background 0.15s, border-color 0.15s, transform 0.15s;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
#chat-toggle:hover { border-color: var(--purple); }
#chat-toggle:active { transform: scale(0.94); }
#chat-toggle svg { width: 20px; height: 20px; }

/* unread badge */
.unread-badge {
  position: absolute; top: -3px; right: -3px;
  width: 16px; height: 16px; border-radius: 50%;
  background: var(--pink); color: #fff;
  font-size: 9px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid var(--bg);
  animation: badge-pop 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
@keyframes badge-pop { from{transform:scale(0)} to{transform:scale(1)} }

/* ─── MOBILE ─── */
@media (max-width: 640px) {
  .char-chip { display: none; }
  .end-btn span { display: none; }
  .end-btn { padding: 10px 12px; }
  .drag-handle { display: block; }
  #chat-ui { max-height: 65vh; }
  .messages { padding: 12px 12px 6px; }
  .msg-bubble { max-width: 82%; font-size: 13px; }
  .input-bar { padding: 10px 12px calc(10px + var(--safe-bottom)); }
  #send { width: 44px; height: 44px; border-radius: 12px; }
  #chat-toggle { bottom: calc(88px + var(--safe-bottom)); right: 12px; }
}

/* ─── LANDSCAPE MOBILE ─── */
@media (max-width: 900px) and (orientation: landscape) {
  #chat-ui { max-height: 80vh; }
  .messages { padding: 8px 14px 4px; }
  .input-bar { padding: 8px 14px calc(8px + var(--safe-bottom)); }
}

/* ─── STATUS BAR / AUTH MODAL ─── */
.auth-modal {
  position: fixed; inset: 0; z-index: 60;
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  opacity: 0; pointer-events: none;
  transition: opacity 0.25s;
}
.auth-modal.show { opacity: 1; pointer-events: auto; }
.auth-card {
  background: #161820;
  border: 1px solid var(--border2);
  border-radius: 20px;
  width: 100%; max-width: 380px;
  padding: 28px 24px;
  transform: translateY(20px);
  transition: transform 0.25s;
}
.auth-modal.show .auth-card { transform: translateY(0); }
.auth-tab-row { display: flex; gap: 0; margin-bottom: 24px; background: rgba(255,255,255,0.04); border-radius: 10px; padding: 4px; }
.auth-tab {
  flex: 1; padding: 9px; border-radius: 8px; background: transparent; border: none;
  color: var(--muted); font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.auth-tab.active { background: var(--surface2); color: var(--text); }
.auth-field {
  width: 100%; background: rgba(255,255,255,0.05); border: 1px solid var(--border2);
  border-radius: 10px; color: var(--text); font-family: 'Inter', sans-serif;
  font-size: 14px; padding: 12px 14px; margin-bottom: 10px; outline: none;
  transition: border-color 0.15s;
}
.auth-field:focus { border-color: rgba(255,45,120,0.4); }
.auth-submit {
  width: 100%; padding: 13px; border-radius: 10px;
  background: var(--pink); border: none; color: #fff;
  font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600;
  cursor: pointer; margin-top: 4px;
  transition: background 0.15s, transform 0.1s;
}
.auth-submit:hover { background: #ff4d8e; }
.auth-submit:active { transform: scale(0.98); }
.close-auth {
  position: absolute; top: 14px; right: 14px;
  width: 28px; height: 28px; border-radius: 7px;
  background: rgba(255,255,255,0.06); border: none; color: var(--muted);
  font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center;
}

/* ─── ANIMATIONS ─── */
.fade-in { animation: fade-in 0.3s ease; }
@keyframes fade-in { from{opacity:0} to{opacity:1} }
/* STT Output */
#stt-output {
  position: fixed; left: 50%; transform: translateX(-50%); bottom: 120px; z-index: 100;
  background: rgba(0,0,0,0.7); color: #fff; padding: 8px 16px; border-radius: 12px;
  font-size: 14px; backdrop-filter: blur(4px); pointer-events: none;
}
/* User profile sync styles */
.hidden { display: none !important; }
</style>
</head>
<body>

<!-- LIVE2D STAGE -->
<canvas id="stage" aria-label="Live2D stage"></canvas>
<model-viewer id="viewer3d" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: none;"
    camera-controls auto-rotate autoplay shadow-intensity="1" touch-action="pan-y">
</model-viewer>

<!-- OVERLAY (closes sidebar) -->
<div class="overlay" id="overlay" onclick="closeSidebar()"></div>

<!-- SIDEBAR -->
<aside class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <span class="sidebar-title">Настройки</span>
    <button class="sidebar-close" onclick="closeSidebar()">×</button>
  </div>

  <div style="padding:16px 20px">
    <div class="sidebar-user">
      <div class="sidebar-user-av" id="sb-av">U</div>
      <div>
        <div class="sidebar-user-name" id="sb-name">Гость</div>
        <div class="sidebar-user-sub"></div>
      </div>
    </div>
  </div>

  <div class="sidebar-body">
    <div class="sidebar-label">Голос</div>
    <select class="s-select" id="lang-select">
        <option value="ru-RU">Русский</option>
        <option value="en-US">English</option>
        <option value="ja-JP">日本語</option>
        <option value="zh-CN">中文</option>
    </select>

    <div class="sidebar-label">Параметры</div>
    <div class="s-row" onclick="toggleSw(this)">
      <div class="s-row-left">Звук ответов</div>
      <div class="sw on" id="audio-sw"></div>
    </div>
    
    <div class="sidebar-divider"></div>

    <button class="sidebar-btn" id="chat-toggle-btn" onclick="toggleChatFromSidebar()">
      <span id="chat-toggle-label">Скрыть чат</span>
    </button>
    <button class="sidebar-btn" onclick="window.location.href='/dashboard/profile.html'">
      Профиль
    </button>
    <button class="sidebar-btn" onclick="window.location.href='/catalog.html'">
      Главная
    </button>
  </div>
</aside>

<!-- TOP BAR -->
<header class="top-bar">
  <button class="hamb" id="hamb" onclick="openSidebar()">
    <svg viewBox="0 0 18 14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
      <line x1="0" y1="1" x2="18" y2="1"/>
      <line x1="0" y1="7" x2="18" y2="7"/>
      <line x1="0" y1="13" x2="18" y2="13"/>
    </svg>
  </button>

  <div class="char-chip">
    <div class="char-chip-dot"></div>
    <span id="char-name-chip">Загрузка...</span>
  </div>

  <button class="end-btn" id="end-session-trigger" onclick="endSession()">
    <span>Завершить</span>
  </button>
</header>

<div id="stt-output" hidden></div>

<!-- CHAT UI -->
<div id="chat-ui">
  <div class="drag-handle" id="drag-handle"></div>

  <!-- Messages -->
  <div class="messages" id="messages"></div>

  <!-- Input bar -->
  <div class="input-bar">
    <div class="chat-input-wrap">
      <textarea id="user-input" placeholder="Напиши сообщение..." rows="1"
        oninput="autoResize(this)" onkeydown="handleKey(event)"></textarea>
      <button class="input-icon-btn" id="mic-btn" title="Голосовой ввод">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <rect x="9" y="2" width="6" height="12" rx="3"/>
          <path d="M5 10a7 7 0 0014 0M12 19v3M9 22h6"/>
        </svg>
      </button>
      <button class="input-icon-btn" id="voice-toggle" title="Озвучка ответов">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
          <path d="M19.07 4.93a10 10 0 010 14.14M15.54 8.46a5 5 0 010 7.07"/>
        </svg>
      </button>
    </div>
    <button id="send" onclick="send()">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="22" y1="2" x2="11" y2="13"/>
        <polygon points="22 2 15 22 11 13 2 9 22 2"/>
      </svg>
    </button>
  </div>
</div>

<script>
{MAKE_MOUTH_LOGIC}

window.SessionUI = {
  states: { IDLE: 'idle', THINKING: 'thinking', TALKING: 'talking', LISTENING: 'listening' },
  update(state) {
    if(state === this.states.THINKING) {
        showTyping();
    } else {
        removeTyping();
    }
  },
  showError(msg, cb) {
      alert("Ошибка: " + msg);
      if(cb) cb();
  }
};

/* ── Sidebar ── */
function openSidebar() {
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('overlay').classList.add('show');
  document.body.style.overflow = 'hidden';
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('show');
  document.body.style.overflow = '';
}

/* ── Toggle switches ── */
function toggleSw(row) {
  row.querySelector('.sw').classList.toggle('on');
}

/* ── Chat toggle ── */
let chatCollapsed = false;
function toggleChatFromSidebar() {
  chatCollapsed = !chatCollapsed;
  document.getElementById('chat-ui').classList.toggle('collapsed', chatCollapsed);
  document.getElementById('chat-toggle-label').textContent = chatCollapsed ? 'Показать чат' : 'Скрыть чат';
  closeSidebar();
}
function toggleChat() {
  chatCollapsed = !chatCollapsed;
  document.getElementById('chat-ui').classList.toggle('collapsed', chatCollapsed);
}
document.getElementById('drag-handle').addEventListener('click', toggleChat);

/* ── End session ── */
function endSession() {
  if (confirm('Завершить сессию и вернуться в каталог?'))
    window.location.href = '/catalog.html';
}

/* ── Textarea auto-resize ── */
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey && window.innerWidth > 640) {
    e.preventDefault();
    if(window.send_function) { window.send_function(); }
  }
}

/* ── Load user from localStorage ── */
const u = localStorage.getItem('username') || 'Гость';
document.getElementById('sb-av').textContent = u.charAt(0).toUpperCase();
document.getElementById('sb-name').textContent = u;

function nowTime() {
  return new Date().toLocaleTimeString('ru-RU', { hour:'2-digit', minute:'2-digit' });
}

let typingEl = null;
function showTyping() {
  if(typingEl) return;
  const msgs = document.getElementById('messages');
  typingEl = document.createElement('div');
  typingEl.className = 'msg ai fade-in';
  typingEl.innerHTML = `<div class="msg-avatar" style="background:transparent; border:none; display:flex; align-items:flex-end;"></div>
    <div class="msg-bubble">
      <div class="typing-indicator" style="padding:4px">
        <div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>
      </div>
    </div>`;
  msgs.appendChild(typingEl);
  msgs.scrollTop = msgs.scrollHeight;
}
function removeTyping() {
  if (typingEl) { typingEl.remove(); typingEl = null; }
}

// User UI function mapped to old addMsg parameters
function appendMsg(text, who, timestamp) {
  const msgs = document.getElementById('messages');
  const div  = document.createElement('div');
  let role = who === 'bot' ? 'ai' : 'user';
  div.className = `msg ${role} fade-in`;
  
  if (role === 'ai') {
    div.innerHTML = `
      <div class="msg-avatar">T</div>
      <div>
        <div class="msg-bubble">${text}</div>
      </div>
      <div class="msg-time">${nowTime()}</div>`;
  } else {
    div.innerHTML = `
      <div class="msg-bubble">${text}</div>
      <div class="msg-time">${nowTime()}</div>`;
  }
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

// Map the old addMsg functionality inside the dynamic block to appendMsg
window.addMsg = appendMsg;

// Execute old send functionality wrapper
function send() {
    if(window.send_function) { window.send_function(); }
}

{CORE_JS}

// Initialize name chip when model loads:
let _chipInt = setInterval(() => {
    if(window.currentModelConfig) {
        document.getElementById('char-name-chip').textContent = window.currentModelConfig.title || window.currentModelConfig.slug;
        clearInterval(_chipInt);
    }
}, 500);
</script>
</body>
</html>""".replace("{PIXI}", pixi_scripts).replace("{VRM}", vrm_scripts).replace("{CORE_JS}", core_js).replace("{MAKE_MOUTH_LOGIC}", make_mouth_logic)

with open('templates/manga.html', 'w', encoding='utf-8') as f:
    f.write(user_html)

print("Merged perfectly!")
