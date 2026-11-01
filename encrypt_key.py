"""One-time: wrap the raw signing key in a passphrase. Run this yourself in a terminal.

    python encrypt_key.py

Writes index_signing_private.pem next to the raw key, checks that it loads, signs,
and verifies against the public key the app ships. It does not delete the raw key.
Once the .pem is backed up and sign_index.py works, delete the raw .key file yourself.
"""

import getpass
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

KEY_DIR = Path(os.environ["USERPROFILE"]) / ".horsey-signing"
RAW = KEY_DIR / "index_signing_private.key"
PEM = KEY_DIR / "index_signing_private.pem"
APP_PUBLIC_KEY = bytes.fromhex("58a9b3f690eff8f58a116e4bf309491790e8e8ee60034854a0beaed067c36f97")


def main():
    if PEM.exists():
        sys.exit(f"{PEM} already exists, not overwriting")
    raw = Ed25519PrivateKey.from_private_bytes(RAW.read_bytes())
    pub = raw.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    if pub != APP_PUBLIC_KEY:
        sys.exit("raw key does not match the public key in the app, stopping")

    pw = getpass.getpass("New passphrase (12+ characters): ").encode()
    if len(pw) < 12:
        sys.exit("passphrase too short, nothing written")
    if getpass.getpass("Repeat passphrase: ").encode() != pw:
        sys.exit("passphrases differ, nothing written")

    PEM.write_bytes(
        raw.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.BestAvailableEncryption(pw),
        )
    )

    loaded = serialization.load_pem_private_key(PEM.read_bytes(), password=pw)
    msg = b"round-trip check"
    Ed25519PublicKey.from_public_bytes(APP_PUBLIC_KEY).verify(loaded.sign(msg), msg)
    print(f"wrote {PEM} and verified it signs correctly.")
    print("Next: copy the .pem to a USB stick, keep the passphrase somewhere else,")
    print("then delete the raw .key file yourself.")


if __name__ == "__main__":
    main()
