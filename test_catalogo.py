import json
import pytest
from sustentabilidad.logica_catalogo import (
    StockInvalidoError,
    DispositivoEcologico,
    PanelSolar,
    GestorInventario,
)


def test_stock_negativo_en_constructor():
    with pytest.raises(StockInvalidoError):
        DispositivoEcologico("BAT-01", "Batería", 180.0, -3)


def test_stock_negativo_en_setter_no_cambia_el_valor():
    panel = PanelSolar("PS-100", "Panel Solar EcoMax", 250.5, 15, 22.5, 450)
    with pytest.raises(StockInvalidoError):
        panel.stock = -5
    assert panel.stock == 15


def test_stock_cero_es_valido():
    assert DispositivoEcologico("BAT-01", "Batería", 180.0, 0).stock == 0


def test_ficha_dispositivo_estandar():
    ficha = DispositivoEcologico("BAT-01", "Batería", 180.0, 8).generar_ficha_tecnica()
    assert ficha["precio"] == "$180.00"
    assert ficha["tipo"] == "Dispositivo Estándar"


def test_ficha_panel_solar_polimorfica():
    ficha = PanelSolar("PS-100", "Panel Solar EcoMax", 250.5, 15, 22.5, 450).generar_ficha_tecnica()
    assert ficha["tipo"] == "Panel Solar Fotovoltaico"
    assert ficha["potencia_w"] == "450.0W"
    assert ficha["eficiencia"] == "22.5%"


def test_guardar_catalogo_json(tmp_path):
    ruta = tmp_path / "catalogo_prueba.json"
    panel = PanelSolar("PS-100", "Panel Solar EcoMax", 250.5, 15, 22.5, 450)
    GestorInventario().guardar_catalogo_json([panel], str(ruta))
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert len(datos) == 1
    assert datos[0]["id_producto"] == "PS-100"