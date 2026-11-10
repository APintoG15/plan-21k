# Plan 21K · 12 dic 2026

Web app para ver el plan de la media maratón desde el iPhone (GitHub Pages).

- `index.html`: la app (generada).
- `fit/`: los mismos .FIT de entrenamientos que se cargan en `GARMIN/NewFiles` del reloj.
- `plan.json`: el plan leído de esos .FIT.
- `tools/`: `fit2plan.py` (FIT → plan.json) y `build.py` (plan.json → index.html).

Actualizar: `python3 tools/fit2plan.py plan.json fit && python3 tools/build.py`
