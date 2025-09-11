from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

class TocinoBase(ABC):
    @abstractmethod
    def satisface(self, obj: Any) -> bool:
        raise NotImplementedError()

    def __call__(self, obj: Any) -> bool:
        return self.satisface(obj)

    def __and__(self, otro: "TocinoBase") -> "And":
        return And(self, otro)

    def __or__(self, otro: "TocinoBase") -> "Or":
        return Or(self, otro)

    def __neg__(self) -> "TocinoBase":
        return Not(self)

@dataclass(frozen=True)
class And(TocinoBase):
    primero: TocinoBase
    segundo: TocinoBase

    def satisface(self, obj: Any) -> bool:
        return self.primero.satisface(obj) and self.segundo.satisface(obj)

@dataclass(frozen=True)
class Or(TocinoBase):
    primero: TocinoBase
    segundo: TocinoBase

    def satisface(self, obj: Any) -> bool:
        return self.primero.satisface(obj) or self.segundo.satisface(obj)

@dataclass(frozen=True)
class Not(TocinoBase):
    sujeto: TocinoBase

    def satisface(self, obj: Any) -> bool:
        return not self.sujeto.satisface(obj)

# --- APP FACTORY (añadir al final de __init__.py) ---
from flask import Flask

def create_app() -> Flask:
    app = Flask(__name__)

    # Observabilidad
    from .observabilidad.metrics import metrics_bp, register_metrics
    register_metrics(app)
    app.register_blueprint(metrics_bp)

    # (Opcional) registra aquí tus blueprints de negocio
    # from .api.campanias import bp as campanias_bp
    # app.register_blueprint(campanias_bp, url_prefix="/campanias")

    # Health simple (útil para compose)
    @app.get("/health")
    def _health():
        return {"status": "ok"}

    return app
