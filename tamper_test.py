import sys, urllib.request
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
PUB = bytes.fromhex("58a9b3f690eff8f58a116e4bf309491790e8e8ee60034854a0beaed067c36f97")
base = "https://mods.badasswizard.boats/"
def get(u):
    r = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 HorseyModManager-test"})
    return urllib.request.urlopen(r, timeout=60).read()
idx = get(base + "index.json")
sig = bytes.fromhex(get(base + "index.sig").decode().strip())
key = Ed25519PublicKey.from_public_bytes(PUB)
def ok(data):
    try:
        key.verify(sig, data)
        return True
    except InvalidSignature:
        return False
print("index.json bytes:", len(idx), "| sig bytes:", len(sig))
print("genuine index verifies (expect True):", ok(idx))
t = bytearray(idx)
t[len(t) // 2] ^= 0x01
print("one-bit flip verifies (expect False):", ok(bytes(t)))
print("appended byte verifies (expect False):", ok(idx + b" "))

