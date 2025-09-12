import time
from flask import Blueprint, jsonify, g

metrics_bp = Blueprint("metrics", __name__)

# Contadores a nivel de módulo
_count = 0
_errors = 0
_lat = []  # latencias en ms (simple para el parcial)

def _pct(arr, p):
    if not arr:
        return None
    s = sorted(arr)
    i = int(len(s) * p)
    i = max(0, min(i, len(s) - 1))
    return s[i]

@metrics_bp.get("/metrics")
def metrics():
    # Copiar para evitar condiciones de carrera
    a = list(_lat)
    return jsonify({
        "count": _count,
        "errors": _errors,
        "p50": _pct(a, 0.50),
        "p95": _pct(a, 0.95),
        "p99": _pct(a, 0.99),
    })

def register_metrics(app):
    @app.before_request
    def _start_timer():
        g._t0 = time.perf_counter()

    @app.after_request
    def _record_metrics(resp):
        # ⬇⬇⬇ el fix está aquí
        global _count, _errors
        try:
            _count += 1
            dt_ms = (time.perf_counter() - getattr(g, "_t0", time.perf_counter())) * 1000.0
            _lat.append(dt_ms)
            # (Opcional) limitar tamaño para no crecer sin fin:
            if len(_lat) > 5000:
                del _lat[:len(_lat)-5000]
            if resp.status_code >= 500:
                _errors += 1
        except Exception:
            _errors += 1
        return resp
