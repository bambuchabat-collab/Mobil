"""Assemble report data and render the HTML page.
Usage: python3 -I build.py draws.json results.json tickets.json template.html out.html prompt.txt
"""
import json, sys, math
import numpy as np

D = json.load(open(sys.argv[1])); R = json.load(open(sys.argv[2])); TK = json.load(open(sys.argv[3]))
tpl = open(sys.argv[4], encoding='utf-8').read(); OUT = sys.argv[5]; PROMPT = open(sys.argv[6], encoding='utf-8').read().strip()
T = len(D); N = 27
main = np.zeros((T, N), int)
for i, d in enumerate(D): main[i, np.array(d['main']) - 1] = 1
pb = np.array([d['pb'] for d in D])
hdate = lambda s: f'{s[8:10]}.{s[5:7]}.{s[0:4]}'
fmt = lambda x, d=1: f'{x:,.{d}f}'.replace(',', ' ').replace('.', ',')

# ---- final formula walk-forward ----
z = lambda v: (v - v.mean()) / (v.std() + 1e-9)
def formula_pick(t):
    s = 0.5 * z(main[:t].sum(0).astype(float)) + 0.35 * z(main[max(0, t - 52):t].sum(0).astype(float)) + 0.15 * z(main[max(0, t - 20):t].sum(0).astype(float))
    s = s + np.random.default_rng(t).random(N) * 1e-9
    return np.argsort(-s)[:6]
def hot(t, w=None):
    s = main[(0 if w is None else max(0, t - w)):t].sum(0).astype(float) + np.random.default_rng(t).random(N) * 1e-9
    return np.argsort(-s)[:6]
START = 30
fh = np.array([main[t, formula_pick(t)].sum() for t in range(START, T)])
rng = np.random.default_rng(5)
nd = T - START
null = np.array([np.take_along_axis(main[START:], np.argsort(rng.random((nd, N)), 1)[:, :6], 1).sum() for _ in range(20000)])
p_formula = float((null >= fh.sum()).mean())
var1 = 6 * (6 / 27) * (21 / 27) * (21 / 26)

periods = [(30, 85), (85, 125), (125, T)]
def mon(s):
    m = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'][int(s[5:7]) - 1]
    return f'{m} {s[2:4]}'
period_heads = [f'{mon(D[a]["date"])} – {mon(D[b - 1]["date"])}' for a, b in periods]
def cells(fn):
    out = []
    for a, b in periods:
        h = int(sum(main[t, fn(t)].sum() for t in range(a, b))); n = b - a
        out.append({'hits': h, 'exp': n * 4 / 3, 'z': (h - n * 4 / 3) / math.sqrt(n * var1)})
    return out
per_rows = [{'name': 'Итоговая формула', 'cells': cells(formula_pick)},
            {'name': 'Горячие за всё время', 'cells': cells(lambda t: hot(t))},
            {'name': 'Горячие за 52 тиража', 'cells': cells(lambda t: hot(t, 52))},
            {'name': 'Горячие за 20 тиражей', 'cells': cells(lambda t: hot(t, 20))}]
last_period = per_rows[0]['cells'][-1]

# pb formula hit rate
def pb_formula(t):
    s = 0.6 * z(np.bincount(pb[:t], minlength=8)[1:].astype(float)) + 0.4 * z(np.bincount(pb[max(0, t - 52):t], minlength=8)[1:].astype(float))
    return int(np.argmax(s + np.random.default_rng(t).random(7) * 1e-9) + 1)
pb_rate = float(np.mean([pb_formula(t) == pb[t] for t in range(START, T)]))

names = {'hot_all': 'Горячие за всё время', 'hot_last10': 'Горячие за 10 тиражей', 'hot_last20': 'Горячие за 20 тиражей',
         'hot_last52': 'Горячие за 52 тиража', 'cold_all': 'Холодные (реже всех)', 'overdue': 'Давно не выпадали',
         'repeat_last': 'Повтор прошлого тиража', 'pair_affinity': 'Частые пары с прошлым тиражом',
         'markov': 'Марковская (что идёт после чего)', 'composite_formula': 'Смесь: частота + пропуск + пары'}
bt = R['backtest']
rows = [{'key': k, 'name': names[k], 'mean': v['mean_hits'], 'ge3': v['ge3_rate'], 'p': v['p_vs_random']} for k, v in bt['strategies'].items()]
rows.sort(key=lambda r: -r['mean'])
ge3_f = float(np.mean(fh >= 3))
rows.insert(0, {'key': 'composite_formula', 'name': '<b>Итоговая формула</b>', 'mean': float(fh.mean()), 'ge3': ge3_f, 'p': p_formula})
for r in rows[1:]:
    if r['key'] == 'composite_formula': r['key'] = 'mix'

F = R['freq']
fm = F['main']; fpb = F['pb']
order = sorted(range(1, 28), key=lambda n: -fm[str(n)])
top_main = [{'n': n, 'c': fm[str(n)]} for n in order[:6]]
bottom_main = [{'n': n, 'c': fm[str(n)]} for n in sorted(range(1, 28), key=lambda n: fm[str(n)])[:4]]
top_pb = [{'n': n, 'c': fpb[str(n)]} for n in sorted(range(1, 8), key=lambda n: -fpb[str(n)])[:2]]
freqs = {'all': main.sum(0).tolist(), '12m': main[-52:].sum(0).tolist(), '6m': main[-26:].sum(0).tolist()}

rep = pb[1:] == pb[:-1]
thirds = [(0, 55), (55, 110), (110, T - 1)]
rep_th = [float(rep[a:b].mean()) for a, b in thirds]
twice = [d['date'] for d in D].index('2026-04-23')
rep_twice = float(rep[twice - 1:].mean())

P = R['patterns']
def share(dct, keys): return sum(dct[str(k)] for k in keys)
patterns = [
    {'k': 'Средняя сумма 6 чисел', 'obs': fmt(P['sum']['mean_obs']), 'th': fmt(P['sum']['mean_theory']), 'ok': True},
    {'k': 'Тиражи с 3 нечётными', 'obs': fmt(100 * P['odd']['obs']['3'], 0) + ' %', 'th': fmt(100 * P['odd']['theory']['3'], 0) + ' %', 'ok': True},
    {'k': 'Тиражи с 3 числами от 1 до 13', 'obs': fmt(100 * P['low1_13']['obs']['3'], 0) + ' %', 'th': fmt(100 * P['low1_13']['theory']['3'], 0) + ' %', 'ok': True},
    {'k': 'Есть хотя бы пара соседних чисел', 'obs': fmt(100 * (1 - P['consecutive_pairs']['obs']['0']), 0) + ' %', 'th': fmt(100 * (1 - P['consecutive_pairs']['theory']['0']), 0) + ' %', 'ok': True},
    {'k': 'Чисел повторяется с прошлого тиража', 'obs': fmt(P['repeat_from_prev']['mean_obs'], 2), 'th': fmt(P['repeat_from_prev']['mean_theory'], 2), 'ok': True},
    {'k': 'Доп. число = прошлому, весь период', 'obs': fmt(100 * P['pb_repeat_prev']['obs'], 1) + ' %', 'th': '14,3 %', 'ok': False},
    {'k': 'Доп. число = прошлому, с 23.04.2026', 'obs': fmt(100 * rep_twice, 1) + ' %', 'th': '14,3 %', 'ok': True},
]

odds = []
avg = R['avg_prize_last52']
for k in ['6+1', '6+0', '5+1', '5+0', '4+1', '4+0', '3+1', '3+0']:
    pr = {'6+1': '480 000 € (4 000 €/мес. × 10 лет)', '6+0': '30 000 € (2 500 €/мес. × 1 год), делится'}.get(k, fmt(avg[k], 2) + ' €')
    odds.append({'k': k, 'p': R['odds'][k], 'prize': pr})

E = R['economics']
plans = TK['plans']; plan_keys = list(plans.keys())
p8 = plans['8']

text = {
 'freq': f"Чаще всех выпадало <b>11</b>: {fm['11']} раз при ожидании {fmt(F['expected_main'])} (σ = {fmt(F['sd_main'])}). Это +{fmt((fm['11'] - F['expected_main']) / F['sd_main'])}σ, но среди 27 чисел хоть одно такое отклонение случайно бывает в {fmt(100 * F['p_max_main_ge'], 1)} % историй. Общий тест хи-квадрат по всем числам: p = {fmt(F['p_chi_main'], 3)}, то есть распределение на границе нормы, но не за ней. В последний месяц 11 не выпало ни разу.",
 'pb': f"Во втором барабане 7 выпала только {fpb['7']} раз при ожидании {fmt(F['expected_pb'])}. Это самая сильная аномалия частот: такое редкое число случайно бывает в {fmt(100 * F['p_min_pb_le'], 1)} % историй. Но в последних 52 тиражах 7 выпадала {int((pb[-52:] == 7).sum())} раз при ожидании {fmt(52 / 7)}, то есть перекос уже почти исчез.",
 'n': f"Каждое поле стоит 1,50 € и в среднем возвращает {fmt(1.5 * E['payout_ratio'], 2)} €: TIPOS выплачивает {fmt(100 * E['payout_ratio'], 1)} % ставок. Поэтому больше полей значит выше шанс на какой-то выигрыш и одновременно больше ожидаемый минус. Подобранные поля выигрывают у случайных только в шансе на мелкий приз: при 8 полях {fmt(100 * p8['p_any_prize'])} % против {fmt(100 * p8['p_any_prize_quickpick'])} %. Шанс на главный приз от подбора не меняется. Даже 36 полей (54 €) не гарантируют 3 совпадения: лучший найденный набор покрывает {fmt(100 * TK['guarantee3']['coverage'], 2)} % тиражей.",
 'bt': f"Каждая формула получала только прошлые тиражи и выбирала 6 чисел на следующий. Проверено {bt['draws_tested']} тиражей с {hdate(bt['from'])}. Случайный выбор угадывает в среднем 1,333 числа. p показывает, как часто случайный выбор набирает столько же или больше совпадений (20 000 симуляций).",
 'bt2': f"Формулы на «горячих» числах действительно обгоняли случай, но только в первый год. Итоговая формула собрана из двух лучших уже после просмотра результатов, поэтому её p завышает пользу. Главное видно по периодам: в последнем ({period_heads[-1]}) она угадала {last_period['hits']} чисел при ожидании {fmt(last_period['exp'], 0)} ({'+' if last_period['z'] >= 0 else ''}{fmt(last_period['z'])}σ). Доп. число формула угадывала в {fmt(100 * pb_rate, 1)} % тиражей при случайных 14,3 %.",
 'anom': f"Доп. число повторяло прошлое в {fmt(100 * P['pb_repeat_prev']['obs'], 1)} % тиражей вместо 14,3 % (перестановочный тест p ≈ 0,0003). Но по третям истории это {fmt(100 * rep_th[0], 0)} % → {fmt(100 * rep_th[1], 0)} % → {fmt(100 * rep_th[2], 0)} %, а с перехода на два тиража в неделю 23.04.2026 эффекта нет ({fmt(100 * rep_twice, 1)} %). Перекос «горячих» чисел исчез примерно тогда же. Всё остальное (суммы, чёт/нечёт, малые/большие, соседние числа, повторы основных чисел) совпадает с теорией.",
 'odds': f"За всё время продано около {fmt(E['tickets_est'] / 1e6, 1)} млн полей, выплачено {fmt(E['wins'] / 1e6, 1)} млн € из {fmt(E['deposits'] / 1e6, 1)} млн €. Главный приз 6+1 выиграли {E['tier1_winners']} раз (при чисто случайной игре ожидалось бы около {fmt(E['tier1_expected'], 0)}). Приз за 6+0 общий: при двух победителях каждый получил 15 000 €, поэтому поля с «узорами» (1-2-3-4-5-6, ряды и диагонали купона) выгоднее не ставить."
}

facts = [
    {'v': fmt(100 * P['pb_repeat_prev']['obs'], 1) + ' %', 'k': 'доп. число повторяло прошлое (норма 14,3 %)'},
    {'v': ' → '.join(fmt(100 * x, 0) for x in rep_th) + ' %', 'k': 'то же по третям истории: эффект угас'},
    {'v': f"{fpb['7']} из {T}", 'k': f"доп. число 7 (ожидалось {fmt(F['expected_pb'])})"},
    {'v': f"{fm['11']} из {T}", 'k': f"число 11 (ожидалось {fmt(F['expected_main'])})"},
]

sources = [
    'Тиражи: tipos.sk, эндпоинты <span class="mono">ExtraVyplata/GetZrebovania</span> и <span class="mono">GetForDate</span>, все 165 тиражей с 25.03.2024 по 02.11.2026.',
    'Сверка: официальная статистика <a href="https://www.tipos.sk/loterie/ciselne-loterie/statistika-zrebovani/extra-vyplata">Štatistika žrebovaní</a> (частоты совпали один в один).',
    'Правила: <a href="https://www.tipos.sk/loterie/extra-vyplata/ako-hrat">Ako hrať</a> (6 из 27 + 1 из 7, 8 полей на купоне), <a href="https://sita.sk/v-pondelok-sa-znova-rozdavala-extra-vyplata-v-loterii-od-tiposu-padli-dve-najvyssie-vyhry/">SITA</a> (1,50 € за поле, старт 25.03.2024).',
    'Срок приёма и время тиража на 5.11.2026 взяты со страницы <a href="https://www.tipos.sk/loterie/extra-vyplata">Extra výplata</a>.',
    'Метод: p-значения считались симуляцией честной лотереи (20 000 историй), шансы купона перебором всех 296 010 комбинаций основных чисел.',
]

data = {'n_draws': T, 'first_h': hdate(D[0]['date']), 'last_h': hdate(D[-1]['date']), 'combos_pb': math.comb(27, 6) * 7,
        'payout': E['payout_ratio'], 'plans': plans, 'plan_keys': plan_keys, 'top_main': top_main, 'bottom_main': bottom_main,
        'top_pb': top_pb, 'pb_freq': fpb, 'exp_main': F['expected_main'], 'formula': TK['formula'], 'freqs': freqs,
        'text': text, 'backtest': {'rows': rows, 'random_ge3': bt['random_ge3_rate']}, 'periods': per_rows, 'period_heads': period_heads,
        'facts': facts, 'patterns': patterns, 'odds': odds, 'p_any1': R['p_any_prize_1ticket'], 'prompt': PROMPT, 'sources': sources}
html = tpl.replace('/*DATA*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
open(OUT, 'w', encoding='utf-8').write(html)
print('formula total', int(fh.sum()), 'mean', fh.mean(), 'p', p_formula, 'pb_rate', pb_rate)
print('periods', json.dumps(per_rows, ensure_ascii=False))
print('rep thirds', rep_th, 'since twice weekly', rep_twice)
