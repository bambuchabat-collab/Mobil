"""Render the all-lotteries page.
Usage: python3 -I build2.py multi.json tickets.json style.css body.html prompt.txt out.html
"""
import json, sys, math
R = json.load(open(sys.argv[1])); TK = json.load(open(sys.argv[2]))
css = open(sys.argv[3], encoding='utf-8').read(); body = open(sys.argv[4], encoding='utf-8').read()
PROMPT = open(sys.argv[5], encoding='utf-8').read().strip(); OUT = sys.argv[6]
RS = json.load(open(sys.argv[7])); FT = json.load(open(sys.argv[8])); JP = json.load(open(sys.argv[9]))

def f(x, d=0):
    return f'{x:,.{d}f}'.replace(',', ' ').replace('.', ',')
def dmy(s): return f'{s[8:10]}.{s[5:7]}.{s[0:4]}'
def pc(x, d=0): return f(100 * x, d) + ' %'

J = R['joker']; L = R['loto535']; B = R['bundle']; LO = R['loto']; V = R['van']; X = R['extra']
EM = R.get('euromiliony'); EJ = R.get('eurojackpot')

rank = [r['n'] for r in TK['formula']['ranking']]
ev3 = [{'main': t['main'], 'pb': t['pb'], 'label': f"популярность {f(100 * r)} %"} for t, r in zip(FT['extra']['tickets'], FT['extra']['rel_popularity'])]
my_fields = FT['loto535']['fields']
my_nums = my_fields[0]

copy_text = '\n'.join([f"Extra výplata 5.11, билет {i + 1}: {' '.join(map(str, t['main']))} + {t['pb']}" for i, t in enumerate(ev3)]
                      + [f"Loto 5 z 35 на 6.11, билет {i + 1}: {' '.join(map(str, t))} + JOKER: ÁNO" for i, t in enumerate(my_fields)])

verdict = [
    f"<b>Лазейка есть, но не в угадывании чисел.</b> Это накопившийся джекпот <b>JOKER</b> (добавка к Loto и Loto 5 z 35 за 0,60 €). Шанс угадать 6 цифр всегда 1 к 1 000 000, а джекпот дорос до {f(J['jackpot_carry'])} € и к пятничному тиражу будет около {f(J['pot_next_est'], 0)} €. При таком джекпоте ставка 0,60 € в среднем возвращает {f(J['ev'], 2)} €, то есть {pc(J['ev_ratio'])}. Во всех остальных играх TIPOS возврат 40–58 %.",
    f"<b>Завтра, Loto 5 z 35: 5 отдельных билетов по одному полю, в каждом JOKER</b>, всего 6 €: {'; '.join(' '.join(map(str, t)) for t in my_fields)}. В среднем такой набор возвращает около {f(5 * B['ev'], 2)} € из 6 €.",
    f"<b>Extra výplata сегодня, 3 билета:</b> {'; '.join(' '.join(map(str, t['main'])) + ' + ' + str(t['pb']) for t in ev3)}. Шанс на главный приз у любого билета одинаковый, 1 к 2 072 070. Эти числа реже выбирают другие игроки, поэтому при выигрыше делиться придётся с меньшим числом людей.",
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
my_note = (f"Поля не пересекаются и собраны из 25 наименее популярных чисел; 10 самых любимых игроками ({', '.join(map(str, FT['loto535']['dropped_popular']))}) не используются. "
           f"Шанс хоть на какой-то выигрыш в Loto 5 z 35 у пяти полей {pc(FT['loto535']['cover_any_prize'], 1)}, это максимум для 5 полей. Номера Joker выбрать нельзя. "
           f"Шанс джекпота Joker при 5 билетах 1 к 200 000. Каждый билет оформляется отдельно, приём ставок до 17:45 в день тиража.")
ev3_note = (f"Три непересекающихся билета: 29,9 % шанса хоть на какой-то выигрыш, это максимум для трёх полей. Из 27 чисел убраны 9 самых популярных у игроков ({', '.join(map(str, FT['extra']['dropped_popular']))}). "
            f"Доп. числа 7, 6 и 5 игроки выбирают примерно на 12 % реже среднего, а 3 на 18 % чаще. «Популярность» у билета: сколько соседей по выигрышу ожидается относительно среднего билета (100 %). Приём ставок до 17:45, тираж в 18:00.")

sources = [
    'Архивы тиражей: tipos.sk, эндпоинты <span class="mono">GetZrebovania</span> и <span class="mono">GetForDate</span> для каждой игры (Loto и Loto 5 z 35 с 2018 года, Euromilióny с 2020, Eurojackpot с 25.03.2022 в формате 5/50 + 2/12, Všetko alebo nič с 01.01.2026).',
    'Правила Joker, Loto 5 z 35 и остальных игр: <a href="https://www.tipos.sk/loterie/ciselne-loterie/informacie-k-loteriam/herny-plan">Herný plán číselných lotérií</a>, статья 24 (Joker), и страницы «Všetko o číselnej lotérii» каждой игры.',
    'Текущие джекпоты: страницы <a href="https://www.tipos.sk/loterie/loto">Loto</a>, <a href="https://www.tipos.sk/loterie/loto-5-z-35">Loto 5 z 35</a>, <a href="https://www.tipos.sk/loterie/eurojackpot">Eurojackpot</a>, <a href="https://www.tipos.sk/loterie/euromiliony">Euromilióny</a>, <a href="https://www.tipos.sk/loterie/vsetko-alebo-nic">Všetko alebo nič</a>.',
    'Премия Extra výplata в октябре 2026 (удвоенные призы 3–8 уровня) закончилась 29.10.2026 и на тираж 5.11 не действует.',
]

ml = RS['ml']; pl = RS['pop_loto535']
research = {
 'text': (f"Я проверил то, что предлагают исследования и «системы». Машинное обучение: логистическая регрессия на 8 признаках истории (частоты за 4 окна, пропуск, прошлые 2 тиража, пары), обучение только на прошлом. "
          f"В Extra výplata она угадывала {f(ml['extra_vyplata']['mean_hits'], 3)} числа против {f(ml['extra_vyplata']['random_mean'], 3)} у случая, в Loto 5 z 35 {f(ml['loto535']['mean_hits'], 3)} против {f(ml['loto535']['random_mean'], 3)} ({f(ml['loto535']['draws_tested'])} тиражей). "
          f"Работает другое: популярность чисел у игроков. По числу победителей в 1 008 тиражах Loto 5 z 35 видно, какие числа ставят чаще. Модель подтвердилась на новых тиражах (p < 0,003) и совпадает в двух половинах истории (корреляция {f(pl['half_corr'], 2)}). "
          f"Любимые числа словацких игроков: {', '.join(map(str, FT['loto535']['most_popular'][:7]))}. Нелюбимые: {', '.join(map(str, FT['loto535']['least_popular'][:7]))}. Это совпадает с исследованиями Ziemba (1986) и Baker и McHale (2009)."),
 'rows': [['Частоты, «горячие» и «холодные» числа', 'не меняет', 'не меняет', 'no'],
          ['Машинное обучение по истории тиражей', 'не меняет', 'не меняет', 'no'],
          ['Поиск перекоса шаров или генератора', 'перекоса нет ни в одной игре', 'не меняет', 'no'],
          ['Поля без пересечений (покрытие)', 'максимум шанса на мелкий приз', 'не меняет', 'yes'],
          ['Непопулярные числа', 'не меняет', 'меньше соседей по выигрышу', 'yes'],
          ['Игра с плюсом в ожидании (Joker)', 'не меняет', 'средний возврат выше ставки', 'yes']]}
data = {'research': research, 'lede': lede, 'verdict': verdict, 'my': {'numbers': my_nums, 'fields': my_fields, 'draw': 'пт 6.11, 18:00', 'cost': 6.0, 'note': my_note},
        'ev3': ev3, 'ev3_note': ev3_note, 'copy_text': copy_text, 'cmp': rows, 'cmp_note': cmp_note,
        'jseries': J['jackpot_series'], 'joker': J, 'jfacts': jfacts, 'jwins': wins, 'text': text, 'games': games,
        'honest': honest, 'prompt': PROMPT, 'sources': sources}
data['joker'] = {k: v for k, v in J.items() if k not in ('ev_series', 'jackpot_series')}
head = '<title>Все лотереи TIPOS</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700&family=Onest:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap">\n'
extra_css = '<style>.slip.one{grid-template-columns:minmax(0,1fr);max-width:420px}.facts{grid-template-columns:repeat(auto-fit,minmax(160px,1fr))}#tb-rs td{white-space:normal;min-width:110px}</style>\n'
html = head + css + '\n' + extra_css + body.replace('/*DATA*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
open(OUT, 'w', encoding='utf-8').write(html)
print('built', OUT, 'best signal', best, 'tests', nt)
