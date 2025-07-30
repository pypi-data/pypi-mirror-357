import keyring
import json
import os
from pathlib import Path

INDEX_PATH = Path.home() / ".appserver_secrets_index.json"

def _load_index():
    if INDEX_PATH.exists():
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_index(index):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

def set_secret(service, key, password):
    keyring.set_password(service, key, password)
    index = _load_index()
    index.setdefault(service, []).append(key)
    index[service] = list(set(index[service]))
    _save_index(index)

def get_secret(service, key):
    try:
        return keyring.get_password(service, key)
    except keyring.errors.PasswordDeleteError:
        return None
    except Exception:
        return None

def list_secrets():
    return _load_index()

def delete_secret(service, key):
    keyring.delete_password(service, key)
    index = _load_index()
    if service in index and key in index[service]:
        index[service].remove(key)
        if not index[service]:
            del index[service]
        _save_index(index)