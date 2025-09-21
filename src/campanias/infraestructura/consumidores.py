def suscribirse_a_eventos_pagos():
    """Proxy to the real consumer implementation.

    Some code paths import `campanias.infraestructura.consumidores` (Spanish) while the
    canonical implementation lives under `campanias.infrastructure.consumidores`.
    This proxy ensures older imports still start the real consumer.
    """
    try:
        from campanias.infrastructure.consumidores import suscribirse_a_eventos_pagos as real_fn
    except Exception as e:
        print('[campanias/infraestructura/consumidores] Could not import real consumer:', e)
        raise
    return real_fn()


def start_consumers():
    # Backwards-compatible entrypoint used by some launchers.
    print('Starting campanias consumers (proxy)')
    try:
        suscribirse_a_eventos_pagos()
    except Exception:
        import traceback
        traceback.print_exc()
