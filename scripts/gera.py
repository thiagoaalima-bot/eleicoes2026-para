import pickle,sys,json,os,collections,urllib.request
D,OUT=sys.argv[1],sys.argv[2]
S=pickle.load(open(D+'/secoes.pkl','rb'))
cm=json.load(urllib.request.urlopen('https://resultados.tse.jus.br/oficial/ele2026/6258/config/mun-e006258-cm.json',timeout=60))
tse2={}
for u in cm['abr']:
    for m in u['mu']: tse2[(u['cd'].upper(),m['cd'])]=('zz'+m['cd']) if u['cd']=='zz' else m['cdi']
def tit(s):
    small={'de','da','do','das','dos','e','em','a','o'}
    w=s.lower().split();return ' '.join(x if (i and x in small) else x[:1].upper()+x[1:] for i,x in enumerate(w))
M=collections.defaultdict(lambda: collections.OrderedDict())
miss=set()
for (uf,cd,z,se),s in sorted(S.items()):
    key=tse2.get((uf,cd))
    if not key: miss.add((uf,cd));continue
    t1,t2=s['1'],s['2']
    def pk(t):
        L,F,B,N=t.get('13',0),t.get('22',0),t.get('95',0),t.get('96',0);O=sum(v for k,v in t.items() if k not in('13','22','95','96'));return [L,F,O,B,N]
    nr,nm,end=s['loc']
    lk=(z,nr)
    loc=M[key].get(lk)
    if loc is None: loc=M[key][lk]=[tit(nm),tit(end),[]]
    loc[2].append([z,se]+pk(t1)+pk(t2))
os.makedirs(OUT+'/sec',exist_ok=True)
tam=0
for key,locs in M.items():
    js=json.dumps({'l':list(locs.values())},ensure_ascii=False,separators=(',',':'))
    open(f'{OUT}/sec/{key}.json','w').write(js);tam+=len(js)
print(len(M),'arquivos', round(tam/1e6,1),'MB', 'sem código:',miss)
