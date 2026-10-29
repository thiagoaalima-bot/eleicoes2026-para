import json,glob,os,sys,collections,urllib.request
R=sys.argv[1]
cm=json.load(urllib.request.urlopen('https://resultados.tse.jus.br/oficial/ele2026/6258/config/mun-e006258-cm.json',timeout=60))
nomes=json.load(open(R+'/mu-nomes.json'))
def tit(s):
    small={'de','da','do','das','dos','e','em'};w=s.lower().split();return ' '.join(x if (i and x in small) else x[:1].upper()+x[1:] for i,x in enumerate(w))
zz={'zz'+m['cd']:tit(m['nm']) for u in cm['abr'] if u['cd']=='zz' for m in u['mu']}
def crit(s):
    L1,F1,L2,F2=s[2],s[3],s[7],s[8];gL,gF=L2-L1,F2-F1
    return [int(gL>0 and gF<0),int(gL>0 and gF<=-10),int(gL-gF>=50)]
out={'uf':{},'zz':zz,'tot':[0,0,0]}
for f in glob.glob(R+'/sec/*.json'):
    key=os.path.basename(f)[:-5];uf='ZZ' if key.startswith('zz') else nomes.get(key,['??'])[0]
    c=[0,0,0]
    for loc in json.load(open(f))['l']:
        for s in loc[2]:
            for i,v in enumerate(crit(s)):c[i]+=v
    U=out['uf'].setdefault(uf,{'c':[0,0,0],'m':{}})
    if any(c):U['m'][key]=c
    for i in range(3):U['c'][i]+=c[i];out['tot'][i]+=c[i]
json.dump(out,open(R+'/vistoria.json','w'),ensure_ascii=False,separators=(',',':'))
print(out['tot'],{u:v['c'] for u,v in sorted(out['uf'].items(),key=lambda x:-x[1]['c'][0])[:8]}, os.path.getsize(R+'/vistoria.json'))
