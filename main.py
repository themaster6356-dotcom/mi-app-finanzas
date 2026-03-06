import flet as ft
from datetime import datetime
import json
import os

# SOLUCIÓN AL ERROR DE ALMACENAMIENTO:
# En Android, 'HOME' no siempre existe. Usamos client_storage para guardar datos de forma segura.
def cargar_datos(page: ft.Page):
    if page.client_storage.contains_key("datos_finanzas"):
        return page.client_storage.get("datos_finanzas")
    return {"ingresos": [], "gastos": [], "deudas": []}

def guardar_datos(page: ft.Page, datos):
    page.client_storage.set("datos_finanzas", datos)

# ── Colores globales (Sin cambios) ──────────────────────────────────────────
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
    
    # Cargamos datos desde el almacenamiento seguro del dispositivo
    datos = cargar_datos(page)

    categorias_gastos = [
        "🚌 Transporte", "🍛 Almuerzos", "🍔 Comida Rápida",
        "🍫 Antojos", "🛒 Supermercado", "🎮 Entretenimiento", "💸 Otros"
    ]

    categoria_seleccionada = {"valor": categorias_gastos[0]}

    # ── Textos de resumen ─────────────────────────────────────────────────────
    txt_balance       = ft.Text("$0.00", size=38, weight="bold", color=GREEN,
                                font_family="monospace")
    txt_ing_card      = ft.Text("$0.00", size=15, weight="bold", color=GREEN)
    txt_gas_card      = ft.Text("$0.00", size=15, weight="bold", color=RED)
    txt_deu_card      = ft.Text("$0.00", size=15, weight="bold", color=ORANGE)

    # ── Campos de entrada ─────────────────────────────────────────────────────
    def campo(label, tipo=ft.KeyboardType.TEXT):
        return ft.TextField(
            label=label,
            keyboard_type=tipo,
            border_color=BORDER,
            focused_border_color=BLUE,
            border_radius=14,
            color=TEXT,
            label_style=ft.TextStyle(color=MUTED, size=12),
            cursor_color=BLUE,
            filled=True,
            fill_color=SURFACE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        )

    ingreso_nombre   = campo("Descripción")
    ingreso_cantidad = campo("Monto ($)", ft.KeyboardType.NUMBER)
    gasto_cantidad   = campo("Monto ($)", ft.KeyboardType.NUMBER)
    deuda_nombre     = campo("¿A quién le debes?")
    deuda_cantidad   = campo("Monto ($)", ft.KeyboardType.NUMBER)

    lista_ingresos_ui = ft.ListView(expand=True, spacing=8)
    lista_gastos_ui   = ft.ListView(expand=True, spacing=8)
    lista_deudas_ui   = ft.ListView(expand=True, spacing=8)
    lista_recientes   = ft.ListView(expand=True, spacing=8)

    chips_row = ft.Row(wrap=True, spacing=8, run_spacing=8)

    def build_chips():
        chips_row.controls.clear()
        for cat in categorias_gastos:
            seleccionado = (cat == categoria_seleccionada["valor"])
            chips_row.controls.append(
                ft.Container(
                    content=ft.Text(cat, size=12,
                                    color=BLUE if seleccionado else MUTED,
                                    weight="bold" if seleccionado else "normal"),
                    bgcolor="rgba(91,140,255,0.13)" if seleccionado else SURFACE,
                    border=ft.border.all(1, BLUE if seleccionado else BORDER),
                    border_radius=20,
                    padding=ft.padding.symmetric(horizontal=12, vertical=7),
                    on_click=lambda e, c=cat: seleccionar_chip(c),
                    animate=ft.Animation(120, ft.AnimationCurve.EASE_IN_OUT),
                )
            )

    def seleccionar_chip(cat):
        categoria_seleccionada["valor"] = cat
        build_chips()
        page.update()

    build_chips()

    def seccion_titulo(texto):
        return ft.Text(texto.upper(), size=11, color=MUTED,
                       weight="bold", font_family="monospace")

    def tarjeta_stat(emoji, txt_ref, label):
        return ft.Container(
            content=ft.Column([
                ft.Text(emoji, size=18),
                txt_ref,
                ft.Text(label, size=10, color=MUTED),
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.START),
            bgcolor=SURFACE,
            border=ft.border.all(1, BORDER),
            border_radius=18,
            padding=ft.padding.symmetric(horizontal=12, vertical=14),
            expand=True,
        )

    def item_lista(icono_emoji, titulo, subtitulo, monto, color_monto, color_bg):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(icono_emoji, size=18),
                    bgcolor=color_bg,
                    border_radius=12,
                    width=40, height=40,
                    alignment=ft.alignment.CENTER, # CORRECCIÓN: CENTER en Mayúsculas
                ),
                ft.Column([
                    ft.Text(titulo, size=13, color=TEXT, weight="w500"),
                    ft.Text(subtitulo, size=11, color=MUTED),
                ], spacing=2, expand=True),
                ft.Text(monto, size=14, color=color_monto,
                        weight="bold", font_family="monospace"),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=SURFACE,
            border=ft.border.all(1, BORDER),
            border_radius=14,
            padding=ft.padding.symmetric(horizontal=14, vertical=12),
        )

    def boton_accion(texto, color_inicio, color_fin, handler):
        return ft.Container(
            content=ft.Text(texto, size=14, color="#ffffff", weight="bold",
                            text_align=ft.TextAlign.CENTER),
            gradient=ft.LinearGradient(
                [color_inicio, color_fin],
                begin=ft.alignment.CENTER_LEFT,  # CORRECCIÓN: Mayúsculas
                end=ft.alignment.CENTER_RIGHT,    # CORRECCIÓN: Mayúsculas
            ),
            border_radius=18,
            padding=ft.padding.symmetric(vertical=16),
            alignment=ft.alignment.CENTER,        # CORRECCIÓN: Mayúsculas
            on_click=handler,
            animate=ft.Animation(100, ft.AnimationCurve.EASE_IN_OUT),
        )

    def mostrar_alerta(mensaje, color):
        snack = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE, weight="bold"),
            bgcolor=color,
            duration=2000,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def actualizar_resumen():
        total_ing = sum(float(i["Monto"]) for i in datos["ingresos"])
        total_gas = sum(float(g["Monto"]) for g in datos["gastos"])
        total_deu = sum(float(d["Monto"]) for d in datos["deudas"])
        balance   = total_ing - total_gas

        txt_ing_card.value = f"${total_ing:,.2f}"
        txt_gas_card.value = f"${total_gas:,.2f}"
        txt_deu_card.value = f"${total_deu:,.2f}"
        txt_balance.value  = f"${balance:,.2f}"
        txt_balance.color  = GREEN if balance >= 0 else RED

    def renderizar_listas():
        lista_ingresos_ui.controls.clear()
        lista_gastos_ui.controls.clear()
        lista_deudas_ui.controls.clear()
        lista_recientes.controls.clear()

        todos = (
            [("ingreso", i) for i in datos["ingresos"]] +
            [("gasto",   g) for g in datos["gastos"]]   +
            [("deuda",   d) for d in datos["deudas"]]
        )
        todos.sort(key=lambda x: x[1]["Fecha"], reverse=True)

        for tipo, mov in todos[:6]:
            if tipo == "ingreso":
                lista_recientes.controls.append(
                    item_lista("💹", mov["Concepto"], mov["Fecha"],
                               f"+${float(mov['Monto']):,.2f}", GREEN,
                               "rgba(0,229,160,0.10)"))
            elif tipo == "gasto":
                lista_recientes.controls.append(
                    item_lista("📉", mov.get("Categoría", "Gasto"), mov["Fecha"],
                               f"-${float(mov['Monto']):,.2f}", RED,
                               "rgba(255,92,122,0.10)"))
            else:
                lista_recientes.controls.append(
                    item_lista("👤", mov["Concepto"], mov["Fecha"],
                               f"${float(mov['Monto']):,.2f}", ORANGE,
                               "rgba(255,170,59,0.10)"))

        for i in reversed(datos["ingresos"]):
            lista_ingresos_ui.controls.append(
                item_lista("💹", i["Concepto"], i["Fecha"],
                           f"+${float(i['Monto']):,.2f}", GREEN,
                           "rgba(0,229,160,0.10)"))

        for g in reversed(datos["gastos"]):
            lista_gastos_ui.controls.append(
                item_lista("📉", g.get("Categoría", "Gasto"), g["Fecha"],
                           f"-${float(g['Monto']):,.2f}", RED,
                           "rgba(255,92,122,0.10)"))

        for d in reversed(datos["deudas"]):
            lista_deudas_ui.controls.append(
                item_lista("👤", d["Concepto"], d["Fecha"],
                           f"${float(d['Monto']):,.2f}", ORANGE,
                           "rgba(255,170,59,0.10)"))

        actualizar_resumen()

    def agregar_ingreso(e):
        try:
            val = float(ingreso_cantidad.value)
            if not ingreso_nombre.value.strip():
                raise ValueError
            datos["ingresos"].append({
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Concepto": ingreso_nombre.value.strip(),
                "Monto": val,
            })
            guardar_datos(page, datos) # CORRECCIÓN: Guardar en storage
            ingreso_nombre.value = ""
            ingreso_cantidad.value = ""
            renderizar_listas()
            mostrar_alerta("✅ Ingreso guardado", GREEN_DIM)
        except Exception:
            mostrar_alerta("⚠️ Ingresa descripción y monto válido", RED_DIM)

    def agregar_gasto(e):
        try:
            val = float(gasto_cantidad.value)
            cat = categoria_seleccionada["valor"]
            datos["gastos"].append({
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Concepto": cat,
                "Categoría": cat,
                "Monto": val,
            })
            guardar_datos(page, datos)
            gasto_cantidad.value = ""
            renderizar_listas()
            mostrar_alerta("✅ Gasto guardado", RED_DIM)
        except Exception:
            mostrar_alerta("⚠️ Ingresa un monto válido", RED_DIM)

    def agregar_deuda(e):
        try:
            val = float(deuda_cantidad.value)
            if not deuda_nombre.value.strip():
                raise ValueError
            datos["deudas"].append({
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Concepto": deuda_nombre.value.strip(),
                "Monto": val,
            })
            guardar_datos(page, datos)
            deuda_nombre.value = ""
            deuda_cantidad.value = ""
            renderizar_listas()
            mostrar_alerta("✅ Deuda registrada", ORANGE_DIM)
        except Exception:
            mostrar_alerta("⚠️ Ingresa nombre y monto válido", RED_DIM)

    # ── VISTAS ───────────────────────────────────────────────────────────────
    mes_actual = datetime.now().strftime("%B %Y").capitalize()

    vista_inicio = ft.Column(
        controls=[
            ft.Container(height=8),
            ft.Container(
                content=ft.Column([
                    ft.Text("BALANCE TOTAL", size=11, color="#7aa0cc",
                            font_family="monospace", weight="bold"),
                    txt_balance,
                    ft.Text(mes_actual, size=11, color="#5a7a9a"),
                ], spacing=4),
                gradient=ft.LinearGradient(
                    ["#1e3a5f", "#0f1e34"],
                    begin=ft.alignment.TOP_LEFT,      # CORRECCIÓN: Mayúsculas
                    end=ft.alignment.BOTTOM_RIGHT,    # CORRECCIÓN: Mayúsculas
                ),
                border=ft.border.all(1, "#2a4a6a"),
                border_radius=24,
                padding=ft.padding.symmetric(horizontal=22, vertical=20),
            ),
            ft.Container(height=10),
            ft.Row([
                tarjeta_stat("💹", txt_ing_card, "Ingresos"),
                tarjeta_stat("📉", txt_gas_card, "Gastos"),
                tarjeta_stat("⚠️", txt_deu_card, "Deudas"),
            ], spacing=10),
            ft.Container(height=14),
            seccion_titulo("Últimos movimientos"),
            ft.Container(height=6),
            ft.Container(content=lista_recientes, expand=True),
        ],
        expand=True, visible=True, scroll=ft.ScrollMode.AUTO, spacing=0,
    )

    def wrap_vista(controles, visible=False):
        return ft.Column(
            controls=controles, expand=True, visible=visible,
            scroll=ft.ScrollMode.AUTO, spacing=12,
        )

    vista_ingreso = wrap_vista([
        ft.Container(height=4),
        ft.Text("Nuevo Ingreso", size=22, weight="bold", color=TEXT, font_family="monospace"),
        ft.Text("Registra lo que entra a tu bolsillo", size=12, color=MUTED),
        ft.Container(height=4),
        ingreso_nombre, ingreso_cantidad,
        boton_accion("＋ Añadir Ingreso", GREEN_DIM, GREEN, agregar_ingreso),
        ft.Divider(color=BORDER, height=20),
        seccion_titulo("Mis ingresos"),
        ft.Container(content=lista_ingresos_ui, expand=True),
    ])

    vista_gasto = wrap_vista([
        ft.Container(height=4),
        ft.Text("Nuevo Gasto", size=22, weight="bold", color=TEXT, font_family="monospace"),
        ft.Text("¿En qué gastaste hoy?", size=12, color=MUTED),
        ft.Container(height=4),
        ft.Text("CATEGORÍA", size=11, color=MUTED, weight="bold", font_family="monospace"),
        chips_row, gasto_cantidad,
        boton_accion("＋ Añadir Gasto", RED_DIM, RED, agregar_gasto),
        ft.Divider(color=BORDER, height=20),
        seccion_titulo("Mis gastos"),
        ft.Container(content=lista_gastos_ui, expand=True),
    ])

    vista_deuda = wrap_vista([
        ft.Container(height=4),
        ft.Text("Nueva Deuda", size=22, weight="bold", color=TEXT, font_family="monospace"),
        ft.Text("Registra lo que debes o te deben", size=12, color=MUTED),
        ft.Container(height=4),
        deuda_nombre, deuda_cantidad,
        boton_accion("＋ Añadir Deuda", ORANGE_DIM, ORANGE, agregar_deuda),
        ft.Divider(color=BORDER, height=20),
        seccion_titulo("Deudas activas"),
        ft.Container(content=lista_deudas_ui, expand=True),
    ])

    contenido = ft.Container(
        content=ft.Stack([vista_inicio, vista_ingreso, vista_gasto, vista_deuda]),
        padding=ft.padding.symmetric(horizontal=18, vertical=10),
        expand=True,
    )

    def cambiar_tab(e):
        idx = e.control.selected_index
        vista_inicio.visible  = (idx == 0)
        vista_ingreso.visible = (idx == 1)
        vista_gasto.visible   = (idx == 2)
        vista_deuda.visible   = (idx == 3)
        page.update()

    page.navigation_bar = ft.NavigationBar(
        bgcolor=SURFACE,
        indicator_color="rgba(91,140,255,0.15)",
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.PIE_CHART_OUTLINE, selected_icon=ft.Icons.PIE_CHART, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.TRENDING_UP, label="Ingresos"),
            ft.NavigationBarDestination(icon=ft.Icons.TRENDING_DOWN, label="Gastos"),
            ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED, label="Deudas"),
        ],
        on_change=cambiar_tab,
    )

    renderizar_listas()
    page.add(contenido)

def main_detector(page: ft.Page):
    import traceback
    try:
        main(page)
    except Exception as e:
        page.add(
            ft.Text("Error crítico:", color=ft.Colors.RED, size=20),
            ft.Text(traceback.format_exc(), color=ft.Colors.WHITE),
        )
        page.bgcolor = "black"
        page.update()

ft.app(target=main_detector)
