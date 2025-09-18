from alpespartners.config.db import db
from sqlalchemy import text


class PayoutRepositorioSQLAlchemy:
    def __init__(self):
        self._session = db.session

    def obtener_por_id(self, payout_id: str):
        r = self._session.execute(text("SELECT id, partner_id, cycle_id, monto_total FROM payouts WHERE id = :id"), {"id": payout_id}).fetchone()
        if not r:
            return None
        return {"id": r[0], "partner_id": r[1], "cycle_id": r[2], "monto_total": r[3]}
