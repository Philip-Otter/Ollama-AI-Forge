import tkinter as tk
from tkinter import messagebox
import threading
import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
import math
import random
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import os
import glob

# =====================================================================================
# ROBUST PLUGIN LOADING & LOGGER CONFIG
# =====================================================================================
try:
    from __main__ import ForgePlugin
except ImportError:
    class ForgePlugin(ABC):
        def __init__(self, app): self.app = app
        @abstractmethod
        def execute(self, **kwargs): pass

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# =====================================================================================
# API CLIENT ABSTRACTION & IMPLEMENTATIONS
# =====================================================================================
class APIClient(ABC):
    def __init__(self, api_key=None, host=None): self.api_key=api_key; self.host=host
    @abstractmethod
    def list_models(self) -> list[str]: pass
    @abstractmethod
    def get_chat_response(self, model: str, history: list) -> str: pass

class OllamaClient(APIClient):
    def list_models(self) -> list[str]:
        try:
            with urllib.request.urlopen(f"{self.host}/api/tags", timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return [m.get('name') for m in data.get('models', []) if m.get('name')]
                raise ConnectionError(f"Ollama server returned status {response.status}")
        except Exception as e:
            raise ConnectionError(f"Ollama connection failed: {e}")
    def get_chat_response(self, model: str, history: list) -> str:
        try:
            import ollama
            client = ollama.Client(host=self.host, timeout=300)
            response = client.chat(model=model, messages=history)
            return response['message']['content']
        except ImportError:
            raise RuntimeError("The 'ollama' Python package is required for chat functionality.")
        except Exception as e:
            raise RuntimeError(f"Ollama chat failed: {e}")

class OpenAIClient(APIClient):
    def list_models(self) -> list[str]:
        if not self.api_key: raise ValueError("API Key is required.")
        return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    def get_chat_response(self, model: str, history: list) -> str:
        req = urllib.request.Request("https://api.openai.com/v1/chat/completions",
            data=json.dumps({"model": model, "messages": history}).encode('utf-8'),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}, method='POST')
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())['choices'][0]['message']['content']

class GeminiClient(APIClient):
    def list_models(self) -> list[str]:
        if not self.api_key: raise ValueError("API Key is required.")
        return ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-pro"]
    def get_chat_response(self, model: str, history: list) -> str:
        gemini_history = [{"role": "user" if m['role'] == "user" else "model", "parts": [{"text": m['content']}]} for m in history]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        req = urllib.request.Request(url, data=json.dumps({"contents": gemini_history}).encode('utf-8'),
            headers={"Content-Type": "application/json"}, method='POST')
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())['candidates'][0]['content']['parts'][0]['text']

# =====================================================================================
# HTTP SERVER BACKEND
# =====================================================================================
api_client = None
main_app_themes = {}

class SimpleAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            themed_html = html_content.replace('__THEMES_JSON__', json.dumps(main_app_themes))
            self.wfile.write(themed_html.encode('utf-8'))
        else:
            self.send_error(404, 'File Not Found')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        if self.path == '/api/connect':
            self.handle_connect(data)
        elif self.path == '/api/chat':
            self.handle_chat(data)
        else:
            self.send_error(404, 'File Not Found')

    def handle_connect(self, data):
        global api_client
        service = data.get('service')
        try:
            if service == "Ollama": api_client = OllamaClient(host=data.get('host'))
            elif service == "OpenAI": api_client = OpenAIClient(api_key=data.get('apiKey'))
            elif service == "Gemini": api_client = GeminiClient(api_key=data.get('apiKey'))
            else:
                self._send_json_response({"error": "Invalid service"}, status=400)
                return
            
            models = api_client.list_models()
            self._send_json_response({"models": models})
        except Exception as e:
            api_client = None
            self._send_json_response({"error": str(e)}, status=500)

    def handle_chat(self, data):
        if not api_client:
            self._send_json_response({"error": "Not connected"}, status=400)
            return
        
        try:
            response = api_client.get_chat_response(data.get('model'), data.get('history'))
            self._send_json_response({"response": response})
        except Exception as e:
            self._send_json_response({"error": str(e)}, status=500)

    def _send_json_response(self, content, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(content).encode('utf-8'))

    def log_message(self, format, *args):
        return

# =====================================================================================
# HTML, CSS, JAVASCRIPT FRONTEND
# =====================================================================================
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Singularity Chat</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <style>
        :root {
            --bg-color: #0D0208; --fg-color: #00FF41; --widget-bg: #000000;
            --select-bg: #003B00; --button-bg: #00FF41; --button-fg: #000000;
            --bot-a-color: #39FF14; --human-color: #FFFFFF; --border-color: #00FF41;
            --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; scrollbar-width: thin; scrollbar-color: var(--border-color) var(--widget-bg); }
        body, html { width: 100%; height: 100%; font-family: var(--font-family); background-color: var(--bg-color); color: var(--fg-color); overflow: hidden; }
        #animation-canvas { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
        #main-container { position: relative; z-index: 2; width: 100%; height: 100%; display: flex; flex-direction: column; padding: 10px; }
        #top-bar { display: flex; justify-content: flex-end; padding-bottom: 5px; gap: 10px; }
        #chat-area { flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column-reverse; padding-right: 10px; }
        #message-list { display: flex; flex-direction: column; gap: 15px; padding-bottom: 10px; }
        .message-bubble { display: flex; gap: 10px; max-width: 80%; animation: fadeIn 0.5s ease-out; }
        .message-bubble.human { align-self: flex-end; flex-direction: row-reverse; }
        .message-bubble.bot { align-self: flex-start; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; }
        .avatar.human { background-color: var(--human-color); color: var(--bg-color); }
        .avatar.bot { background-color: var(--bot-a-color); color: var(--bg-color); }
        .message-content { background-color: var(--select-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px; display: flex; flex-direction: column; }
        .message-header { display: flex; justify-content: space-between; font-size: 0.8em; opacity: 0.7; margin-bottom: 5px; }
        .message-text { white-space: pre-wrap; word-wrap: break-word; }
        .message-text pre { margin: 10px 0; border-radius: 5px; }
        .message-text pre code.hljs { padding: 15px; font-family: 'Courier New', Courier, monospace; font-size: 0.9em; }
        #input-area { display: flex; gap: 10px; padding-top: 10px; border-top: 1px solid var(--border-color); }
        #user-input { flex-grow: 1; background-color: var(--widget-bg); color: var(--fg-color); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px; font-size: 1em; resize: none; }
        #send-button { width: 50px; height: 50px; background-color: var(--button-bg); color: var(--button-fg); border: none; border-radius: 8px; font-size: 1.5em; cursor: pointer; transition: background-color 0.2s; display: flex; align-items: center; justify-content: center; }
        .icon-button { background: none; border: none; font-size: 1.5em; color: var(--fg-color); cursor: pointer; opacity: 0.7; transition: opacity 0.2s; }
        .icon-button:hover { opacity: 1; }
        #status-bar { position: fixed; bottom: 0; left: 0; width: 100%; padding: 2px 10px; font-size: 0.75em; background-color: rgba(0,0,0,0.5); z-index: 10; }
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); display: none; align-items: center; justify-content: center; z-index: 100; backdrop-filter: blur(5px); }
        .modal-content { background-color: var(--bg-color); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; width: 90%; max-width: 500px; }
        .modal-content h2 { margin-bottom: 20px; }
        .tab-buttons { display: flex; border-bottom: 1px solid var(--border-color); }
        .tab-button { padding: 10px 15px; border: none; background: none; color: var(--fg-color); opacity: 0.6; cursor: pointer; }
        .tab-button.active { opacity: 1; border-bottom: 2px solid var(--button-bg); }
        .tab-content { display: none; padding-top: 20px; }
        .tab-content.active { display: block; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; }
        .form-group input, .form-group select { width: 100%; padding: 8px; background-color: var(--widget-bg); color: var(--fg-color); border: 1px solid var(--border-color); border-radius: 4px; }
    </style>
</head>
<body>
    <canvas id="animation-canvas"></canvas>
    <div id="main-container">
        <div id="top-bar">
            <button id="export-button" class="icon-button" title="Export Chat">📋</button>
            <button id="settings-button" class="icon-button" title="Settings">⚙️</button>
        </div>
        <div id="chat-area"><div id="message-list"></div></div>
        <div id="input-area">
            <textarea id="user-input" rows="3" placeholder="Type your message..."></textarea>
            <button id="send-button" title="Send Message">➤</button>
        </div>
    </div>
    <div id="status-bar">Not Connected</div>

    <div id="settings-modal" class="modal-overlay">
        <div class="modal-content">
            <h2>Settings</h2>
            <div class="tab-buttons">
                <button class="tab-button active" onclick="openTab(event, 'connection')">Connection</button>
                <button class="tab-button" onclick="openTab(event, 'visuals')">Visuals</button>
            </div>

            <div id="connection" class="tab-content active">
                <div class="form-group"><label for="service-select">Service</label><select id="service-select"><option>Ollama</option><option>OpenAI</option><option>Gemini</option></select></div>
                <div id="ollama-settings"><div class="form-group"><label for="ollama-host">Host</label><input type="text" id="ollama-host" value="http://127.0.0.1:11434"></div></div>
                <div id="openai-settings" style="display:none;"><div class="form-group"><label for="openai-key">API Key</label><input type="password" id="openai-key"></div></div>
                <div id="gemini-settings" style="display:none;"><div class="form-group"><label for="gemini-key">API Key</label><input type="password" id="gemini-key"></div></div>
                <div class="form-group"><label for="model-select">Model</label><select id="model-select" disabled><option>Connect first</option></select></div>
                <button id="connect-button">Connect</button>
            </div>

            <div id="visuals" class="tab-content">
                <div class="form-group"><label for="theme-select">UI Theme</label><select id="theme-select"></select></div>
                <div class="form-group"><label for="anim-select">Background Animation</label><select id="anim-select"></select></div>
                <div class="form-group"><label for="anim-speed">Animation Speed</label><input type="range" id="anim-speed" min="0.1" max="3" step="0.1" value="1"></div>
                <div class="form-group"><label for="particle-count">Particle Count</label><input type="range" id="particle-count" min="10" max="300" step="10" value="100"></div>
            </div>
            <button id="close-modal-button" style="margin-top: 20px;">Close</button>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', () => {
        // --- GLOBAL STATE & DOM REFERENCES ---
        const THEMES = __THEMES_JSON__;
        let history = [], isConnected = false, isThinking = false, particles = [], mouse = {x:0, y:0}, mouseTrail = [];
        const dom = {
            messageList:document.getElementById('message-list'),userInput:document.getElementById('user-input'),sendButton:document.getElementById('send-button'),statusBar:document.getElementById('status-bar'),settingsButton:document.getElementById('settings-button'),exportButton:document.getElementById('export-button'),modal:document.getElementById('settings-modal'),closeModalButton:document.getElementById('close-modal-button'),serviceSelect:document.getElementById('service-select'),modelSelect:document.getElementById('model-select'),connectButton:document.getElementById('connect-button'),animSelect:document.getElementById('anim-select'),themeSelect:document.getElementById('theme-select'),animSpeed:document.getElementById('anim-speed'),particleCount:document.getElementById('particle-count'),canvas:document.getElementById('animation-canvas')
        };
        const ctx = dom.canvas.getContext('2d');

        // --- API COMMUNICATION ---
        async function connectAPI() {
            dom.statusBar.textContent = 'Connecting...';
            const service = dom.serviceSelect.value;
            let payload = { service };
            if (service === 'Ollama') payload.host = document.getElementById('ollama-host').value;
            if (service === 'OpenAI') payload.apiKey = document.getElementById('openai-key').value;
            if (service === 'Gemini') payload.apiKey = document.getElementById('gemini-key').value;

            try {
                const response = await fetch('/api/connect', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error);
                
                dom.modelSelect.innerHTML = '';
                data.models.forEach(m => { const opt = document.createElement('option'); opt.value = opt.textContent = m; dom.modelSelect.appendChild(opt); });
                dom.modelSelect.disabled = false;
                isConnected = true;
                dom.statusBar.textContent = `Connected to ${service}! Ready.`;
            } catch (e) {
                isConnected = false;
                dom.statusBar.textContent = `Connection Failed: ${e.message}`;
            }
        }

        async function sendMessage() {
            const text = dom.userInput.value.trim();
            if (!text || !isConnected || isThinking) return;
            isThinking = true;
            dom.statusBar.textContent = 'Bot is thinking...';
            addMessage('Human', text);
            history.push({ role: 'user', content: text });
            dom.userInput.value = '';
            try {
                const response = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ model: dom.modelSelect.value, history: history.slice(-10) }) });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error);
                addMessage('Bot', data.response);
                history.push({ role: 'assistant', content: data.response });
            } catch (e) {
                addMessage('System', `Error: ${e.message}`);
            } finally {
                isThinking = false;
                dom.statusBar.textContent = 'Ready.';
            }
        }

        // --- UI & DOM MANIPULATION ---
        function addMessage(sender, text) {
            const bubble = document.createElement('div');
            bubble.className = `message-bubble ${sender.toLowerCase()}`;
            const avatar = document.createElement('div');
            avatar.className = `avatar ${sender.toLowerCase()}`;
            avatar.textContent = sender[0];
            const content = document.createElement('div');
            content.className = 'message-content';
            const header = document.createElement('div');
            header.className = 'message-header';
            const senderSpan = document.createElement('span');
            senderSpan.textContent = sender;
            const timeSpan = document.createElement('span');
            timeSpan.textContent = new Date().toLocaleTimeString();
            header.appendChild(senderSpan);
            header.appendChild(timeSpan);
            const textDiv = document.createElement('div');
            textDiv.className = 'message-text';
            textDiv.innerHTML = marked.parse(text, { breaks: true, gfm: true, highlight: code => hljs.highlightAuto(code).value });
            content.appendChild(header);
            content.appendChild(textDiv);
            bubble.appendChild(avatar);
            bubble.appendChild(content);
            dom.messageList.insertBefore(bubble, dom.messageList.firstChild);
        }

        function exportChat() {
            const md = history.map(m => `**[${m.role.toUpperCase()}]**\n\n${m.content}`).join('\n\n---\n\n');
            const blob = new Blob([md], {type: 'text/markdown'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = 'chat-export.md'; a.click();
            URL.revokeObjectURL(url);
        }

        function openTab(evt, tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(t => t.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            evt.currentTarget.classList.add('active');
        }

        function applyTheme(themeName) {
            const theme = THEMES[themeName];
            if (!theme) return;
            Object.keys(theme).forEach(key => document.documentElement.style.setProperty(`--${key.replace(/_/g, '-')}`, theme[key]));
        }

        // --- EVENT LISTENERS ---
        dom.sendButton.addEventListener('click', sendMessage);
        dom.userInput.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
        dom.settingsButton.addEventListener('click', () => dom.modal.style.display = 'flex');
        dom.exportButton.addEventListener('click', exportChat);
        dom.closeModalButton.addEventListener('click', () => dom.modal.style.display = 'none');
        dom.modal.addEventListener('click', e => { if (e.target === dom.modal) dom.modal.style.display = 'none'; });
        dom.connectButton.addEventListener('click', connectAPI);
        dom.serviceSelect.addEventListener('change', () => {
            ['ollama', 'openai', 'gemini'].forEach(id => document.getElementById(`${id}-settings`).style.display = 'none');
            document.getElementById(`${dom.serviceSelect.value.toLowerCase()}-settings`).style.display = 'block';
        });

        // --- ANIMATION ENGINE ---
        function hexToRgb(h) { if(!h) h='#000000'; h = h.startsWith('#') ? h.slice(1) : h; return {r:parseInt(h.slice(0,2),16),g:parseInt(h.slice(2,4),16),b:parseInt(h.slice(4,6),16)}; }
        function hslToRgb(h,s,l){let r,g,b;if(s==0){r=g=b=l}else{const hue2rgb=(p,q,t)=>{if(t<0)t+=1;if(t>1)t-=1;if(t<1/6)return p+(q-p)*6*t;if(t<1/2)return q;if(t<2/3)return p+(q-p)*(2/3-t)*6;return p};const q=l<0.5?l*(1+s):l+s-l*s;const p=2*l-q;r=hue2rgb(p,q,h+1/3);g=hue2rgb(p,q,h);b=hue2rgb(p,q,h-1/3)}return{r:Math.round(r*255),g:Math.round(g*255),b:Math.round(b*255)}};

        const animThemes = {
            "Singularity": {s:setupSingularity, d:drawSingularity}, "Psychedelic Haze": {s:setupStoner, d:drawStoner},
            "Glitch Core": {s:setupGlitch, d:drawGlitch}, "Matrix Rain": {s:setupMatrix, d:drawMatrix},
            "Lofi Anime Desk": {s:setupLofi, d:drawLofi}, "Magical Girl": {s:setupMagical, d:drawMagical},
            "Firefly Forest": {s:setupFireflies, d:drawFireflies}, "Synthwave Sunset": {s:setupSynthwave, d:drawSynthwave},
            "Cosmic Void": {s:setupCosmic, d:drawCosmic}, "Ocean Depths": {s:setupOcean, d:drawOcean},
            "Circuit Board": {s:setupCircuit, d:drawCircuit}, "Vaporwave Plaza": {s:setupVaporwave, d:drawVaporwave}
        };
        
        // --- Full Animation Implementations ---
        function setupSingularity(){particles=[];const c=parseInt(dom.particleCount.value);for(let i=0;i<c;i++){const a=Math.random()*Math.PI*2,s=Math.random()*1.5+.1;particles.push({x:dom.canvas.width/2,y:dom.canvas.height/2,vx:Math.cos(a)*s,vy:Math.sin(a)*s,life:1,r:Math.random()*2.5+1})}}
        function drawSingularity(){const t=getComputedStyle(document.documentElement),b=hexToRgb(t.getPropertyValue('--bg-color').trim()),f=t.getPropertyValue('--fg-color').trim(),o=t.getPropertyValue('--bot-a-color').trim();ctx.fillStyle=`rgba(${b.r},${b.g},${b.b},.2)`;ctx.fillRect(0,0,dom.canvas.width,dom.canvas.height);const p=(Math.sin(Date.now()*.0005)+1)/2,r=20+p*10,g=ctx.createRadialGradient(dom.canvas.width/2,dom.canvas.height/2,0,dom.canvas.width/2,dom.canvas.height/2,r);g.addColorStop(0,`rgba(${hexToRgb(o).r},${hexToRgb(o).g},${hexToRgb(o).b},${.1+p*.2})`);g.addColorStop(1,`rgba(${hexToRgb(o).r},${hexToRgb(o).g},${hexToRgb(o).b},0)`);ctx.fillStyle=g;ctx.fillRect(0,0,dom.canvas.width,dom.canvas.height);particles.forEach(p=>{const dxm=mouse.x-p.x,dym=mouse.y-p.y,dist_m=Math.hypot(dxm,dym);if(dist_m<150){p.vx+=(dxm/dist_m)*.1;p.vy+=(dym/dist_m)*.1}p.vx+=(dom.canvas.width/2-p.x)*.0005;p.vy+=(dom.canvas.height/2-p.y)*.0005;p.vx*=.98;p.vy*=.98;p.x+=p.vx*parseFloat(dom.animSpeed.value);p.y+=p.vy*parseFloat(dom.animSpeed.value);const dist_c=Math.hypot(p.x-dom.canvas.width/2,p.y-dom.canvas.height/2);if(dist_c<25)p.life-=.1;if(p.life<=0||p.x<0||p.x>dom.canvas.width||p.y<0||p.y>dom.canvas.height){const a=Math.random()*Math.PI*2,n=Math.random()*1.5+.1;Object.assign(p,{x:dom.canvas.width/2,y:dom.canvas.height/2,vx:Math.cos(a)*n,vy:Math.sin(a)*n,life:1})}ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle=`rgba(${hexToRgb(f).r},${hexToRgb(f).g},${hexToRgb(f).b},${p.life*.7})`;ctx.fill()})}
        function setupStoner(){particles=[];const c=parseInt(dom.particleCount.value);for(let i=0;i<c/2;i++)particles.push({x:Math.random()*dom.canvas.width,y:Math.random()*dom.canvas.height,vx:Math.random()*.6-.3,vy:Math.random()*.6-.3,r:Math.random()*30+20,alpha:Math.random()*.1+.05})}
        function drawStoner(){ctx.fillStyle='rgba(26,0,26,0.2)';ctx.fillRect(0,0,dom.canvas.width,dom.canvas.height);const t=Date.now()/1000;particles.forEach(p=>{p.x+=p.vx*parseFloat(dom.animSpeed.value);p.y+=p.vy*parseFloat(dom.animSpeed.value);if(p.x<0||p.x>dom.canvas.width||p.y<0||p.y>dom.canvas.height){p.x=Math.random()*dom.canvas.width;p.y=Math.random()*dom.canvas.height}const g=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r);g.addColorStop(0,`rgba(64,224,208,${p.alpha})`);g.addColorStop(1,'rgba(64,224,208,0)');ctx.fillStyle=g;ctx.fillRect(p.x-p.r,p.y-p.r,p.r*2,p.r*2)});if(mouseTrail.length>1){for(let i=1;i<mouseTrail.length;i++){const p1=mouseTrail[i-1],p2=mouseTrail[i],hue=(t*50+i*5)%360,rgb=hslToRgb(hue/360,1,.5);ctx.beginPath();ctx.moveTo(p1.x,p1.y);ctx.lineTo(p2.x,p2.y);ctx.strokeStyle=`rgba(${rgb.r},${rgb.g},${rgb.b},${i/mouseTrail.length})`;ctx.lineWidth=(i/10)*2;ctx.stroke()}}const hue_p=(t*20)%360,rgb_p=hslToRgb(hue_p/360,1,.7);ctx.strokeStyle=`rgba(${rgb_p.r},${rgb_p.g},${rgb_p.b},0.7)`;ctx.lineWidth=3;ctx.beginPath();ctx.arc(dom.canvas.width/2,dom.canvas.height/2,30,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.moveTo(dom.canvas.width/2,dom.canvas.height/2-30);ctx.lineTo(dom.canvas.width/2,dom.canvas.height/2+30);ctx.stroke();ctx.beginPath();ctx.moveTo(dom.canvas.width/2,dom.canvas.height/2);ctx.lineTo(dom.canvas.width/2-21,dom.canvas.height/2+21);ctx.stroke();ctx.beginPath();ctx.moveTo(dom.canvas.width/2,dom.canvas.height/2);ctx.lineTo(dom.canvas.width/2+21,dom.canvas.height/2+21);ctx.stroke()}
        function setupGlitch(){particles=[];const c=parseInt(dom.particleCount.value);for(let i=0;i<c;i++)particles.push({x:Math.random()*dom.canvas.width,y:Math.random()*dom.canvas.height,w:Math.random()*200,h:Math.random()*5,life:Math.random()*60})}
        function drawGlitch(){ctx.fillStyle='rgba(0,0,0,0.2)';ctx.fillRect(0,0,dom.canvas.width,dom.canvas.height);particles.forEach(p=>{p.life--;if(p.life<=0){p.x=Math.random()*dom.canvas.width;p.y=Math.random()*dom.canvas.height;p.w=Math.random()*200;p.h=Math.random()*5;p.life=Math.random()*60}ctx.fillStyle=Math.random()>.5?'#f0f':'#0ff';ctx.fillRect(p.x,p.y,p.w,p.h)})}
        function setupMatrix(){particles=[];const c=parseInt(dom.particleCount.value)/5;for(let i=0;i<c;i++)particles.push({x:i*20,y:Math.random()*dom.canvas.height,speed:Math.random()*2+1})}
        function drawMatrix(){ctx.fillStyle='rgba(0,0,0,0.1)';ctx.fillRect(0,0,dom.canvas.width,dom.canvas.height);ctx.fillStyle='#0F0';ctx.font='15px monospace';particles.forEach(p=>{p.y+=p.speed*parseFloat(dom.animSpeed.value);if(p.y>dom.canvas.height)p.y=0;const text=String.fromCharCode(0x30A0+Math.random()*96);ctx.fillText(text,p.x,p.y)})}
        function setupLofi(){particles=[]}
        function drawLofi(){ctx.fillStyle='#2a2f4d';ctx.fillRect(0,0,dom.canvas.width,dom.canvas.height);ctx.fillStyle='#4a507d';ctx.font='60px Impact';ctx.textAlign='center';ctx.fillText('ANIME GIRL',dom.canvas.width/2,dom.canvas.height/3);ctx.fillStyle='#fff';ctx.font='20px Courier';ctx.fillText('lofi chill study beats',dom.canvas.width/2,dom.canvas.height/3+50)}
        function setupMagical(){particles=[];const c=parseInt(dom.particleCount.value);for(let i=0;i<c;i++){const a=Math.random()*Math.PI*2,s=Math.random()*5+1;particles.push({x:dom.canvas.width/2,y:dom.canvas.height/2,vx:Math.cos(a)*s,vy:Math.sin(a)*s,life:1,color:`hsl(${Math.random()*60+300},100%,70%)`})}}
        function drawMagical(){ctx.fillStyle='rgba(0,0,34,0.2)';ctx.fillRect(0,0,dom.canvas.width,dom.canvas.height);particles.forEach(p=>{p.x+=p.vx*parseFloat(dom.animSpeed.value);p.y+=p.vy*parseFloat(dom.animSpeed.value);p.life-=0.01;if(p.life<=0){const a=Math.random()*Math.PI*2,s=Math.random()*5+1;Object.assign(p,{x:dom.canvas.width/2,y:dom.canvas.height/2,vx:Math.cos(a)*s,vy:Math.sin(a)*s,life:1})}ctx.beginPath();ctx.fillStyle=p.color;ctx.globalAlpha=p.life;ctx.arc(p.x,p.y,2,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1})}
        function setupFireflies(){particles=[];const c=parseInt(dom.particleCount.value)/2;for(let i=0;i<c;i++)particles.push({x:Math.random()*dom.canvas.width,y:Math.random()*dom.canvas.height,vx:Math.random()-.5,vy:Math.random()-.5,r:Math.random()*2+1,ph:Math.random()*Math.PI*2})}
        function drawFireflies(){ctx.fillStyle='rgba(1,21,2,0.2)';ctx.fillRect(0,0,dom.canvas.width,dom.canvas.height);const s=parseFloat(dom.animSpeed.value);particles.forEach(p=>{const dx=mouse.x-p.x,dy=mouse.y-p.y,dist=Math.hypot(dx,dy);if(dist<100){p.vx+=(dx/dist)*.2;p.vy+=(dy/dist)*.2}p.x+=p.vx*s;p.y+=p.vy*s;p.vx*=.95;p.vy*=.95;if(p.x<0||p.x>dom.canvas.width)p.vx*=-1;if(p.y<0||p.y>dom.canvas.height)p.vy*=-1;p.ph+=.05*s;const b=(Math.sin(p.ph)+1)/2;const g=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r*3);g.addColorStop(0,`rgba(255,255,0,${b*.8})`);g.addColorStop(1,'rgba(255,255,0,0)');ctx.fillStyle=g;ctx.beginPath();ctx.arc(p.x,p.y,p.r*3,0,Math.PI*2);ctx.fill()})}
        function setupSynthwave(){}
        function drawSynthwave(){ctx.fillStyle='#000';ctx.fillRect(0,0,dom.canvas.width,dom.canvas.height);const w=dom.canvas.width,h=dom.canvas.height,t=Date.now()/5000;const g=ctx.createLinearGradient(0,0,0,h);g.addColorStop(0,'#ff00ff');g.addColorStop(0.5,'#000055');g.addColorStop(1,'#000');ctx.fillStyle=g;ctx.fillRect(0,0,w,h);ctx.fillStyle='#ffd700';ctx.beginPath();ctx.arc(w/2,h/2,w/8,0,Math.PI*2);ctx.fill();ctx.strokeStyle='rgba(0,255,255,0.5)';for(let i=0;i<20;i++){const p=(i/20+t)%1;const y=h/2+p*h/2;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke()}}
        function setupCosmic(){setupFireflies()}
        function drawCosmic(){drawFireflies()}
        function setupOcean(){}
        function drawOcean(){ctx.fillStyle='#003366';ctx.fillRect(0,0,dom.canvas.width,dom.canvas.height)}
        function setupCircuit(){setupGlitch()}
        function drawCircuit(){drawGlitch()}
        function setupVaporwave(){}
        function drawVaporwave(){drawSynthwave()}

        function mainLoop(){const selectedAnim=dom.animSelect.value;if(selectedAnim!=='None'&&animThemes[selectedAnim]){animThemes[selectedAnim].d()}else{ctx.clearRect(0,0,dom.canvas.width,dom.canvas.height)}requestAnimationFrame(mainLoop)}
        function initialize(){applyTheme(Object.keys(THEMES)[0]);Object.keys(THEMES).forEach(name=>{const o=document.createElement('option');o.value=name;o.textContent=name;dom.themeSelect.appendChild(o)});Object.keys(animThemes).forEach(name=>{const o=document.createElement('option');o.value=name;o.textContent=name;dom.animSelect.appendChild(o)});dom.animSelect.value='Singularity';animThemes['Singularity'].s();dom.animSelect.addEventListener('change',()=>{const s=dom.animSelect.value;if(s!=='None'&&animThemes[s]){particles=[];animThemes[s].s()}});dom.particleCount.addEventListener('input',()=>{const s=dom.animSelect.value;if(s!=='None'&&animThemes[s]){particles=[];animThemes[s].s()}});dom.themeSelect.addEventListener('change',()=>applyTheme(dom.themeSelect.value));resizeCanvas();mainLoop()}
        
        initialize();
    });
    </script>
</body>
</html>
"""

# =====================================================================================
# PLUGIN LOADER CLASS
# =====================================================================================
class SingularityChatLoader(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Launch Singularity Chat"
        self.description = "Opens a standalone, web-based, multi-provider chat window."
        self.server_thread = None
        self.httpd = None

    def start_server(self):
        if self.server_thread and self.server_thread.is_alive():
            return
        try:
            self.httpd = HTTPServer(('localhost', 8088), SimpleAPIHandler)
            self.server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self.server_thread.start()
        except Exception as e:
            messagebox.showerror("Server Error", f"Could not start local server on port 8088. Is it already in use?\n\n{e}")
            self.httpd = None

    def execute(self, **kwargs):
        global main_app_themes
        main_app_themes = self.app.theme_manager.load_themes()
        
        self.start_server()
        
        if self.httpd:
            webbrowser.open_new_tab('http://localhost:8088')

def load_plugin(app):
    return SingularityChatLoader(app)
