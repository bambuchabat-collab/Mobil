"""Render the all-lotteries page.
Usage: python3 -I build2.py multi.json tickets.json style.css body.html prompt.txt out.html
"""
import json, sys, math
R = json.load(open(sys.argv[1])); TK = json.load(open(sys.argv[2]))
css = open(sys.argv[3], encoding='utf-8').read(); body = open(sys.argv[4], encoding='utf-8').read()
PROMPT = open(sys.argv[5], encoding='utf-8').read().strip(); OUT = sys.argv[6]

def f(x, d=0):
    return f'{x:,.{d}f}'.replace(',', ' ').replace('.', ',')
def dmy(s): return f'{s[8:10]}.{s[5:7]}.{s[0:4]}'
def pc(x, d=0): return f(100 * x, d) + ' %'

J = R['joker']; L = R['loto535']; B = R['bundle']; LO = R['loto']; V = R['van']; X = R['extra']
EM = R.get('euromiliony'); EJ = R.get('eurojackpot')

rank = [r['n'] for r in TK['formula']['ranking']]
ev3 = [{'main': sorted(rank[0:6]), 'pb': 2, 'label': 'места 1–6 формулы'},
       {'main': sorted(rank[6:12]), 'pb': 1, 'label': 'места 7–12'},
       {'main': sorted(rank[12:18]), 'pb': 3, 'label': 'места 13–18'}]
my_nums = L['pool']['formula_pick']

copy_text = '\n'.join([f"Extra výplata 5.11, билет {i + 1}: {' '.join(map(str, t['main']))} + {t['pb']}" for i, t in enumerate(ev3)]
                      + [f"Loto 5 z 35 на 6.11: {' '.join(map(str, my_nums))} + JOKER: ÁNO"])

verdict = [
    f"<b>Лазейка есть, но не в угадывании чисел.</b> Это накопившийся джекпот <b>JOKER</b> (добавка к Loto и Loto 5 z 35 за 0,60 €). Шанс угадать 6 цифр всегда 1 к 1 000 000, а джекпот дорос до {f(J['jackpot_carry'])} € и к пятничному тиражу будет около {f(J['pot_next_est'], 0)} €. При таком джекпоте ставка 0,60 € в среднем возвращает {f(J['ev'], 2)} €, то есть {pc(J['ev_ratio'])}. Во всех остальных играх TIPOS возврат 40–58 %.",
    f"<b>Мой билет:</b> Loto 5 z 35, одно поле {' '.join(map(str, my_nums))} + JOKER: ÁNO, всего 1,20 €. Тираж в пятницу 6.11 в 18:00, купить можно уже сегодня. В среднем такой билет возвращает {f(B['ev'], 2)} € из 1,20 € ({pc(B['ev_ratio'])}).",
    f"<b>Extra výplata сегодня, 3 билета по формуле:</b> {'; '.join(' '.join(map(str, t['main'])) + ' + ' + str(t['pb']) for t in ev3)}. У каждого шанс на главный приз одинаковый: 1 к 2 072 070.",
    "<b>Числа не предсказываются ни в одной лотерее.</b> Формулы на частотах в последней трети истории ни в одной игре не обогнали случайный выбор с запасом, который выдержал бы поправку на число проверок. Частоты чисел и цифры Joker в пределах нормы.",
]

rows = []
rows.append({'name': 'JOKER (к Loto / Loto 5 z 35)', 'price': 0.60, 'ev': J['ev'], 'ratio': J['ev_ratio'], 'top': f"≈ {f(J['pot_next_est'])} €", 'p': 1e-6})
rows.append({'name': 'Loto 5 z 35 + JOKER, билет', 'price': 1.20, 'ev': B['ev'], 'ratio': B['ev_ratio'], 'top': f"{f(J['pot_next_est'])} € + {f(L['pot_next_est'])} €", 'p': 1e-6})
rows.append({'name': 'Extra výplata', 'price': 1.50, 'ev': X['ev'], 'ratio': X['ev_ratio'], 'top': '480 000 € рентой', 'p': X['p_jackpot']})
rows.append({'name': 'Loto 5 z 35', 'price': 0.60, 'ev': L['ev'], 'ratio': L['ev_ratio'], 'top': f"≈ {f(L['pot_next_est'])} €", 'p': L['p_jackpot']})
rows.append({'name': 'Všetko alebo nič', 'price': 1.50, 'ev': V['ev'], 'ratio': V['ev_ratio'], 'top': '100 000 €', 'p': V['p_top']})
if EM: rows.append({'name': 'Euromilióny', 'price': 1.50, 'ev': EM['ev_upper'], 'ratio': EM['ev_ratio'], 'top': f"{f(EM['jackpot'])} €", 'p': EM['p_jackpot'], 'upper': True})
if EJ: rows.append({'name': 'Eurojackpot', 'price': 2.00, 'ev': EJ['ev_upper'], 'ratio': EJ['ev_ratio'], 'top': f"{f(EJ['jackpot'] / 1e6)} млн €", 'p': EJ['p_jackpot'], 'upper': True})
rows.append({'name': 'Loto (2 тяга)', 'price': 1.20, 'ev': LO['ev'], 'ratio': LO['ev_ratio'], 'top': f"{f(LO['jackpot'])} €", 'p': LO['p_jackpot']})
rows.append({'name': 'Euromilióny JOKER', 'price': 0.50, 'ev': R['em_joker']['ev'], 'ratio': R['em_joker']['ev_ratio'], 'top': '20 000 €', 'p': 1e-6})
rows.append({'name': 'Eurojackpot JOKER', 'price': 1.00, 'ev': R['ej_joker']['ev'], 'ratio': R['ej_joker']['ev_ratio'], 'top': '50 000 €', 'p': 1e-6})
rows.sort(key=lambda r: -r['ratio'])

games = []
def grow(name, P, extra=None):
    games.append({'name': name, 'draws': P['draws'], 'from': dmy(P['from']),
                  'top': ', '.join(f"{t['n']}" for t in P['top'][:5]), 'bottom': ', '.join(f"{t['n']}" for t in P['bottom']),
                  'p_chi': P['p_chi'], 'z': P['backtest']['formula']['z'], 'zl': P['backtest']['formula']['z_last_third'],
                  'pick': ' '.join(map(str, P['formula_pick'])) + (f' + {extra}' if extra else '')})
grow('Loto 5 z 35', L['pool'])
grow('Loto, 1. ťah', LO['pool'])
if EM: grow('Euromilióny', EM['pool'], EM['extra']['top'][0])
if EJ: grow('Eurojackpot', EJ['pool'], ' '.join(map(str, sorted(EJ['extra']['top']))))
grow('Všetko alebo nič', V['pool'])

# strongest single backtest signal across all games/strategies (for honesty about multiple testing)
allz = []
for name, P in [('Loto 5 z 35', L['pool']), ('Loto', LO['pool']), ('Všetko alebo nič', V['pool'])] + ([('Euromilióny', EM['pool'])] if EM else []) + ([('Eurojackpot', EJ['pool'])] if EJ else []):
    for k, v in P['backtest'].items(): allz.append((v['z'], name, k, v['z_last_third']))
allz.sort(reverse=True)
best = allz[0]
nt = len(allz)
names = {'formula': 'итоговая формула', 'hot_all': 'горячие за всё время', 'hot_52': 'горячие за 52', 'hot_20': 'горячие за 20', 'cold_all': 'холодные', 'repeat_last': 'повтор прошлого', 'overdue': 'давно не выпадавшие'}

wins = [[dmy(w[0]), w[1], w[2]] for w in J['wins'][::-1][:10]]
jfacts = [
    {'v': f"{f(J['jackpot_carry'])} €", 'k': 'джекпот Joker сейчас (после тиража 4.11)'},
    {'v': f"{f(J['break_even_pot'])} €", 'k': 'с какого джекпота Joker окупается в среднем'},
    {'v': f"{f(J['max_carry'])} €", 'k': f"прошлый максимум с 2018 года ({dmy(J['max_carry_date'])})"},
    {'v': f"{J['n_wins']} из {f(J['draws'])}", 'k': 'тиражей с выигранным джекпотом Joker с 2018'},
]
text = {
 'j1': f"Joker не зависит от ваших чисел: терминал печатает случайное шестизначное число, и надо совпасть с выпавшими цифрами по позициям. Шанс на джекпот всегда 1 к 1 000 000, а призы за 5, 4, 3 и 2 последние цифры фиксированные (3 300, 330, 33 и 3,30 €) и вместе дают {f(J['fixed_ev'], 2)} € на ставку. Если джекпот никто не взял, он переходит на следующий тираж. Поэтому выгодность Joker зависит только от накопленной суммы: выше {f(J['break_even_pot'])} € ставка в среднем возвращает больше, чем стоит. С 2018 года так было лишь в {pc(J['share_draws_ev_positive'], 1)} тиражей, и сейчас как раз такой период.",
 'j2': f"Риск дележа учтён. Сейчас продаётся около {f(J['tickets_per_draw'])} ставок Joker за тираж, поэтому с вероятностью около {pc(1 - math.exp(-J['tickets_per_draw'] / 1e6))} у победителя будет совладелец джекпота. В среднем это снижает выигрыш до {pc(J['share_factor'])} от джекпота. Цифры Joker распределены равномерно на всех шести позициях (минимальное p = {f(min(p['p'] for p in J['digits']['positions']), 2)}), подкрутки нет. Джекпот выпадает в среднем раз в {f(J['draws'] / J['n_wins'], 1)} тиража, последний раз его взяли {dmy(J['wins'][-1][0])}.",
 'g': f"Для каждой лотереи сделано то же, что и для Extra výplata: частоты, тест хи-квадрат (p методом Монте-Карло) и проверка семи формул на прошлых тиражах, где формула видела только прошлое. «Формула» в таблице: 50 % частоты за всё время, 35 % за 52 тиража, 15 % за 20 тиражей. Отклонение в σ показывает, на сколько формула угадывала больше (+) или меньше (−) случайного выбора.",
 'gnote': f"Всего проверено {nt} пар «игра × формула». Лучший результат: {names[best[2]]} в {best[1]}, {'+' if best[0] >= 0 else ''}{f(best[0], 1)}σ за всё время и {'+' if best[3] >= 0 else ''}{f(best[3], 1)}σ в последней трети. При {nt} проверках одно отклонение больше 2σ ожидается само по себе, так что это не преимущество.",
}
cmp_note = ("Возврат на 1 € = ожидаемая сумма выигрышей при сегодняшних джекпотах и средних призах за последние 104 тиража, делённая на ставку. "
            "Для Joker и Loto 5 z 35 учтены рост джекпота к следующему тиражу и вероятность дележа. "
            "* У Eurojackpot и Euromilióny это верхняя оценка без дележа джекпота, реальный возврат ещё ниже.")
honest = [
    f"Положительное ожидание не значит выигрыш. Один билет Loto 5 z 35 + Joker за 1,20 € с вероятностью около 99,9999 % джекпот не возьмёт. Чаще всего вы получите 0 € или мелкий приз: хоть какой-то выигрыш в Joker бывает примерно 1 раз из 100 (3,30 € и выше), в Loto 5 z 35 примерно 1 раз из 72.",
    f"Больше билетов увеличивают шанс линейно: 10 билетов (12 €) дают 1 к 100 000 на джекпот Joker. Средний результат на 1 € остаётся около {f(B['ev_ratio'], 2)} €, но разброс огромный. Тратьте только ту сумму, которую не жалко потерять.",
    "Окно временное. Когда джекпот Joker кто-то выиграет, он сбросится до 6 600 €, и Joker снова станет невыгодным (около 21 % возврата).",
    "Номер Joker выбрать нельзя, его печатает генератор. Один Joker на одну ставку, и к нему нужно хотя бы одно поле Loto или Loto 5 z 35. Самый дешёвый вариант: одно поле Loto 5 z 35.",
    "Loto 5 z 35 отдельно становится выгодной, когда её джекпот выше примерно " + f(L['break_even_pot']) + " €. С 2018 года так было только в " + pc(L['share_jack_ge_be'], 1) + " тиражей, сейчас нет.",
]
lede = (f"Разобраны все числовые лотереи TIPOS, кроме Keno: {f(L['pool']['draws'] + LO['pool']['draws'] + V['pool']['draws'] + (EM['pool']['draws'] if EM else 0) + (EJ['pool']['draws'] if EJ else 0) + 165)} тиражей "
        f"с официального сайта, правила сверены с игровым планом TIPOS. Цены и джекпоты на утро 5.11.2026.")
my_note = (f"Числа поля по той же формуле, что и для Extra výplata. Они не повышают шанс в Loto 5 z 35 (там формула тоже не обгоняет случай), выгоду даёт только Joker. "
           f"Шанс джекпота Joker 1 к 1 000 000, Loto 5 z 35 1 к {f(1 / L['p_jackpot'])}. Тираж в пятницу 6.11 в 18:00, приём ставок до 17:45 в день тиража.")
ev3_note = "Три непересекающихся билета из 18 лучших чисел формулы. Они покрывают столько же комбинаций, сколько лучшие 3 поля оптимизатора: 29,9 % шанса хоть на какой-то выигрыш. Приём ставок до 17:45, тираж в 18:00."

sources = [
    'Архивы тиражей: tipos.sk, эндпоинты <span class="mono">GetZrebovania</span> и <span class="mono">GetForDate</span> для каждой игры (Loto и Loto 5 z 35 с 2018 года, Euromilióny с 2020, Eurojackpot с 25.03.2022 в формате 5/50 + 2/12, Všetko alebo nič с 01.01.2026).',
    'Правила Joker, Loto 5 z 35 и остальных игр: <a href="https://www.tipos.sk/loterie/ciselne-loterie/informacie-k-loteriam/herny-plan">Herný plán číselných lotérií</a>, статья 24 (Joker), и страницы «Všetko o číselnej lotérii» каждой игры.',
    'Текущие джекпоты: страницы <a href="https://www.tipos.sk/loterie/loto">Loto</a>, <a href="https://www.tipos.sk/loterie/loto-5-z-35">Loto 5 z 35</a>, <a href="https://www.tipos.sk/loterie/eurojackpot">Eurojackpot</a>, <a href="https://www.tipos.sk/loterie/euromiliony">Euromilióny</a>, <a href="https://www.tipos.sk/loterie/vsetko-alebo-nic">Všetko alebo nič</a>.',
    'Премия Extra výplata в октябре 2026 (удвоенные призы 3–8 уровня) закончилась 29.10.2026 и на тираж 5.11 не действует.',
]

data = {'lede': lede, 'verdict': verdict, 'my': {'numbers': my_nums, 'draw': 'пт 6.11, 18:00', 'cost': 1.20, 'note': my_note},
        'ev3': ev3, 'ev3_note': ev3_note, 'copy_text': copy_text, 'cmp': rows, 'cmp_note': cmp_note,
        'jseries': J['jackpot_series'], 'joker': J, 'jfacts': jfacts, 'jwins': wins, 'text': text, 'games': games,
        'honest': honest, 'prompt': PROMPT, 'sources': sources}
data['joker'] = {k: v for k, v in J.items() if k not in ('ev_series', 'jackpot_series')}
head = '<title>Все лотереи TIPOS</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700&family=Onest:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap">\n'
extra_css = '<style>.slip.one{grid-template-columns:minmax(0,1fr);max-width:420px}.facts{grid-template-columns:repeat(auto-fit,minmax(160px,1fr))}</style>\n'
html = head + css + '\n' + extra_css + body.replace('/*DATA*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
open(OUT, 'w', encoding='utf-8').write(html)
print('built', OUT, 'best signal', best, 'tests', nt)
