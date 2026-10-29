import zipfile,csv,io,collections,pickle,sys
D=sys.argv[1]
z=zipfile.ZipFile(D+'/br.zip');f=io.TextIOWrapper(z.open('votacao_secao_2026_BR.csv'),encoding='latin-1');r=csv.reader(f,delimiter=';');h=next(r)
i={k:j for j,k in enumerate(h)}
# chave: (UF, cd_mun_tse, zona, secao) -> {'t1':{nr:v}, 't2':{nr:v}, 'loc':(nr_local, nome, endereco), 'mun': nome}
S={};vot={}
for row in r:
    k=(row[i['SG_UF']],row[i['CD_MUNICIPIO']].zfill(5),int(row[i['NR_ZONA']]),int(row[i['NR_SECAO']]))
    s=S.get(k)
    if s is None:s=S[k]={'1':{},'2':{},'loc':(row[i['NR_LOCAL_VOTACAO']],row[i['NM_LOCAL_VOTACAO']],row[i['DS_LOCAL_VOTACAO_ENDERECO']]),'mun':row[i['NM_MUNICIPIO']]}
    t=row[i['NR_TURNO']];nr=row[i['NR_VOTAVEL']];s[t][nr]=s[t].get(nr,0)+int(row[i['QT_VOTOS']])
    vot[nr]=row[i['NM_VOTAVEL']]
pickle.dump(S,open(D+'/secoes.pkl','wb'))
print(len(S),'seções');print({k:v for k,v in vot.items() if k in('13','22','95','96','97')})
tot=collections.Counter()
for s in S.values():
    for t in '12':
        for nr,v in s[t].items(): tot[(t,nr)]+=v
print(tot[('1','13')],tot[('1','22')],tot[('2','13')],tot[('2','22')],tot[('2','95')],tot[('2','96')])
