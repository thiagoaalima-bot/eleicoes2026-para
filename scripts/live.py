#!/usr/bin/env python3
"""Cópia de reserva dos totais do TSE (Brasil, cada UF, exterior e cidades do exterior) em live.json.
O site usa esta cópia quando o TSE recusa a leitura direta (429 em picos de acesso).
Uso: python3 scripts/live.py 6258 live.json"""
import json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
ele, out = sys.argv[1], sys.argv[2]
B = f"https://resultados.tse.jus.br/oficial/ele2026/{ele}"; EC = "e" + ele.zfill(6)
def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "votopa"}), timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(1 + 2 * i)
    return None
def resumo(d):
    c = {}
    for cg in d.get("carg", []):
        for a in cg.get("agr", []):
            for p in a.get("par", []):
                for k in p.get("cand", []): c[k["n"]] = int(k.get("vap") or 0)
    s = d.get("s") or {}
    pst = float(str(s.get("pstn", "0")).replace(",", ".") or 0)
    return {"pst": round(pst, 2), "final": d.get("tf") == "s" and pst >= 100, "c": c}
br = get(f"{B}/dados/br/br-c0001-{EC}-u.json")
if not br: print("TSE sem resposta para o Brasil"); sys.exit(0)
ufs = "ac al am ap ba ce df es go ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to zz".split()
cm = get(f"{B}/config/mun-{EC}-cm.json") or {}
zzc = [m["cd"] for u in cm.get("abr", []) if u["cd"] == "zz" for m in u["mu"]]
with ThreadPoolExecutor(6) as ex:
    rs = list(ex.map(lambda u: get(f"{B}/dados/{u}/{u}-c0001-{EC}-u.json"), ufs))
    zs = list(ex.map(lambda cd: get(f"{B}/dados/zz/zz{cd}-c0001-{EC}-u.json"), zzc))
old = {}
try: old = json.load(open(out))
except Exception: pass
res = {"dg": br.get("dg"), "hg": br.get("hg"), "br": resumo(br),
       "uf": {u.upper(): resumo(d) for u, d in zip(ufs, rs) if d},
       "zz": {cd: resumo(d) for cd, d in zip(zzc, zs) if d}}
for k in ("uf", "zz"):  # mantém o que não veio desta vez
    for kk, v in (old.get(k) or {}).items(): res[k].setdefault(kk, v)
json.dump(res, open(out, "w"), separators=(",", ":"))
print(f"live.json: Brasil {res['br']['pst']}% · {len(res['uf'])} UFs · {len(res['zz'])} cidades do exterior · {res['hg']}")
