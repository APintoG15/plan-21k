import json, sys, os
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
plan = json.load(open(os.path.join(root, 'plan.json')))
t = open(os.path.join(here, 'template.html')).read()
out = t.replace('/*PLAN_JSON*/[]', json.dumps(plan, ensure_ascii=False, separators=(',', ':')))

open(os.path.join(root, 'index.html'), 'w').write(out)
print('index.html', len(out), 'bytes')
