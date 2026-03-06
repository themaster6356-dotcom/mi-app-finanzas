import flet as ft
from datetime import datetime

# Paleta de colores en Hexadecimal (esto nunca falla)
BG = "#0f1117"
SURFACE = "#1a1d27"
BORDER = "#2a2f45"
TEXT = "#eef0f8"
MUTED = "#6b7190"
GREEN = "#00e5a0"
RED = "#ff5c7a"
ORANGE = "#ffaa3b"
BLUE = "#5b8cff"

def main(page: ft.Page):
    page.title = "Mis Finanzas"
    page.bgcolor = BG
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # Solución al error 'client_storage': Verificamos si existe antes de usarlo
    def cargar_datos():
        try:
            if hasattr(page, "client_storage") and page.client_storage.contains_key("finanzas_data"):
                return page.client_storage.get("finanzas_data")
        except:
            pass
        return {"ingresos": [], "gastos": [], "deudas": []}

    datos = cargar_datos()

    def guardar():
        try:
            page.client_storage.set("finanzas_data", datos)
        except:
            pass
        actualizar_ui()

    # --- ELEMENTOS UI ---
    txt_balance = ft.Text("$0.00", size=38, weight="bold", color=GREEN)
    txt_ing_card = ft.Text("$0.00", size=15, weight="bold", color=GREEN)
    txt_gas_card = ft.Text("$0.00", size=15, weight="bold", color=RED)
    
    lista_recientes = ft.ListView(expand=True, spacing=10)

    # --- FUNCIONES DE DISEÑO CORREGIDAS ---
    def tarjeta_stat(emoji, ref, label):
        return ft.Container(
            content=ft.Column([
                ft.Text(emoji, size=18),
                ref,
                ft.Text(label, size=10, color=MUTED),
            ], spacing=4),
            bgcolor=SURFACE, border=ft.border.all(1, BORDER),
            border_radius=18, padding=14, expand=True
        )

    def actualizar_ui():
        t_ing = sum(float(i["m"]) for i in datos["ingresos"])
        t_gas = sum(float(g["m"]) for g in datos["gastos"])
        txt_balance.value = f"${(t_ing - t_gas):,.2f}"
        txt_ing_card.value = f"${t_ing:,.2f}"
        txt_gas_card.value = f"${t_gas:,.2f}"
        
        lista_recientes.controls.clear()
        for g in datos["gastos"][-5:]:
            lista_recientes.controls.append(
                ft.ListTile(title=ft.Text(g["c"]), subtitle=ft.Text(g["f"]), trailing=ft.Text(f"-${g['m']}", color=RED))
            )
        page.update()

    # --- FORMULARIOS ---
    # Cambiamos ft.icons.DESCRIPTION por ft.Icons.EDIT_NOTE (Mayúsculas correctas)
    in_nom = ft.TextField(label="Descripción", border_radius=12, prefix_icon=ft.Icons.EDIT_NOTE)
    in_mon = ft.TextField(label="Monto", keyboard_type=ft.KeyboardType.NUMBER, border_radius=12)
    
    # Dropdown sin 'prefix_icon' (para evitar el TypeError de tu foto)
    drop_cat = ft.Dropdown(
        label="Categoría",
        options=[ft.dropdown.Option("Comida"), ft.dropdown.Option("Transporte"), ft.dropdown.Option("Otros")],
        border_radius=12
    )

    def click_guardar(e):
        if in_nom.value and in_mon.value:
            datos["gastos"].append({
                "c": in_nom.value, 
                "m": float(in_mon.value), 
                "f": datetime.now().strftime("%d/%m"),
                "cat": drop_cat.value
            })
            in_nom.value = ""; in_mon.value = ""
            guardar()

    # --- TABS (Corregido: 'label' en lugar de 'text') ---
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                label="Inicio", # 'label' es lo correcto, no 'text'
                icon=ft.Icons.HOME,
                content=ft.Column([
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column([ft.Text("BALANCE TOTAL", size=11, weight="bold"), txt_balance]),
                        gradient=ft.LinearGradient(["#1e3a5f", "#0f1e34"], begin=ft.alignment.top_left),
                        border_radius=25, padding=25
                    ),
                    ft.Row([
                        tarjeta_stat("💹", txt_ing_card, "Ingresos"),
                        tarjeta_stat("📉", txt_gas_card, "Gastos"),
                    ], spacing=10),
                    ft.Text("RECIENTES", size=12, weight="bold", color=MUTED),
                    lista_recientes
                ], expand=True, spacing=15)
            ),
            ft.Tab(
                label="Añadir",
                icon=ft.Icons.ADD_CIRCLE,
                content=ft.Column([
                    ft.Text("Nuevo Registro", size=20, weight="bold"),
                    in_nom, in_mon, drop_cat,
                    ft.ElevatedButton("Guardar", on_click=click_guardar, bgcolor=BLUE, color="white")
                ], padding=20, spacing=15)
            )
        ],
        expand=True
    )

    page.add(ft.Container(content=tabs, expand=True, padding=10))
    actualizar_ui()

ft.app(target=main)
