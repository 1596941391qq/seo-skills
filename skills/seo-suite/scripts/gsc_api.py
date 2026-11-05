#!/usr/bin/env python3
"""GSC API 客户端(纯 stdlib;pipeline-completeness.md R2-1,data-onboarding.md T2)。
服务账号(Service Account)RS256 JWT 直连 Search Console API,一次拉取产规范化 CSV
供 6 脚本复用(gsc_mining / traffic_funnel / monitor / sensor_volatility / did_attribution /
seo_vs_ads),消灭 4 形态手工导出(R2-2 落地层的前置件)。

核心:RSA 签名纯 stdlib 实现(零第三方依赖,与套件纪律一致):
  PEM(PKCS#8 `BEGIN PRIVATE KEY` / PKCS#1 `BEGIN RSA PRIVATE KEY`)→ base64 → 手工 ASN.1 DER
  TLV 解析取 modulus/privateExponent → PKCS#1 v1.5 签名:
  EM = 00 01 FF..FF 00 || DigestInfo(SHA-256) → s = pow(m, d, n)(原生大整数,无需长除法)。
  已与 `openssl dgst -sha256 -sign` 对拍逐字节一致(确定性填充,tests/test_gsc_api.py)。

用法:
  python3 gsc_api.py auth --sa service_account.json [--subject user@domain.com] [--show-token]
  python3 gsc_api.py sites --sa service_account.json [--json]
  python3 gsc_api.py query --site sc-domain:example.com --start 2026-09-01 --end 2026-09-28
                         [--dimensions query,page] [--rows 25000] [--out gsc.csv] [--json]
凭证寻径(优先级):--sa > --key > env GSC_SA_FILE > ~/.config/seo-suite/gsc.json。
  文件形态:Google Cloud 原生 service_account.json,或套件包装 {"credentials": {...}}(自动解包,
  与 doctor.py 对 gsc.json 的 credentials 键探测同口径)。需含 private_key / client_email / token_uri。
  subject 仅 Workspace 域级委派场景需要(GSC 一般直接授权 SA 邮箱,subject 留空)。

规范化 CSV 契约(与现有消费方逐列对齐,列头大小写不敏感方均可读):
  列: [Date]*,Query,Page,[Country,CountryCode,Device,SearchAppearance,Hour]*,Clicks,Impressions,
      CTR,Position(*仅 --dimensions 含对应维度时;country 维:Country=英文国名、CountryCode=ISO alpha-3)
  - Query/Page 恒在场(维度未请求时留空)——page 单维拉取可直接喂 traffic_funnel
    (Page/Impressions/Clicks)与 monitor gsc.csv;query 维喂 gsc_mining --mode query;
    query+page 喂 gsc_mining --mode matrix;date,query 喂 sensor_volatility(Date/Query/Position);
    page+date 喂 did_attribution(Page,Clicks[,Date])。
  - CTR 用小数(0.0317)而非百分比串:gsc_mining.parse_ctr 对 <1% 的 "0.50%" 形态会 100 倍
    误读(float>1 才 ÷100),小数形态全区间无歧义;Position 2 位小数;Clicks/Impressions 取整。
分页:searchanalytics.query 单页上限 25000 行,startRow 循环翻页至取满 --rows 或页短循环。

诚实边界(不假装能做到的):
  - 无 refresh 场景:SA JWT 换的 access_token 自含 1h 有效期,过期重签即可,不存在 refresh token;
  - token 仅内存缓存 50 分钟(不落盘,进程退出即失效);
  - 配额每站点、每用户 1,200 QPM;每项目 40,000 QPM(developers.google.com/webmaster-tools/limits):批量拉取自然远低于此,429 时
    错误信息附降频提示;
  - 匿名查询(privacy 保护)不出现在 API 结果中——导出 CSV 同口径,不是数据丢失。

SSRF 防御(照套件惯例,本工具端点固定):token_uri 与 API 端点强制 https + googleapis.com
域白名单(token_uri 来自 SA json 属外部输入,防凭证文件被改指向内网探测)。

退出码: 0 正常 / 1 运行错(网络/HTTP/auth 失败/凭证文件坏)/ 2 用法错(参数/维度/日期/SSRF 拒)。
"""
import argparse
import base64
import binascii
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date as _date

SCHEMA_VERSION = 1               # --json 顶层 schema 版本(输出契约)
UA = "seo-suite-gsc/1.0"
GSC_API_BASE = "https://searchconsole.googleapis.com/webmasters/v3"
GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
GRANT_TYPE = "urn:ietf:params:oauth:grant-type:jwt-bearer"
DEFAULT_SA_CANDIDATES = (os.path.join(".config", "seo-suite", "gsc.json"),)  # 末位回退(家目录下)
ROW_LIMIT_MAX = 25000            # searchanalytics.query 单页硬上限
TOKEN_CACHE_TTL = 50 * 60        # token 内存缓存 50 分钟(官方有效期 3600s,留 10min 余量)
FETCH_LIMIT = 4_000_000          # 响应体读取上限(与 field_data 同量级)
TOKEN_TTL_JWT = 3600             # JWT exp-iat(官方建议 ≤3600)
# Search Analytics: query 参考页(2026-08-11 版):dimensions 可用 filters[].dimension 的全部名字
# (country / device / page / query / searchAppearance)外加 date、hour。小写输入 → API 原名。
API_DIMENSIONS = {"date": "date", "hour": "hour", "query": "query", "page": "page",
                  "country": "country", "device": "device", "searchappearance": "searchAppearance"}
ALLOWED_DIMENSIONS = tuple(API_DIMENSIONS.values())
CSV_BASE_COLUMNS = ["Query", "Page", "Clicks", "Impressions", "CTR", "Position"]
# 可选维度列:只在请求了该维度时出现,插在 Page 之后、Clicks 之前(query/page 老输出逐字节不变)
EXTRA_DIM_COLUMNS = (("country", "Country"), ("country", "CountryCode"), ("device", "Device"),
                     ("searchAppearance", "SearchAppearance"), ("hour", "Hour"))
# API 的 country 值是 ISO 3166-1 alpha-3(小写);market_fit --gsc-country 按 GSC 网页导出的
# 英文国名映射市场 → Country 列给英文国名(表外的回落为大写 alpha-3),CountryCode 列给原码。
ISO3_COUNTRY_NAME = {
    "dza": "Algeria", "ago": "Angola", "arg": "Argentina", "aus": "Australia", "aut": "Austria",
    "bhr": "Bahrain", "blr": "Belarus", "bel": "Belgium", "btn": "Bhutan", "bol": "Bolivia",
    "bra": "Brazil", "can": "Canada", "chl": "Chile", "chn": "China", "col": "Colombia",
    "cri": "Costa Rica", "cub": "Cuba", "dom": "Dominican Republic", "ecu": "Ecuador",
    "egy": "Egypt", "slv": "El Salvador", "fra": "France", "deu": "Germany", "gtm": "Guatemala",
    "hnd": "Honduras", "hkg": "Hong Kong", "ind": "India", "idn": "Indonesia", "irq": "Iraq",
    "irl": "Ireland", "ita": "Italy", "jpn": "Japan", "jor": "Jordan", "kaz": "Kazakhstan",
    "kor": "South Korea", "kwt": "Kuwait", "kgz": "Kyrgyzstan", "lbn": "Lebanon", "lby": "Libya",
    "lie": "Liechtenstein", "lux": "Luxembourg", "mac": "Macau", "mex": "Mexico", "mco": "Monaco",
    "mar": "Morocco", "moz": "Mozambique", "npl": "Nepal", "nld": "Netherlands",
    "nzl": "New Zealand", "nic": "Nicaragua", "omn": "Oman", "pan": "Panama", "pry": "Paraguay",
    "per": "Peru", "pol": "Poland", "prt": "Portugal", "pri": "Puerto Rico", "qat": "Qatar",
    "rus": "Russia", "smr": "San Marino", "sau": "Saudi Arabia", "zaf": "South Africa",
    "esp": "Spain", "sdn": "Sudan", "che": "Switzerland", "twn": "Taiwan", "tha": "Thailand",
    "tun": "Tunisia", "tur": "Turkey", "are": "United Arab Emirates", "gbr": "United Kingdom",
    "usa": "United States", "ury": "Uruguay", "uzb": "Uzbekistan", "vat": "Vatican City",
    "ven": "Venezuela", "vnm": "Vietnam", "yem": "Yemen", "sgp": "Singapore", "mys": "Malaysia",
    "phl": "Philippines", "ukr": "Ukraine", "swe": "Sweden", "nor": "Norway", "dnk": "Denmark",
    "fin": "Finland", "grc": "Greece", "cze": "Czechia", "hun": "Hungary", "rou": "Romania",
    "isr": "Israel", "pak": "Pakistan", "bgd": "Bangladesh", "nga": "Nigeria", "ken": "Kenya",
}

# SHA-256 的 DigestInfo DER 前缀(RFC 8017 §9.2 note 1):SEQUENCE{SEQUERCE{OID 2.16.840.1.101.3.4.2.1,
# NULL}, OCTET STRING} 头 —— 拼接 32 字节摘要即完整 DigestInfo。
_SHA256_DIGESTINFO_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")
# rsaEncryption OID(1.2.840.113549.1.1.1)内容字节(DER TLV 06 09 之后的 9 字节值)
_RSA_OID = bytes.fromhex("2a864886f70d010101")

USAGE_EPILOG = """
凭证寻径: --sa PATH > --key PATH > $GSC_SA_FILE > ~/.config/seo-suite/gsc.json
  (接受 Google Cloud 原生 service_account.json 或套件 {"credentials":{...}} 包装)
规范化 CSV 列: [Date]*,Query,Page,[Country,CountryCode,Device,SearchAppearance,Hour]*,
  Clicks,Impressions,CTR,Position(*仅维度含对应项;country 单维 CSV 可喂 market_fit --gsc-country)
  可直接喂 gsc_mining / traffic_funnel --gsc / monitor(.seo-monitor/gsc.csv) /
  sensor_volatility --gsc / did_attribution;CTR 为小数(0.0317)非百分比串。
诚实边界: 无 refresh 场景(SA token 自含);token 只进内存(50 分钟缓存,不落盘);
  配额每站点/每用户 1,200 QPM;单页 25000 行,startRow 分页;匿名查询 API 不返回(与导出同口径)。
退出码: 0 正常 / 1 运行错(auth/网络/HTTP/凭证) / 2 用法错(参数/SSRF 拒)"""


class GuardError(Exception):
    """端点白名单拒(SSRF 防御)——用法级错误(exit 2)。"""


class SaError(Exception):
    """SA 凭证文件问题(缺失/缺键/坏 PEM)——运行错(exit 1)。"""


class ApiError(Exception):
    """API 语义错误(invalid_grant / 响应缺字段)——运行错(exit 1)。"""


class UsageError(Exception):
    """参数校验失败——用法错(exit 2)。"""


# ---------- RSA:PEM → ASN.1 DER → (n, e, d),PKCS#1 v1.5 签名(纯 stdlib) ----------

def _der_read(buf, off):
    """读一个 TLV;返回 (tag, value_bytes, 下一偏移)。支持长形长度(0x81/0x82..)。"""
    if off + 2 > len(buf):
        raise ValueError("DER 截断:偏移 %d 处无完整 tag+len" % off)
    tag = buf[off]
    ln = buf[off + 1]
    off += 2
    if ln & 0x80:
        nbytes = ln & 0x7F
        if nbytes == 0 or off + nbytes > len(buf):
            raise ValueError("DER 长度字节非法(0x%02x)" % ln)
        ln = int.from_bytes(buf[off:off + nbytes], "big")
        off += nbytes
    if off + ln > len(buf):
        raise ValueError("DER 内容越界:声明 %d 字节但只剩 %d" % (ln, len(buf) - off))
    return tag, buf[off:off + ln], off + ln


def _der_children(content):
    """顺序读出容器内全部子 TLV;返回 [(tag, value), ...]。"""
    out, off = [], 0
    while off < len(content):
        tag, val, off = _der_read(content, off)
        out.append((tag, val))
    return out


def _parse_pkcs1_rsa_private(der):
    """PKCS#1 RSAPrivateKey ::= SEQUENCE{version, n, e, d, p, q, ...} → (n, e, d)。"""
    tag, content, _ = _der_read(der, 0)
    if tag != 0x30:
        raise ValueError("PKCS#1 顶层应为 SEQUENCE(0x30),实得 0x%02x" % tag)
    ch = _der_children(content)
    ints = [v for t, v in ch if t == 0x02]
    if len(ints) < 4:
        raise ValueError("PKCS#1 私钥应含 ≥4 个 INTEGER(version/n/e/d...),实得 %d" % len(ints))
    if int.from_bytes(ints[0], "big") != 0:
        raise ValueError("PKCS#1 version 应为 0(multi-prime 不支持)")
    n, e, d = (int.from_bytes(v, "big") for v in ints[1:4])   # 首个 INTEGER 是 version
    if n.bit_length() < 512:
        raise ValueError("RSA 模数过小(%d bit,需 ≥512)" % n.bit_length())
    if e < 3 or d <= 0 or pow(pow(2, e, n), d, n) != 2:      # 廉价自洽校验(签名-验证回环)
        raise ValueError("RSA (n,e,d) 自洽校验失败:非有效密钥三元组")
    return n, e, d


def _parse_pkcs8(der):
    """PKCS#8 PrivateKeyInfo ::= SEQUENCE{version 0, SEQUENCE{OID rsaEncryption[,NULL]},
    OCTET STRING pkcs1-der} → 解包后走 PKCS#1 解析。"""
    tag, content, _ = _der_read(der, 0)
    if tag != 0x30:
        raise ValueError("PKCS#8 顶层应为 SEQUENCE(0x30),实得 0x%02x" % tag)
    ch = _der_children(content)
    if len(ch) < 3 or ch[0][0] != 0x02 or ch[1][0] != 0x30 or ch[2][0] != 0x04:
        raise ValueError("PKCS#8 结构不符(应 version INTEGER + algid SEQUENCE + OCTET STRING)")
    alg = _der_children(ch[1][1])
    if len(alg) < 1 or alg[0][0] != 0x06 or alg[0][1] != _RSA_OID:
        raise ValueError("PKCS#8 算法 OID 非 rsaEncryption(仅支持 RSA 密钥)")
    return _parse_pkcs1_rsa_private(ch[2][1])


def parse_private_key_pem(pem):
    """PEM 文本 → (n, e, d)。认 PKCS#8(`BEGIN PRIVATE KEY`,Google SA json 原生形态)
    与 PKCS#1(`BEGIN RSA PRIVATE KEY`,openssl -traditional 形态)两种标签;
    加密 PEM(`ENCRYPTED`)不支持(值为外部输入,本工具零交互解密)。"""
    m = re.search(r"-----BEGIN ([A-Z ]+)-----(.*?)-----END \1-----", pem or "", re.S)
    if not m:
        raise ValueError("PEM 中找不到 BEGIN/END 块(需 PKCS#8 或 PKCS#1 RSA 私钥)")
    label, b64body = m.group(1), "".join(m.group(2).split())
    try:
        der = base64.b64decode(b64body, validate=True)
    except (binascii.Error, ValueError) as e:
        raise ValueError("PEM base64 解码失败: %s" % e)
    if label == "PRIVATE KEY":
        return _parse_pkcs8(der)
    if label == "RSA PRIVATE KEY":
        return _parse_pkcs1_rsa_private(der)
    raise ValueError("不支持的 PEM 标签 %r(需 PRIVATE KEY / RSA PRIVATE KEY)" % label)


def rsa_sign(sha256_digest, private_key_pem):
    """RS256 签名(PKCS#1 v1.5,RFC 8017 §8.2.1):32 字节 SHA-256 摘要 → k 字节签名。
    纯函数零网络;与 `openssl dgst -sha256 -sign` 输出逐字节一致(确定性填充)。"""
    if len(sha256_digest) != 32:
        raise ValueError("需 32 字节 SHA-256 摘要,实得 %d" % len(sha256_digest))
    n, _e, d = parse_private_key_pem(private_key_pem)
    k = (n.bit_length() + 7) // 8
    t = _SHA256_DIGESTINFO_PREFIX + sha256_digest
    ps_len = k - len(t) - 3
    if ps_len < 8:
        raise ValueError("RSA 模数过小:填充区 %d 字节 <8" % ps_len)
    em = b"\x00\x01" + b"\xff" * ps_len + b"\x00" + t      # EM = 00 01 FF.. 00 || DigestInfo
    sig = pow(int.from_bytes(em, "big"), d, n)              # 原生大整数模幂,无需长除法
    return sig.to_bytes(k, "big")


# ---------- JWT(RS256)与 token 交换 ----------

def b64url(raw):
    """base64url 无填充(RFC 7515)。"""
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def build_jwt(sa, subject=None, now=None, ttl=TOKEN_TTL_JWT):
    """SA json → RS256 JWT 字符串(纯函数,now 可注入供确定性测试)。
    claims: iss=client_email / scope=webmasters.readonly / aud=token_uri / iat / exp=iat+ttl
    [,sub=subject(域委派)]。"""
    iat = int(time.time() if now is None else now)
    header = {"alg": "RS256", "typ": "JWT"}
    claims = {"iss": sa["client_email"], "scope": GSC_SCOPE, "aud": sa["token_uri"],
              "exp": iat + ttl, "iat": iat}
    if subject:
        claims["sub"] = subject
    h = b64url(json.dumps(header, separators=(",", ":")).encode())
    c = b64url(json.dumps(claims, separators=(",", ":")).encode())
    sig = rsa_sign(hashlib.sha256(("%s.%s" % (h, c)).encode("ascii")).digest(), sa["private_key"])
    return "%s.%s.%s" % (h, c, b64url(sig))


def _http_json(url, data=None, headers=None, timeout=30):
    """唯一网络出口(测试打桩点):GET(data=None)/POST;返回解析后的 dict;
    HTTPError 原样上抛(body 由调用方的 describe_http_error 读)。"""
    req = urllib.request.Request(url, data=data, headers=headers or {"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read(FETCH_LIMIT).decode("utf-8", "replace"))


_token_cache = {}          # {(client_email, subject): {"token":…, "expires_at":…}}


def fetch_token(sa, subject=None, timeout=30, now=None):
    """签 JWT → POST token_uri(grant_type=jwt-bearer)→ token 响应 dict(不缓存)。"""
    guard_googleapis(sa["token_uri"])                      # token_uri 来自凭证文件,属外部输入
    jwt = build_jwt(sa, subject=subject, now=now)
    body = urllib.parse.urlencode({"grant_type": GRANT_TYPE, "assertion": jwt}).encode("ascii")
    resp = _http_json(sa["token_uri"], data=body, timeout=timeout,
                      headers={"User-Agent": UA,
                               "Content-Type": "application/x-www-form-urlencoded",
                               "Accept": "application/json"})
    if not isinstance(resp, dict) or not resp.get("access_token"):
        raise ApiError("token 响应缺 access_token: %s" % json.dumps(resp)[:200])
    return resp


def get_access_token(sa, subject=None, timeout=30, now=None):
    """取 access_token,内存缓存 50 分钟(键=client_email+subject;不落盘)。
    now 可注入供测试(rewind 缓存到期路径)。"""
    key = (sa.get("client_email") or "", subject or "")
    t = time.time() if now is None else now
    hit = _token_cache.get(key)
    if hit and t < hit["expires_at"]:
        return hit["token"]
    resp = fetch_token(sa, subject=subject, timeout=timeout, now=now)
    ttl = min(int(resp.get("expires_in") or 3600), TOKEN_CACHE_TTL)
    _token_cache[key] = {"token": resp["access_token"], "expires_at": t + ttl,
                         "resp": resp}
    return resp["access_token"]


def cached_token_entry(sa, subject=None):
    """测试/自省用:读缓存条目(不触发网络)。"""
    return _token_cache.get((sa.get("client_email") or "", subject or ""))


# ---------- SSRF 防御(端点固定 googleapis.com,域白名单即可) ----------

def guard_googleapis(url):
    """端点守卫:仅 https + googleapis.com(或子域)。本工具端点本应固定,但 token_uri
    来自 SA json(外部输入),防凭证文件被改指向内网/元数据端点探测。"""
    p = urllib.parse.urlsplit(url or "")
    host = (p.hostname or "").lower()
    if p.scheme != "https" or not host:
        raise GuardError("SSRF 守卫:仅允许 https 端点: %s" % url)
    if host != "googleapis.com" and not host.endswith(".googleapis.com"):
        raise GuardError("SSRF 守卫:端点域不在 googleapis.com 白名单: %s" % url)
    return True


# ---------- GSC API:sites / searchanalytics.query(分页) ----------

def _auth_headers(token):
    return {"User-Agent": UA, "Authorization": "Bearer " + token,
            "Content-Type": "application/json", "Accept": "application/json"}


def list_sites(sa, subject=None, timeout=30):
    """webmasters/v3/sites:列已验证站点 → [{siteUrl, permissionLevel}...]。"""
    url = GSC_API_BASE + "/sites"
    guard_googleapis(url)
    token = get_access_token(sa, subject=subject, timeout=timeout)
    return _http_json(url, headers=_auth_headers(token), timeout=timeout).get("siteEntry") or []


def query_url(site):
    """searchanalytics.query 端点;site 含 ':'/'/'(sc-domain:example.com 或 https://…/)
    必须整体 percent-encode 进路径。"""
    guard_googleapis(GSC_API_BASE)
    return "%s/sites/%s/searchAnalytics/query" % (GSC_API_BASE, urllib.parse.quote(site, safe=""))


def searchanalytics_query(sa, site, start, end, dimensions, rows_cap=ROW_LIMIT_MAX,
                          subject=None, timeout=30, page_meta=None):
    """分页拉取:rowLimit=min(25000, 剩余),startRow 递增,页短(want)即止;
    返回 API rows 原始列表(≤rows_cap)。page_meta 收每页请求/到货行数(测试与 --json 用)。"""
    url = query_url(site)
    token = get_access_token(sa, subject=subject, timeout=timeout)
    rows, offset = [], 0
    while offset < rows_cap:
        want = min(ROW_LIMIT_MAX, rows_cap - offset)
        body = {"startDate": start, "endDate": end, "dimensions": list(dimensions),
                "rowLimit": want, "startRow": offset}
        if "hour" in dimensions:       # 参考页:按 HOUR 分组时用 dataState=hourly_all
            body["dataState"] = "hourly_all"
        data = _http_json(url, data=json.dumps(body).encode("utf-8"),
                          headers=_auth_headers(token), timeout=timeout)
        got = data.get("rows") or []
        rows.extend(got)
        if page_meta is not None:
            page_meta.append({"startRow": offset, "rowLimit": want, "got": len(got)})
        if len(got) < want:            # 页短循环 = 数据见底
            break
        offset += len(got)
    return rows[:rows_cap]


# ---------- 规范化:API rows → 契约记录 / CSV ----------

def normalize_rows(rows, dimensions):
    """API rows(keys 顺序=dimensions)→ 契约记录 dicts:
    {Date?, Query, Page, Clicks, Impressions, CTR(小数 float), Position(float)}。
    Query/Page 恒在场(维度缺席留空串)——同份表既能喂 query 侧也能喂 page 侧消费方。"""
    out = []
    for r in rows:
        keys = r.get("keys") or []
        dmap = dict(zip(dimensions, keys))
        rec = {
            "Date": dmap.get("date", ""),
            "Query": dmap.get("query", ""),
            "Page": dmap.get("page", ""),
            "Clicks": int(round(float(r.get("clicks") or 0))),
            "Impressions": int(round(float(r.get("impressions") or 0))),
            "CTR": round(float(r.get("ctr") or 0.0), 6),
            "Position": round(float(r.get("position") or 0.0), 2),
        }
        if "country" in dimensions:
            code = (dmap.get("country") or "").strip()
            rec["CountryCode"] = code.upper()
            rec["Country"] = ISO3_COUNTRY_NAME.get(code.lower(), code.upper())
        if "device" in dimensions:
            rec["Device"] = dmap.get("device", "")
        if "searchAppearance" in dimensions:
            rec["SearchAppearance"] = dmap.get("searchAppearance", "")
        if "hour" in dimensions:
            rec["Hour"] = dmap.get("hour", "")
        out.append(rec)
    return out


def csv_header(dimensions):
    extra = [col for dim, col in EXTRA_DIM_COLUMNS if dim in dimensions]
    return ((["Date"] if "date" in dimensions else []) + CSV_BASE_COLUMNS[:2] + extra
            + CSV_BASE_COLUMNS[2:])


def csv_field(col, rec):
    """CSV 单元格格式:CTR 小数(%g 紧凑,全区间无 parse_ctr 歧义)/ Position %.2f / 其余原样。"""
    if col == "CTR":
        return "%g" % rec["CTR"]
    if col == "Position":
        return "%.2f" % rec["Position"]
    return rec[col]


def write_csv(records, dimensions, out=None):
    """写规范化 CSV:out=None → 返回字符串(stdout 用);否则落盘返回行数。"""
    header = csv_header(dimensions)
    if out is None:
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(header)
        for rec in records:
            w.writerow([csv_field(c, rec) for c in header])
        return buf.getvalue()
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for rec in records:
            w.writerow([csv_field(c, rec) for c in header])
    return len(records)


# ---------- 错误呈现(HTTPError → 人话 + 补救提示) ----------

def describe_http_error(e):
    """HTTPError → (exit_code, message)。400 invalid_grant 给三因提示;403 给授权路径;
    429 给配额降频提示(1200 qpm 注记)。"""
    body = ""
    try:
        body = e.read(500).decode("utf-8", "replace")
    except Exception:
        pass
    err = ""
    try:
        err = (json.loads(body) or {}).get("error") or ""
    except Exception:
        pass
    msg = "HTTP %s %s%s" % (e.code, err or getattr(e, "reason", ""), (" " + body[:180]) if body and not err else "")
    if e.code == 400 and err == "invalid_grant":
        msg += ("\n  invalid_grant 三个常见因:① SA 邮箱未在 GSC 授权"
                "(Search Console → 设置 → 用户和权限 → 添加 SA 邮箱);"
                "② 用了 --subject 但 Workspace 未给 SA 配域级委派(不用委派就别传 --subject);"
                "③ 本机时钟偏差 >5min(核对 iat/exp)")
    elif e.code == 403:
        msg += ("\n  403:SA 邮箱对该站点无权限——GSC 用户和权限里加 SA 邮箱"
                "(permissionLevel ≥ restricted);确认 --site 前缀(sc-domain:example.com"
                " 或 https://example.com/,与 sites 列表完全一致)")
    elif e.code == 429:
        msg += "\n  429:配额每站点/每用户 1,200 QPM——降频或稍后重试"
    return 1, msg


# ---------- 凭证装载 ----------

def load_sa(path):
    """读 SA json;套件包装形态({"credentials": {...}})自动解包(与 doctor 探测同口径);
    校验必需键 + token_uri 白名单。"""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise SaError("SA 凭证文件无法读取 %s: %s" % (path, e))
    except json.JSONDecodeError as e:
        raise SaError("SA 凭证文件不是合法 JSON %s: %s" % (path, e))
    if isinstance(data, dict) and isinstance(data.get("credentials"), dict):
        data = data["credentials"]
    if not isinstance(data, dict):
        raise SaError("SA 凭证文件结构不符 %s(应为对象)" % path)
    for k in ("private_key", "client_email", "token_uri"):
        if not data.get(k):
            raise SaError("SA json 缺 %s 键(%s)——需 Google Cloud 原生 service_account.json"
                          " 或套件 {\"credentials\":{...}} 包装" % (k, path))
    try:
        guard_googleapis(data["token_uri"])
    except GuardError as e:
        raise SaError("SA json token_uri 被守卫拒绝:%s(%s)" % (e, path))
    return data


def resolve_sa_path(args):
    """--sa > --key > $GSC_SA_FILE > ~/.config/seo-suite/gsc.json(存在才用)。"""
    path = getattr(args, "sa", None) or getattr(args, "key", None) \
        or os.environ.get("GSC_SA_FILE")
    if not path:
        cand = os.path.join(os.path.expanduser("~"), *DEFAULT_SA_CANDIDATES)
        path = cand if os.path.isfile(cand) else None
    if not path:
        raise UsageError(
            "未指定 SA 凭证:--sa PATH / --key PATH / env GSC_SA_FILE / "
            "~/.config/seo-suite/gsc.json 四选一(申请:Google Cloud 控制台 → IAM → "
            "服务账号 → 密钥,JSON 格式;data-onboarding.md T2)")
    return path


# ---------- URL Inspection(按每站每天配额排预算) ----------

INSPECT_URL = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
INSPECT_QPD = 2000          # 每站点每天;facts.md「API 配额」
INSPECT_QPM = 600           # 每站点每分钟


def url_inspect(sa, site, url, subject=None, timeout=30, language="en-US"):
    """urlInspection.index.inspect → 只留判断要用的字段(收录判定、覆盖状态、Google 选的 canonical、最近抓取)。"""
    guard_googleapis(INSPECT_URL)
    token = get_access_token(sa, subject=subject, timeout=timeout)
    body = json.dumps({"inspectionUrl": url, "siteUrl": site, "languageCode": language}).encode("utf-8")
    resp = _http_json(INSPECT_URL, data=body, headers=_auth_headers(token), timeout=timeout)
    r = (resp.get("inspectionResult") or {}).get("indexStatusResult") or {}
    return {"url": url, "verdict": r.get("verdict"), "coverage": r.get("coverageState"),
            "indexing": r.get("indexingState"), "robots": r.get("robotsTxtState"),
            "page_fetch": r.get("pageFetchState"), "google_canonical": r.get("googleCanonical"),
            "user_canonical": r.get("userCanonical"), "last_crawl": r.get("lastCrawlTime"),
            "crawled_as": r.get("crawledAs")}


def quota_left(ledger_path, site, day):
    """台账 {日期: {站点: 已用}};返回今天这个站点还剩多少(不含其他工具在同一属性上的用量,保守起见再留 10%)。"""
    try:
        with open(ledger_path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    used = int((data.get(day) or {}).get(site) or 0)
    return max(0, int(INSPECT_QPD * 0.9) - used), data


def record_quota(ledger_path, data, site, day, n):
    data.setdefault(day, {})[site] = int((data.get(day) or {}).get(site) or 0) + n
    for old in sorted(data)[:-14]:          # 只留两周
        data.pop(old, None)
    os.makedirs(os.path.dirname(os.path.abspath(ledger_path)), exist_ok=True)
    tmp = ledger_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, ledger_path)


# ---------- CLI 子命令 ----------

def parse_dimensions(spec):
    raw = [d.strip().lower() for d in (spec or "").split(",") if d.strip()]
    if not raw:
        raise UsageError("--dimensions 不能为空(可选:%s)" % "/".join(ALLOWED_DIMENSIONS))
    bad = [d for d in raw if d not in API_DIMENSIONS]
    if bad:
        raise UsageError("不支持的维度 %s(Search Analytics API 只有 %s)"
                         % (bad, "/".join(ALLOWED_DIMENSIONS)))
    dims = [API_DIMENSIONS[d] for d in raw]
    seen, uniq = set(), []
    for d in dims:                        # 去重保序
        if d not in seen:
            seen.add(d)
            uniq.append(d)
    return uniq


def parse_gsc_date(v, what):
    try:
        return _date.fromisoformat(v or "").isoformat()
    except ValueError:
        raise UsageError("%s 需 YYYY-MM-DD 格式,实得 %r" % (what, v))


def _mask_token(tok):
    return (tok[:10] + "…" + tok[-4:]) if len(tok) > 16 else "…"


def cmd_auth(args):
    sa = load_sa(resolve_sa_path(args))
    t = time.time()
    resp = fetch_token(sa, subject=args.subject, timeout=args.timeout)   # auth 直连验链,不走缓存
    ttl = min(int(resp.get("expires_in") or 3600), TOKEN_CACHE_TTL)
    _token_cache[(sa["client_email"], args.subject or "")] = {
        "token": resp["access_token"], "expires_at": t + ttl, "resp": resp}   # 顺手播种缓存
    tok = resp["access_token"]
    if args.json:
        print(json.dumps({
            "schema_version": SCHEMA_VERSION, "ok": True,
            "client_email": sa["client_email"], "subject": args.subject or None,
            "scope": GSC_SCOPE, "token_uri": sa["token_uri"],
            "token_type": resp.get("token_type"), "expires_in": resp.get("expires_in"),
            "cached_for_sec": ttl, "quota_note": "1200 qpm(searchconsole API)",
            "access_token": tok if args.show_token else _mask_token(tok),
        }, ensure_ascii=False, indent=1))
        return 0
    print("client_email : %s" % sa["client_email"])
    print("subject      : %s" % (args.subject or "(无——SA 自身身份)"))
    print("scope        : %s" % GSC_SCOPE)
    print("token_uri    : %s" % sa["token_uri"])
    print("token_type   : %s  expires_in: %ss(内存缓存 %ds,不落盘)"
          % (resp.get("token_type"), resp.get("expires_in"), ttl))
    if args.show_token:
        print("access_token : %s" % tok)          # 显式要求才打全量(默认不泄)
    else:
        print("access_token : %s(--show-token 打全量;仅 stdout,勿入日志/报告)" % _mask_token(tok))
    return 0


def cmd_sites(args):
    sa = load_sa(resolve_sa_path(args))
    sites = list_sites(sa, subject=args.subject, timeout=args.timeout)
    if args.json:
        print(json.dumps({"schema_version": SCHEMA_VERSION, "count": len(sites), "sites": sites},
                         ensure_ascii=False, indent=1))
        return 0
    print("== 已验证站点(%d)==" % len(sites))
    for s in sites:
        print("%-50s %s" % (s.get("siteUrl", ""), s.get("permissionLevel", "")))
    if not sites:
        print("(空:SA 邮箱未关联任何站点——GSC 用户和权限里加 SA 邮箱)")
    return 0


def cmd_query(args):
    sa = load_sa(resolve_sa_path(args))
    if not args.site:
        raise UsageError("--site 必填(sc-domain:example.com 或 https://example.com/,sites 命令可列)")
    dimensions = parse_dimensions(args.dimensions)
    start = parse_gsc_date(args.start, "--start")
    end = parse_gsc_date(args.end, "--end")
    rows_cap = args.rows
    if rows_cap < 1:
        raise UsageError("--rows 需 ≥1,实得 %d" % rows_cap)
    page_meta = []
    rows = searchanalytics_query(sa, args.site, start, end, dimensions,
                                 rows_cap=rows_cap, subject=args.subject,
                                 timeout=args.timeout, page_meta=page_meta)
    records = normalize_rows(rows, dimensions)
    if args.json:
        print(json.dumps({
            "schema_version": SCHEMA_VERSION, "source": "gsc_api.py",
            "site": args.site, "startDate": start, "endDate": end,
            "dimensions": dimensions, "row_count": len(records),
            "api_pages": page_meta, "quota_note": "1200 qpm(searchconsole API)",
            "csv_columns": csv_header(dimensions),
            "rows": records,
        }, ensure_ascii=False, indent=1))
        return 0
    if args.out:
        n = write_csv(records, dimensions, out=args.out)
        print("已写 %d 行 × %d 列(%s)→ %s" % (n, len(csv_header(dimensions)),
                                              ",".join(csv_header(dimensions)), args.out))
        print("API 请求 %d 页:%s(配额每站点/每用户 1,200 QPM;喂法见 --help CSV 契约)"
              % (len(page_meta),
                 " ".join("+%d←%d" % (m["startRow"], m["got"]) for m in page_meta)))
        return 0
    sys.stdout.write(write_csv(records, dimensions))       # 无 --out:CSV 走 stdout(可管道)
    return 0


def cmd_inspect(args):
    sa = load_sa(resolve_sa_path(args))
    urls = list(args.urls or [])
    if args.urls_file:
        with open(args.urls_file, encoding="utf-8") as f:
            urls += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    if not urls:
        raise UsageError("没有要查的 URL(位置参数或 --urls-file)")
    day = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 8 * 3600))   # 配额按太平洋时间日切
    left, data = quota_left(args.ledger, args.site, day)
    budget = min(args.budget, left)
    todo, skipped = urls[:budget], urls[budget:]
    out, done = [], 0
    t_min = time.time()
    for i, u in enumerate(todo):
        if i and i % INSPECT_QPM == 0:                       # 每分钟上限
            time.sleep(max(0.0, 60 - (time.time() - t_min)))
            t_min = time.time()
        try:
            out.append(url_inspect(sa, args.site, u, subject=args.subject, timeout=args.timeout))
        except urllib.error.HTTPError as e:
            out.append({"url": u, "error": describe_http_error(e)})
        done += 1
    record_quota(args.ledger, data, args.site, day, done)
    res = {"schema_version": SCHEMA_VERSION, "site": args.site, "day_pt": day, "inspected": done,
           "skipped_for_quota": skipped, "quota_left": left - done, "results": out}
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        for r in out:
            print("%s\t%s\t%s\t%s" % (r["url"], r.get("verdict") or r.get("error"), r.get("coverage") or "",
                                       r.get("google_canonical") or ""))
        if skipped:
            print("配额不够,%d 个没查:今天还剩 %d" % (len(skipped), left - done))
    return 0


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--sa", help="service_account.json 路径(优先级 --sa > --key > "
                                     "$GSC_SA_FILE > ~/.config/seo-suite/gsc.json)")
    common.add_argument("--key", help="同 --sa 的别名(对齐套件 --key 惯例)")
    common.add_argument("--subject", help="域委派模拟用户 user@domain.com(仅 Workspace "
                                          "域级委派场景;普通 SA 授权留空)")
    common.add_argument("--timeout", type=int, default=30, help="单请求超时秒数(默认 30)")
    common.add_argument("--json", action="store_true", help="结构化输出(schema_version=1)")

    p = argparse.ArgumentParser(
        prog="gsc_api.py",
        description="GSC API 客户端(纯 stdlib,RS256 JWT 手写 RSA 签名)——R2-1:"
                    "auth 验凭证链 / sites 列验证站点 / query 拉性能数据产规范化 CSV。",
        epilog=USAGE_EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", metavar="{auth,sites,query,inspect}")

    pa = sub.add_parser("auth", parents=[common],
                        help="验 SA 凭证链:签 JWT → token_uri 换 access_token(不落盘)")
    pa.add_argument("--show-token", action="store_true",
                    help="打全量 access token(默认打码;仅 stdout,勿入日志/报告)")

    sub.add_parser("sites", parents=[common], help="列 SA 有权的已验证站点")

    pq = sub.add_parser("query", parents=[common],
                        help="searchanalytics.query 分页拉取 → 规范化 CSV")
    pq.add_argument("--site", required=True,
                    help="sc-domain:example.com 或 https://example.com/(与 sites 列表一致)")
    pq.add_argument("--start", required=True, help="起始日 YYYY-MM-DD")
    pq.add_argument("--end", required=True, help="截止日 YYYY-MM-DD")
    pq.add_argument("--dimensions", default="query,page",
                    help="逗号分隔,可选 date/hour/query/page/country/device/searchAppearance"
                         "(默认 query,page;加 date 喂 sensor_volatility;country 单维喂 "
                         "market_fit --gsc-country;hour 自动带 dataState=hourly_all)")
    pq.add_argument("--rows", type=int, default=ROW_LIMIT_MAX,
                    help="总行数上限(默认 25000;单页 25000,startRow 分页)")
    pq.add_argument("--out", help="CSV 落盘路径(缺省 CSV 走 stdout)")

    pi = sub.add_parser("inspect", parents=[common],
                        help="URL Inspection:收录判定、Google 选的 canonical、最近抓取(按配额排预算)")
    pi.add_argument("--site", required=True, help="同 query 的 --site")
    pi.add_argument("urls", nargs="*")
    pi.add_argument("--urls-file")
    pi.add_argument("--budget", type=int, default=100, help="这次最多查几个(默认 100;每站每天 2000)")
    pi.add_argument("--ledger", default=os.path.join("seo-ops", "ledger", "inspect-quota.json"),
                    help="配额台账(默认 seo-ops/ledger/inspect-quota.json)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    handlers = {"auth": cmd_auth, "sites": cmd_sites, "query": cmd_query, "inspect": cmd_inspect}
    try:
        return handlers[args.cmd](args)
    except UsageError as e:
        sys.stderr.write("[用法] %s\n" % e)
        return 2
    except GuardError as e:
        sys.stderr.write("[拒] %s\n" % e)
        return 2
    except SaError as e:
        sys.stderr.write("[凭证] %s\n" % e)
        return 1
    except ApiError as e:
        sys.stderr.write("[API] %s\n" % e)
        return 1
    except urllib.error.HTTPError as e:
        code, msg = describe_http_error(e)
        sys.stderr.write("[HTTP] %s\n" % msg)
        return code
    except urllib.error.URLError as e:
        sys.stderr.write("[网络] %s(端点不可达或代理拦截;googleapis.com 需可直连)\n" % e)
        return 1
    except (ValueError, OSError) as e:            # 坏 PEM / 文件 IO 等
        sys.stderr.write("[错误] %s\n" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
