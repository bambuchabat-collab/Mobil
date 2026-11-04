import json, subprocess, sys, time
OUT=sys.argv[1]
H=['-sS','-A','Mozilla/5.0','-H','X-Requested-With: XMLHttpRequest','-X','POST']
def post(url,data):
    for i in range(4):
        r=subprocess.run(['curl',*H,'--data-urlencode',data[0],*sum([['--data-urlencode',d] for d in data[1:]],[]),url],capture_output=True,text=True)
        if r.returncode==0 and r.stdout.strip():
            v=json.loads(r.stdout); return json.loads(v) if isinstance(v,str) else v
        time.sleep(2**i)
    raise SystemExit('fail '+url+str(data))
dates=[]
for y in (2024,2025,2026):
    for m in range(1,13):
        if y==2024 and m<3: continue
        if y==2026 and m>11: continue
        d=post('https://www.tipos.sk/Millennium.CiselneLoterie/ExtraVyplata/GetZrebovania',[f'Rok={y}',f'Mesiac={m}'])
        dates+= [x[:10] for x in d]
dates=sorted(set(dates)); print(len(dates),dates[0],dates[-1],file=sys.stderr)
res=[]
for i,dt in enumerate(dates):
    r=post('https://www.tipos.sk/Millennium.CiselneLoterie/ExtraVyplata/GetForDate',[f'datumZrebovania={dt}'])
    if i==0: print(json.dumps(r,ensure_ascii=False)[:1500],file=sys.stderr)
    res.append({'date':dt,'raw':r})
json.dump(res,open(OUT,'w'),ensure_ascii=False)
print('saved',len(res),file=sys.stderr)
