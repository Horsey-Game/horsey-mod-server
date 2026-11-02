"""Scan the mod zips and write index.json for the mod manager.

Run on the server after adding or changing a zip:
    /mnt/data1/horsey-server/venv/bin/python build_index.py
Then sign on the PC with sign_index.py and upload index.json and index.sig.
"""

import hashlib
import json
import re
import zipfile
from pathlib import Path

FILES = Path("/mnt/data2/horsey-server/files")
SEQ_FILE = FILES.parent / "index_sequence.txt"
BASE_URL = "https://mods.badasswizard.boats"
SHIM_API_VERSION = 1
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
MANAGER_PATTERN = re.compile(r"^horsey-mod-manager-(\d+(?:\.\d+)*)-setup\.exe$")


def read_manifest(zf):
    names = zf.namelist()
    if "manifest.json" in names:
        return json.loads(zf.read("manifest.json"))
    for name in names:
        if name.endswith("/manifest.json") and name.count("/") == 1:
            return json.loads(zf.read(name))
    raise ValueError("no manifest.json")


def describe(path):
    with zipfile.ZipFile(path) as zf:
        manifest = read_manifest(zf)
    mod_id = str(manifest.get("id", ""))
    api = manifest.get("api_version", 0)
    if not ID_PATTERN.match(mod_id):
        raise ValueError("bad id")
    if not isinstance(api, int) or not 1 <= api <= SHIM_API_VERSION:
        raise ValueError(f"api_version {api} not supported")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "id": mod_id,
        "name": manifest.get("name", mod_id),
        "version": str(manifest.get("version", "")),
        "author": manifest.get("author", ""),
        "description": manifest.get("description", ""),
        "api_version": api,
        "dependencies": manifest.get("dependencies", []),
        "sha256": digest,
        "size": path.stat().st_size,
        "download_url": f"{BASE_URL}/files/{path.name}",
    }


# sucht den installer mit der höchsten version im files-ordner
def manager_entry():
    best = None
    for path in FILES.glob("horsey-mod-manager-*-setup.exe"):
        match = MANAGER_PATTERN.match(path.name)
        if not match:
            continue
        version = match.group(1)
        key = tuple(int(part) for part in version.split("."))
        if best is None or key > best[0]:
            best = (key, version, path)
    if best is None:
        return None
    _, version, path = best
    return {
        "version": version,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size": path.stat().st_size,
        "download_url": f"{BASE_URL}/files/{path.name}",
    }


def next_sequence():
    last = int(SEQ_FILE.read_text().strip()) if SEQ_FILE.exists() else 0
    return last + 1


def main():
    mods = []
    for path in sorted(FILES.glob("*.zip")):
        try:
            mods.append(describe(path))
        except (ValueError, KeyError, zipfile.BadZipFile) as err:
            print(f"skipped {path.name}: {err}")
    seq = next_sequence()
    SEQ_FILE.write_text(str(seq))
    shim = FILES / "version.dll"
    shim_entry = None
    if shim.exists():
        shim_entry = {
            "sha256": hashlib.sha256(shim.read_bytes()).hexdigest(),
            "size": shim.stat().st_size,
            "download_url": f"{BASE_URL}/files/version.dll",
        }
    # manager-eintrag nur wenn ein installer im files-ordner liegt
    index = {"sequence": seq, "shim": shim_entry, "manager": manager_entry(), "mods": mods}
    (FILES / "index.json").write_text(json.dumps(index, indent=2))
    print(f"wrote index.json with {len(mods)} mod(s), sequence {seq}")


if __name__ == "__main__":
    main()
