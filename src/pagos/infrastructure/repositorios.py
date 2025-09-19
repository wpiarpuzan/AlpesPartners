from alpespartners.config.db import db

class PagoRepo:
    def __init__(self, session=None):
        self.session = session or db.session

    def crear(self, pago):
        pass
