"""Download draw history of a TIPOS number game.
Usage: python3 -I fetch_all.py <Game> <start_year> <out.json>
Game is one of Loto, Loto5z35, Eurojackpot, Euromiliony, VsetkoAleboNic, ExtraVyplata.
"""
import json, subprocess, sys, time, datetime
from concurrent.futures import ThreadPoolExecutor

G, Y0, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3]
BASE = f'https://www.tipos.sk/Millennium.CiselneLoterie/{G}/'
H = ['-sS', '--max-time', '30', '-A', 'Mozilla/5.0', '-H', 'X-Requested-With: XMLHttpRequest', '-X', 'POST']

def post(path, fields):
    args = []
    for f in fields: args += ['--data-urlencode', f]
    for i in range(5):
        r = subprocess.run(['curl', *H, *args, BASE + path], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            try:
                v = json.loads(r.stdout); return json.loads(v) if isinstance(v, str) else v
            except Exception:
                pass
        time.sleep(1.5 * 2 ** i)
    return None

today = datetime.date.today()
months = [(y, m) for y in range(Y0, today.year + 1) for m in range(1, 13) if (y, m) <= (today.year, today.month)]
with ThreadPoolExecutor(6) as ex:
    lists = list(ex.map(lambda ym: post('GetZrebovania', [f'Rok={ym[0]}', f'Mesiac={ym[1]}']) or [], months))
dates = sorted({d[:10] for l in lists for d in l})
print(G, len(dates), dates[:1], dates[-1:], file=sys.stderr)
def one(d):
    return {'date': d, 'raw': post('GetForDate', [f'datumZrebovania={d}'])}
with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(one, dates))
bad = [r['date'] for r in res if not r['raw']]
print(G, 'saved', len(res), 'missing', len(bad), bad[:5], file=sys.stderr)
json.dump(res, open(OUT, 'w'), ensure_ascii=False)
