import flet as ft
from datetime import datetime

# Colores seguros en Hexadecimal
BG, SURFACE = "#0f1117", "#1a1d27"
TEXT, MUTED = "#eef0f8", "#6b7190"
GREEN, RED, BLUE = "#00e5a0", "#ff5c7a", "#5b8cff"

def main(page: ft.Page):
    page.title = "Mis Finanzas"
    page.bgcolor = BG
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # Evita el error: 'Page' object has no attribute 'client_storage'
    def cargar_datos():
        try:
            if hasattr(page, "client_storage") and page.client_storage.contains_key("finanzas_v1"):
                return page.client_storage.get("finanzas_v1")
        except: pass
        return {"ingresos": [], "gastos": []}

    datos = cargar_datos()

    def guardar():
        try:
            page.client_storage.set("finanzas_v1", datos)
        except: pass
        actualizar_interfaz()

    # --- UI Elements ---
    txt_balance = ft.Text("$0.00", size=34, weight="bold", color=GREEN)
    lista_recientes = ft.ListView(expand=True, spacing=10)

    def actualizar_interfaz():
        t_ing = sum(float(i["m"]) for i in datos["ingresos"])
        t_gas = sum(float(g["m"]) for g in datos["gastos"])
        txt_balance.value = f"${(t_ing - t_gas):,.2f}"
        
        lista_recientes.controls.clear()
        for g in datos["gastos"][-5:]:
            lista_recientes.controls.append(
                ft.ListTile(title=ft.Text(g["c"]), trailing=ft.Text(f"-${g['m']}", color=RED))
            )
        page.update()

    # --- Vistas ---
    # Corregido: ft.Icons.EDIT_NOTE en lugar de DESCRIPTION
    in_nom = ft.TextField(label="Descripción", border_radius=12, prefix_icon=ft.Icons.EDIT_NOTE)
    in_mon = ft.TextField(label="Monto", keyboard_type="number", border_radius=12)
    
    # Corregido: Sin prefix_icon (causa error en Dropdown)
    drop_cat = ft.Dropdown(
        label="Categoría",
        options=[ft.dropdown.Option("Comida"), ft.dropdown.Option("Varios")],
        border_radius=12
    )

    def agregar_gasto(e):
        if in_nom.value and in_mon.value:
            datos["gastos"].append({"c": in_nom.value, "m": in_mon.value, "f": "Hoy"})
            in_nom.value = ""; in_mon.value = ""; guardar()

    # --- Estructura de Tabs (Corregido 'label' y alineaciones) ---
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                label="Inicio", # NO 'text'
                icon=ft.Icons.HOME,
                content=ft.Column([
                    ft.Container(
                        content=txt_balance,
                        padding=30,
                        alignment=ft.alignment.center # Alineación segura
                    ),
                    ft.Text("RECIENTES", size=12, weight="bold", color=MUTED),
                    lista_recientes
                ], expand=True)
            ),
            ft.Tab(
                label="Añadir",
                icon=ft.Icons.ADD_CIRCLE,
                content=ft.Column([
                    in_nom, in_mon, drop_cat,
                    ft.ElevatedButton("Guardar", on_click=agregar_gasto, bgcolor=BLUE, color="white")
                ], padding=20, spacing=15)
            )
        ], expand=True
    )

    page.add(ft.Container(content=tabs, expand=True, padding=10))
    actualizar_interfaz()

ft.app(target=main)
