#!/usr/bin/env python3
"""Presidente, 1º e 2º turno: totais completos (aptos, comparecimento, abstenção, válidos, brancos, nulos e votos por candidato)
do Brasil, de cada UF, do exterior, de cada cidade do exterior e de cada município. Uso: python3 scripts/presid.py 6257 pres-t1.json"""
import json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
ele, out = sys.argv[1], sys.argv[2]
B = f"https://resultados.tse.jus.br/oficial/ele2026/{ele}"; EC = "e" + ele.zfill(6)
def get(url, tries=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "votopa"}), timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(1.5 * (i + 1))
    print("falhou", url, file=sys.stderr); return None
N = lambda x: int(float(str(x or 0).replace(",", ".")))
def resumo(d, nr):
    if not d: return None
    v = {}
    for cg in d.get("carg", []):
        for a in cg.get("agr", []):
            for p in a.get("par", []):
                for k in p.get("cand", []): v[k["n"]] = N(k.get("vap"))
    for n in v:
        if n not in nr: nr.append(n)
    e, vv, s = d.get("e", {}), d.get("v", {}), d.get("s", {})
    return {"pst": float(str(s.get("pstn", 0)).replace(",", ".")), "ap": N(e.get("te")), "co": N(e.get("c")), "ab": N(e.get("a")),
            "vv": N(vv.get("vv")), "vb": N(vv.get("vb")), "vn": N(vv.get("tvn")), "v": v}
cm = get(f"{B}/config/mun-{EC}-cm.json")
ufs = [u["cd"] for u in cm["abr"]]
mus = [(u["cd"], m["cd"], m["cdi"]) for u in cm["abr"] for m in u["mu"]]
nr = []
with ThreadPoolExecutor(6) as ex:
    br = get(f"{B}/dados/br/br-c0001-{EC}-u.json")
    U = list(ex.map(lambda u: get(f"{B}/dados/{u}/{u}-c0001-{EC}-u.json"), ufs))
    M = []
    for i, r in enumerate(ex.map(lambda t: get(f"{B}/dados/{t[0]}/{t[0]}{t[1]}-c0001-{EC}-u.json"), mus)):
        M.append(r)
        if i % 500 == 0: print(i, "de", len(mus), flush=True)
pack = lambda r: None if not r else [r["pst"], r["ap"], r["co"], r["ab"], r["vv"], r["vb"], r["vn"]] + [r["v"].get(n, 0) for n in nr]
R = {"br": resumo(br, nr)}
RU = {u.upper(): resumo(d, nr) for u, d in zip(ufs, U)}
RM = {}
for (u, cd, cdi), d in zip(mus, M):
    RM[cdi if u != "zz" else "zz" + cd] = resumo(d, nr)
res = {"ele": ele, "dg": br.get("dg"), "hg": br.get("hg"), "campos": ["pst", "aptos", "comparecimento", "abstencao", "validos", "brancos", "nulos"], "nr": nr,
       "br": pack(R["br"]), "uf": {k: pack(v) for k, v in RU.items()}, "mu": {k: pack(v) for k, v in RM.items()}}
json.dump(res, open(out, "w"), separators=(",", ":"))
print("ok", out, len(res["mu"]), "unidades;", sum(1 for v in res["mu"].values() if v is None), "falharam")
