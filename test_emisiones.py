import pytest
from sustentabilidad.logica_emisiones import (
    calcular_emisiones_carbono,
    obtener_metricas_consumo,
)


class TestCalculoEmisiones:
    def test_valores_nominales(self):
        assert calcular_emisiones_carbono(100) == 40.0
        assert calcular_emisiones_carbono(0) == 0.0
        assert calcular_emisiones_carbono(250, factor_emision=0.5) == 125.0

    def test_consumo_negativo(self):
        with pytest.raises(ValueError):
            calcular_emisiones_carbono(-10)


class TestMetricasConsumo:
    def test_total_y_planta_mayor(self):
        registros = [
            {"planta": "Planta Norte", "consumo_kwh": 100},
            {"planta": "Planta Sur", "consumo_kwh": 400},
        ]
        resumen = obtener_metricas_consumo(registros)
        assert resumen["total_emisiones"] == 200.0
        assert resumen["planta_mayor_consumo"] == "Planta Sur"

    def test_lista_vacia(self):
        resumen = obtener_metricas_consumo([])
        assert resumen == {"total_emisiones": 0.0, "planta_mayor_consumo": "Ninguna"}

    def test_consumo_negativo_en_historial(self):
        with pytest.raises(ValueError):
            obtener_metricas_consumo([{"planta": "Planta X", "consumo_kwh": -5}])