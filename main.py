import flet as ft
from datetime import datetime

# ── Tu Paleta de Colores Original ──────────────────────────────────────────
BG          = "#0f1117"
SURFACE     = "#1a1d27"
CARD        = "#21253a"
BORDER      = "#2a2f45"
TEXT        = "#eef0f8"
MUTED       = "#6b7190"
GREEN       = "#00e5a0"
GREEN_DIM   = "#00c98a"
RED         = "#ff5c7a"
RED_DIM     = "#e03060"
ORANGE      = "#ffaa3b"
ORANGE_DIM  = "#e08830"
BLUE        = "#5b8cff"

def main(page: ft.Page):
    page.title        = "Mis Finanzas"
    page.theme_mode   = ft.ThemeMode.DARK
    page.bgcolor      = BG
    page.padding      = 0
    
    # --- Gestión de Datos Segura para Android ---
    def cargar_datos():
        if page.client_storage.contains_key("datos_finanzas"):
            return page.client_storage.get("datos_finanzas")
        return {"ingresos": [], "gastos": [], "deudas": []}

    def guardar_datos_y_refrescar():
        page.client_storage.set("datos_finanzas", datos)
        renderizar_listas()

    datos = cargar_datos()

    categorias_gastos = ["🚌 Transporte", "🍛 Almuerzos", "🍔 Comida Rápida", "🍫 Antojos", "🛒 Supermercado", "🎮 Entretenimiento", "💸 Otros"]
    cat_sel = {"valor": categorias_gastos[0]}

    # --- Elementos de Resumen ---
    txt_balance = ft.Text("$0.00", size=38, weight="bold", color=GREEN)
    txt_ing_card = ft.Text("$0.00", size=15, weight="bold", color=GREEN)
    txt_gas_card = ft.Text("$0.00", size=15, weight="bold", color=RED)
    txt_deu_card = ft.Text("$0.00", size=15, weight="bold", color=ORANGE)

    # Listas UI
    lista_recientes = ft.ListView(expand=True, spacing=8)
    lista_ingresos_ui = ft.ListView(expand=True, spacing=8)
    lista_gastos_ui = ft.ListView(expand=True, spacing=8)
    lista_deudas_ui = ft.ListView(expand=True, spacing=8)

    # --- Funciones de Diseño Originales (Corregidas para Android) ---
    def tarjeta_stat(emoji, txt_ref, label):
        return ft.Container(
            content=ft.Column([
                ft.Text(emoji, size=18),
                txt_ref,
                ft.Text(label, size=10, color=MUTED),
            ], spacing=4, horizontal_alignment="start"),
            bgcolor=SURFACE, border=ft.border.all(1, BORDER), border_radius=18, padding=14, expand=True,
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

    def campo(label, tipo=ft.KeyboardType.TEXT):
        return ft.TextField(label=label, keyboard_type=tipo, border_color=BORDER, focused_border_color=BLUE, border_radius=14, color=TEXT, filled=True, fill_color=SURFACE, content_padding=16)

    def boton_accion(texto, c1, c2, func):
        return ft.Container(content=ft.Text(texto, size=14, color="white", weight="bold", text_align="center"), 
                            gradient=ft.LinearGradient([c1, c2], begin="centerLeft", end="centerRight"),
                            border_radius=18, padding=16, alignment=ft.alignment.center, on_click=func)

    # --- Lógica de Listas ---
    def renderizar_listas():
        t_ing = sum(float(i["Monto"]) for i in datos["ingresos"])
        t_gas = sum(float(g["Monto"]) for g in datos["gastos"])
        t_deu = sum(float(d["Monto"]) for d in datos["deudas"])
        
        txt_balance.value, txt_ing_card.value, txt_gas_card.value, txt_deu_card.value = f"${(t_ing-t_gas):,.2f}", f"${t_ing:,.2f}", f"${t_gas:,.2f}", f"${t_deu:,.2f}"
        
        lista_recientes.controls.clear()
        # Combinar y mostrar últimos 5
        todo = [("💹", i["Concepto"], i["Fecha"], f"+${float(i['Monto']):,.2f}", GREEN, "rgba(0,229,160,0.1)") for i in datos["ingresos"]] + \
               [("📉", g["Categoría"], g["Fecha"], f"-${float(g['Monto']):,.2f}", RED, "rgba(255,92,122,0.1)") for g in datos["gastos"]]
        todo.sort(key=lambda x: x[2], reverse=True)
        for x in todo[:5]: lista_recientes.controls.append(item_lista(*x))
        page.update()

    # --- Vistas ---
    ing_n = campo("Descripción"); ing_m = campo("Monto", ft.KeyboardType.NUMBER)
    gas_m = campo("Monto", ft.KeyboardType.NUMBER)
    deu_n = campo("¿A quién le debes?"); deu_m = campo("Monto", ft.KeyboardType.NUMBER)

    def add_i(e):
        if ing_n.value and ing_m.value:
            datos["ingresos"].append({"Fecha": datetime.now().strftime("%Y-%m-%d"), "Concepto": ing_n.value, "Monto": float(ing_m.value)})
            ing_n.value = ""; ing_m.value = ""; guardar_datos_y_refrescar()

    def add_g(e):
        if gas_m.value:
            datos["gastos"].append({"Fecha": datetime.now().strftime("%Y-%m-%d"), "Categoría": cat_sel["valor"], "Monto": float(gas_m.value)})
            gas_m.value = ""; guardar_datos_y_refrescar()

    vista_inicio = ft.Column([
        ft.Container(height=10),
        ft.Container(content=ft.Column([ft.Text("BALANCE TOTAL", size=11, color="#7aa0cc", weight="bold"), txt_balance], spacing=4),
                     gradient=ft.LinearGradient(["#1e3a5f", "#0f1e34"], begin="topLeft", end="bottomRight"), border_radius=24, padding=20),
        ft.Row([tarjeta_stat("💹", txt_ing_card, "Ingresos"), tarjeta_stat("📉", txt_gas_card, "Gastos"), tarjeta_stat("⚠️", txt_deu_card, "Deudas")], spacing=10),
        ft.Text("RECIENTES", size=11, color=MUTED, weight="bold"),
        lista_recientes
    ], expand=True)

    vista_ingreso = ft.Column([ft.Text("Nuevo Ingreso", size=22, weight="bold"), ing_n, ing_m, boton_accion("＋ Añadir", GREEN_DIM, GREEN, add_i)], visible=False, spacing=15)
    vista_gasto = ft.Column([ft.Text("Nuevo Gasto", size=22, weight="bold"), gas_m, boton_accion("＋ Añadir", RED_DIM, RED, add_g)], visible=False, spacing=15)

    vistas = [vista_inicio, vista_ingreso, vista_gasto]

    def cambiar_tab(e):
        for i, v in enumerate(vistas): v.visible = (i == e.control.selected_index)
        page.update()

    page.navigation_bar = ft.NavigationBar(bgcolor=SURFACE, on_change=cambiar_tab, destinations=[
        ft.NavigationDestination(icon=ft.Icons.HOME, label="Inicio"),
        ft.NavigationDestination(icon=ft.Icons.ADD_CIRCLE_OUTLINE, label="Ingreso"),
        ft.NavigationDestination(icon=ft.Icons.REMOVE_CIRCLE_OUTLINE, label="Gasto"),
    ])

    page.add(ft.Container(content=ft.Stack(vistas), padding=18, expand=True))
    renderizar_listas()

ft.app(target=main)
