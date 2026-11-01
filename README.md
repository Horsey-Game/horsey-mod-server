# horsey game mod loader server

the scripts that run the mod server and sign the mod list

this is the server branch. the mod manager app is on the manager branch and the shim is on the shim branch

gpl-3.0 see LICENSE

## whats in here

- app.py the flask app behind gunicorn. it serves index.json index.sig and the mod zips
- build_index.py scans the zips and writes index.json with a sequence number
- sign_index.py signs index.json with your ed25519 key on your pc
- encrypt_key.py wraps the raw signing key in a passphrase. you only run this once
- tamper_test.py checks the live index signature against the public key
- horsey-mods.service the systemd unit with hardening

## how publishing a mod works

1. drop the new zip into the files folder on the server
2. run build_index.py on the server. it bumps the sequence number
3. copy index.json down to your pc
4. sign it with sign_index.py and enter your passphrase
5. upload index.json and index.sig back to the files folder
6. run tamper_test.py to make sure the signature checks out

the sequence number has to keep going up. the app refuses any signed list older than one it already accepted so dont reset it

## keys

the private signing key never goes in this repo and never goes on the server. the public key is the only key that belongs anywhere near the code. the .gitignore blocks *.key and *.pem but check before you push anyway

## running it

gunicorn runs the app on 127.0.0.1:8099 and a cloudflare tunnel forwards the public hostname to it. see horsey-mods.service for the systemd setup
