import requests, json, binascii, time, urllib3, base64, re, socket, threading, random, os, jwt, sys
from protobuf_decoder.protobuf_decoder import Parser
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 27, 2, '', 'my_message.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x10my_message.proto">\n\tMyMessage\x12\x0f\n\x07\x66ield21\x18\x15 \x01(\x03'
    b'\x12\x0f\n\x07\x66ield22\x18\x16 \x01(\x0c\x12\x0f\n\x07\x66ield23\x18\x17 \x01(\x0c\x62\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'my_message_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_MYMESSAGE']._serialized_start = 20
    _globals['_MYMESSAGE']._serialized_end = 82

Key, Iv = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56]), \
          bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def EnC_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return cipher.encrypt(pad(bytes.fromhex(HeX), AES.block_size)).hex()

def DEc_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return unpad(cipher.decrypt(bytes.fromhex(HeX)), AES.block_size).hex()

def EnC_PacKeT(HeX, K, V):
    return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()

def DEc_PacKeT(HeX, K, V):
    return unpad(AES.new(K, AES.MODE_CBC, V).decrypt(bytes.fromhex(HeX)), 16).hex()

def EnC_Uid(H, Tp):
    e, H = [], int(H)
    while H:
        e.append((H & 0x7F) | (0x80 if H > 0x7F else 0)); H >>= 7
    return bytes(e).hex() if Tp == 'Uid' else None

def EnC_Vr(N):
    if N < 0: ''
    H = []
    while True:
        BesTo = N & 0x7F; N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)

def DEc_Uid(H):
    n = s = 0
    for b in bytes.fromhex(H):
        n |= (b & 0x7F) << s
        if not b & 0x80: break
        s += 7
    return n

def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return EnC_Vr(field_header) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr(field_header) + EnC_Vr(len(encoded_value)) + encoded_value

def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            packet.extend(CrEaTe_LenGTh(field, CrEaTe_ProTo(value)))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(CrEaTe_LenGTh(field, value))
    return packet

def DecodE_HeX(H):
    R = hex(H)
    F = str(R)[2:]
    if len(F) == 1: F = "0" + F; return F
    else: return F

def Fix_PackEt(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data['wire_type'] = result.wire_type
        if result.wire_type == "varint":
            field_data['data'] = result.data
        if result.wire_type == "string":
            field_data['data'] = result.data
        if result.wire_type == "bytes":
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = Fix_PackEt(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

def DeCode_PackEt(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_dict = Fix_PackEt(parsed_results)
        return json.dumps(parsed_results_dict)
    except Exception as e:
        return None

def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i + 3] for i in range(0, len(str(n)), 3))

def ArA_CoLor():
    Tp = ["32CD32", "00BFFF", "00FA9A", "90EE90", "FF4500", "FF6347", "FF69B4", "FF8C00", "FF6347",
          "FFD700", "FFDAB9", "F0F0F0", "F0E68C", "D3D3D3", "A9A9A9", "D2691E", "CD853F", "BC8F8F",
          "6A5ACD", "483D8B", "4682B4", "9370DB", "C71585", "FF8C00", "FFA07A"]
    return random.choice(Tp)

def xBunnEr():
    bN = [902000306, 902000305, 902000003, 902000016, 902000017, 902000019, 902000020, 902000021,
          902000023, 902000070, 902000087, 902000108, 902000011, 902049020, 902049018, 902049017,
          902049016, 902049015, 902049003, 902033016, 902033017, 902033018, 902048018, 902000306, 902000305]
    return random.choice(bN)

def spmroom(K, V, uid):
    fields = {1: 22, 2: {1: int(uid)}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0E15', K, V)

def openroom(K, V):
    fields = {1: 2, 2: {1: 1, 2: 15, 3: 3, 4: "[C][B]x[FF0000]AyOuB", 5: "11", 6: 8, 7: 30, 8: 1,
              9: 1, 11: 1, 14: 35670336, 15: {1: "IDC4", 2: 269, 3: "ME"}, 16: "\x01\x07\t\n\x0b\x12\x19 '",
              18: 10757192, 27: 1, 34: "\x00\x01", 40: "fr", 46: 1104, 48: 1, 49: "\x08\x15",
              50: {1: 35670336, 2: 10757192, 3: 80}, 56: 1}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0E15', K, V)

def SEnd_InV(Nu, Uid, K, V):
    fields = {1: 2, 2: {1: int(Uid), 2: "ME", 4: int(Nu)}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', K, V)

def ExiT(id, K, V):
    fields = {1: 7, 2: {1: int(11037044965)}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', K, V)

def GeT_Status(PLayer_Uid, K, V):
    PLayer_Uid = EnC_Uid(PLayer_Uid, Tp='Uid')
    if len(PLayer_Uid) == 8: Pk = f'080112080a04{PLayer_Uid}1005'
    elif len(PLayer_Uid) == 10: Pk = f"080112090a05{PLayer_Uid}1005"
    return GeneRaTePk(Pk, '0f15', K, V)

def SPam_Room(Uid, Rm, Nm, K, V):
    fields = {1: 78, 2: {1: int(Rm), 2: f"[{ArA_CoLor()}]{Nm}", 3: {2: 1, 3: 1}, 4: 330, 5: 1,
              6: 201, 10: xBunnEr(), 11: int(Uid), 12: 1}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0e15', K, V)

def Join_Room(room_id, K, V):
    fields = {1: 3, 2: {1: int(room_id), 8: {1: "IDC1", 2: 3000, 3: "ME"}, 9: "\x01\t\n\x12\x19 ",
              10: 1, 12: b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01",
              13: 3, 14: 3, 16: "ME"}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0e10', K, V)

def _V(b, i):
    r = s = 0
    while True:
        c = b[i]; i += 1
        r |= (c & 0x7F) << s
        if c < 0x80: break
        s += 7
    return r, i

def PrOtO(hx):
    b, i, R = bytes.fromhex(hx), 0, {}
    while i < len(b):
        H, i = _V(b, i)
        F, T = H >> 3, H & 7
        if T == 0:
            R[F], i = _V(b, i)
        elif T == 2:
            L, i = _V(b, i)
            S = b[i:i+L]; i += L
            try: R[F] = S.decode()
            except:
                try: R[F] = PrOtO(S.hex())
                except: R[F] = S
        elif T == 5:
            R[F] = int.from_bytes(b[i:i+4], 'little'); i += 4
        else:
            raise ValueError(f'Unknown wire type: {T}')
    return R

def GeT_KEy(obj, target):
    values = []
    def collect(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == target: values.append(v)
                collect(v)
        elif isinstance(o, list):
            for v in o: collect(v)
    collect(obj)
    return values[-1] if values else None

def GeneRaTePk(Pk, N, K, V):
    PkEnc = EnC_PacKeT(Pk, K, V)
    _ = DecodE_HeX(int(len(PkEnc) // 2))
    if len(_) == 2: HeadEr = N + "000000"
    elif len(_) == 3: HeadEr = N + "00000"
    elif len(_) == 4: HeadEr = N + "0000"
    elif len(_) == 5: HeadEr = N + "000"
    return bytes.fromhex(HeadEr + _ + PkEnc)


def GeT_PLayer_InFo(uid, Token):
    try:
        data = bytes.fromhex(EnC_AEs(f"08{EnC_Uid(uid, Tp='Uid')}1007"))
        url = "https://clientbp.ggpolarbear.com/GetPlayerPersonalShow"
        headers = {
            'X-Unity-Version': '2022.3.47f1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'Authorization': f'Bearer {Token}',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': 'clientbp.ggpolarbear.com',
            'Connection': 'close',
            'Accept-Encoding': 'gzip'
        }
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
        if response.status_code not in (200, 201):
            return None
        packet = binascii.hexlify(response.content).decode('utf-8')
        BesTo_data = json.loads(DeCode_PackEt(packet))
        d = BesTo_data["1"]["data"]
        info = {
            "nickname": str(d["3"]["data"]),
            "uid": str(d["1"]["data"]),
            "level": d.get("6", {}).get("data"),
            "likes": d.get("21", {}).get("data"),
            "server": d.get("5", {}).get("data"),
        }
        try:
            info["last_login"] = datetime.fromtimestamp(d["24"]["data"]).strftime("%d/%m/%y %I:%M %p")
        except Exception:
            info["last_login"] = None
        try:
            info["created"] = datetime.fromtimestamp(d["44"]["data"]).strftime("%d/%m/%y")
        except Exception:
            info["created"] = None
        try:
            info["bio"] = BesTo_data["9"]["data"]["9"]["data"]
        except Exception:
            info["bio"] = None
        return info
    except Exception:
        return None
