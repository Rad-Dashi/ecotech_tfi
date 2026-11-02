import json
import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RUTA_CATALOGO_JSON = BASE_DIR / "catalogo_ecotech.json"


# --- PASO 2.1: Excepción Personalizada ---
class StockInvalidoError(Exception):
    """Excepción lanzada cuando se intenta asignar un stock negativo."""
    def __init__(self, mensaje="El stock no puede ser un valor negativo."):
        super().__init__(mensaje)


# --- PASO 2.2: Clase Base del Catálogo ---
class DispositivoEcologico:
    """Representa un producto sustentable base con validación de stock."""
    def __init__(self, id_producto, nombre, precio, stock):
        self.id_producto = id_producto.strip()
        self.nombre = nombre.strip()
        self.precio = float(precio)
        self._stock = 0
        # Invocamos al setter público para validar desde la creación
        self.stock = int(stock)

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, valor):
        if int(valor) < 0:
            raise StockInvalidoError(
                f"Operación rechazada para '{self.nombre}': El stock no puede ser negativo ({valor})."
            )
        self._stock = int(valor)

    def generar_ficha_tecnica(self):
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "precio": f"${self.precio:.2f}",
            "stock": self.stock,
            "tipo": "Dispositivo Estándar"
        }


# --- PASO 2.3: Subclase Especializada ---
class PanelSolar(DispositivoEcologico):
    """Subclase que extiende DispositivoEcologico con potencia y eficiencia."""
    def __init__(self, id_producto, nombre, precio, stock, eficiencia, potencia_w):
        super().__init__(id_producto, nombre, precio, stock)
        self.eficiencia = float(eficiencia)
        self.potencia_w = float(potencia_w)

    def generar_ficha_tecnica(self):
        ficha_base = super().generar_ficha_tecnica()
        ficha_base.update({
            "tipo": "Panel Solar Fotovoltaico",
            "potencia_w": f"{self.potencia_w}W",
            "eficiencia": f"{self.eficiencia}%"
        })
        return ficha_base


# --- PUNTO 2.B: Persistencia y Gestión del Catálogo (CRUD) ---
class GestorInventario:
    """Gestiona la lectura y escritura del catálogo en catalogo_ecotech.json."""

    def guardar_catalogo_json(self, lista_dispositivos, ruta_archivo=RUTA_CATALOGO_JSON):
        """
        Recibe objetos (o diccionarios ya generados) y los guarda en el JSON.
        """
        datos_serializables = []
        for item in lista_dispositivos:
            # Si es un objeto de nuestras clases, llamamos a generar_ficha_tecnica()
            if hasattr(item, "generar_ficha_tecnica"):
                datos_serializables.append(item.generar_ficha_tecnica())
            else:
                datos_serializables.append(item)

        with open(ruta_archivo, mode="w", encoding="utf-8") as archivo:
            json.dump(datos_serializables, archivo, indent=4, ensure_ascii=False)

    def leer_catalogo_json(self, ruta_archivo=RUTA_CATALOGO_JSON):
        """Lee los productos del archivo JSON o crea un catálogo inicial si no existe."""
        if not os.path.exists(ruta_archivo):
            panel_inicial = PanelSolar("PS-100", "Panel Solar EcoMax", 250.5, 15, 22.5, 450)
            bateria_inicial = DispositivoEcologico("BAT-01", "Batería Reciclable", 180.0, 8)
            self.guardar_catalogo_json([panel_inicial, bateria_inicial], ruta_archivo)

        with open(ruta_archivo, mode="r", encoding="utf-8") as archivo:
            return json.load(archivo)

###################################################################################################
# BLOQUE DE EJECUCIÓN: prueba final solicitada en consola
###################################################################################################

if __name__ == "__main__":
    panel = PanelSolar("PS-100", "Panel Solar EcoMax", 250.5, 15, 22.5, 450)
    bateria = DispositivoEcologico("BAT-01", "Batería Reciclable", 180.0, 8)
    print(panel.generar_ficha_tecnica())

    try:
        panel.stock = -5
    except StockInvalidoError as error:
        print(f"Advertencia controlada: {error}")

    GestorInventario().guardar_catalogo_json([panel, bateria], BASE_DIR / "catalogo_demo.json")
    print("Catálogo exportado correctamente.")
