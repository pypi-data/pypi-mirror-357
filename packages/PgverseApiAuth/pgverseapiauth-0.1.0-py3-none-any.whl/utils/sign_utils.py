from api.config.AppConfig import config
import hmac
import hashlib
import base64


def generate_sign(path, secret_key):
    sign_string = f"GET {path} HTTP/1.1"
    signature = hmac.new(secret_key.encode(), sign_string.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()
