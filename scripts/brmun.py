#!/usr/bin/env python3
"""Resultado de presidente por município (todo o Brasil) a partir do site de resultados do TSE.
Uso: python3 scripts/brmun.py 6258 brmun-t2.json
Grava {"ele","dg","hg","nr":[números],"m":{codigo_ibge:[% seções apuradas, votos por número...]}}.
Municípios já 100% apurados no arquivo anterior não são baixados de novo."""
import json, sys, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

ele, out = sys.argv[1], sys.argv[2]
B = f"https://resultados.tse.jus.br/oficial/ele2026/{ele}"
EC = "e" + ele.zfill(6)

def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "votopa"}), timeout=30) as r:
                return json.load(r)
        except Exception as e:
            err = e
            time.sleep(1 + 2 * i)
    print("falhou", url, err, file=sys.stderr)
    return None

cm = get(f"{B}/config/mun-{EC}-cm.json")
muns = [(u["cd"], m["cd"], m["cdi"]) for u in cm["abr"] if u["cd"] != "zz" for m in u["mu"]]
old = {}
if os.path.exists(out):
    try: old = json.load(open(out))
    except Exception: old = {}
prev = old.get("m", {}); nr = old.get("nr") or []

def one(t):
    uf, cd, cdi = t
    p = prev.get(cdi)
    if p and p[0] >= 100: return cdi, None
    d = get(f"{B}/dados/{uf}/{uf}{cd}-c0001-{EC}-u.json")
    if not d: return cdi, None
    v = {}
    for c in d.get("carg", []):
        for a in c.get("agr", []):
            for pa in a.get("par", []):
                for k in pa.get("cand", []):
                    v[k["n"]] = int(k.get("vap") or 0)
    pst = float(str(d["s"]["pstn"]).replace(",", ".") or 0) if d.get("s") else 0
    if d.get("tf") != "s" and pst >= 100: pst = 99.99
    return cdi, (pst, v, d.get("dg"), d.get("hg"))

with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(one, muns))
new = {cdi: r for cdi, r in res if r}
for _, (pst, v, dg, hg) in new.items():
    for n in v:
        if n not in nr: nr.append(n)
tot = {n: sum(r[1].get(n, 0) for r in new.values()) for n in nr}
nr.sort(key=lambda n: -tot.get(n, 0))
m = {}
onr = old.get("nr") or []
for cdi, p in prev.items():
    m[cdi] = [p[0]] + [p[1 + onr.index(n)] if n in onr and 1 + onr.index(n) < len(p) else 0 for n in nr]
for cdi, (pst, v, dg, hg) in new.items():
    m[cdi] = [round(pst, 2)] + [v.get(n, 0) for n in nr]
# carimbo de data/hora mais recente
stamps = [(r[2], r[3]) for r in new.values() if r[2]]
def key(s):
    d, h = s; dd, mm, yy = d.split("/"); return yy + mm + dd + h
dg, hg = max(stamps, key=key) if stamps else (old.get("dg"), old.get("hg"))
res = {"ele": ele, "dg": dg, "hg": hg, "nr": nr, "m": m}
s = json.dumps(res, separators=(",", ":"))
if json.dumps({**old, "dg": None, "hg": None}, sort_keys=True) != json.dumps({**res, "dg": None, "hg": None}, sort_keys=True) or not os.path.exists(out):
    open(out, "w").write(s)
    print(f"{len(m)} municípios, {len(new)} baixados agora, dados até {dg} {hg}")
else:
    print("sem mudanças")

# Na coleta automática do GitHub, também atualiza a cópia de reserva dos totais (live.json) e a deixa pronta para o commit
if os.environ.get("GITHUB_ACTIONS") and ele == "6258":
    import subprocess
    try:
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "live.py"), ele, "live.json"], timeout=240)
        subprocess.run(["git", "add", "live.json"])
    except Exception as e:
        print("live.json falhou:", e)
