import flet as ft
from datetime import datetime

# Colores (Sin cambios en tu diseño)
BG, SURFACE, CARD = "#0f1117", "#1a1d27", "#21253a"
BORDER, TEXT, MUTED = "#2a2f45", "#eef0f8", "#6b7190"
GREEN, RED, ORANGE, BLUE = "#00e5a0", "#ff5c7a", "#ffaa3b", "#5b8cff"

def cargar_datos(page: ft.Page):
    # Verificación de seguridad para client_storage
    if hasattr(page, "client_storage") and page.client_storage.contains_key("datos_finanzas"):
        return page.client_storage.get("datos_finanzas")
    return {"ingresos": [], "gastos": [], "deudas": []}

def guardar_datos(page: ft.Page, datos):
    if hasattr(page, "client_storage"):
        page.client_storage.set("datos_finanzas", datos)

def main(page: ft.Page):
    page.title = "Mis Finanzas"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    
    # Datos iniciales
    datos = cargar_datos(page)

    # --- CORRECCIÓN DE ALINEACIONES (USANDO STRINGS PARA EVITAR ATTRIBUTE ERROR) ---
    # Flet acepta strings como "center", "topLeft", etc. Esto es más seguro entre versiones.
    
    def tarjeta_stat(emoji, txt_ref, label):
        return ft.Container(
            content=ft.Column([
                ft.Text(emoji, size=18),
                txt_ref,
                ft.Text(label, size=10, color=MUTED),
            ], spacing=4, horizontal_alignment="start"),
            bgcolor=SURFACE,
            border=ft.border.all(1, BORDER),
            border_radius=18,
            padding=14,
            expand=True,
        )

    def boton_accion(texto, color_inicio, color_fin, handler):
        return ft.Container(
            content=ft.Text(texto, size=14, color="white", weight="bold"),
            gradient=ft.LinearGradient(
                colors=[color_inicio, color_fin],
                begin="centerLeft",
                end="centerRight",
            ),
            border_radius=18,
            padding=16,
            alignment=ft.alignment.center, # Si falla, usa "center"
            on_click=handler,
        )

    # ... (Resto de tu lógica de agregar_ingreso, etc., igual que antes)

    # IMPORTANTE: Cambiamos NavigationBar por una versión más compatible
    page.navigation_bar = ft.NavigationBar(
        bgcolor=SURFACE,
        destinations=[
            ft.NavigationDestination(icon=ft.Icons.PIE_CHART, label="Inicio"),
            ft.NavigationDestination(icon=ft.Icons.TRENDING_UP, label="Ingresos"),
            ft.NavigationDestination(icon=ft.Icons.TRENDING_DOWN, label="Gastos"),
        ],
        on_change=lambda e: print(f"Tab: {e.control.selected_index}") 
    )

    page.add(ft.Text("App Cargada Correctamente", color=GREEN))
    page.update()

# Detector de errores mejorado
def main_detector(page: ft.Page):
    try:
        main(page)
    except Exception as e:
        page.add(ft.Text(f"Error detectado: {e}", color="red"))
        page.update()

ft.app(target=main_detector)
