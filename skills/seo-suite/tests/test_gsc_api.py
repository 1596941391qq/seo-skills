#!/usr/bin/env python3
"""gsc_api.py 测试(R2-1 大件):零网络(_http_json 全打桩)+ RSA 纯 stdlib 对拍。
覆盖六块(任务规格):
  ① RSA 签名对拍:openssl 可用时现场 genkey(2048)+ `openssl dgst -sha256 -sign`
     逐字节比(确定性 PKCS#1 v1.5);不可用时退固定向量(1024-bit 密钥 + openssl 预签
     签名,PKCS#8/PKCS#1 双形态同一签名)——任何环境都有真凭实据的对拍;
  ② JWT 结构与 claims(header RS256/无填充 b64url;iss/scope/aud/exp-iat=3600/sub 条件在场;
     第三段 = sha256(h.c) 的 rsa_sign,即真签名非占位);
  ③ ASN.1 解析边界(垃圾 PEM/坏 base64/不支持标签/截断 DER/非 RSA OID/顶层 tag 错/
     version≠0/模数过小/长形长度 0x81·0x82·越界·indefinite);
  ④ 分页循环(rowLimit 上限 25000、want 收缩、短页即止、startRow 递进——纯函数级 + CLI 级);
  ⑤ CSV 列契约对齐(gsc_mining 能直接挖 striking distance/蚕食;CTR 小数口径过
     parse_ctr 全区间含 <1%;traffic_funnel.load_gsc 与 monitor.check_gsc 吃 page 维 CSV;
     date 维表头首列 Date);
  ⑥ token 缓存(50 分钟命中不重发;到期重签)/错误处理(invalid_grant 三因提示、
     403/429 提示、SA 装载变体与缺键、SSRF 端点守卫、用法错 exit 2)。
用法: python3 tests/test_gsc_api.py(tests/run_tests.py 自动发现本文件)"""
import base64
import binascii
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
sys.path.insert(0, SCRIPTS)

import gsc_api  # noqa: E402 (需先入 SCRIPTS 路径)

# ─── 固定向量(1024-bit RSA,openssl 3.6.3 预生成;无 openssl 环境的对拍锚) ───
VEC_PAYLOAD_HEX = "6773632d6170692d66697865642d766563746f722d7061796c6f6164"  # b"gsc-api-fixed-vector-payload"
VEC_SIG_HEX = (
    "874d74f48747d0eeb3aa877a973c843aab2fe62195faa65dfbd87ed4607536e63"
    "487abefb66a4a2e74f61b8dccca78df639199888f85469e434a6725752e859f22"
    "f04a5e5c0795f1c6b9f1fa0feee202a33b2b599da9c44ebcfccba99e3652e1e8"
    "bf03f8d9b87dd251dc9aa3bf4f9a3af3af5fb294835b6032f07ac4408a5fee")
VEC_PEM_PKCS8 = """-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBANUc8RggUxyB60oh
y4V+Uv0eYq8IlGDGEIUwvIXtrTsxHUAhL6WwAFEE1yUuxsPYK36JQwV6VLFoUm5O
SP8svi6bMoqsB6IHorBMxgtZVQVbew2Mnw0ZGUt+P1Fz7sKanTmUk8adTw5wsWb4
3PT9Y/w+zhcNkVtIUjkOb1Ralg1NAgMBAAECgYBMz4qiHHx4KOdqJ7YYHkjBDGOb
HKeGHb00lDVOvDSUwgX96DgpKr9idDErKKnhSpeamtR6M/Y0nxoewb6TokfFEi62
BXc1WAnUZsGDVGFvR11lsKMgGQiK2N2jDGUDG+iVfrHD7JHJK/mU8IMpYjrjOidt
3hn16mRzU8/yVh2r4QJBAOwrwc4h5gJqEMGHoXVhjgbNAm99dFP1RcRWQaJEH+ZK
EaYJ4hsJJ65KLSpxAc0gu3NgTNCC74oj8GkR+mqBU3UCQQDnAZSM/Zn0WEaUrzk4
DhZmSLLLy6JTyrsdQWFMH1IjDt+WHC+Av4ElihTFwtwI4tAzPLdU4/rUqlCTjh6v
0s95AkBlIsPm4ytdg1BToCJrYvBwRyCw39eOEK3ky09mDqhedP+jy/2wuDXu9ELt
NuGfl1HOscGTVU8BKCzOwe0r6N/1AkBj/RQentqXn+oVC2856ycY6NizS5YcrMCn
HhiOSXRVBmgS4mpRURMGe6kYHIr/MaWqt9om3XNBv+KWq8puklIJAkEAph4D6Cba
+cTYtxhyLDjH015VvnRX/9GrEQmoWGNWytplyeHRQs/IeJJNBQG1DBPDBgXjRltv
2LekLMtVNE2FOQ==
-----END PRIVATE KEY-----"""
VEC_PEM_PKCS1 = """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDVHPEYIFMcgetKIcuFflL9HmKvCJRgxhCFMLyF7a07MR1AIS+l
sABRBNclLsbD2Ct+iUMFelSxaFJuTkj/LL4umzKKrAeiB6KwTMYLWVUFW3sNjJ8N
GRlLfj9Rc+7Cmp05lJPGnU8OcLFm+Nz0/WP8Ps4XDZFbSFI5Dm9UWpYNTQIDAQAB
AoGATM+Kohx8eCjnaie2GB5IwQxjmxynhh29NJQ1Trw0lMIF/eg4KSq/YnQxKyip
4UqXmprUejP2NJ8aHsG+k6JHxRIutgV3NVgJ1GbBg1Rhb0ddZbCjIBkIitjdowxl
AxvolX6xw+yRySv5lPCDKWI64zonbd4Z9epkc1PP8lYdq+ECQQDsK8HOIeYCahDB
h6F1YY4GzQJvfXRT9UXEVkGiRB/mShGmCeIbCSeuSi0qcQHNILtzYEzQgu+KI/Bp
EfpqgVN1AkEA5wGUjP2Z9FhGlK85OA4WZkiyy8uiU8q7HUFhTB9SIw7flhwvgL+B
JYoUxcLcCOLQMzy3VOP61KpQk44er9LPeQJAZSLD5uMrXYNQU6Aia2LwcEcgsN/X
jhCt5MtPZg6oXnT/o8v9sLg17vRC7Tbhn5dRzrHBk1VPASgszsHtK+jf9QJAY/0U
Hp7al5/qFQtvOesnGOjYs0uWHKzApx4Yjkl0VQZoEuJqUVETBnupGByK/zGlqrfa
Jt1zQb/ilqvKbpJSCQJBAKYeA+gm2vnE2LcYciw4x9NeVb50V//RqxEJqFhjVsra
Zcnh0ULPyHiSTQUBtQwTwwYF40Zbb9i3pCzLVTRNhTk=
-----END RSA PRIVATE KEY-----"""

TOKEN_URL = "https://oauth2.googleapis.com/token"
QUERY_URL_FOR = lambda site: ("%s/sites/%s/searchAnalytics/query"
                              % (gsc_api.GSC_API_BASE,
                                 urllib.parse.quote(site, safe="")))
import urllib.parse  # noqa: E402 (QUERY_URL_FOR 用)

FAKE_TOKEN = "ya29-fake-access-token-0123456789abcdef"


def b64d(seg):
    return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))


def make_sa(pem=VEC_PEM_PKCS8, token_uri=TOKEN_URL, email="tester@proj.iam.gserviceaccount.com"):
    return {"private_key": pem, "client_email": email, "token_uri": token_uri}


class _ApiStub:
    """_http_json 打桩:token 端点发假 token;query 端点按 startRow/rowLimit + PAGE_CAP
    现场造 rows(TOTAL 控制总量);记录全部调用供断言。零网络。"""

    def __init__(self, total=25, page_cap=25, rows_for=None, token=FAKE_TOKEN):
        self.total, self.page_cap, self.token = total, page_cap, token
        self._rows_for = rows_for
        self.calls = []

    def __call__(self, url, data=None, headers=None, timeout=30):
        self.calls.append({"url": url, "data": data, "headers": dict(headers or {})})
        if "oauth2.googleapis.com/token" in url:
            return {"access_token": self.token, "expires_in": 3600,
                    "token_type": "Bearer", "scope": gsc_api.GSC_SCOPE}
        if url.endswith("/sites"):
            return {"siteEntry": []}
        if "searchAnalytics/query" in url:
            body = json.loads(data.decode("utf-8"))
            off, want = int(body["startRow"]), int(body["rowLimit"])
            n = max(0, min(want, self.page_cap, self.total - off))
            rows = (self._rows_for(off, n) if self._rows_for
                    else [{"keys": ["kw%05d" % (off + i), "https://example.com/p%d" % (i % 3)],
                           "clicks": float(off + i), "impressions": 100.0,
                           "ctr": 0.0317, "position": 6.0 + (i % 10)} for i in range(n)])
            return {"rows": rows}
        raise AssertionError("意外端点: %s" % url)


def http_error(code, body, reason="Error"):
    return urllib.error.HTTPError("https://x.googleapis.com/", code, reason, {},
                                  io.BytesIO(body.encode("utf-8")))


class GscApiCase(unittest.TestCase):
    """公共底座:每用例前后清 token 缓存 + 重置 urlopen 打桩。"""

    def setUp(self):
        gsc_api._token_cache.clear()
        self._tmp = tempfile.mkdtemp(prefix="gsc_api_t_")

    def tearDown(self):
        gsc_api._token_cache.clear()
        shutil.rmtree(self._tmp, ignore_errors=True)

    def sa_file(self, **kw):
        path = os.path.join(self._tmp, "sa.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(make_sa(**kw) if kw else make_sa(), f)
        return path

    def run_cli(self, argv, stub=None):
        """进程内 main():捕获 stdout/stderr,可选打桩 _http_json;返回 (rc, out, err, stub)。"""
        out, err = io.StringIO(), io.StringIO()
        st = stub or _ApiStub()
        with mock.patch.object(gsc_api, "_http_json", st):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = gsc_api.main(argv)
        return rc, out.getvalue(), err.getvalue(), st


# ─── ① RSA 签名对拍 ───

class RsaSignParityTests(GscApiCase):

    def test_fixed_vector_pkcs8(self):
        """固定向量(PKCS#8):rsa_sign 输出与 openssl 预签名逐字节一致。"""
        payload = bytes.fromhex(VEC_PAYLOAD_HEX)
        sig = gsc_api.rsa_sign(hashlib.sha256(payload).digest(), VEC_PEM_PKCS8)
        self.assertEqual(sig.hex(), VEC_SIG_HEX)

    def test_fixed_vector_pkcs1(self):
        """固定向量(PKCS#1 traditional 形态):同一密钥同一签名——双标签解析等价。"""
        payload = bytes.fromhex(VEC_PAYLOAD_HEX)
        sig = gsc_api.rsa_sign(hashlib.sha256(payload).digest(), VEC_PEM_PKCS1)
        self.assertEqual(sig.hex(), VEC_SIG_HEX)
        self.assertEqual(sig, gsc_api.rsa_sign(hashlib.sha256(payload).digest(), VEC_PEM_PKCS8))

    @unittest.skipUnless(shutil.which("openssl"), "openssl 不在场,固定向量已覆盖")
    def test_live_openssl_parity(self):
        """现场对拍:openssl genpkey(2048-bit)→ `openssl dgst -sha256 -sign` 三种载荷
        (空/ASCII/含 \\x00 二进制)逐字节比对。"""
        key = os.path.join(self._tmp, "k.pem")
        subprocess.run(["openssl", "genpkey", "-algorithm", "RSA",
                        "-pkeyopt", "rsa_keygen_bits:2048", "-out", key],
                       check=True, capture_output=True, timeout=60)
        with open(key, encoding="ascii") as f:
            pem = f.read()
        for payload in (b"", b"header.claims ASCII payload", bytes(range(256))):
            pf = os.path.join(self._tmp, "p.bin")
            sf = os.path.join(self._tmp, "s.bin")
            with open(pf, "wb") as f:
                f.write(payload)
            subprocess.run(["openssl", "dgst", "-sha256", "-sign", key, "-out", sf, pf],
                           check=True, capture_output=True, timeout=60)
            with open(sf, "rb") as f:
                expect = f.read()
            self.assertEqual(gsc_api.rsa_sign(hashlib.sha256(payload).digest(), pem), expect,
                             msg="payload=%r" % payload[:20])

    def test_pubkey_verify_roundtrip(self):
        """第三只眼:固定向量签名用公钥指数验(pow(sig,e,n)==EM)——确认 v=d 的解析正确。"""
        payload = bytes.fromhex(VEC_PAYLOAD_HEX)
        digest = hashlib.sha256(payload).digest()
        n, e, d = gsc_api.parse_private_key_pem(VEC_PEM_PKCS8)
        sig = gsc_api.rsa_sign(digest, VEC_PEM_PKCS8)
        t = gsc_api._SHA256_DIGESTINFO_PREFIX + digest
        em = b"\x00\x01" + b"\xff" * (len(sig) - len(t) - 3) + b"\x00" + t
        self.assertEqual(pow(int.from_bytes(sig, "big"), e, n),
                         int.from_bytes(em, "big"))


# ─── ③ ASN.1 解析边界 ───

class Asn1BoundaryTests(GscApiCase):

    def test_malformed_pem_and_base64(self):
        for bad, why in [("不是 PEM", "无 BEGIN/END"),
                         ("-----BEGIN PRIVATE KEY-----!!!not-base64!!!"
                          "-----END PRIVATE KEY-----", "坏 base64")]:
            with self.assertRaises(ValueError, msg=why):
                gsc_api.parse_private_key_pem(bad)

    def test_unsupported_labels(self):
        for label in ("ENCRYPTED PRIVATE KEY", "CERTIFICATE", "EC PRIVATE KEY"):
            pem = "-----BEGIN %s-----\nAAAA\n-----END %s-----" % (label, label)
            with self.assertRaises(ValueError, msg=label):
                gsc_api.parse_private_key_pem(pem)

    def test_truncated_der(self):
        der = base64.b64decode("".join(VEC_PEM_PKCS8.splitlines()[1:-1]))
        for cut in (10, len(der) // 2, len(der) - 1):
            with self.assertRaises(ValueError, msg="cut=%d" % cut):
                gsc_api.parse_private_key_pem(
                    "-----BEGIN PRIVATE KEY-----\n%s\n-----END PRIVATE KEY-----"
                    % base64.b64encode(der[:cut]).decode())

    def test_non_rsa_oid_pkcs8(self):
        """ecPrivateKey OID(1.2.840.10045.2.1)的 PKCS#8 → 明确拒绝。"""
        ec_oid = bytes.fromhex("06072a8648ce3d0201")
        algid = b"\x30" + bytes([len(ec_oid)]) + ec_oid
        inner = b"\x02\x01\x00" + algid + b"\x04\x01\x00"       # version + algid + 桥 OCTET
        der = b"\x30" + bytes([len(inner)]) + inner
        pem = "-----BEGIN PRIVATE KEY-----\n%s\n-----END PRIVATE KEY-----" \
              % base64.b64encode(der).decode()
        with self.assertRaisesRegex(ValueError, "rsaEncryption"):
            gsc_api.parse_private_key_pem(pem)

    def test_wrong_top_tag_and_version(self):
        der1 = base64.b64decode("".join(VEC_PEM_PKCS1.splitlines()[1:-1]))
        # 顶层 tag 错(把 SEQUENCE 0x30 换 SET 0x31)
        self.assertRaisesRegex(ValueError, "SEQUENCE",
                               gsc_api._parse_pkcs1_rsa_private, b"\x31" + der1[1:])
        # PKCS#1 version≠0(multi-prime)→ 拒(等长替换 version INTEGER 值,DER 结构不破)
        i = der1.index(b"\x02\x01\x00")                          # 首个 INTEGER 即 version
        with self.assertRaisesRegex(ValueError, "version"):
            gsc_api._parse_pkcs1_rsa_private(der1[:i] + b"\x02\x01\x01" + der1[i + 3:])
        # 对照:原样 version=0 解析正常
        self.assertEqual(gsc_api._parse_pkcs1_rsa_private(der1)[0].bit_length(), 1024)

    def test_der_read_long_form_lengths(self):
        """长形长度三态:0x81(≤255)/0x82(≤65535)/声明越界;indefinite(0x80)拒。"""
        tag, val, off = gsc_api._der_read(b"\x04\x81\x05" + b"\x01" * 5 + b"tail", 0)
        self.assertEqual((tag, val, off), (0x04, b"\x01" * 5, 8))
        tag, val, _ = gsc_api._der_read(b"\x02\x82\x00\x03\xab\xcd\xef", 0)
        self.assertEqual(val, b"\xab\xcd\xef")
        self.assertRaisesRegex(ValueError, "越界",
                               gsc_api._der_read, b"\x04\x82\x00\x05abc", 0)
        self.assertRaisesRegex(ValueError, "非法",
                               gsc_api._der_read, b"\x04\x80", 0)
        # 真密钥里确有长形长度(1024-bit:SEQUENCE 0x82 / n INTEGER 0x81)
        der = base64.b64decode("".join(VEC_PEM_PKCS1.splitlines()[1:-1]))
        self.assertIn(b"\x30\x82", der[:4])
        self.assertIn(b"\x02\x81\x81", der)

    def test_modulus_too_small(self):
        tiny = b"\x30\x0f\x02\x01\x00\x02\x02\x01\x03\x02\x02\x01\x03\x02\x02\x01\x03"
        pem = "-----BEGIN RSA PRIVATE KEY-----\n%s\n-----END RSA PRIVATE KEY-----" \
              % base64.b64encode(tiny).decode()
        with self.assertRaisesRegex(ValueError, "模数过小"):
            gsc_api.parse_private_key_pem(pem)


# ─── ② JWT 结构与 claims ───

class JwtTests(GscApiCase):

    def test_structure_and_claims(self):
        sa = make_sa()
        jwt = gsc_api.build_jwt(sa, now=1_700_000_000)
        h, c, s = jwt.split(".")
        self.assertEqual(len(jwt.split(".")), 3)
        self.assertNotIn("=", jwt)                               # b64url 无填充
        self.assertEqual(json.loads(b64d(h)), {"alg": "RS256", "typ": "JWT"})
        claims = json.loads(b64d(c))
        self.assertEqual(claims["iss"], sa["client_email"])
        self.assertEqual(claims["scope"], gsc_api.GSC_SCOPE)     # webmasters.readonly
        self.assertEqual(claims["aud"], sa["token_uri"])
        self.assertEqual(claims["exp"] - claims["iat"], 3600)    # exp=iat+3600
        self.assertNotIn("sub", claims)                          # 无 subject 不伪造 sub
        # 第三段 = sha256("h.c") 的 RS256 真签名(非占位)
        self.assertEqual(b64d(s), gsc_api.rsa_sign(
            hashlib.sha256(("%s.%s" % (h, c)).encode("ascii")).digest(), sa["private_key"]))

    def test_subject_and_determinism(self):
        sa = make_sa()
        j1 = gsc_api.build_jwt(sa, subject="u@domain.com", now=1_700_000_000)
        j2 = gsc_api.build_jwt(sa, subject="u@domain.com", now=1_700_000_000)
        self.assertEqual(j1, j2)                                 # 确定性(同 now 同 JWT)
        self.assertEqual(json.loads(b64d(j1.split(".")[1]))["sub"], "u@domain.com")
        j3 = gsc_api.build_jwt(sa, now=1_700_000_001)
        self.assertNotEqual(j1, j3)                              # iat 变 → 签名变


# ─── ⑥ token 缓存 / 错误处理 ───

class TokenCacheTests(GscApiCase):

    def test_cache_50min_then_reissue(self):
        sa = make_sa()
        st = _ApiStub()
        with mock.patch.object(gsc_api, "_http_json", st):
            t0 = 1_000_000
            tok1 = gsc_api.get_access_token(sa, now=t0)
            tok1b = gsc_api.get_access_token(sa, now=t0 + 2900)  # 48min20s:命中
            self.assertEqual((tok1, tok1b), (FAKE_TOKEN, FAKE_TOKEN))
            self.assertEqual(len(st.calls), 1, "50 分钟窗口内不得重签")
            entry = gsc_api.cached_token_entry(sa)
            self.assertLessEqual(entry["expires_at"] - t0, 3000)  # 缓存 TTL ≤50min
            tok2 = gsc_api.get_access_token(sa, now=t0 + 3001)    # 过窗 → 重签
        self.assertEqual(tok2, FAKE_TOKEN)
        self.assertEqual(len(st.calls), 2)
        # 缓存键含 subject:不同 subject 不串用
        with mock.patch.object(gsc_api, "_http_json", st):
            gsc_api.get_access_token(sa, subject="u@d.com", now=t0 + 3002)
        self.assertEqual(len(st.calls), 3)

    def test_token_post_body_and_headers(self):
        sa = make_sa()
        st = _ApiStub()
        with mock.patch.object(gsc_api, "_http_json", st):
            gsc_api.fetch_token(sa, subject=None, now=1_700_000_000)
        call = st.calls[0]
        self.assertEqual(call["url"], TOKEN_URL)
        self.assertIn("application/x-www-form-urlencoded", call["headers"]["Content-Type"])
        params = dict(urllib.parse.parse_qsl(call["data"].decode("ascii")))
        self.assertEqual(params["grant_type"], gsc_api.GRANT_TYPE)
        h, c, s = params["assertion"].split(".")
        self.assertEqual(json.loads(b64d(c))["iss"], sa["client_email"])


class ErrorHandlingTests(GscApiCase):

    def test_auth_invalid_grant_hint(self):
        """400 invalid_grant → exit 1 + 三因提示(SA 授权/subject 委派/时钟)。"""
        def boom(url, data=None, headers=None, timeout=30):
            raise http_error(400, '{"error":"invalid_grant","error_description":"bad"}')
        rc, out, err, _ = self.run_cli(["auth", "--sa", self.sa_file()], stub=boom)
        self.assertEqual(rc, 1)
        self.assertIn("invalid_grant", err)
        self.assertIn("用户和权限", err)                     # ① SA 未授权提示
        self.assertIn("域级委派", err)                       # ② subject 提示
        self.assertIn("时钟", err)                           # ③ 时钟偏差提示

    def test_http_error_hints_403_429(self):
        for code, body, needle in (
                (403, '{"error":"PERMISSION_DENIED"}', "restricted"),
                (429, '{"error":"RATE_LIMITED"}', "1,200 QPM")):  # 2026-10-21 配额文案改为官方「每站点/每用户 1,200 QPM」
            msg = gsc_api.describe_http_error(http_error(code, body))[1]
            self.assertIn(needle, msg, "code=%d" % code)
        code, msg = gsc_api.describe_http_error(http_error(400, '{"error":"invalid_grant"}'))
        self.assertEqual(code, 1)
        self.assertIn("invalid_grant", msg)

    def test_sa_loading_variants_and_errors(self):
        p = self.sa_file()
        sa = gsc_api.load_sa(p)                                   # 原生 SA json
        self.assertEqual(sa["client_email"], "tester@proj.iam.gserviceaccount.com")
        wrapped = os.path.join(self._tmp, "wrapped.json")         # 套件 gsc.json 包装
        with open(wrapped, "w", encoding="utf-8") as f:
            json.dump({"credentials": make_sa(), "ga4_property_id": 123}, f)
        self.assertEqual(gsc_api.load_sa(wrapped)["token_uri"], TOKEN_URL)
        for drop in ("private_key", "client_email", "token_uri"):
            sa = make_sa()
            sa[drop] = ""
            with open(os.path.join(self._tmp, "bad.json"), "w", encoding="utf-8") as f:
                json.dump(sa, f)
            with self.assertRaisesRegex(gsc_api.SaError, drop):
                gsc_api.load_sa(f.name)
        with open(os.path.join(self._tmp, "evil.json"), "w", encoding="utf-8") as f:
            json.dump(make_sa(token_uri="http://169.254.169.254/token"), f)
        with self.assertRaisesRegex(gsc_api.SaError, "守卫"):
            gsc_api.load_sa(f.name)
        with open(os.path.join(self._tmp, "notjson.json"), "w", encoding="utf-8") as f:
            f.write("{oops")
        self.assertRaises(gsc_api.SaError, gsc_api.load_sa, f.name)

    def test_env_and_flag_precedence(self):
        """GSC_SA_FILE 生效;--sa 优先于 env(坏 env 路径不影响)。"""
        env = dict(os.environ, GSC_SA_FILE=self.sa_file())
        with mock.patch.dict(os.environ, env, clear=False):
            rc, out, err, _ = self.run_cli(["sites", "--json"])
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(payload["count"], 0)                     # _ApiStub query-only → siteEntry 缺省 []
        env_bad = dict(os.environ, GSC_SA_FILE="/nonexistent/sa.json")
        with mock.patch.dict(os.environ, env_bad, clear=False):
            rc, out, err, _ = self.run_cli(["sites", "--sa", self.sa_file()])
        self.assertEqual(rc, 0, err)


# ─── auth / sites 子命令 ───

class AuthSitesTests(GscApiCase):

    def test_auth_cli_masked_by_default(self):
        p = self.sa_file()
        rc, out, err, st = self.run_cli(["auth", "--sa", p])
        self.assertEqual(rc, 0)
        self.assertIn("tester@proj.iam.gserviceaccount.com", out)
        self.assertIn("webmasters.readonly", out)
        self.assertIn(FAKE_TOKEN[:10], out)                       # 打码头 10 字符
        self.assertNotIn(FAKE_TOKEN, out)                         # 全量 token 默认不出现
        rc, out, _, _ = self.run_cli(["auth", "--sa", p, "--show-token"])
        self.assertEqual(rc, 0)
        self.assertIn(FAKE_TOKEN, out)                            # 显式 --show-token 才给全量
        rc, out, _, _ = self.run_cli(["auth", "--sa", p, "--json"])
        self.assertEqual(json.loads(out)["ok"], True)

    def test_sites_cli_and_json(self):
        site = {"siteUrl": "sc-domain:example.com", "permissionLevel": "siteOwner"}

        def sites_stub(url, data=None, headers=None, timeout=30):
            if url.endswith("/sites"):
                return {"siteEntry": [site]}
            return _ApiStub()(url, data, headers, timeout)
        rc, out, err, _ = self.run_cli(["sites", "--sa", self.sa_file()], stub=sites_stub)
        self.assertEqual(rc, 0)
        self.assertIn("sc-domain:example.com", out)
        self.assertIn("siteOwner", out)
        rc, out, _, _ = self.run_cli(["sites", "--sa", self.sa_file(), "--json"],
                                     stub=sites_stub)
        payload = json.loads(out)
        self.assertEqual((payload["schema_version"], payload["count"], payload["sites"]), (1, 1, [site]))


# ─── ④ 分页循环 ───

class PaginationTests(GscApiCase):

    def test_pagination_loop_math(self):
        """纯函数级(ROW_LIMIT_MAX 打桩为 3,免造 5 万行数据):
        want=min(上限,剩余)逐页收缩、短页即止(数据见底)、startRow 递进、整除收束。"""
        sa = make_sa()
        meta = []
        st = _ApiStub(total=5)                                    # 语义同真 API:给满 want,见底短给
        with mock.patch.object(gsc_api, "_http_json", st), \
                mock.patch.object(gsc_api, "ROW_LIMIT_MAX", 3):
            rows = gsc_api.searchanalytics_query(
                sa, "sc-domain:example.com", "2026-09-01", "2026-09-28",
                ("query", "page"), rows_cap=4, page_meta=meta)
        # p1 want=min(3,4)=3 拿满;p2 want=min(3,1)=1 拿满 → offset=4=cap 收束
        self.assertEqual(len(rows), 4)
        self.assertEqual([(m["startRow"], m["rowLimit"]) for m in meta], [(0, 3), (3, 1)])
        # 短页即止:cap=7 > 数据 5 → p2 want=3 只剩 2 → break
        meta2 = []
        st2 = _ApiStub(total=5)
        with mock.patch.object(gsc_api, "_http_json", st2), \
                mock.patch.object(gsc_api, "ROW_LIMIT_MAX", 3):
            rows2 = gsc_api.searchanalytics_query(
                sa, "sc-domain:example.com", "2026-09-01", "2026-09-28",
                ("query",), rows_cap=7, page_meta=meta2)
        self.assertEqual(len(rows2), 5)
        self.assertEqual([(m["startRow"], m["rowLimit"]) for m in meta2], [(0, 3), (3, 3)])

    def test_query_cli_big_pagination_end_to_end(self):
        """CLI 级:25000 硬上限 + 跨页拼接 + 短页终止(data 25005,要 25010)。"""
        out_csv = os.path.join(self._tmp, "gsc.csv")
        st = _ApiStub(total=25005, page_cap=25000)
        rc, out, err, _ = self.run_cli(
            ["query", "--sa", self.sa_file(), "--site", "sc-domain:example.com",
             "--start", "2026-09-01", "--end", "2026-09-28",
             "--rows", "25010", "--out", out_csv], stub=st)
        self.assertEqual(rc, 0, err)
        pages = [c for c in st.calls if "searchAnalytics" in c["url"]]
        self.assertEqual(len(pages), 2)
        bodies = [json.loads(c["data"]) for c in pages]
        self.assertEqual([(b["startRow"], b["rowLimit"]) for b in bodies],
                         [(0, 25000), (25000, 10)])               # 单页 ≤25000,末页收缩到 10
        with open(out_csv, encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertEqual(len(lines), 1 + 25005)                   # 表头 + 25005 行
        self.assertEqual(lines[0], "Query,Page,Clicks,Impressions,CTR,Position")
        self.assertEqual(len(st.calls) - len(pages), 1)           # token 换取恰 1 次(缓存生效)

    def test_site_url_quoted_in_request(self):
        sa = make_sa()
        with mock.patch.object(gsc_api, "_http_json", _ApiStub(total=1)):
            gsc_api.searchanalytics_query(sa, "sc-domain:example.com", "2026-09-01",
                                          "2026-09-28", ("query",), rows_cap=1)
        url = gsc_api.query_url("sc-domain:example.com")
        self.assertIn("/sites/sc-domain%3Aexample.com/searchAnalytics/query", url)
        self.assertEqual(url, QUERY_URL_FOR("sc-domain:example.com"))


# ─── ⑤ CSV 列契约对齐 ───

class CsvContractTests(GscApiCase):

    QUERY_ROWS = [   # (query, page, clicks, impressions, ctr, position)
        ("cheap flights", "https://example.com/a", 10, 500, 0.02, 6.2),    # SD 命中
        ("head term", "https://example.com/a", 50, 5000, 0.05, 4.0),       # pos<5 出 SD
        ("cheap flights", "https://example.com/b", 3, 150, 0.018, 8.1),    # 同词第二页 → 蚕食
        ("tiny ctr", "https://example.com/c", 0, 100, 0.0005, 12.0),       # CTR<1% 关键口径
        ("out of band", "https://example.com/c", 1, 60, 0.005, 22.0),      # pos>20 出 SD
    ]

    def _matrix_csv(self):
        def rows_for(off, n):
            return [{"keys": [q, p], "clicks": float(c), "impressions": float(i),
                     "ctr": ctr, "position": pos}
                    for (q, p, c, i, ctr, pos) in self.QUERY_ROWS[off:off + n]]
        out_csv = os.path.join(self._tmp, "matrix.csv")
        st = _ApiStub(total=len(self.QUERY_ROWS), page_cap=100, rows_for=rows_for)
        rc, out, err, _ = self.run_cli(
            ["query", "--sa", self.sa_file(), "--site", "sc-domain:example.com",
             "--start", "2026-09-01", "--end", "2026-09-28",
             "--dimensions", "query,page", "--out", out_csv], stub=st)
        self.assertEqual(rc, 0, err)
        with open(out_csv, encoding="utf-8") as f:
            return f.read()

    def test_header_no_date_by_default(self):
        csv_text = self._matrix_csv()
        self.assertTrue(csv_text.startswith(
            "Query,Page,Clicks,Impressions,CTR,Position\n"))
        self.assertNotIn("Date", csv_text.splitlines()[0])

    def test_gsc_mining_reads_csv_end_to_end(self):
        """gsc_mining 子进程直接吃本 CSV:SD 计数/蚕食组/CTR<1% 不 100 倍误读。"""
        p = os.path.join(self._tmp, "matrix.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write(self._matrix_csv())
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "gsc_mining.py"), p],
                           capture_output=True, text=True, encoding="utf-8", timeout=60,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(r.returncode, 0, r.stderr)
        # query×page 导出先按词合并(2026-11-06):cheap flights 两页合成一个词(加权 6.6),加 tiny ctr 12.0 共 2 词
        self.assertIn("striking distance(pos5-20, 曝光≥20): 2 词", r.stdout)
        self.assertIn("cheap flights", r.stdout)
        r2 = subprocess.run([sys.executable, os.path.join(SCRIPTS, "gsc_mining.py"),
                             p, "--mode", "matrix"],
                            capture_output=True, text=True, encoding="utf-8", timeout=60,
                            env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertIn("已去掉 #锚点和语言版本): 1 组", r2.stdout)   # cheap flights 次页 150/650=23%
        self.assertIn("cheap flights", r2.stdout)

    def test_ctr_fraction_safe_for_parse_ctr(self):
        """CTR 小数口径:含 <1% 全区间过 gsc_mining.parse_ctr 无歧义
        (百分串 "0.5%" 会被其 float>1 判据 100 倍误读——本 CSV 不产该形态)。"""
        import gsc_mining
        rows = [ln.split(",") for ln in self._matrix_csv().splitlines()[1:]]
        ctrs = {r[0]: r[4] for r in rows}
        self.assertEqual(ctrs["tiny ctr"], "0.0005")              # 落盘即小数
        for q, cell in ctrs.items():
            expect = dict((x[0], x[4]) for x in self.QUERY_ROWS)[q]
            self.assertAlmostEqual(gsc_mining.parse_ctr(cell), expect, places=6, msg=q)

    def test_traffic_funnel_and_monitor_consume_page_csv(self):
        """page 维拉取:traffic_funnel.load_gsc / monitor.check_gsc(gsc.csv)直接可吃。"""
        def rows_for(off, n):
            return [{"keys": ["https://example.com/%s" % p], "clicks": float(c),
                      "impressions": float(i), "ctr": ctr, "position": pos}
                    for (p, c, i, ctr, pos) in [("a", 7, 90, 0.07, 3.0),
                                                ("b", 3, 40, 0.02, 11.5),
                                                ("a", 2, 10, 0.01, 5.0)][off:off + n]]
        out_csv = os.path.join(self._tmp, "gsc.csv")
        st = _ApiStub(total=3, page_cap=100, rows_for=rows_for)
        rc, out, err, _ = self.run_cli(
            ["query", "--sa", self.sa_file(), "--site", "https://example.com/",
             "--start", "2026-09-01", "--end", "2026-09-28",
             "--dimensions", "page", "--out", out_csv], stub=st)
        self.assertEqual(rc, 0, err)
        with open(out_csv, encoding="utf-8") as f:
            header = f.readline().strip()
        self.assertEqual(header, "Query,Page,Clicks,Impressions,CTR,Position")  # Query 留空列
        import traffic_funnel
        g = traffic_funnel.load_gsc(out_csv)                       # 缺 Page/Clicks 会 SystemExit
        self.assertEqual(g["//example.com/a"]["clicks"], 9.0)     # 同 URL 多行累加(norm_url 去 scheme)
        self.assertEqual(g["//example.com/b"]["impressions"], 40.0)
        import monitor
        res = monitor.check_gsc(os.path.dirname(out_csv))          # 文件名恰为 gsc.csv
        self.assertEqual(res["state"], "ok")
        self.assertEqual(res["metrics"]["clicks_total"], 12)
        self.assertEqual(res["metrics"]["queries"], 3)

    def test_date_dimensions_header_first_column(self):
        """date 维:Date 首列(sensor_volatility 的 Date,Query,Position 口径)。"""
        out_csv = os.path.join(self._tmp, "dq.csv")

        def date_rows(off, n):                                    # keys 顺序 = dimensions
            return [{"keys": ["2026-09-0%d" % (off + i + 1), "dated kw"],
                      "clicks": 1.0, "impressions": 10.0, "ctr": 0.1, "position": 7.0}
                    for i in range(n)]
        rc, out, err, _ = self.run_cli(
            ["query", "--sa", self.sa_file(), "--site", "sc-domain:example.com",
             "--start", "2026-09-01", "--end", "2026-09-28",
             "--dimensions", "date,query", "--out", out_csv],
            stub=_ApiStub(total=1, rows_for=date_rows))
        self.assertEqual(rc, 0, err)
        with open(out_csv, encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertEqual(lines[0], "Date,Query,Page,Clicks,Impressions,CTR,Position")
        first = lines[1].split(",")
        self.assertRegex(first[0], r"^\d{4}-\d{2}-\d{2}$")

    def test_query_json_output_shape(self):
        rc, out, err, _ = self.run_cli(
            ["query", "--sa", self.sa_file(), "--site", "sc-domain:example.com",
             "--start", "2026-09-01", "--end", "2026-09-28",
             "--dimensions", "query,page", "--json"], stub=_ApiStub(total=3))
        self.assertEqual(rc, 0, err)
        payload = json.loads(out)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["row_count"], 3)
        self.assertEqual(payload["dimensions"], ["query", "page"])
        self.assertEqual(len(payload["api_pages"]), 1)
        self.assertEqual(payload["rows"][0]["Clicks"], 0)
        self.assertIn("1200 qpm", payload["quota_note"])


# ─── CLI 行为:--help / 用法错 / SSRF 守卫 ───

class CliAndGuardTests(GscApiCase):

    def test_help_subprocess(self):
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "gsc_api.py"), "--help"],
                           capture_output=True, text=True, encoding="utf-8", timeout=60,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(r.returncode, 0)
        self.assertIn("auth", r.stdout)
        self.assertIn("规范化 CSV", r.stdout)
        for sub in ("auth", "sites", "query"):
            r2 = subprocess.run([sys.executable, os.path.join(SCRIPTS, "gsc_api.py"), sub, "--help"],
                                capture_output=True, text=True, encoding="utf-8", timeout=60)
            self.assertEqual(r2.returncode, 0, sub)

    def test_usage_errors_exit_2(self):
        p = self.sa_file()
        cases = [
            (["query", "--sa", p, "--site", "s", "--start", "2026-9-1",
              "--end", "2026-09-30"], "YYYY-MM-DD"),                       # 坏日期
            (["query", "--sa", p, "--site", "s", "--start", "2026-09-01",
              "--end", "2026-09-30", "--dimensions", "browser"], "不支持的维度"),  # API 没有的维度
            # B10(2026-10-21 改):旧用例拿 device 当契约外维度;device/country 是 API 文档列出的维度,已支持
            (["query", "--sa", p, "--site", "s", "--start", "2026-09-01",
              "--end", "2026-09-30", "--rows", "0"], "≥1"),                # rows 非法
        ]
        for argv, needle in cases:
            rc, out, err, _ = self.run_cli(argv, stub=_ApiStub(total=1))
            self.assertEqual(rc, 2, argv)
            self.assertIn(needle, err)
        # 未指定凭证(隔离 HOME/env,防误吃真实 ~/.config/seo-suite/gsc.json)
        env = {k: v for k, v in os.environ.items() if k != "GSC_SA_FILE"}
        env.update(HOME=self._tmp, GSC_SA_FILE="")
        with mock.patch.dict(os.environ, env, clear=True):
            rc, out, err, _ = self.run_cli(["sites"], stub=_ApiStub())
        self.assertEqual(rc, 2)
        self.assertIn("GSC_SA_FILE", err)

    def test_endpoint_guard(self):
        self.assertTrue(gsc_api.guard_googleapis("https://oauth2.googleapis.com/token"))
        self.assertTrue(gsc_api.guard_googleapis(
            "https://searchconsole.googleapis.com/webmasters/v3/sites"))
        self.assertTrue(gsc_api.guard_googleapis("https://foo.googleapis.com/x"))  # 子域放行
        for evil in ("http://oauth2.googleapis.com/token",        # 非 https
                     "file:///etc/passwd",                        # 非 http(s)
                     "https://169.254.169.254/latest/meta-data",  # 云元数据(IP 非白名单域)
                     "https://oauth2.googleapis.com.evil.com/t",  # 假后缀域
                     "https://evil.com/token",                    # 白名单外域
                     "https://oauth2.googleapis.com@evil.com/token"):  # userinfo 戏法(hostname=evil.com)
            with self.assertRaisesRegex(gsc_api.GuardError, "守卫|https", msg=evil):
                gsc_api.guard_googleapis(evil)
        # 坏 token_uri 走 CLI:SaError → exit 1,不触网
        rc, out, err, _ = self.run_cli(["auth", "--sa", self.sa_file(token_uri="https://evil.com/t")],
                                       stub=_ApiStub())
        self.assertEqual(rc, 1)
        self.assertIn("守卫", err)


if __name__ == "__main__":
    unittest.main(verbosity=1)
