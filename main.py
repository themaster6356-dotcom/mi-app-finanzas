import flet as ft
import pandas as pd
from datetime import datetime
import json
import os

# Ruta segura para guardar datos en el celular
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

def main(page: ft.Page):
    page.title = "Mis Finanzas"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    datos = cargar_datos()
    
    categorias_gastos = [
        "🚌 Transporte", "🍛 Almuerzos", "🍔 Comida Rápida", 
        "🍫 Antojos", "🛒 Supermercado", "🎮 Entretenimiento", "💸 Otros"
    ]

    # --- ELEMENTOS CON MAYÚSCULAS CORREGIDAS (Colors e Icons) ---
    txt_total_ingresos = ft.Text("Ingresos: $0.00", size=16, color=ft.Colors.GREEN_700, weight="bold")
    txt_total_gastos = ft.Text("Gastos: $0.00", size=16, color=ft.Colors.RED_700, weight="bold")
    txt_total_deudas = ft.Text("Deudas Activas: $0.00", size=16, color=ft.Colors.ORANGE_700, weight="bold")
    txt_balance = ft.Text("$0.00", size=40, weight="bold", color=ft.Colors.BLUE_GREY_800)
    
    ingreso_nombre = ft.TextField(label="Descripción", width=300, prefix_icon=ft.Icons.DESCRIPTION)
    ingreso_cantidad = ft.TextField(label="Monto ($)", width=300, keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.Icons.ATTACH_MONEY)
    lista_ingresos_ui = ft.ListView(expand=1, spacing=10)

    gasto_categoria = ft.Dropdown(label="Categoría", width=300, options=[ft.dropdown.Option(cat) for cat in categorias_gastos], prefix_icon=ft.Icons.CATEGORY)
    gasto_cantidad = ft.TextField(label="Monto ($)", width=300, keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.Icons.MONEY_OFF)
    lista_gastos_ui = ft.ListView(expand=1, spacing=10)

    deuda_nombre = ft.TextField(label="¿A quién?", width=300, prefix_icon=ft.Icons.ACCOUNT_BALANCE_WALLET)
    deuda_cantidad = ft.TextField(label="Monto ($)", width=300, keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.Icons.WARNING_AMBER_ROUNDED)
    lista_deudas_ui = ft.ListView(expand=1, spacing=10)

    def mostrar_alerta(mensaje, color):
        snack = ft.SnackBar(ft.Text(mensaje, color=ft.Colors.WHITE), bgcolor=color)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def actualizar_resumen():
        total_ing = sum([float(i["Monto"]) for i in datos["ingresos"]])
        total_gas = sum([float(g["Monto"]) for g in datos["gastos"]])
        total_deu = sum([float(d["Monto"]) for d in datos["deudas"]])
        balance = total_ing - total_gas
        txt_total_ingresos.value = f"Ingresos: ${total_ing:,.2f}"
        txt_total_gastos.value = f"Gastos: ${total_gas:,.2f}"
        txt_total_deudas.value = f"Deudas: ${total_deu:,.2f}"
        txt_balance.value = f"${balance:,.2f}"
        txt_balance.color = ft.Colors.GREEN_700 if balance >= 0 else ft.Colors.RED_700
        page.update()

    def renderizar_listas():
        lista_ingresos_ui.controls.clear()
        lista_gastos_ui.controls.clear()
        lista_deudas_ui.controls.clear()
        for i in datos["ingresos"]:
            lista_ingresos_ui.controls.append(ft.ListTile(leading=ft.Icon(ft.Icons.ARROW_UPWARD, color=ft.Colors.GREEN), title=ft.Text(i["Concepto"]), subtitle=ft.Text(f"${i['Monto']}")))
        for g in datos["gastos"]:
            lista_gastos_ui.controls.append(ft.ListTile(leading=ft.Icon(ft.Icons.ARROW_DOWNWARD, color=ft.Colors.RED), title=ft.Text(g["Categoría"]), subtitle=ft.Text(f"${g['Monto']}")))
        for d in datos["deudas"]:
            lista_deudas_ui.controls.append(ft.ListTile(leading=ft.Icon(ft.Icons.WARNING_ROUNDED, color=ft.Colors.ORANGE), title=ft.Text(d["Concepto"]), subtitle=ft.Text(f"${d['Monto']}")))
        actualizar_resumen()

    def agregar_item(tipo, nombre, monto, cat=None):
        try:
            val = float(monto.value)
            nuevo = {"Fecha": datetime.now().strftime("%Y-%m-%d"), "Concepto": nombre.value or cat, "Monto": val}
            if cat: nuevo["Categoría"] = cat
            datos[tipo].append(nuevo)
            guardar_datos(datos)
            nombre.value = ""
            monto.value = ""
            renderizar_listas()
            mostrar_alerta("¡Guardado!", ft.Colors.GREEN)
        except:
            mostrar_alerta("Error en el monto", ft.Colors.RED)

    # --- PESTAÑAS ---
    t = ft.Tabs(
        selected_index=0, expand=1,
        tabs=[
            ft.Tab(text="Inicio", icon=ft.Icons.PIE_CHART_OUTLINE, content=ft.Column([
                ft.Container(height=20),
                txt_balance,
                ft.Card(content=ft.Container(padding=15, content=ft.Column([txt_total_ingresos, txt_total_gastos, txt_total_deudas]))),
                ft.FilledButton("Exportar Excel", icon=ft.Icons.DOWNLOAD, on_click=lambda _: mostrar_alerta("Generando...", ft.Colors.BLUE)),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
            ft.Tab(text="Ingreso", icon=ft.Icons.TRENDING_UP, content=ft.Column([ingreso_nombre, ingreso_cantidad, ft.ElevatedButton("Añadir", on_click=lambda _: agregar_item("ingresos", ingreso_nombre, ingreso_cantidad), bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
            ft.Tab(text="Gasto", icon=ft.Icons.TRENDING_DOWN, content=ft.Column([gasto_categoria, gasto_cantidad, ft.ElevatedButton("Añadir", on_click=lambda _: agregar_item("gastos", gasto_categoria, gasto_cantidad, cat=gasto_categoria.value), bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
            ft.Tab(text="Deuda", icon=ft.Icons.ACCOUNT_BALANCE_WALLET, content=ft.Column([deuda_nombre, deuda_cantidad, ft.ElevatedButton("Añadir", on_click=lambda _: agregar_item("deudas", deuda_nombre, deuda_cantidad), bgcolor=ft.Colors.ORANGE, color=ft.Colors.WHITE)], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        ]
    )
    renderizar_listas()
    page.add(t)

def main_detector(page: ft.Page):
    import traceback
    try:
        main(page)
    except Exception:
        page.add(ft.Text("Error crítico:", color=ft.Colors.RED, size=20), ft.Text(traceback.format_exc(), color=ft.Colors.WHITE))
        page.bgcolor = "black"
        page.update()

ft.app(target=main_detector)

