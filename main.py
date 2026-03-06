import flet as ft
from datetime import datetime
import json
import os

ARCHIVO_DATOS = os.path.join(os.getcwd(), "mis_finanzas_datos.json")

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"ingresos": [], "gastos": [], "deudas": []}

def guardar_datos(datos):
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4)
    except Exception:
        pass

# Colores seguros
BG, SURFACE, CARD = "#0f1117", "#1a1d27", "#21253a"
BORDER, TEXT, MUTED = "#2a2f45", "#eef0f8", "#6b7190"
GREEN, RED, ORANGE, BLUE = "#00e5a0", "#ff5c7a", "#ffaa3b", "#5b8cff"

def main(page: ft.Page):
    page.title = "Mis Finanzas"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 0

    datos = cargar_datos()

    categorias_gastos = ["🚌 Transporte", "🍛 Almuerzos", "🍔 Comida", "🍫 Antojos", "🛒 Super", "🎮 Juegos", "💸 Otros"]
    categoria_seleccionada = {"valor": categorias_gastos[0]}

    txt_balance = ft.Text("$0.00", size=38, weight="bold", color=GREEN)
    txt_ing_card = ft.Text("$0.00", size=15, weight="bold", color=GREEN)
    txt_gas_card = ft.Text("$0.00", size=15, weight="bold", color=RED)
    txt_deu_card = ft.Text("$0.00", size=15, weight="bold", color=ORANGE)

    lista_ingresos_ui = ft.ListView(expand=True, spacing=8)
    lista_gastos_ui = ft.ListView(expand=True, spacing=8)
    lista_deudas_ui = ft.ListView(expand=True, spacing=8)
    lista_recientes = ft.ListView(expand=True, spacing=8)

    def crear_campo(label, tipo=ft.KeyboardType.TEXT):
        return ft.TextField(label=label, keyboard_type=tipo, border_color=BORDER, focused_border_color=BLUE, border_radius=14, color=TEXT, bgcolor=SURFACE, content_padding=ft.padding.symmetric(horizontal=16, vertical=14))

    ingreso_nombre = crear_campo("Descripción")
    ingreso_cantidad = crear_campo("Monto ($)", ft.KeyboardType.NUMBER)
    gasto_cantidad = crear_campo("Monto ($)", ft.KeyboardType.NUMBER)
    deuda_nombre = crear_campo("¿A quién?")
    deuda_cantidad = crear_campo("Monto ($)", ft.KeyboardType.NUMBER)

    chips_row = ft.Row(wrap=True, spacing=8, run_spacing=8)

    def build_chips():
        chips_row.controls.clear()
        for cat in categorias_gastos:
            sel = (cat == categoria_seleccionada["valor"])
            chips_row.controls.append(
                ft.Container(
                    content=ft.Text(cat, size=12, color=BLUE if sel else MUTED),
                    bgcolor="rgba(91,140,255,0.1)" if sel else SURFACE,
                    border=ft.border.all(1, BLUE if sel else BORDER),
                    border_radius=20, padding=ft.padding.symmetric(horizontal=12, vertical=7),
                    on_click=lambda e, c=cat: seleccionar_chip(c)
                )
            )

    def seleccionar_chip(cat):
        categoria_seleccionada["valor"] = cat
        build_chips()
        page.update()

    def tarjeta_stat(emoji, txt_ref, label):
        return ft.Container(content=ft.Column([ft.Text(emoji, size=18), txt_ref, ft.Text(label, size=10, color=MUTED)], spacing=4), bgcolor=SURFACE, border=ft.border.all(1, BORDER), border_radius=18, padding=14, expand=True)

    def item_lista(emoji, titulo, fecha, monto, col, bg_col):
        # Solución del error de alineación (usamos "center" como texto)
        return ft.Container(
            content=ft.Row([
                ft.Container(ft.Text(emoji), bgcolor=bg_col, border_radius=12, width=40, height=40, alignment="center"),
                ft.Column([ft.Text(titulo, size=13, weight="w500"), ft.Text(fecha, size=11, color=MUTED)], expand=True),
                ft.Text(monto, size=14, color=col, weight="bold")
            ]),
            bgcolor=SURFACE, border=ft.border.all(1, BORDER), border_radius=14, padding=12
        )

    def actualizar_resumen():
        t_ing = sum(float(i["Monto"]) for i in datos["ingresos"])
        t_gas = sum(float(g["Monto"]) for g in datos["gastos"])
        t_deu = sum(float(d["Monto"]) for d in datos["deudas"])
        bal = t_ing - t_gas

        txt_ing_card.value = f"${t_ing:,.2f}"
        txt_gas_card.value = f"${t_gas:,.2f}"
        txt_deu_card.value = f"${t_deu:,.2f}"
        txt_balance.value = f"${bal:,.2f}"
        txt_balance.color = GREEN if bal >= 0 else RED
        renderizar_listas()

    def renderizar_listas():
        lista_recientes.controls.clear()
        lista_ingresos_ui.controls.clear()
        lista_gastos_ui.controls.clear()
        lista_deudas_ui.controls.clear()

        todos = [("ing", i) for i in datos["ingresos"]] + [("gas", g) for g in datos["gastos"]]
        todos.sort(key=lambda x: x[1]["Fecha"], reverse=True)

        for tipo, m in todos[:6]:
            col, bg = (GREEN, "rgba(0,229,160,0.1)") if tipo == "ing" else (RED, "rgba(255,92,122,0.1)")
            emo = "💹" if tipo == "ing" else "📉"
            lista_recientes.controls.append(item_lista(emo, m["Concepto"], m["Fecha"], f"${m['Monto']}", col, bg))

        for i in reversed(datos["ingresos"]): lista_ingresos_ui.controls.append(item_lista("💹", i["Concepto"], i["Fecha"], f"${i['Monto']}", GREEN, "rgba(0,229,160,0.1)"))
        for g in reversed(datos["gastos"]): lista_gastos_ui.controls.append(item_lista("📉", g["Concepto"], g["Fecha"], f"${g['Monto']}", RED, "rgba(255,92,122,0.1)"))
        for d in reversed(datos["deudas"]): lista_deudas_ui.controls.append(item_lista("👤", d["Concepto"], d["Fecha"], f"${d['Monto']}", ORANGE, "rgba(255,170,59,0.1)"))
        page.update()

    def agregar_registro(tipo, nombre_ctrl, monto_ctrl):
        try:
            val = float(monto_ctrl.value)
            concepto = nombre_ctrl.value if hasattr(nombre_ctrl, 'value') else categoria_seleccionada["valor"]
            if not concepto: return
            datos[tipo].append({"Fecha": datetime.now().strftime("%d/%m/%y"), "Concepto": concepto, "Monto": val})
            guardar_datos(datos)
            if hasattr(nombre_ctrl, 'value'): nombre_ctrl.value = ""
            monto_ctrl.value = ""
            actualizar_resumen()
        except: pass

    vista_inicio = ft.Column([
        ft.Container(
            # Solución del error de alineación en el gradiente (usamos texto)
            content=ft.Column([ft.Text("BALANCE TOTAL", size=10, weight="bold", color="#7aa0cc"), txt_balance]),
            gradient=ft.LinearGradient(["#1e3a5f", "#0f1e34"], begin="topLeft", end="bottomRight"),
            border_radius=25, padding=25
        ),
        ft.Row([tarjeta_stat("💹", txt_ing_card, "Ingresos"), tarjeta_stat("📉", txt_gas_card, "Gastos"), tarjeta_stat("⚠️", txt_deu_card, "Deudas")], spacing=10),
        ft.Text("RECIENTES", size=11, weight="bold", color=MUTED),
        lista_recientes
    ], expand=True, spacing=15, visible=True)

    vista_ingreso = ft.Column([
        ft.Text("Nuevo Ingreso", size=22, weight="bold"),
        ingreso_nombre, ingreso_cantidad,
        ft.ElevatedButton("Añadir", on_click=lambda _: agregar_registro("ingresos", ingreso_nombre, ingreso_cantidad), bgcolor=GREEN, color="black"),
        lista_ingresos_ui
    ], expand=True, visible=False)

    vista_gasto = ft.Column([
        ft.Text("Nuevo Gasto", size=22, weight="bold"),
        chips_row, gasto_cantidad,
        ft.ElevatedButton("Añadir", on_click=lambda _: agregar_registro("gastos", None, gasto_cantidad), bgcolor=RED, color="white"),
        lista_gastos_ui
    ], expand=True, visible=False)

    vista_deuda = ft.Column([
        ft.Text("Nueva Deuda", size=22, weight="bold"),
        deuda_nombre, deuda_cantidad,
        ft.ElevatedButton("Añadir", on_click=lambda _: agregar_registro("deudas", deuda_nombre, deuda_cantidad), bgcolor=ORANGE, color="black"),
        lista_deudas_ui
    ], expand=True, visible=False)

    def cambiar_tab(e):
        idx = e.control.selected_index
        vista_inicio.visible = (idx == 0)
        vista_ingreso.visible = (idx == 1)
        vista_gasto.visible = (idx == 2)
        vista_deuda.visible = (idx == 3)
        page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.PIE_CHART_OUTLINE, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.TRENDING_UP, label="Ingresos"),
            ft.NavigationBarDestination(icon=ft.Icons.TRENDING_DOWN, label="Gastos"),
            ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_BALANCE_WALLET, label="Deudas"),
        ], bgcolor=SURFACE, on_change=cambiar_tab
    )

    build_chips()
    page.add(ft.Container(content=ft.Stack([vista_inicio, vista_ingreso, vista_gasto, vista_deuda]), padding=20, expand=True))
    actualizar_resumen()

def main_detector(page: ft.Page):
    import traceback
    try: main(page)
    except Exception:
        page.add(ft.Text("Error crítico:", color="red"), ft.Text(traceback.format_exc(), color="white"))
        page.update()

ft.app(target=main_detector)
