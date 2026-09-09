# -*- coding: utf-8 -*-
"""Живые соединения Karing: какой домен каким правилом отправлен и куда.

Читает Clash API самого Karing (порт и секрет берутся из service_core.json),
поэтому ничего настраивать не надо — только Karing должен быть запущен.

    python check_connections.py            # все соединения
    python check_connections.py apple      # только домены, где встречается 'apple'
    python check_connections.py ad ads doubleclick
"""
import io
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

CORE = os.path.expandvars(r"%APPDATA%\karing\karing\service_core.json")


def api():
    cfg = json.load(io.open(CORE, encoding="utf-8"))["experimental"]["clash_api"]
    url = "http://%s/connections" % cfg["external_controller"]
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + cfg["secret"]})
    # мимо системного прокси — иначе Karing вернёт 502 на свой же порт
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=8) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    needles = [a.lower() for a in sys.argv[1:]]
    rows = set()
    for c in api().get("connections") or []:
        m = c.get("metadata", {})
        host = m.get("host") or m.get("destinationIP") or "?"
        # 'Имя правила[Самостоятельная настройка] => route(куда)'
        rule = re.sub(r"\[[^\]]*\]", "", c.get("rule") or "")
        rule = rule.split("=>")[0].strip() or "(без правила)"
        out = " <- ".join(c.get("chains") or [])
        if needles and not any(n in host.lower() for n in needles):
            continue
        rows.add((host, rule, out))
    if not rows:
        print("Совпадений нет." if needles else "Активных соединений нет.")
        return
    w = max(len(r[0]) for r in rows)
    for host, rule, out in sorted(rows):
        print("%-*s  %-45s  %s" % (w, host, rule[:45], out))


if __name__ == "__main__":
    main()
