import flet as ft
from datetime import datetime

# Colores en Hexadecimal para evitar el error 'ft.colors'
BG, SURFACE, CARD = "#0f1117", "#1a1d27", "#21253a"
BORDER, TEXT, MUTED = "#2a2f45", "#eef0f8", "#6b7190"
GREEN, RED, ORANGE, BLUE = "#00e5a0", "#ff5c7a", "#ffaa3b", "#5b8cff"

def main(page: ft.Page):
    page.title = "Mis Finanzas"
    page.bgcolor = BG
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # Solución al error 'client_storage': Verificamos soporte
    def cargar_datos():
        try:
            if page.client_storage.contains_key("finanzas_v1"):
                return page.client_storage.get("finanzas_v1")
        except Exception: pass
        return {"ingresos": [], "gastos": [], "deudas": []}

    datos = cargar_datos()

    def guardar():
        page.client_storage.set("finanzas_v1", datos)
        actualizar_interfaz()

    # --- CATEGORÍAS ---
    categorias = ["🚌 Transporte", "🍛 Almuerzos", "🍔 Comida", "🍫 Antojos", "🛒 Super", "🎮 Ocio", "💸 Otros"]
    cat_seleccionada = {"valor": categorias[0]}

    # --- ELEMENTOS DE UI (Referencias) ---
    txt_balance = ft.Text("$0.00", size=38, weight="bold", color=GREEN)
    txt_ing_res = ft.Text("$0.00", size=15, weight="bold", color=GREEN)
    txt_gas_res = ft.Text("$0.00", size=15, weight="bold", color=RED)
    txt_deu_res = ft.Text("$0.00", size=15, weight="bold", color=ORANGE)
    
    lista_recientes = ft.ListView(expand=True, spacing=10)

    # --- COMPONENTES VISUALES ---
    def tarjeta_stat(emoji, txt_ref, label):
        return ft.Container(
            content=ft.Column([
                ft.Text(emoji, size=18),
                txt_ref,
                ft.Text(label, size=10, color=MUTED),
            ], spacing=4),
            bgcolor=SURFACE, border=ft.border.all(1, BORDER), border_radius=18, padding=14, expand=True
        )

    def item_lista(icono, titulo, subtitulo, monto, col_monto, col_bg):
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text(icono, size=18), bgcolor=col_bg, border_radius=12, width=40, height=40, alignment=ft.alignment.center),
                ft.Column([ft.Text(titulo, size=13, color=TEXT, weight="w500"), ft.Text(subtitulo, size=11, color=MUTED)], spacing=2, expand=True),
                ft.Text(monto, size=14, color=col_monto, weight="bold")
            ], spacing=12),
            bgcolor=SURFACE, border=ft.border.all(1, BORDER), border_radius=14, padding=12
        )

    # --- LÓGICA DE ACTUALIZACIÓN ---
    def actualizar_interfaz():
        t_ing = sum(float(i["m"]) for i in datos["ingresos"])
        t_gas = sum(float(g["m"]) for g in datos["gastos"])
        t_deu = sum(float(d["m"]) for d in datos["deudas"])
        
        txt_balance.value = f"${(t_ing - t_gas):,.2f}"
        txt_ing_res.value = f"${t_ing:,.2f}"
        txt_gas_res.value = f"${t_gas:,.2f}"
        txt_deu_res.value = f"${t_deu:,.2f}"
        
        lista_recientes.controls.clear()
        # Combinar registros para "Recientes"
        items = []
        for i in datos["ingresos"]: items.append(("💹", i["c"], i["f"], f"+${i['m']:,.2f}", GREEN, "rgba(0,229,160,0.1)"))
        for g in datos["gastos"]: items.append(("📉", g["cat"], g["f"], f"-${g['m']:,.2f}", RED, "rgba(255,92,122,0.1)"))
        
        for x in items[-5:]: # Mostrar últimos 5
            lista_recientes.controls.append(item_lista(*x))
        page.update()

    # --- VISTAS DE ENTRADA ---
    # Campos corregidos para evitar errores de iconos y tipos
    in_ing_nom = ft.TextField(label="Descripción", border_radius=15, border_color=BORDER, bgcolor=SURFACE)
    in_ing_mon = ft.TextField(label="Monto", keyboard_type="number", border_radius=15, border_color=BORDER, bgcolor=SURFACE)
    
    in_gas_mon = ft.TextField(label="Monto Gastado", keyboard_type="number", border_radius=15, border_color=BORDER, bgcolor=SURFACE)
    
    def agregar_ingreso(e):
        if in_ing_nom.value and in_ing_mon.value:
            datos["ingresos"].append({"f": datetime.now().strftime("%d/%m"), "c": in_ing_nom.value, "m": float(in_ing_mon.value)})
            in_ing_nom.value = ""; in_ing_mon.value = ""
            guardar()

    def agregar_gasto(e):
        if in_gas_mon.value:
            datos["gastos"].append({"f": datetime.now().strftime("%d/%m"), "cat": cat_sel_txt.value, "m": float(in_gas_mon.value)})
            in_gas_mon.value = ""
            guardar()

    # Dropdown corregido: Se quita 'prefix_icon' porque da error en Android
    cat_sel_txt = ft.Dropdown(
        label="Categoría",
        options=[ft.dropdown.Option(c) for c in categorias],
        value=categorias[0],
        border_radius=15,
        bgcolor=SURFACE
    )

    # --- NAVEGACIÓN Y VISTAS ---
    # Corrección de 'top_left' y 'center' usando strings para mayor compatibilidad
    # Corrección de Tab(text=...) a Tab(label=...)
    
    vista_inicio = ft.Column([
        ft.Container(height=10),
        ft.Container(
            content=ft.Column([ft.Text("BALANCE TOTAL", size=11, weight="bold"), txt_balance]),
            gradient=ft.LinearGradient(["#1e3a5f", "#0f1e34"], begin="topLeft", end="bottomRight"),
            border_radius=25, padding=25
        ),
        ft.Row([
            tarjeta_stat("💹", txt_ing_res, "Ingresos"),
            tarjeta_stat("📉", txt_gas_res, "Gastos"),
            tarjeta_stat("⚠️", txt_deu_res, "Deudas"),
        ], spacing=10),
        ft.Text("RECIENTES", size=12, weight="bold", color=MUTED),
        lista_recientes
    ], expand=True)

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(label="Inicio", icon=ft.Icons.HOME, content=vista_inicio),
            ft.Tab(label="Ingreso", icon=ft.Icons.ADD_CIRCLE, content=ft.Column([
                ft.Text("Registrar Ingreso", size=20, weight="bold"),
                in_ing_nom, in_ing_mon,
                ft.ElevatedButton("Guardar Ingreso", on_click=agregar_ingreso, bgcolor=GREEN, color="black")
            ], padding=20, spacing=20)),
            ft.Tab(label="Gasto", icon=ft.Icons.REMOVE_CIRCLE, content=ft.Column([
                ft.Text("Registrar Gasto", size=20, weight="bold"),
                cat_sel_txt, in_gas_mon,
                ft.ElevatedButton("Guardar Gasto", on_click=agregar_gasto, bgcolor=RED, color="white")
            ], padding=20, spacing=20)),
        ], expand=True
    )

    page.add(ft.Container(content=tabs, expand=True, padding=10))
    actualizar_interfaz()

ft.app(target=main)
