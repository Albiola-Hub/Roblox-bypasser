import os
import requests
from flask import Flask, render_template_string, request, Response, stream_with_context

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox Account Birthday Editor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0c10;
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }
        .card {
            background: #1e1f25;
            border-radius: 24px;
            max-width: 650px;
            width: 100%;
            padding: 2rem;
            border: 1px solid #2c2e3a;
            box-shadow: 0 20px 35px -10px rgba(0,0,0,0.5);
        }
        h1 {
            font-size: 1.8rem;
            background: linear-gradient(135deg, #fff, #6c8cff);
            background-clip: text;
            -webkit-background-clip: text;
            color: transparent;
            margin-bottom: 0.5rem;
        }
        .sub {
            color: #8e8e9e;
            font-size: 0.85rem;
            margin-bottom: 2rem;
            border-left: 3px solid #3a6eff;
            padding-left: 0.75rem;
        }
        .input-group { margin-bottom: 1.5rem; }
        label {
            color: #c0c0d0;
            font-weight: 500;
            font-size: 0.85rem;
            display: block;
            margin-bottom: 0.5rem;
        }
        input {
            width: 100%;
            background: #0e0f14;
            border: 1px solid #2d2f3a;
            border-radius: 14px;
            padding: 12px 16px;
            color: #f0f0f8;
            font-family: monospace;
        }
        input:focus {
            outline: none;
            border-color: #3a6eff;
            box-shadow: 0 0 0 3px rgba(58,110,255,0.2);
        }
        .execute-btn {
            background: linear-gradient(95deg, #1e2a5e, #2a3a7a);
            border: none;
            width: 100%;
            padding: 14px;
            font-size: 1.2rem;
            font-weight: bold;
            color: white;
            border-radius: 40px;
            margin: 1rem 0 1.5rem;
            cursor: pointer;
        }
        .status-header {
            display: flex;
            justify-content: space-between;
            color: #8e8e9e;
            font-size: 0.75rem;
            margin-bottom: 8px;
        }
        textarea {
            width: 100%;
            background: #0a0b0f;
            border: 1px solid #2c2e3a;
            border-radius: 16px;
            padding: 16px;
            color: #b9fbc0;
            font-family: monospace;
            font-size: 0.8rem;
            min-height: 250px;
            resize: vertical;
        }
        .info-note {
            background: #0f1118;
            border-radius: 14px;
            padding: 12px;
            margin-top: 20px;
            font-size: 0.7rem;
            color: #6e6e82;
            text-align: center;
        }
        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .btn-loading { opacity: 0.8; pointer-events: none; }
    </style>
</head>
<body>
<div class="card">
    <h1>⚡ Roblox Birthday Editor</h1>
    <div class="sub">Update birthdate to <strong>May 9, 2013</strong></div>

    <form id="bypassForm">
        <div class="input-group">
            <label>🍪 .ROBLOSECURITY Cookie</label>
            <input type="text" id="cookie" placeholder="Paste your .ROBLOSECURITY cookie">
        </div>
        <div class="input-group">
            <label>🔒 Password</label>
            <input type="password" id="password" placeholder="Account password">
        </div>
        <button type="submit" id="execBtn" class="execute-btn">🚀 EXECUTE BYPASS</button>
    </form>

    <div class="status-box">
        <div class="status-header"><span>📡 LIVE LOGS</span><span>real-time</span></div>
        <textarea id="logArea" readonly placeholder="Logs will appear here..."></textarea>
    </div>
    <div class="info-note">
        ⚠️ Roblox API flow: CSRF → reauth → birthdate update.
    </div>
</div>

<script>
    const form = document.getElementById('bypassForm');
    const execBtn = document.getElementById('execBtn');
    const logArea = document.getElementById('logArea');

    function appendLog(text) {
        logArea.value += text;
        logArea.scrollTop = logArea.scrollHeight;
    }

    async function executeBypass(cookie, password) {
        logArea.value = "";
        appendLog("[*] Starting process...\\n");

        execBtn.disabled = true;
        execBtn.classList.add('btn-loading');
        const originalHTML = execBtn.innerHTML;
        execBtn.innerHTML = '<span class="spinner"></span> PROCESSING...';

        try {
            const response = await fetch('/bypass', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cookie, password })
            });
            if (!response.ok) {
                const err = await response.text();
                appendLog(`[ERROR] ${response.status}: ${err}\\n`);
                return;
            }
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                appendLog(decoder.decode(value, { stream: true }));
            }
        } catch (err) {
            appendLog(`[!] Network error: ${err.message}\\n`);
        } finally {
            execBtn.disabled = false;
            execBtn.classList.remove('btn-loading');
            execBtn.innerHTML = originalHTML;
        }
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const cookie = document.getElementById('cookie').value.trim();
        const password = document.getElementById('password').value;
        if (!cookie || !password) {
            appendLog("[!] Fill both fields.\\n");
            return;
        }
        executeBypass(cookie, password);
    });
</script>
</body>
</html>
"""

def generate_updates(cookie, password):
    yield "[*] Starting Roblox birthdate bypass process...\n"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "RobloxApp/610 (Android 13; Pixel 7 Pro)",
        "X-Roblox-Channel": "7",
        "Origin": "https://www.roblox.com",
        "Referer": "https://www.roblox.com/",
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    session.cookies.set(".ROBLOSECURITY", cookie, domain=".roblox.com")

    # Step 1: CSRF token
    yield "[1/3] Fetching X-CSRF-TOKEN...\n"
    try:
        resp = session.post("https://auth.roblox.com/v2/logout", allow_redirects=False)
        if resp.status_code == 403 and "x-csrf-token" in resp.headers:
            csrf = resp.headers["x-csrf-token"]
            session.headers.update({"X-CSRF-TOKEN": csrf})
            yield f"[+] CSRF token acquired.\n"
        else:
            yield f"[-] Failed to get CSRF token (HTTP {resp.status_code})\n"
            if resp.status_code == 401:
                yield "[-] Error: Invalid or Expired Cookie.\n"
            return
    except Exception as e:
        yield f"[!] Request error: {str(e)}\n"
        return

    # Step 2: Reauthenticate
    yield "[2/3] Re-authenticating with password...\n"
    try:
        r2 = session.post("https://twostepverification.roblox.com/v1/users/reauthenticate",
                          json={"password": password})
        if r2.status_code == 200:
            yield "[+] Reauthentication successful.\n"
        else:
            yield f"[-] Reauthentication failed (HTTP {r2.status_code})\n"
            if r2.status_code == 401:
                yield "[-] Error: Invalid or Expired Cookie.\n"
            elif r2.status_code == 400:
                yield "[-] Incorrect password.\n"
            return
    except Exception as e:
        yield f"[!] Error: {str(e)}\n"
        return

    # Step 3: Update birthdate
    yield "[3/3] Updating birthdate to May 9, 2013...\n"
    try:
        r3 = session.post("https://users.roblox.com/v1/birthdate",
                          json={"birthMonth": 5, "birthDay": 9, "birthYear": 2013})
        if r3.status_code == 200:
            yield "[✓] SUCCESS! Birthdate changed to 5/9/2013.\n"
        else:
            yield f"[-] Birthdate update failed (HTTP {r3.status_code})\n"
            if r3.status_code == 403 and "Challenge" in r3.text:
                yield "[-] Bypassed failed: Facial Age Verification Required by Roblox.\n"
            elif r3.status_code == 401:
                yield "[-] Error: Invalid or Expired Cookie.\n"
            else:
                yield f"[-] Response snippet: {r3.text[:150]}\n"
    except Exception as e:
        yield f"[!] Error: {str(e)}\n"
        return
    yield "[*] Process completed.\n"

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/bypass', methods=['POST'])
def bypass():
    data = request.get_json()
    cookie = data.get('cookie', '').strip()
    password = data.get('password', '').strip()
    if not cookie or not password:
        return Response("Missing cookie or password", status=400)
    return Response(stream_with_context(generate_updates(cookie, password)),
                    mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
