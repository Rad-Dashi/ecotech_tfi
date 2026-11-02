from django.urls import path
from . import views

urlpatterns = [
    # Pestaña 1 (Página de inicio): Ejercicio 1 - Sensores
    path('', views.vista_sensores, name='vista_sensores'),
    # Pestaña 2: Ejercicio 2 - Catálogo e Inventario
    path('catalogo/', views.vista_catalogo, name='vista_catalogo'),
    # Pestaña 3: Ejercicio 3 - Panel de Sustentabilidad y Emisiones
    path('sustentabilidad/', views.vista_panel_sustentabilidad, name='vista_panel_sustentabilidad'),
]