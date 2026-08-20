import os, requests, threading, time, sys, jwt, socket, urllib3, json, ssl, http.client, gzip, random
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from io import BytesIO
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from xCore import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE_DIR, 'accounts.json')

connected_clients = {}      
connected_clients_lock = threading.Lock()
all_accounts = {}           
all_accounts_lock = threading.Lock()
ACCOUNTS = []

spam_speed = 5.0
spam_running = False
current_target = None
current_target_info = None  
target_info_lock = threading.Lock()
state_lock = threading.Lock()

GREEN = '\033[92m'; YELLOW = '\033[93m'; RED = '\033[91m'; RESET = '\033[0m'


def set_acc_status(acc_id, status):
    with all_accounts_lock:
        if acc_id in all_accounts:
            all_accounts[acc_id]['status'] = status


class MyMessage:
    def __init__(self):
        self.field21 = 0
        self.field22 = b''
        self.field23 = b''

    def ParseFromString(self, data):
        try:
            from xCore import MyMessage as RealMyMessage
            msg = RealMyMessage()
            msg.ParseFromString(data)
            self.field21 = msg.field21
            self.field22 = msg.field22
            self.field23 = msg.field23
        except Exception:
            if len(data) > 0:
                self.field21 = int.from_bytes(data[:8], 'little') if len(data) >= 8 else 0
                self.field22 = data[8:24] if len(data) >= 24 else b''
                self.field23 = data[24:40] if len(data) >= 40 else b''


class FF_CLient:
    def __init__(self, id, password):
        self.id = id
        self.password = password
        self.key = None
        self.iv = None
        self.CliEnts = None
        self.CliEnts2 = None
        self.running = True
        self.target_id = None
        self.room_opened = False
        self.spam_thread_started = False
        self.send_lock = threading.Lock()
        self.account_uid = None
        threading.Thread(target=self.start_client, daemon=True).start()

    def start_client(self):
        set_acc_status(self.id, 'connecting')
        while self.running:
            try:
                self.Get_FiNal_ToKen_0115()
                return
            except Exception as e:
                set_acc_status(self.id, 'connecting')
                print(f"{RED}Account {self.id}: connection error: {e}{RESET}")
                time.sleep(5)

    def Get_FiNal_ToKen_0115(self):
        while self.running:
            try:
                result = self.Guest_GeneRaTe(self.id, self.password)
                if not result:
                    set_acc_status(self.id, 'connecting')
                    time.sleep(2)
                    continue

                token, key, iv, ts, ip, port, ip2, port2 = result
                if not all([ip, port, ip2, port2]):
                    time.sleep(2)
                    continue

                self.JwT_ToKen = token

                try:
                    self.AfTer_DeC_JwT = jwt.decode(token, options={"verify_signature": False})
                    self.AccounT_Uid = self.AfTer_DeC_JwT.get('account_id')
                    if not self.AccounT_Uid:
                        raise ValueError("No account_id in JWT")
                    self.account_uid = self.AccounT_Uid
                    self.EncoDed_AccounT = hex(self.AccounT_Uid)[2:]
                    self.HeX_VaLue = DecodE_HeX(ts)
                    self.TimE_HEx = self.HeX_VaLue
                    self.JwT_ToKen_ = token.encode().hex()
                except Exception:
                    time.sleep(1)
                    continue

                try:
                    encrypted_token = EnC_PacKeT(self.JwT_ToKen_, key, iv)
                    header_length = hex(len(encrypted_token) // 2)[2:]
                    uid_length = len(self.EncoDed_AccounT)
                    prefix_map = {7: '000000000', 8: '00000000', 9: '0000000', 10: '000000'}
                    prefix = prefix_map.get(uid_length, '00000000')
                    self.Header = f'0115{prefix}{self.EncoDed_AccounT}{self.TimE_HEx}00000{header_length}'
                    self.FiNal_ToKen_0115 = self.Header + encrypted_token
                except Exception:
                    time.sleep(1)
                    continue

                self.AutH_ToKen = self.FiNal_ToKen_0115
                connection_thread = threading.Thread(
                    target=self.Connect_SerVer,
                    args=(self.JwT_ToKen, self.AutH_ToKen, ip, port, key, iv, ip2, port2),
                    daemon=True
                )
                connection_thread.start()
                connection_thread.join(timeout=30)
                return
            except Exception:
                set_acc_status(self.id, 'connecting')
                time.sleep(2)

    def Connect_SerVer_OnLine(self, Token, tok, host, port, key, iv, host2, port2):
        try:
            self.AutH_ToKen_0115 = tok
            self.CliEnts2 = socket.create_connection((host2, int(port2)))
            self.CliEnts2.settimeout(10)
            self.CliEnts2.send(bytes.fromhex(self.AutH_ToKen_0115))

            if not self.room_opened:
                self.CliEnts2.send(openroom(self.key, self.iv))
                self.room_opened = True
                print(f"{GREEN}Bot {self.id} Is Online ✅{RESET}")

            self.start_continuous_spam()
        except Exception:
            return

        while self.running:
            try:
                self.DaTa2 = self.CliEnts2.recv(99999)
                if self.DaTa2:
                    if '0500' in self.DaTa2.hex()[0:4] and len(self.DaTa2.hex()) > 30:
                        try:
                            self.packet = json.loads(DeCode_PackEt(f'08{self.DaTa2.hex().split("08", 1)[1]}'))
                            self.AutH = self.packet['5']['data']['7']['data']
                        except Exception:
                            pass
            except socket.timeout:
                continue
            except Exception:
                time.sleep(0.5)

    def start_continuous_spam(self):
        if self.spam_thread_started:
            return
        self.spam_thread_started = True

        def spam_loop():
            while self.running:
                with state_lock:
                    running = spam_running
                if not (running and self.target_id):
                    time.sleep(0.2)
                    continue
                try:
                    current = self.target_id
                    with self.send_lock:
                        if self.CliEnts2 and self.key and self.iv:
                            self.CliEnts2.send(spmroom(self.key, self.iv, current))
                            self.CliEnts2.send(SEnd_InV(1, current, self.key, self.iv))
                        else:
                            time.sleep(1)
                            continue
                    print(f"{YELLOW}from {self.id} => to {current}{RESET}")
                except Exception:
                    print(f"{RED}from {self.id} => to {self.target_id} ERROR{RESET}")
                    time.sleep(1)
                    continue
                time.sleep(spam_speed)

        threading.Thread(target=spam_loop, daemon=True).start()

    def set_target(self, target_id):
        self.target_id = target_id

    def Connect_SerVer(self, Token, tok, host, port, key, iv, host2, port2):
        try:
            self.AutH_ToKen_0115 = tok
            self.CliEnts = socket.create_connection((host, int(port)))
            self.CliEnts.send(bytes.fromhex(self.AutH_ToKen_0115))
            self.DaTa = self.CliEnts.recv(1024)

            online_thread = threading.Thread(
                target=self.Connect_SerVer_OnLine,
                args=(Token, tok, host, port, key, iv, host2, port2),
                daemon=True
            )
            online_thread.start()

            self.key = key
            self.iv = iv

            with connected_clients_lock:
                connected_clients[self.id] = self
            set_acc_status(self.id, 'online')

            while self.running:
                try:
                    self.DaTa = self.CliEnts.recv(1024)
                    if len(self.DaTa) == 0:
                        break
                except Exception:
                    break

            with connected_clients_lock:
                connected_clients.pop(self.id, None)
            set_acc_status(self.id, 'connecting')

            if self.running:
                time.sleep(5)
                return
        except Exception:
            with connected_clients_lock:
                connected_clients.pop(self.id, None)
            set_acc_status(self.id, 'connecting')
            if self.running:
                time.sleep(5)
                return

    def GeT_Key_Iv(self, serialized_data):
        my_message = MyMessage()
        my_message.ParseFromString(serialized_data)
        timestamp = my_message.field21
        key = my_message.field22
        iv = my_message.field23
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        combined_timestamp = timestamp_obj.seconds * 1_000_000_000 + timestamp_obj.nanos
        return combined_timestamp, key, iv

    def Guest_GeneRaTe(self, uid, password):
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close"
        }
        dataa = {
            "uid": f"{uid}", "password": f"{password}", "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067"
        }
        try:
            response = requests.post(url, headers=headers, data=dataa, timeout=10)
            response.raise_for_status()
            resp = response.json()
            if 'access_token' not in resp:
                return None
            return self.ToKen_GeneRaTe(resp['access_token'], resp['open_id'])
        except Exception:
            time.sleep(1)
            return None

    def GeT_LoGin_PorTs(self, JwT_ToKen, PayLoad):
        url = 'https://clientbp.ggpolarbear.com/GetLoginData'
        headers = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {JwT_ToKen}',
            'X-Unity-Version': '2022.3.47f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
            'Host': 'clientbp.ggpolarbear.com',
            'Connection': 'close',
            'Accept-Encoding': 'gzip'
        }
        for attempt in range(3):
            try:
                res = requests.post(url, headers=headers, data=PayLoad, verify=False, timeout=10)
                if res.status_code == 503:
                    time.sleep(1)
                    continue
                res.raise_for_status()
                besto = json.loads(DeCode_PackEt(res.content.hex()))
                if '32' not in besto or '14' not in besto:
                    continue
                address = besto['32']['data']
                address2 = besto['14']['data']
                ip, ip2 = address[:len(address) - 6], address2[:len(address2) - 6]
                port, port2 = address[len(address) - 5:], address2[len(address2) - 5:]
                return ip, port, ip2, port2
            except Exception:
                time.sleep(1)
                continue
        return None, None, None, None

    def ToKen_GeneRaTe(self, Access_ToKen, Access_Uid):
        try:
            self.PLaFTrom = "4"
            self.Version, self.V = '2024010012', '1.130.1'
            pyl = {
                3: str(datetime.now())[:-7], 4: "free fire", 5: 2, 7: self.V,
                8: "Android OS 11 / API-30 (RQ3A.210805.001)", 9: "Handheld", 10: "Verizon",
                11: "WIFI", 12: 1080, 13: 2400, 14: "440", 15: "ARMv8", 16: 6144,
                17: "Adreno (TM) 650", 18: "OpenGL ES 3.2 V@1.50",
                19: "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57", 20: "", 21: "en",
                22: Access_Uid, 23: self.PLaFTrom, 24: "Handheld", 25: "google G011A",
                29: Access_ToKen, 30: 3, 41: "Verizon", 42: "WIFI",
                57: "1ac4b80ecf0478a44203bf8fac6120f5", 60: 32966, 61: 29779, 62: 2479,
                63: 914, 64: 31176, 65: 32966, 66: 31176, 67: 32966, 70: 4, 73: 2,
                74: "/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/lib/arm",
                76: 1, 77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/base.apk",
                78: 6, 79: 1, 81: "64", 83: self.Version, 86: "OpenGLES3", 87: 255,
                88: self.PLaFTrom,
                89: "J\u0003FD\u0004\r_UH\u0003\u000b\u0016_\u0003D^J>\u000fWT\u0000\\=\nQ_;\u0000\r;Z\u0005a",
                90: "Phoenix", 91: "AZ", 92: 10214, 93: "3rd_party",
                94: "KqsHT7gtKWkK0gY/HwmdwXIhSiz4fQldX3YjZeK86XBTthKAf1bW4Vsz6Di0S8vqr0Jc4HX3TMQ8KaUU3GeVvYzWF9I=",
                95: 111207, 97: 1, 98: 1, 99: f"{self.PLaFTrom}", 100: f"{self.PLaFTrom}"
            }
            pyl_hex = CrEaTe_ProTo(pyl).hex()
            payload = bytes.fromhex(EnC_AEs(pyl_hex))

            context = ssl._create_unverified_context()
            conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=context, timeout=10)
            headers = {
                'X-Unity-Version': '2018.4.11f1', 'ReleaseVersion': 'OB54',
                'Content-Type': 'application/x-www-form-urlencoded', 'X-GA': 'v1 1',
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
                'Host': 'loginbp.ggpolarbear.com', 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'
            }
            conn.request("POST", "/MajorLogin", body=payload, headers=headers)
            response = conn.getresponse()
            raw_data = response.read()
            if response.getheader('Content-Encoding') == 'gzip':
                with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f:
                    raw_data = f.read()
            if response.status not in [200, 201]:
                return None

            besto = json.loads(DeCode_PackEt(raw_data.hex()))
            jwt_token = besto['8']['data']
            combined_timestamp, key, iv = self.GeT_Key_Iv(raw_data)
            ip, port, ip2, port2 = self.GeT_LoGin_PorTs(jwt_token, payload)
            return jwt_token, key, iv, combined_timestamp, ip, port, ip2, port2
        except Exception:
            return None


def load_accounts_from_file(filename=None):
    filename = filename or ACCOUNTS_FILE
    accounts = []
    try:
        if not os.path.exists(filename):
            return accounts
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            for uid, password in data.items():
                if password:
                    accounts.append({'id': uid, 'password': password})
        return accounts
    except Exception:
        return accounts


def start_account(account):
    try:
        FF_CLient(account['id'], account['password'])
    except Exception:
        set_acc_status(account['id'], 'offline')
        time.sleep(1)


def start_accounts():
    global ACCOUNTS
    time.sleep(1)
    print(f"Loading accounts from: {ACCOUNTS_FILE}")
    ACCOUNTS = load_accounts_from_file()
    if not ACCOUNTS:
        print(f"{RED}No accounts found in accounts.json{RESET}")
        return
    with all_accounts_lock:
        for a in ACCOUNTS:
            all_accounts[a['id']] = {'id': a['id'], 'password': a['password'], 'status': 'offline'}
    # Start accounts gradually to avoid a startup thread burst.
    for account in ACCOUNTS:
        threading.Thread(target=start_account, args=(account,), daemon=True).start()
        time.sleep(0.5)


def fetch_target_info(uid):
    """Fetch player info using the first connected client's JWT (ggpolarbear GetPlayerPersonalShow)."""
    global current_target_info
    token = None
    with connected_clients_lock:
        for _, c in connected_clients.items():
            if getattr(c, 'JwT_ToKen', None):
                token = c.JwT_ToKen
                break
    info = None
    if token:
        info = GeT_PLayer_InFo(uid, token)
    with target_info_lock:
        current_target_info = info
    return info


def set_target_for_all(target_id):
    global current_target
    current_target = target_id
    with connected_clients_lock:
        for _, client in connected_clients.items():
            client.set_target(target_id)
    
    threading.Thread(target=fetch_target_info, args=(target_id,), daemon=True).start()



PAGE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BLRX SpaM RooM</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',Tahoma,sans-serif; }
  body { background:#0a0e17; color:#e6edf3; min-height:100vh; }
  header {
    background:linear-gradient(135deg,#1a0533 0%,#3b0764 50%,#7c1d1d 100%);
    padding:28px 20px; text-align:center; border-bottom:2px solid #a855f7;
    box-shadow:0 4px 30px rgba(168,85,247,.35);
  }
  header h1 { font-size:2.2rem; letter-spacing:2px; color:#fff;
    text-shadow:0 0 20px #a855f7, 0 0 40px #ef4444; }
  header p { color:#c4b5fd; margin-top:6px; font-size:.95rem; }
  .container { max-width:1100px; margin:24px auto; padding:0 16px; }
  .cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:14px; margin-bottom:22px; }
  .card { background:#111827; border:1px solid #2d3748; border-radius:14px; padding:18px; text-align:center; }
  .card .num { font-size:2rem; font-weight:bold; }
  .card .lbl { color:#9ca3af; font-size:.85rem; margin-top:4px; }
  .green { color:#22c55e; } .red { color:#ef4444; } .yellow { color:#eab308; } .purple { color:#a855f7; }
  .panel { background:#111827; border:1px solid #2d3748; border-radius:14px; padding:20px; margin-bottom:22px; }
  .panel h2 { font-size:1.1rem; margin-bottom:14px; color:#c4b5fd; }
  .target-row { display:flex; gap:10px; flex-wrap:wrap; }
  input[type=text] {
    flex:1; min-width:220px; background:#0a0e17; border:1px solid #4b5563; color:#fff;
    padding:12px 14px; border-radius:10px; font-size:1rem; outline:none;
  }
  input[type=text]:focus { border-color:#a855f7; box-shadow:0 0 0 2px rgba(168,85,247,.25); }
  button {
    padding:12px 26px; border:none; border-radius:10px; font-size:1rem; font-weight:bold;
    cursor:pointer; transition:.2s;
  }
  .btn-start { background:linear-gradient(135deg,#16a34a,#22c55e); color:#fff; }
  .btn-start:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(34,197,94,.4); }
  .btn-stop { background:linear-gradient(135deg,#b91c1c,#ef4444); color:#fff; }
  .btn-stop:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(239,68,68,.4); }
  button:disabled { opacity:.5; cursor:not-allowed; transform:none!important; }
  #playerInfo { margin-top:16px; display:none; }
  #playerInfo.show { display:block; }
  .pinfo { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; }
  .pinfo div { background:#0a0e17; border:1px solid #374151; border-radius:10px; padding:12px; }
  .pinfo .k { color:#9ca3af; font-size:.75rem; }
  .pinfo .v { color:#fff; font-weight:bold; margin-top:3px; word-break:break-all; }
  table { width:100%; border-collapse:collapse; }
  th, td { padding:10px 12px; text-align:right; font-size:.9rem; }
  th { color:#9ca3af; border-bottom:1px solid #374151; }
  td { border-bottom:1px solid #1f2937; }
  .badge { padding:3px 12px; border-radius:20px; font-size:.78rem; font-weight:bold; }
  .b-online { background:rgba(34,197,94,.15); color:#22c55e; border:1px solid #22c55e; }
  .b-off { background:rgba(239,68,68,.15); color:#ef4444; border:1px solid #ef4444; }
  .b-con { background:rgba(234,179,8,.15); color:#eab308; border:1px solid #eab308; }
  .pulse { animation:p 1.2s infinite; }
  @keyframes p { 0%,100%{opacity:1} 50%{opacity:.4} }
  .sec-title { display:flex; align-items:center; gap:8px; }
  .dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
  #toast { position:fixed; bottom:24px; left:50%; transform:translateX(-50%); background:#1f2937;
    border:1px solid #a855f7; padding:12px 24px; border-radius:12px; display:none; z-index:99; }
</style>
</head>
<body>
<header>
  <h1> BLRX SpaM RooM </h1>
  <p>VIP SPAM</p>
</header>

<div class="container">
  <div class="cards">
    <div class="card"><div class="num green" id="cOnline">0</div><div class="lbl">حسابات متصلة 🟢</div></div>
    <div class="card"><div class="num red" id="cOffline">0</div><div class="lbl">حسابات غير متصلة 🔴</div></div>
    <div class="card"><div class="num purple" id="cTotal">0</div><div class="lbl">إجمالي الحسابات</div></div>
    <div class="card"><div class="num yellow" id="cSpam">متوقف</div><div class="lbl">حالة السبام</div></div>
  </div>

  <div class="panel">
    <h2>🎯 إرسال طلبات الرومات</h2>
    <div class="target-row">
      <input type="text" id="uidInput" placeholder="أدخل ايدي اللاعب (UID)..." inputmode="numeric">
      <button class="btn-start" id="btnStart" onclick="startSpam()">▶ تشغيل</button>
      <button class="btn-stop" id="btnStop" onclick="stopSpam()">⏹ إيقاف</button>
    </div>
    <div id="playerInfo">
      <div class="pinfo">
        <div><div class="k">👤 اسم اللاعب</div><div class="v" id="pName">-</div></div>
        <div><div class="k">🆔 الايدي</div><div class="v" id="pUid">-</div></div>
        <div><div class="k">⭐ اللفل</div><div class="v" id="pLevel">-</div></div>
        <div><div class="k">❤️ اللايكات</div><div class="v" id="pLikes">-</div></div>
        <div><div class="k">🌍 السيرفر</div><div class="v" id="pServer">-</div></div>
        <div><div class="k">🕐 آخر دخول</div><div class="v" id="pLogin">-</div></div>
      </div>
    </div>
  </div>

  <div class="panel">
    <h2 class="sec-title"><span class="dot" style="background:#22c55e"></span> الحسابات المتصلة</h2>
    <table>
      <thead><tr><th>الحساب (UID)</th><th>ايدي اللاعب</th><th>الحالة</th></tr></thead>
      <tbody id="tblOnline"></tbody>
    </table>
  </div>

  <div class="panel">
    <h2 class="sec-title"><span class="dot" style="background:#ef4444"></span> الحسابات الغير متصلة</h2>
    <table>
      <thead><tr><th>الحساب (UID)</th><th>الحالة</th></tr></thead>
      <tbody id="tblOffline"></tbody>
    </table>
  </div>
</div>

<div id="toast"></div>

<script>
function toast(msg){
  const t = document.getElementById('toast');
  t.textContent = msg; t.style.display = 'block';
  setTimeout(()=> t.style.display='none', 3000);
}

async function startSpam(){
  const uid = document.getElementById('uidInput').value.trim();
  if(!uid || !/^\d+$/.test(uid)){ toast('⚠️ أدخل ايدي صحيح (أرقام فقط)'); return; }
  document.getElementById('btnStart').disabled = true;
  try{
    const r = await fetch('/api/start?uid=' + encodeURIComponent(uid));
    const j = await r.json();
    if(j.success){ toast('✅ تم تشغيل الطلبات على: ' + uid); }
    else { toast('❌ ' + (j.message || 'فشل التشغيل')); }
  }catch(e){ toast('❌ خطأ في الاتصال'); }
  document.getElementById('btnStart').disabled = false;
}

async function stopSpam(){
  try{
    const r = await fetch('/api/stop');
    const j = await r.json();
    toast(j.success ? '⏹ تم إيقاف الطلبات' : '❌ فشل الإيقاف');
  }catch(e){ toast('❌ خطأ في الاتصال'); }
}

function badge(status){
  if(status === 'online') return '<span class="badge b-online">متصل</span>';
  if(status === 'connecting') return '<span class="badge b-con pulse">جاري الاتصال...</span>';
  return '<span class="badge b-off">غير متصل</span>';
}

async function refresh(){
  try{
    const r = await fetch('/api/status');
    const j = await r.json();

    document.getElementById('cOnline').textContent = j.online.length;
    document.getElementById('cOffline').textContent = j.offline.length;
    document.getElementById('cTotal').textContent = j.total;

    const spamEl = document.getElementById('cSpam');
    if(j.spam_running){
      spamEl.textContent = 'يعمل ⚡'; spamEl.className = 'num green pulse';
    } else {
      spamEl.textContent = 'متوقف'; spamEl.className = 'num yellow';
    }

    const to = document.getElementById('tblOnline');
    to.innerHTML = j.online.length
      ? j.online.map(a => `<tr><td>${a.id}</td><td>${a.player_uid || '-'}</td><td>${badge(a.status)}</td></tr>`).join('')
      : '<tr><td colspan="3" style="text-align:center;color:#6b7280">لا توجد حسابات متصلة حالياً</td></tr>';

    const tf = document.getElementById('tblOffline');
    tf.innerHTML = j.offline.length
      ? j.offline.map(a => `<tr><td>${a.id}</td><td>${badge(a.status)}</td></tr>`).join('')
      : '<tr><td colspan="2" style="text-align:center;color:#6b7280">جميع الحسابات متصلة ✅</td></tr>';

    const pi = document.getElementById('playerInfo');
    if(j.target_info){
      pi.classList.add('show');
      document.getElementById('pName').textContent = j.target_info.nickname || '-';
      document.getElementById('pUid').textContent = j.target_info.uid || j.target || '-';
      document.getElementById('pLevel').textContent = j.target_info.level ?? '-';
      document.getElementById('pLikes').textContent = j.target_info.likes ?? '-';
      document.getElementById('pServer').textContent = j.target_info.server || '-';
      document.getElementById('pLogin').textContent = j.target_info.last_login || '-';
    } else if(j.target){
      pi.classList.add('show');
      document.getElementById('pName').textContent = 'جاري الجلب...';
      document.getElementById('pUid').textContent = j.target;
      document.getElementById('pLevel').textContent = '...';
      document.getElementById('pLikes').textContent = '...';
      document.getElementById('pServer').textContent = '...';
      document.getElementById('pLogin').textContent = '...';
    } else {
      pi.classList.remove('show');
    }
  }catch(e){}
}
setInterval(refresh, 3000);
refresh();
</script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(PAGE)


@app.route('/api/start', methods=['GET'])
def api_start():
    global spam_running
    uid = request.args.get('uid', '').strip()
    if not uid or not uid.isdigit():
        return jsonify({"success": False, "message": "uid مطلوب (أرقام فقط)"}), 400
    with connected_clients_lock:
        if not connected_clients:
            return jsonify({"success": False, "message": "لا توجد حسابات متصلة حالياً"}), 400
    with state_lock:
        spam_running = True
    set_target_for_all(uid)
    return jsonify({"success": True, "message": f"Spam started on {uid}", "target": uid,
                    "interval_seconds": spam_speed})


@app.route('/api/stop', methods=['GET'])
def api_stop():
    global spam_running, current_target, current_target_info
    with state_lock:
        spam_running = False
        current_target = None
    with target_info_lock:
        current_target_info = None
    with connected_clients_lock:
        for _, client in connected_clients.items():
            client.target_id = None
    return jsonify({"success": True, "message": "Spam stopped"})


@app.route('/api/status', methods=['GET'])
def api_status():
    with connected_clients_lock:
        online_ids = set(connected_clients.keys())
        online_list = [
            {'id': c.id, 'player_uid': getattr(c, 'account_uid', None), 'status': 'online'}
            for c in connected_clients.values()
        ]
    with all_accounts_lock:
        offline_list = [
            {'id': a['id'], 'status': a['status']}
            for a in all_accounts.values() if a['id'] not in online_ids
        ]
        total = len(all_accounts)
    with state_lock:
        running = spam_running
        target = current_target
    with target_info_lock:
        info = current_target_info
    return jsonify({
        "online": online_list,
        "offline": offline_list,
        "total": total,
        "spam_running": running,
        "target": target,
        "target_info": info,
        "interval_seconds": spam_speed
    })



@app.route('/spam', methods=['GET'])
def legacy_spam():
    return api_start()


@app.route('/stop', methods=['GET'])
def legacy_stop():
    return api_stop()


def run_api():
    print(f"{GREEN}[START]{RESET} xAyOuB SpaM RooM API ... (interval={spam_speed}s per invite)")
    threading.Thread(target=start_accounts, daemon=True).start()
    port = int(os.environ.get('PORT', 50019))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)


if __name__ == "__main__":
    run_api()
