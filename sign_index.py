"""Sign index.json on your PC. The private key never goes on the server.

Usage:
    python sign_index.py path\\to\\index.json
Writes index.sig next to it (hex). Upload both files to the server's files folder.

Uses index_signing_private.pem (passphrase-protected) if it exists, otherwise the raw key.
"""

import getpass
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

KEY_DIR = Path(os.environ["USERPROFILE"]) / ".horsey-signing"
PEM = KEY_DIR / "index_signing_private.pem"
RAW = KEY_DIR / "index_signing_private.key"


def load_key():
    if PEM.exists():
        pw = getpass.getpass("Signing key passphrase: ").encode()
        return serialization.load_pem_private_key(PEM.read_bytes(), password=pw)
    return Ed25519PrivateKey.from_private_bytes(RAW.read_bytes())


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    index_path = Path(sys.argv[1])
    key = load_key()
    signature = key.sign(index_path.read_bytes())
    sig_path = index_path.with_name("index.sig")
    sig_path.write_text(signature.hex())
    print(f"wrote {sig_path}")


if __name__ == "__main__":
    main()
