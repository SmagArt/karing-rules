# -*- coding: utf-8 -*-
"""Проверка имён встроенных наборов в diversion_rules_custom.json.

Списки допустимых кодов лежат внутри самого Karing
(assets/datas/geosite_codes.txt и рядом), интернет не нужен.
Невалидное имя Karing выбрасывает молча — отсюда и валидатор.

    python check_rulesets.py
"""
import io
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

RULES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diversion_rules_custom.json")
FILES = {"geosite": "geosite_codes.txt", "geoip": "geoip_codes.txt", "acl": "acl_codes.txt"}


def karing_datas():
    """Папка с *_codes.txt: берём из пути запущенного karing.exe."""
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-Process karing -ErrorAction SilentlyContinue | Select-Object -First 1).Path"],
        capture_output=True, text=True).stdout.strip()
    if not out:
        sys.exit("Karing не запущен — не могу найти папку приложения. Запусти его и повтори.")
    return os.path.join(os.path.dirname(out), "data", "flutter_assets", "assets", "datas")


def main():
    d = karing_datas()
    codes = {k: {l.strip() for l in io.open(os.path.join(d, f), encoding="utf-8") if l.strip()}
             for k, f in FILES.items()}
    rules = json.load(io.open(RULES, encoding="utf-8"))["rules"]
    bad = []
    total = 0
    for r in rules:
        for name in r.get("rule_set_build_in") or []:
            total += 1
            kind, _, code = name.partition(":")
            if code not in codes.get(kind, set()):
                bad.append((r.get("name", "?"), name))
    print("правил: %d, наборов: %d" % (len(rules), total))
    if not bad:
        print("Все имена валидны.")
        return
    print("НЕВАЛИДНЫ (Karing выбросит их молча):")
    for rule, name in bad:
        print("  %-28s <- %s" % (name, rule))
    sys.exit(1)


if __name__ == "__main__":
    main()
