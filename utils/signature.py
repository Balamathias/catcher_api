import hashlib
import json
import re
from typing import Dict, Union
from urllib.parse import unquote

from base64 import b64encode, b64decode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)
from cryptography.hazmat.backends import default_backend


SignatureParams = Dict[str, Union[str, int, float, bool, None]]


def get_str_a(params: SignatureParams) -> str:
    sorted_keys = sorted(params.keys())
    pairs = []

    for key in sorted_keys:
        value = params[key]
        if value is None:
            continue

        string_value = str(value).strip() if isinstance(value, str) else str(value)
        if string_value == "":
            continue

        pairs.append(f"{key}={string_value}")

    return "&".join(pairs)


def get_md5_str(str_a: str) -> str:
    return hashlib.md5(str_a.encode("utf-8")).hexdigest().upper()


def format_public_key(public_key: str) -> str:
    key = re.sub(r"\s+", "", public_key)

    if "-----BEGIN" not in key:
        key = f"-----BEGIN PUBLIC KEY-----\n" + "\n".join(re.findall(".{1,64}", key)) + "\n-----END PUBLIC KEY-----"

    if "-----BEGIN RSAPUBLICKEY-----" in key:
        key = key.replace("-----BEGIN RSAPUBLICKEY-----", "-----BEGIN PUBLIC KEY-----") \
                 .replace("-----END RSAPUBLICKEY-----", "-----END PUBLIC KEY-----")
    return key


def generate_palm_pay_signature(params: SignatureParams, private_key_pem: str) -> str:
    str_a = get_str_a(params)
    md5_str = get_md5_str(str_a)

    private_key = load_pem_private_key(private_key_pem.encode(), password=None, backend=default_backend())
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise ValueError("Only RSA private keys are supported")
    
    signature = private_key.sign(
        md5_str.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA1()
    )
    return b64encode(signature).decode("utf-8")


def verify_palm_pay_signature(params: SignatureParams, public_key_pem: str, signature_b64: str) -> bool:
    str_a = get_str_a(params)
    md5_str = get_md5_str(str_a)
    formatted_key = format_public_key(public_key_pem)

    try:
        public_key = load_pem_public_key(formatted_key.encode(), backend=default_backend())
        if not isinstance(public_key, rsa.RSAPublicKey):
            raise ValueError("Only RSA public keys are supported")
        
        public_key.verify(
            b64decode(signature_b64),
            md5_str.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        return True
    except Exception as e:
        print("Verification failed:", e)
        return False


def verify_palm_pay_callback_signature(raw_json_body: str, public_key_pem: str) -> bool:
    try:
        parsed = json.loads(raw_json_body)
        received_sign = parsed.pop("sign", None)

        if not received_sign:
            print("Missing signature.")
            return False

        decoded_sign = received_sign if '%' not in received_sign else unquote(received_sign)
        return verify_palm_pay_signature(parsed, public_key_pem, decoded_sign)
    except Exception as e:
        print("Callback signature verification failed:", e)
        return False
