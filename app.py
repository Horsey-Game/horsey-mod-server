from flask import Flask, abort, request, send_from_directory
from flask_limiter import Limiter

FILES = "/mnt/data2/horsey-server/files"


def client_ip():
    return request.headers.get("CF-Connecting-IP", request.remote_addr)


app = Flask(__name__)
limiter = Limiter(
    client_ip,
    app=app,
    default_limits=["120 per minute"],
    storage_uri="memory://",
)


@app.get("/index.json")
@limiter.limit("60 per minute")
def index():
    return send_from_directory(FILES, "index.json", mimetype="application/json")


@app.get("/index.sig")
@limiter.limit("60 per minute")
def index_signature():
    return send_from_directory(FILES, "index.sig", mimetype="text/plain")


@app.get("/files/<name>")
@limiter.limit("20 per minute")
def download(name):
    # nur mod-zips, die shim und den manager-installer ausliefern
    manager_installer = name.startswith("horsey-mod-manager-") and name.endswith("-setup.exe")
    if not (name.endswith(".zip") or name == "version.dll" or manager_installer):
        abort(404)
    return send_from_directory(FILES, name, as_attachment=True)
