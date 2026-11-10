"""Lee los .FIT de entrenamientos del plan y genera plan.json para la web app."""
import sys, json, glob, os, re
from fit_tool.fit_file import FitFile

def read_fit(path):
    f = FitFile.from_file(path); wk = None; steps = []
    for r in f.records:
        m = r.message; n = getattr(m, 'NAME', None)
        if n not in ('workout', 'workout_step'): continue
        d = {fl.name: fl.get_value() for fl in m.fields if fl.is_valid()}
        if n == 'workout': wk = d
        else: steps.append(d)
    return wk, sorted(steps, key=lambda s: s['message_index'])

def pace(mms):  # mm/s -> s/km
    return round(1_000_000 / mms) if mms else None

def to_nodes(steps):
    nodes = []
    for s in steps:
        dt = s.get('duration_type')
        if dt == 6:  # repeat
            start = s['duration_value']; n = s.get('target_value', 1)
            inner = [x for x in nodes if x['idx'] >= start]
            nodes = [x for x in nodes if x['idx'] < start]
            nodes.append({'idx': start, 'kind': 'repeat', 'times': n, 'steps': inner})
        elif dt == 0:  # time
            nodes.append({'idx': s['message_index'], 'kind': 'rest', 'sec': s['duration_value'] // 1000})
        else:
            inten = {0: 'active', 1: 'rest', 2: 'warmup', 3: 'cooldown'}.get(s.get('intensity', 0), 'active')
            lo, hi = s.get('custom_target_value_low'), s.get('custom_target_value_high')
            nodes.append({'idx': s['message_index'], 'kind': inten, 'm': s['duration_value'] // 100,
                          'fast': pace(hi), 'slow': pace(lo), 'note': s.get('notes', '')})
    return nodes

def clean(n):
    n.pop('idx', None)
    if n['kind'] == 'repeat': [clean(x) for x in n['steps']]
    return n

TYPES = [('CARRERA', 'race'), ('Intervalos', 'intervals'), ('Tempo', 'tempo'),
         ('Ritmo Carrera', 'racepace'), ('Easy', 'easy'), ('Fondo', 'long')]

def main(dirs, out):
    files = []
    for d in dirs: files += glob.glob(os.path.join(d, '**', '*.fit'), recursive=True)
    by_key = {}
    for p in sorted(files):
        wk, steps = read_fit(p)
        name = wk['wkt_name']
        m = re.match(r'S(\d+) (\w+) (\d+)/(\d+) (.*) \(([\d.]+)km\)', name)
        week, day, dd, mm, title, km = m.groups()
        typ = next(t for k, t in TYPES if title.startswith(k))
        key = f"2026-{int(mm):02d}-{int(dd):02d}"
        by_key[key] = {'date': key, 'week': int(week), 'day': day, 'title': title,
                       'type': typ, 'km': float(km),
                       'blocks': [clean(n) for n in to_nodes(steps)],
                       'file': os.path.basename(p)}
    plan = sorted(by_key.values(), key=lambda w: w['date'])
    json.dump(plan, open(out, 'w'), ensure_ascii=False, indent=1)
    print(len(plan), 'entrenamientos ->', out)

if __name__ == '__main__':
    main(sys.argv[2:], sys.argv[1])
