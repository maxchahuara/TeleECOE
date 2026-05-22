#!/usr/bin/env python3
"""Crea una estacion 5 sin camara y desactiva la RCP con camara.

Es idempotente: conserva la estacion historica rcp y clona su rubrica a
rcp_sin_camara solo si todavia no existe.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))
os.environ.setdefault("DATABASE_URL", "sqlite:///" + str(PROJECT_DIR / "evaluaciones.db"))
os.environ.setdefault("SECRET_KEY", "teleecoe-local-dev-change-me")

from app import create_app
from app.models.models import Categoria, Criterio, Estacion
from extensions import db


SOURCE_ID = "rcp"
TARGET_ID = "rcp_sin_camara"


def clone_station_questions(source: Estacion, target: Estacion) -> None:
    for source_category in sorted(source.categorias, key=lambda item: (item.orden or 0, item.id)):
        target_category = Categoria(
            estacion_id=target.id,
            nombre=source_category.nombre,
            orden=source_category.orden,
            tipo=source_category.tipo,
        )
        db.session.add(target_category)
        db.session.flush()

        for source_criterion in sorted(source_category.criterios, key=lambda item: item.id):
            db.session.add(Criterio(
                id=f"{TARGET_ID}_{source_criterion.id}",
                categoria_id=target_category.id,
                texto=source_criterion.texto,
                puntos=source_criterion.puntos,
                tipo=source_criterion.tipo,
                opciones=source_criterion.opciones,
            ))


def main() -> None:
    app = create_app()
    with app.app_context():
        source = db.session.get(Estacion, SOURCE_ID)
        if not source:
            raise SystemExit("source_station_missing=rcp")

        target = db.session.get(Estacion, TARGET_ID)
        created = False
        if not target:
            target = Estacion(
                id=TARGET_ID,
                nombre="Estación 5: RCP sin cámara",
                orden=5,
                activa=True,
            )
            db.session.add(target)
            db.session.flush()
            clone_station_questions(source, target)
            created = True
        else:
            target.nombre = "Estación 5: RCP sin cámara"
            target.orden = 5
            target.activa = True

        source.activa = False
        source.orden = 5
        db.session.commit()

        categories = Categoria.query.filter_by(estacion_id=target.id).count()
        criteria = (
            Criterio.query
            .join(Categoria)
            .filter(Categoria.estacion_id == target.id)
            .count()
        )
        print(f"created={created}")
        print(f"source_active={source.esta_activa}")
        print(f"target_active={target.esta_activa}")
        print(f"target_categories={categories}")
        print(f"target_criteria={criteria}")


if __name__ == "__main__":
    main()
