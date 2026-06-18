# ============================================================
# 🚀 AKIRA CTX - COMPLETE SERVER (All-in-One)
# ============================================================

from flask import Flask, render_template_string, request, jsonify, session
from flask_cors import CORS
import subprocess
import os
import threading
import time
import tempfile
import ctypes
import sys
import winreg
import psutil
import requests
import json
import random
import base64
import hashlib
import re
from datetime import datetime, timedelta
from functools import wraps

# ============================================================
# 📦 INITIALIZATION
# ============================================================
app = Flask(__name__)
app.secret_key = "AKIRA_CTX_SECRET_KEY_2026_SUPER_SECURE"
CORS(app)

# Toggle to disable authentication checks (useful when removing login UI)
DISABLE_AUTH = True

# Global state
APP_VERSION = "1.0.0"
APP_NAME = "AKIRA CTX"

# ============================================================
# 💾 DATABASE (In-Memory - For Demo)
# ============================================================
class Database:
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.licenses = {}
        self.logs = []
    
    def add_user(self, username, password_hash, license_key, expiry_days=30):
        self.users[username] = {
            'password': password_hash,
            'license': license_key,
            'created': int(time.time()),
            'expiry': int(time.time()) + (expiry_days * 86400),
            'last_login': None,
            'ip': None,
            'hwid': None
        }
        return True
    
    def get_user(self, username):
        return self.users.get(username)
    
    def user_exists(self, username):
        return username in self.users
    
    def verify_password(self, username, password):
        user = self.get_user(username)
        if not user:
            return False
        return user['password'] == hashlib.sha256(password.encode()).hexdigest()
    
    def create_session(self, username):
        token = base64.b64encode(f"{username}:{int(time.time())}:{random.randint(1000,9999)}".encode()).decode()
        self.sessions[token] = {
            'username': username,
            'created': int(time.time()),
            'expiry': int(time.time()) + 86400
        }
        return token
    
    def verify_session(self, token):
        session_data = self.sessions.get(token)
        if not session_data:
            return None
        if session_data['expiry'] < int(time.time()):
            del self.sessions[token]
            return None
        return session_data['username']
    
    def revoke_session(self, token):
        if token in self.sessions:
            del self.sessions[token]
    
    def log(self, action, username="system", details=""):
        self.logs.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'username': username,
            'details': details
        })

db = Database()

# ============================================================
# 🔐 SECURITY & PROTECTION
# ============================================================
class SecurityManager:
    @staticmethod
    def check_debugger():
        try:
            if sys.gettrace() is not None:
                return True
            if hasattr(sys, 'gettrace') and sys.gettrace():
                return True
            if ctypes.windll.kernel32.IsDebuggerPresent():
                return True
            debuggers = ['ollydbg', 'x64dbg', 'cheatengine', 'windbg', 'ida', 'debug']
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name'].lower()
                    for dbg in debuggers:
                        if dbg in name:
                            return True
                except:
                    pass
        except:
            pass
        return False
    
    @staticmethod
    def check_vm():
        try:
            vm_processes = ['vbox', 'vmware', 'qemu', 'xenserver', 'parallels']
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name'].lower()
                    for vm in vm_processes:
                        if vm in name:
                            return True
                except:
                    pass
            try:
                import wmi
                c = wmi.WMI()
                for disk in c.Win32_DiskDrive():
                    model = str(disk.Model).lower()
                    if any(vm in model for vm in ['virtual', 'vbox', 'vmware', 'qemu']):
                        return True
                for bios in c.Win32_BIOS():
                    if 'virtual' in str(bios.SerialNumber).lower():
                        return True
            except:
                pass
        except:
            pass
        return False
    
    @staticmethod
    def check_integrity():
        return True
    
    @staticmethod
    def check_blacklist():
        blacklisted = ['cheatengine', 'ollydbg', 'x64dbg', 'processhacker']
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name'].lower()
                for bad in blacklisted:
                    if bad in name:
                        return True
            except:
                pass
        return False
    
    @staticmethod
    def anti_bruteforce(username, ip):
        return True

# ============================================================
# 🔑 AUTHENTICATION SYSTEM
# ============================================================
class AuthSystem:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def validate_username(username):
        if len(username) < 3 or len(username) > 20:
            return False
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False
        return True
    
    @staticmethod
    def validate_password(password):
        return len(password) >= 6
    
    @staticmethod
    def validate_license(license_key):
        if len(license_key) < 8:
            return False
        if not re.match(r'^[A-Z0-9]{8,}$', license_key.upper()):
            return False
        return True
    
    @staticmethod
    def generate_license():
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        parts = [''.join(random.choice(chars) for _ in range(4)) for _ in range(4)]
        return '-'.join(parts)

class KeyAuthAPI:
    def __init__(self):
        self.app_name = "Ooyahya57's Application"
        self.owner_id = "vfvwjRpq4b"
        self.version = "1.0"
    
    def login(self, username, password, hwid="", ip=""):
        if not AuthSystem.validate_username(username):
            return {'success': False, 'message': 'Invalid username!'}
        if not AuthSystem.validate_password(password):
            return {'success': False, 'message': 'Invalid password!'}
        
        user = db.get_user(username)
        if not user:
            return {'success': False, 'message': 'User not found!'}
        if not db.verify_password(username, password):
            return {'success': False, 'message': 'Invalid password!'}
        if user['expiry'] < int(time.time()):
            return {'success': False, 'message': 'License expired!'}
        
        user['last_login'] = int(time.time())
        user['ip'] = ip
        user['hwid'] = hwid
        token = db.create_session(username)
        db.log('login', username, f"IP: {ip}")
        
        return {
            'success': True,
            'message': f'Welcome {username}!',
            'token': token,
            'expiry': user['expiry']
        }
    
    def register(self, username, password, license_key, hwid="", ip=""):
        if not AuthSystem.validate_username(username):
            return {'success': False, 'message': 'Invalid username! (3-20 chars, a-z, 0-9, _)'}
        if db.user_exists(username):
            return {'success': False, 'message': 'Username already exists!'}
        if not AuthSystem.validate_password(password):
            return {'success': False, 'message': 'Password must be at least 6 characters!'}
        if not AuthSystem.validate_license(license_key):
            return {'success': False, 'message': 'Invalid license key!'}
        
        password_hash = AuthSystem.hash_password(password)
        db.add_user(username, password_hash, license_key)
        db.log('register', username, f"IP: {ip}, License: {license_key}")
        
        return {'success': True, 'message': 'Registration successful!'}
    
    def verify(self, token):
        username = db.verify_session(token)
        if username:
            return {'success': True, 'username': username, 'message': 'Session valid'}
        return {'success': False, 'message': 'Session expired or invalid'}

keyauth = KeyAuthAPI()

# ============================================================
# 🎮 FEATURE MANAGER
# ============================================================
class FeatureManager:
    def __init__(self):
        self.features = {
            'aimbot_ai': {'enabled': False, 'description': 'AI Aimbot'},
            'aimbot_nike': {'enabled': False, 'description': 'Nike Aimbot'},
            'scope_2': {'enabled': False, 'description': 'Scope 2'},
            'scope_4': {'enabled': False, 'description': 'Scope 4'},
            'switch_awm': {'enabled': False, 'description': 'AWM Switch'},
            'sniper': {'enabled': False, 'description': 'Sniper No Scope'},
            'amo_akira': {'enabled': False, 'description': 'Amo Akira'},
            'amo_awm': {'enabled': False, 'description': 'Amo AWM'},
            'chams_menu': {'enabled': False, 'description': 'Chams Menu'},
            'fix_chams': {'enabled': False, 'description': 'Fix Chams'},
            'streamer': {'enabled': False, 'description': 'Streamer Mode'},
            'block_internet': {'enabled': False, 'description': 'Block Internet'}
        }
        self.emulator_processes = ["HD-Player.exe", "ProjectTitan.exe", "Nox.exe"]
    
    def get_emulator_pid(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in self.emulator_processes:
                    return proc.info['pid']
            except:
                pass
        return None
    
    def write_memory(self, pid, address, data):
        print(f"[MEMORY] Writing to PID {pid} at address {hex(address)}")
        return True
    
    def activate_feature(self, feature_name):
        if feature_name not in self.features:
            return False
        self.features[feature_name]['enabled'] = True
        pid = self.get_emulator_pid()
        if pid:
            print(f"[FEATURE] Activating {feature_name} on PID {pid}")
        db.log('feature_activated', 'system', f"{feature_name}")
        return True
    
    def deactivate_feature(self, feature_name):
        if feature_name not in self.features:
            return False
        self.features[feature_name]['enabled'] = False
        db.log('feature_deactivated', 'system', f"{feature_name}")
        return True
    
    def block_emulator_internet(self):
        paths = [
            r"%ProgramFiles%\BlueStacks_nxt\HD-Player.exe",
            r"%ProgramFiles%\BlueStacks\HD-Player.exe",
        ]
        for path in paths:
            expanded = os.path.expandvars(path)
            if os.path.exists(expanded):
                subprocess.run(
                    f'netsh advfirewall firewall add rule name="AKIRA_Block" dir=in action=block program="{expanded}"',
                    shell=True, capture_output=True
                )
        return True
    
    def unblock_emulator_internet(self):
        subprocess.run('netsh advfirewall firewall delete rule name="AKIRA_Block"', shell=True, capture_output=True)
        return True
    
    def fake_lag(self, duration=2):
        def run():
            self.block_emulator_internet()
            time.sleep(duration)
            self.unblock_emulator_internet()
        threading.Thread(target=run, daemon=True).start()
        return True
    
    def clean_temp(self):
        temp_dirs = [tempfile.gettempdir(), os.path.expandvars("%TEMP%"), os.path.expandvars("%WINDIR%\\Temp")]
        for td in temp_dirs:
            if os.path.exists(td):
                try:
                    for root, dirs, files in os.walk(td):
                        for f in files:
                            try:
                                os.remove(os.path.join(root, f))
                            except:
                                pass
                except:
                    pass
        return True
    
    def optimize_system(self):
        try:
            subprocess.run('ipconfig /flushdns', shell=True, capture_output=True)
            prefetch_path = os.path.expandvars("%WINDIR%\\Prefetch")
            if os.path.exists(prefetch_path):
                for f in os.listdir(prefetch_path):
                    if f.endswith('.pf'):
                        try:
                            os.remove(os.path.join(prefetch_path, f))
                        except:
                            pass
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
                winreg.CloseKey(key)
            except:
                pass
        except:
            pass
        return True

feature_manager = FeatureManager()

# ============================================================
# 🌟 PARTICLES SYSTEM
# ============================================================
class ParticlesSystem:
    @staticmethod
    def generate(particle_type="storm", count=50):
        particles = []
        for i in range(count):
            p = {
                'x': random.randint(0, 1920),
                'y': random.randint(0, 1080),
                'size': random.randint(2, 8),
                'speed': random.random() * 2 + 0.5,
                'alpha': random.random() * 0.8 + 0.2,
                'id': i
            }
            if particle_type == "storm":
                p['color'] = f"hsl({random.randint(0, 60)}, 100%, 50%)"
                p['size'] = random.randint(3, 10)
            elif particle_type == "dots":
                p['color'] = f"rgba(255,255,255,{p['alpha']})"
            elif particle_type == "squares":
                p['color'] = f"rgba(255,0,0,{p['alpha']})"
                p['size'] = random.randint(4, 12)
            elif particle_type == "triangles":
                p['color'] = f"rgba(0,150,255,{p['alpha']})"
                p['size'] = random.randint(3, 10)
            else:
                p['color'] = f"rgba(255,0,0,{p['alpha']})"
            particles.append(p)
        return particles

# ============================================================
# 🛡️ DECORATORS
# ============================================================
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if DISABLE_AUTH:
            return f(*args, **kwargs)

        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            token = session.get('token', '')
        if not token or not db.verify_session(token):
            return jsonify({'success': False, 'message': 'Authentication required!'}), 401
        return f(*args, **kwargs)
    return decorated_function

def security_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if SecurityManager.check_debugger():
            return jsonify({'success': False, 'message': 'Debugger detected!'}), 403
        if SecurityManager.check_vm():
            return jsonify({'success': False, 'message': 'Virtual Machine detected!'}), 403
        if SecurityManager.check_blacklist():
            return jsonify({'success': False, 'message': 'Blacklisted software detected!'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# 🌐 API ENDPOINTS
# ============================================================
@app.route('/api/login', methods=['POST'])
@security_check
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    hwid = data.get('hwid', '')
    ip = request.remote_addr
    result = keyauth.login(username, password, hwid, ip)
    if result['success']:
        session['token'] = result['token']
        session['username'] = username
        db.log('api_login', username, f"IP: {ip}")
    return jsonify(result)

@app.route('/api/register', methods=['POST'])
@security_check
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    license_key = data.get('license', '').strip()
    hwid = data.get('hwid', '')
    ip = request.remote_addr
    result = keyauth.register(username, password, license_key, hwid, ip)
    return jsonify(result)

@app.route('/api/verify', methods=['GET'])
def verify():
    token = session.get('token', '')
    if not token:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
    return jsonify(keyauth.verify(token))

@app.route('/api/logout', methods=['POST'])
@require_auth
def logout():
    token = session.get('token', '')
    db.revoke_session(token)
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out!'})

@app.route('/api/features', methods=['GET'])
@require_auth
def get_features():
    return jsonify(feature_manager.features)

@app.route('/api/feature/<feature_name>', methods=['POST'])
@require_auth
def toggle_feature(feature_name):
    data = request.json
    enabled = data.get('enabled', False)
    if feature_name not in feature_manager.features:
        return jsonify({'success': False, 'message': 'Feature not found!'})
    if enabled:
        success = feature_manager.activate_feature(feature_name)
    else:
        success = feature_manager.deactivate_feature(feature_name)
    return jsonify({
        'success': success,
        'feature': feature_name,
        'enabled': enabled,
        'message': f'{feature_name} {"activated" if enabled else "deactivated"}'
    })

@app.route('/api/fake_lag', methods=['POST'])
@require_auth
def fake_lag():
    data = request.json
    duration = data.get('duration', 2)
    feature_manager.fake_lag(duration)
    return jsonify({'success': True, 'duration': duration, 'message': f'Fake Lag {duration}s'})

@app.route('/api/clean_temp', methods=['POST'])
@require_auth
def clean_temp():
    feature_manager.clean_temp()
    return jsonify({'success': True, 'message': 'Temp cleaned!'})

@app.route('/api/optimize', methods=['POST'])
@require_auth
def optimize():
    feature_manager.optimize_system()
    return jsonify({'success': True, 'message': 'System optimized!'})

@app.route('/api/particles/<particle_type>', methods=['GET'])
def get_particles(particle_type):
    count = int(request.args.get('count', 50))
    return jsonify(ParticlesSystem.generate(particle_type, count))

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'version': APP_VERSION,
        'name': APP_NAME,
        'uptime': time.time() - app.config.get('start_time', time.time()),
        'users': len(db.users),
        'sessions': len(db.sessions)
    })

# ============================================================
# 📄 HTML + CSS + JS (All in One)
# ============================================================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AKIRA CTX - VIP Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        /* ============================================================
           RESET & VARIABLES
           ============================================================ */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Poppins', sans-serif;
        }
        :root {
            --bg-primary: #0a0a0a;
            --bg-secondary: #111111;
            --bg-card: rgba(20, 20, 30, 0.9);
            --text-primary: #ffffff;
            --text-secondary: #aaaaaa;
            --accent: #ff0000;
            --accent-glow: rgba(255, 0, 0, 0.3);
            --border-color: rgba(255, 0, 0, 0.15);
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
        }
        body {
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow: hidden;
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: var(--bg-secondary); }
        ::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 10px; }

        /* ============================================================
           PARTICLES CANVAS
           ============================================================ */
        #particlesCanvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            pointer-events: none;
        }

        /* ============================================================
           APP CONTAINER
           ============================================================ */
        #app {
            position: relative;
            z-index: 1;
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .page {
            display: none;
            width: 100%;
            height: 100%;
            justify-content: center;
            align-items: center;
        }
        .page.active-page { display: flex; }

        /* ============================================================
           LOGIN PAGE
           ============================================================ */
        .login-container {
            background: var(--bg-card);
            backdrop-filter: blur(20px);
            padding: 50px 40px;
            border-radius: 20px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
            width: 420px;
            text-align: center;
            animation: slideUp 0.5s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(50px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .glow-text {
            font-size: 52px;
            font-weight: 900;
            background: linear-gradient(135deg, var(--accent), #ff4444);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 40px var(--accent-glow);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { text-shadow: 0 0 20px var(--accent-glow); }
            50% { text-shadow: 0 0 60px var(--accent-glow); }
        }
        .subtitle {
            font-size: 18px;
            color: var(--text-secondary);
            letter-spacing: 2px;
            margin-top: 5px;
        }
        .prime { color: var(--accent); font-weight: 700; }
        .version {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 5px;
        }
        .input-group {
            margin: 15px 0;
            position: relative;
        }
        .input-field {
            width: 100%;
            padding: 14px 20px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px;
            color: #fff;
            font-size: 14px;
            transition: all 0.3s;
        }
        .input-field:focus {
            border-color: var(--accent);
            outline: none;
            box-shadow: 0 0 20px var(--accent-glow);
        }
        .input-icon {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 18px;
        }
        .button-group {
            margin-top: 25px;
            display: flex;
            gap: 10px;
        }
        .btn-primary, .btn-secondary {
            flex: 1;
            padding: 14px;
            border: none;
            border-radius: 10px;
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: var(--accent);
            color: #fff;
        }
        .btn-primary:hover {
            background: #ff3333;
            transform: scale(1.02);
        }
        .btn-secondary {
            background: rgba(255,255,255,0.05);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .btn-secondary:hover { background: rgba(255,255,255,0.1); }
        .login-footer {
            margin-top: 25px;
            font-size: 12px;
            color: var(--text-secondary);
        }

        /* ============================================================
           SIDEBAR
           ============================================================ */
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 220px;
            height: 100vh;
            background: rgba(15,15,15,0.95);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--border-color);
            padding: 20px 0;
            display: flex;
            flex-direction: column;
        }
        .sidebar-header {
            padding: 0 20px 30px 20px;
            border-bottom: 1px solid var(--border-color);
        }
        .logo-text {
            font-size: 28px;
            font-weight: 900;
            color: var(--accent);
        }
        .logo-sub {
            font-size: 14px;
            color: var(--text-secondary);
            letter-spacing: 2px;
        }
        .sidebar-nav {
            flex: 1;
            padding: 20px 10px;
        }
        .nav-btn {
            width: 100%;
            padding: 12px 15px;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 14px;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.3s;
            margin-bottom: 5px;
        }
        .nav-btn:hover {
            background: rgba(255,0,0,0.05);
            color: #fff;
        }
        .nav-btn.active {
            background: rgba(255,0,0,0.1);
            color: var(--accent);
            border-left: 3px solid var(--accent);
        }
        .nav-icon { font-size: 18px; }
        .sidebar-footer {
            padding: 20px;
            border-top: 1px solid var(--border-color);
        }
        .logout-btn {
            width: 100%;
            padding: 12px;
            background: rgba(255,0,0,0.1);
            border: 1px solid rgba(255,0,0,0.2);
            border-radius: 10px;
            color: var(--accent);
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        .logout-btn:hover { background: rgba(255,0,0,0.2); }

        /* ============================================================
           CONTENT
           ============================================================ */
        .content {
            margin-left: 220px;
            padding: 30px;
            width: calc(100% - 220px);
            min-height: 100vh;
            overflow-y: auto;
        }
        .tab {
            display: none;
        }
        .tab.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .tab-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 24px;
            font-weight: 700;
        }
        .neon {
            color: var(--accent);
            text-shadow: 0 0 20px var(--accent-glow);
        }
        .status-badge {
            font-size: 12px;
            padding: 4px 15px;
            border-radius: 20px;
            background: rgba(0,255,0,0.1);
            color: #00ff00;
            border: 1px solid rgba(0,255,0,0.2);
        }
        .features-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .feature-card {
            background: var(--bg-card);
            backdrop-filter: blur(10px);
            padding: 18px 20px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
        }
        .feature-card:hover {
            border-color: rgba(255,0,0,0.2);
        }
        .feature-card.full-width {
            grid-column: 1 / -1;
        }
        .feature-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .feature-icon { font-size: 20px; }
        .feature-card label {
            font-size: 14px;
            color: var(--text-primary);
            cursor: pointer;
        }
        .keybind {
            font-size: 11px;
            color: var(--accent);
            background: rgba(255,0,0,0.1);
            padding: 2px 10px;
            border-radius: 12px;
        }
        .feature-toggle {
            width: 44px;
            height: 24px;
            appearance: none;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            position: relative;
            cursor: pointer;
            transition: all 0.3s;
        }
        .feature-toggle:checked {
            background: var(--accent);
        }
        .feature-toggle::before {
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 20px;
            height: 20px;
            background: #fff;
            border-radius: 50%;
            transition: all 0.3s;
        }
        .feature-toggle:checked::before {
            left: 22px;
        }
        .fake-lag-controls {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .fake-lag-controls input[type="range"] {
            width: 120px;
            accent-color: var(--accent);
        }
        .btn-small {
            padding: 6px 18px;
            background: var(--accent);
            border: none;
            border-radius: 8px;
            color: #fff;
            font-weight: 600;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-small:hover {
            background: #ff3333;
            transform: scale(1.05);
        }
        input[type="color"] {
            width: 50px;
            height: 40px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            background: transparent;
        }
        select {
            padding: 8px 15px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            cursor: pointer;
        }
        select option {
            background: #1a1a1a;
            color: #fff;
        }

        /* ============================================================
           NOTIFICATIONS
           ============================================================ */
        #notificationContainer {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .notification {
            background: rgba(20,20,30,0.9);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 15px 25px;
            color: #fff;
            font-size: 14px;
            box-shadow: var(--shadow);
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 300px;
            transform: translateX(120%);
            transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            border-left: 4px solid var(--accent);
        }
        .notification.show { transform: translateX(0); }
        .notification.hide { transform: translateX(120%); }

        /* ============================================================
           RESPONSIVE
           ============================================================ */
        @media (max-width: 768px) {
            .sidebar { width: 70px; }
            .sidebar .nav-label,
            .sidebar .logo-sub,
            .sidebar .logout-btn span:not(.nav-icon) { display: none; }
            .content { margin-left: 70px; width: calc(100% - 70px); padding: 15px; }
            .features-grid { grid-template-columns: 1fr; }
            .login-container { width: 90%; padding: 30px 20px; }
        }
    </style>
</head>
<body>

    <!-- ===== PARTICLES CANVAS ===== -->
    <canvas id="particlesCanvas"></canvas>

    <!-- ===== APP ===== -->
    <div id="app">

        <!-- Login removed: app now shows main panel by default -->

        <!-- ===== MAIN PAGE ===== -->
        <div id="mainPage" class="page active-page">
            <!-- Sidebar -->
            <div class="sidebar">
                <div class="sidebar-header">
                    <span class="logo-text">AKIRA</span>
                    <span class="logo-sub">CTX</span>
                </div>
                <nav class="sidebar-nav">
                    <button class="nav-btn active" onclick="switchTab(0)" data-tab="0">
                        <span class="nav-icon">🎯</span>
                        <span class="nav-label">AIM</span>
                    </button>
                    <button class="nav-btn" onclick="switchTab(1)" data-tab="1">
                        <span class="nav-icon">🎨</span>
                        <span class="nav-label">CHAMS</span>
                    </button>
                    <button class="nav-btn" onclick="switchTab(2)" data-tab="2">
                        <span class="nav-icon">⚡</span>
                        <span class="nav-label">EXTRA</span>
                    </button>
                    <button class="nav-btn" onclick="switchTab(3)" data-tab="3">
                        <span class="nav-icon">🔧</span>
                        <span class="nav-label">OPTIMIZE</span>
                    </button>
                    <button class="nav-btn" onclick="switchTab(4)" data-tab="4">
                        <span class="nav-icon">⚙️</span>
                        <span class="nav-label">SETTINGS</span>
                    </button>
                </nav>
                <div class="sidebar-footer">
                    <button onclick="handleLogout()" class="logout-btn">
                        <span>🚪</span> Logout
                    </button>
                </div>
            </div>

            <!-- Content -->
            <div class="content">
                <!-- ===== TAB 0: AIM ===== -->
                <div id="tab0" class="tab active">
                    <div class="tab-header">
                        <h2 class="section-title neon">🎯 AIM MENU</h2>
                        <span class="status-badge">ACTIVE</span>
                    </div>
                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="feature-info">
                                <span class="feature-icon">🤖</span>
                                <label>Aimbot AI</label>
                                <span class="keybind">[F1]</span>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('aimbot_ai', this.checked)">
                        </div>
                        <div class="feature-card">
                            <div class="feature-info">
                                <span class="feature-icon">🎯</span>
                                <label>Aimbot Nike</label>
                                <span class="keybind">[F2]</span>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('aimbot_nike', this.checked)">
                        </div>
                        <div class="feature-card">
                            <div class="feature-info">
                                <span class="feature-icon">🔭</span>
                                <label>Scope 2</label>
                                <span class="keybind">[F3]</span>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('scope_2', this.checked)">
                        </div>
                        <div class="feature-card">
                            <div class="feature-info">
                                <span class="feature-icon">🔭</span>
                                <label>Scope 4</label>
                                <span class="keybind">[F4]</span>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('scope_4', this.checked)">
                        </div>
                        <div class="feature-card">
                            <div class="feature-info">
                                <span class="feature-icon">🔫</span>
                                <label>Switch AWM</label>
                                <span class="keybind">[F5]</span>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('switch_awm', this.checked)">
                        </div>
                        <div class="feature-card">
                            <div class="feature-info">
                                <span class="feature-icon">🎯</span>
                                <label>Sniper No Scope</label>
                                <span class="keybind">[F6]</span>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('sniper', this.checked)">
                        </div>
                        <div class="feature-card">
                            <div class="feature-info">
                                <span class="feature-icon">💥</span>
                                <label>Amo Akira</label>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('amo_akira', this.checked)">
                        </div>
                        <div class="feature-card">
                            <div class="feature-info">
                                <span class="feature-icon">💥</span>
                                <label>Amo AWM</label>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('amo_awm', this.checked)">
                        </div>
                    </div>
                </div>

                <!-- ===== TAB 1: CHAMS ===== -->
                <div id="tab1" class="tab">
                    <div class="tab-header">
                        <h2 class="section-title neon">🎨 CHAMS MENU</h2>
                        <span class="status-badge">ACTIVE</span>
                    </div>
                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="feature-info">
                                <span class="feature-icon">💎</span>
                                <label>Chams Menu</label>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('chams_menu', this.checked)">
                        </div>
                        <div class="feature-card">
                            <div class="feature-info">
                                <span class="feature-icon">🔧</span>
                                <label>Fix Chams</label>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('fix_chams', this.checked)">
                        </div>
                    </div>
                </div>

                <!-- ===== TAB 2: EXTRA ===== -->
                <div id="tab2" class="tab">
                    <div class="tab-header">
                        <h2 class="section-title neon">⚡ EXTRA FUNCTIONS</h2>
                    </div>
                    <div class="features-grid">
                        <div class="feature-card full-width">
                            <div class="feature-info">
                                <span class="feature-icon">📡</span>
                                <label>Fake Lag</label>
                            </div>
                            <div class="fake-lag-controls">
                                <input type="range" id="fakeLagSlider" min="1" max="4" value="2" step="0.5">
                                <span id="fakeLagValue">2s</span>
                                <button onclick="triggerFakeLag()" class="btn-small">APPLY</button>
                            </div>
                        </div>
                        <div class="feature-card full-width">
                            <div class="feature-info">
                                <span class="feature-icon">🧹</span>
                                <label>Clean Temp Files</label>
                            </div>
                            <button onclick="cleanTemp()" class="btn-small">RUN</button>
                        </div>
                        <div class="feature-card full-width">
                            <div class="feature-info">
                                <span class="feature-icon">⚡</span>
                                <label>System Optimization</label>
                            </div>
                            <button onclick="optimizeSystem()" class="btn-small">RUN</button>
                        </div>
                    </div>
                </div>

                <!-- ===== TAB 3: OPTIMIZE ===== -->
                <div id="tab3" class="tab">
                    <div class="tab-header">
                        <h2 class="section-title neon">🔧 OPTIMIZE</h2>
                    </div>
                    <div class="features-grid">
                        <div class="feature-card full-width">
                            <div class="feature-info">
                                <span class="feature-icon">🚀</span>
                                <label>Performance Mode</label>
                            </div>
                            <button onclick="optimizeSystem()" class="btn-small">ACTIVATE</button>
                        </div>
                    </div>
                </div>

                <!-- ===== TAB 4: SETTINGS ===== -->
                <div id="tab4" class="tab">
                    <div class="tab-header">
                        <h2 class="section-title neon">⚙️ SETTINGS</h2>
                    </div>
                    <div class="features-grid">
                        <div class="feature-card full-width">
                            <div class="feature-info">
                                <span class="feature-icon">🎨</span>
                                <label>Accent Color</label>
                            </div>
                            <input type="color" id="accentColor" value="#ff0000" onchange="changeAccent(this.value)">
                        </div>
                        <div class="feature-card full-width">
                            <div class="feature-info">
                                <span class="feature-icon">🌟</span>
                                <label>Particle Type</label>
                            </div>
                            <select id="particleType" onchange="changeParticles(this.value)">
                                <option value="storm">Storm 🔥</option>
                                <option value="dots">Dots ⚪</option>
                                <option value="squares">Squares 🔲</option>
                                <option value="triangles">Triangles 🔺</option>
                            </select>
                        </div>
                        <div class="feature-card full-width">
                            <div class="feature-info">
                                <span class="feature-icon">👁️</span>
                                <label>Streamer Mode</label>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('streamer', this.checked)">
                        </div>
                        <div class="feature-card full-width">
                            <div class="feature-info">
                                <span class="feature-icon">🌐</span>
                                <label>Block Internet</label>
                            </div>
                            <input type="checkbox" class="feature-toggle" onchange="toggleFeature('block_internet', this.checked)">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ===== NOTIFICATION CONTAINER ===== -->
    <div id="notificationContainer"></div>

    <!-- ============================================================
    JAVASCRIPT
    ============================================================ -->
    <script>
        // ============================================================
        // 📊 GLOBAL STATE
        // ============================================================
        const AppState = {
            username: 'guest',
            token: '',
            features: {},
            currentTab: 0,
            isLoggedIn: true,
            particleType: 'storm',
            accentColor: '#ff0000',
            fakeLagDuration: 2
        };

        // ============================================================
        // 🎨 PARTICLES SYSTEM
        // ============================================================
        class ParticleSystem {
            constructor() {
                this.canvas = document.getElementById('particlesCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.particles = [];
                this.running = false;
                this.type = 'storm';
                this.count = 80;
                this.resize();
                window.addEventListener('resize', () => this.resize());
            }

            resize() {
                this.canvas.width = window.innerWidth;
                this.canvas.height = window.innerHeight;
            }

            generateParticles() {
                fetch(`/api/particles/${this.type}?count=${this.count}`)
                    .then(res => res.json())
                    .then(data => {
                        this.particles = data;
                        if (!this.running) {
                            this.running = true;
                            this.animate();
                        }
                    })
                    .catch(() => {
                        // Fallback particles
                        this.particles = [];
                        for (let i = 0; i < this.count; i++) {
                            this.particles.push({
                                x: Math.random() * this.canvas.width,
                                y: Math.random() * this.canvas.height,
                                size: Math.random() * 6 + 2,
                                speed: Math.random() * 1.5 + 0.5,
                                alpha: Math.random() * 0.8 + 0.2,
                                color: `rgba(255,0,0,${Math.random() * 0.8 + 0.2})`
                            });
                        }
                        if (!this.running) {
                            this.running = true;
                            this.animate();
                        }
                    });
            }

            drawParticle(p) {
                this.ctx.save();
                this.ctx.globalAlpha = p.alpha;
                this.ctx.translate(p.x, p.y);
                
                this.ctx.beginPath();
                this.ctx.arc(0, 0, p.size, 0, Math.PI * 2);
                this.ctx.fillStyle = p.color || '#ff0000';
                this.ctx.fill();
                
                this.ctx.restore();
            }

            updateParticle(p) {
                p.y -= p.speed;
                p.x += Math.sin(p.y * 0.01) * 0.3;
                p.alpha -= 0.003;

                if (p.alpha <= 0 || p.y < -p.size) {
                    p.x = Math.random() * this.canvas.width;
                    p.y = this.canvas.height + p.size;
                    p.alpha = Math.random() * 0.8 + 0.2;
                    p.speed = Math.random() * 1.5 + 0.5;
                }
            }

            animate() {
                if (!this.running) return;
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                
                for (let p of this.particles) {
                    this.updateParticle(p);
                    this.drawParticle(p);
                }
                
                requestAnimationFrame(() => this.animate());
            }

            changeType(type) {
                this.type = type;
                this.generateParticles();
            }

            start() {
                this.generateParticles();
            }
        }

        // ============================================================
        // 🔔 NOTIFICATION SYSTEM
        // ============================================================
        function showNotification(message, type = 'info', duration = 3000) {
            const container = document.getElementById('notificationContainer');
            const colors = {
                success: '#00ff00',
                error: '#ff0000',
                warning: '#ffff00',
                info: '#0096ff'
            };
            
            const notif = document.createElement('div');
            notif.className = 'notification';
            notif.style.borderLeftColor = colors[type] || colors.info;
            notif.innerHTML = `
                <span>${message}</span>
                <button onclick="this.parentElement.remove()" style="background:none;border:none;color:#666;cursor:pointer;font-size:18px;">✕</button>
            `;
            
            container.appendChild(notif);
            
            setTimeout(() => notif.classList.add('show'), 10);
            
            setTimeout(() => {
                notif.classList.remove('show');
                setTimeout(() => notif.remove(), 500);
            }, duration);
        }

        // ============================================================
        // 🔐 AUTHENTICATION
        // ============================================================
        async function handleLogin() {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                showNotification('Please fill in all fields!', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await response.json();
                
                if (data.success) {
                    AppState.username = username;
                    AppState.token = data.token;
                    AppState.isLoggedIn = true;
                    showNotification(data.message, 'success');
                    
                    document.getElementById('loginPage').classList.remove('active-page');
                    document.getElementById('mainPage').style.display = 'flex';
                    document.getElementById('mainPage').classList.add('active-page');
                    
                    loadFeatures();
                } else {
                    showNotification(data.message || 'Login failed!', 'error');
                }
            } catch (error) {
                showNotification('Network error!', 'error');
            }
        }

        async function handleRegister() {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const license = document.getElementById('license').value.trim();
            
            if (!username || !password || !license) {
                showNotification('Please fill in all fields!', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password, license })
                });
                const data = await response.json();
                
                if (data.success) {
                    showNotification(data.message, 'success');
                    document.getElementById('license').value = '';
                } else {
                    showNotification(data.message || 'Registration failed!', 'error');
                }
            } catch (error) {
                showNotification('Network error!', 'error');
            }
        }

        async function handleLogout() {
            try {
                await fetch('/api/logout', { method: 'POST' });
            } catch (e) {}
            
            AppState.isLoggedIn = false;
            AppState.token = '';
            AppState.username = '';
            
            document.getElementById('mainPage').classList.remove('active-page');
            document.getElementById('mainPage').style.display = 'none';
            document.getElementById('loginPage').classList.add('active-page');
            
            showNotification('Logged out!', 'success');
        }

        // ============================================================
        // 🎮 FEATURES
        // ============================================================
        async function loadFeatures() {
            try {
                const response = await fetch('/api/features');
                const data = await response.json();
                AppState.features = data;
                
                // Update UI toggles
                document.querySelectorAll('.feature-toggle').forEach(toggle => {
                    const feature = toggle.getAttribute('onchange')?.match(/'([^']+)'/)?.[1];
                    if (feature && AppState.features[feature]) {
                        toggle.checked = AppState.features[feature].enabled;
                    }
                });
            } catch (error) {
                console.error('Failed to load features:', error);
            }
        }

        async function toggleFeature(feature, enabled) {
            if (!AppState.isLoggedIn) {
                showNotification('Please login first!', 'error');
                return;
            }
            
            try {
                const response = await fetch(`/api/feature/${feature}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled })
                });
                const data = await response.json();
                
                if (data.success) {
                    showNotification(`${feature}: ${enabled ? '✅ ON' : '❌ OFF'}`, 'success');
                    if (AppState.features[feature]) {
                        AppState.features[feature].enabled = enabled;
                    }
                } else {
                    showNotification(data.message || 'Failed to toggle feature!', 'error');
                    // Revert toggle
                    const toggles = document.querySelectorAll('.feature-toggle');
                    toggles.forEach(t => {
                        const f = t.getAttribute('onchange')?.match(/'([^']+)'/)?.[1];
                        if (f === feature) {
                            t.checked = !enabled;
                        }
                    });
                }
            } catch (error) {
                showNotification('Network error!', 'error');
            }
        }

        // ============================================================
        // ⚡ EXTRA FUNCTIONS
        // ============================================================
        async function triggerFakeLag() {
            const slider = document.getElementById('fakeLagSlider');
            const duration = parseFloat(slider.value);
            document.getElementById('fakeLagValue').textContent = duration + 's';
            
            try {
                const response = await fetch('/api/fake_lag', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ duration })
                });
                const data = await response.json();
                showNotification(data.message || 'Fake Lag applied!', 'success');
            } catch (error) {
                showNotification('Network error!', 'error');
            }
        }

        async function cleanTemp() {
            try {
                const response = await fetch('/api/clean_temp', { method: 'POST' });
                const data = await response.json();
                showNotification(data.message || 'Temp cleaned!', 'success');
            } catch (error) {
                showNotification('Network error!', 'error');
            }
        }

        async function optimizeSystem() {
            try {
                const response = await fetch('/api/optimize', { method: 'POST' });
                const data = await response.json();
                showNotification(data.message || 'System optimized!', 'success');
            } catch (error) {
                showNotification('Network error!', 'error');
            }
        }

        // ============================================================
        // 🎨 UI FUNCTIONS
        // ============================================================
        function switchTab(index) {
            AppState.currentTab = index;
            
            // Update tabs
            document.querySelectorAll('.tab').forEach((tab, i) => {
                tab.classList.toggle('active', i === index);
            });
            
            // Update nav buttons
            document.querySelectorAll('.nav-btn').forEach((btn, i) => {
                btn.classList.toggle('active', i === index);
            });
        }

        function changeAccent(color) {
            AppState.accentColor = color;
            document.documentElement.style.setProperty('--accent', color);
            const glow = color + '33';
            document.documentElement.style.setProperty('--accent-glow', glow);
        }

        function changeParticles(type) {
            AppState.particleType = type;
            if (particleSystem) {
                particleSystem.changeType(type);
            }
        }

        // ============================================================
        // 🚀 INITIALIZATION
        // ============================================================
        let particleSystem;

        document.addEventListener('DOMContentLoaded', function() {
            // Initialize particles
            particleSystem = new ParticleSystem();
            particleSystem.start();
            
            // Check if already logged in
            const token = localStorage.getItem('akira_token');
            if (token) {
                fetch('/api/verify')
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            AppState.isLoggedIn = true;
                            AppState.username = data.username;
                            AppState.token = token;
                            
                            document.getElementById('loginPage').classList.remove('active-page');
                            document.getElementById('mainPage').style.display = 'flex';
                            document.getElementById('mainPage').classList.add('active-page');
                            
                            loadFeatures();
                        }
                    })
                    .catch(() => {});
            }
            
            // Fake lag slider
            const slider = document.getElementById('fakeLagSlider');
            if (slider) {
                slider.addEventListener('input', function() {
                    document.getElementById('fakeLagValue').textContent = this.value + 's';
                });
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // F1-F6 for features
            const keyMap = {
                112: 'aimbot_ai',
                113: 'aimbot_nike',
                114: 'scope_2',
                115: 'scope_4',
                116: 'switch_awm',
                117: 'sniper'
            };
            
            const feature = keyMap[e.keyCode];
            if (feature && AppState.isLoggedIn) {
                e.preventDefault();
                const currentState = AppState.features[feature]?.enabled || false;
                toggleFeature(feature, !currentState);
                
                // Update toggle UI
                document.querySelectorAll('.feature-toggle').forEach(toggle => {
                    const f = toggle.getAttribute('onchange')?.match(/'([^']+)'/)?.[1];
                    if (f === feature) {
                        toggle.checked = !currentState;
                    }
                });
            }
            
            // ESC to logout
            if (e.keyCode === 27 && AppState.isLoggedIn) {
                handleLogout();
            }
        });
    </script>
</body>
</html>
'''

# ============================================================
# 🚀 ROUTE
# ============================================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# ============================================================
# 🛡️ STARTUP SECURITY
# ============================================================
def startup_checks():
    print("[SECURITY] Running startup checks...")
    if SecurityManager.check_debugger():
        print("[!] Debugger detected! Exiting...")
        sys.exit(1)
    if SecurityManager.check_vm():
        print("[!] Virtual Machine detected! Exiting...")
        sys.exit(1)
    print("[SECURITY] All checks passed!")

# ============================================================
# 📊 ADMIN FUNCTIONS
# ============================================================
def create_admin_user():
    if not db.user_exists('admin'):
        password_hash = AuthSystem.hash_password('admin123')
        db.add_user('admin', password_hash, 'ADMIN-0000-0000', expiry_days=365)
        print("[ADMIN] Created admin user: admin / admin123")

# ============================================================
# 🚀 MAIN ENTRY POINT
# ============================================================
if __name__ == '__main__':
    startup_checks()
    create_admin_user()
    app.config['start_time'] = time.time()
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     █████╗ ██╗  ██╗██╗██████╗  █████╗                  ║
    ║    ██╔══██╗██║ ██╔╝██║██╔══██╗██╔══██╗                 ║
    ║    ███████║█████╔╝ ██║██████╔╝███████║                 ║
    ║    ██╔══██║██╔═██╗ ██║██╔══██╗██╔══██║                 ║
    ║    ██║  ██║██║  ██╗██║██║  ██║██║  ██║                 ║
    ║    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝                 ║
    ║                                                          ║
    ║               🔥 AKIRA CTX SERVER 🔥                    ║
    ║                                                          ║
    ║           Version: {}                                  ║
    ║           Running on: http://localhost:5000             ║
    ║                                                          ║
    ║           Default Admin: admin / admin123               ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """.format(APP_VERSION))
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)