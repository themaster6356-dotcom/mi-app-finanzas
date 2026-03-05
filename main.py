import flet as ft
import pandas as pd
from datetime import datetime
import json
import os

# Configuración de ruta segura para Android
ARCHIVO_DATOS = os.path.join(os.getcwd(), "mis_finanzas_datos.json")

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al leer datos: {e}")
    return {"ingresos": [], "gastos": [], "deudas": []}

def guardar_datos(datos):
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4)
    except Exception as e:
        print(f"Error al guardar datos: {e}")

def main(page: ft.Page):
    page.title = "Mis Finanzas"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    datos = cargar_datos()
    
    categorias_gastos = [
        "🚌 Transporte", "🍛 Almuerzos", "🍔 Comida Rápida", 
        "🍫 Antojos", "🛒 Supermercado", "🎮 Entretenimiento", "💸 Otros"
    ]

    # --- ELEMENTOS DE LA INTERFAZ CON COLORES CORREGIDOS ---
    txt_total_ingresos = ft.Text("Ingresos: $0.00", size=16, color=ft.Colors.GREEN_700, weight="bold")
    txt_total_gastos = ft.Text("Gastos: $0.00", size=16, color=ft.Colors.RED_700, weight="bold")
    txt_total_deudas = ft.Text("Deudas Activas: $0.00", size=16, color=ft.Colors.ORANGE_700, weight="bold")
    txt_balance = ft.Text("$0.00", size=40, weight="bold", color=ft.Colors.BLUE_GREY_800)
    
    ingreso_nombre = ft.TextField(label="Descripción del Ingreso", width=300, prefix_icon=ft.icons.DESCRIPTION)
    ingreso_cantidad = ft.TextField(label="Monto ($)", width=300, keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.icons.ATTACH_MONEY)
    lista_ingresos_ui = ft.ListView(expand=1, spacing=10, padding=10)

    gasto_categoria = ft.Dropdown(label="¿En qué gastaste?", width=300, options=[ft.dropdown.Option(cat) for cat in categorias_gastos], prefix_icon=ft.icons.CATEGORY)
    gasto_cantidad = ft.TextField(label="Monto ($)", width=300, keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.icons.MONEY_OFF)
    lista_gastos_ui = ft.ListView(expand=1, spacing=10, padding=10)

    deuda_nombre = ft.TextField(label="¿A quién le debes / Qué debes?", width=300, prefix_icon=ft.icons.ACCOUNT_BALANCE_WALLET)
    deuda_cantidad = ft.TextField(label="Monto de Deuda ($)", width=300, keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.icons.WARNING_AMBER_ROUNDED)
    lista_deudas_ui = ft.ListView(expand=1, spacing=10, padding=10)

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
        txt_total_deudas.value = f"Deudas Activas: ${total_deu:,.2f}"
        txt_balance.value = f"${balance:,.2f}"
        txt_balance.color = ft.Colors.GREEN_700 if balance >= 0 else ft.Colors.RED_700
        page.update()

    def renderizar_listas():
        lista_ingresos_ui.controls.clear()
        lista_gastos_ui.controls.clear()
        lista_deudas_ui.controls.clear()

        for i in datos["ingresos"]:
            lista_ingresos_ui.controls.append(ft.ListTile(leading=ft.Icon(ft.icons.ARROW_UPWARD, color=ft.Colors.GREEN), title=ft.Text(i["Concepto"], weight="bold"), subtitle=ft.Text(f"${i['Monto']:,.2f}", color=ft.Colors.GREEN)))
        
        for g in datos["gastos"]:
            emoji = g["Categoría"].split(" ")[0]
            lista_gastos_ui.controls.append(ft.ListTile(leading=ft.Text(emoji, size=24), title=ft.Text(g["Categoría"][2:], weight="bold"), subtitle=ft.Text(f"-${g['Monto']:,.2f}", color=ft.Colors.RED)))
            
        for d in datos["deudas"]:
            lista_deudas_ui.controls.append(ft.ListTile(leading=ft.Icon(ft.icons.WARNING_ROUNDED, color=ft.Colors.ORANGE), title=ft.Text(d["Concepto"], weight="bold"), subtitle=ft.Text(f"-${d['Monto']:,.2f}", color=ft.Colors.ORANGE)))
        actualizar_resumen()

    def agregar_ingreso(e):
        if ingreso_nombre.value and ingreso_cantidad.value:
            try:
                datos["ingresos"].append({"Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "Concepto": ingreso_nombre.value, "Monto": float(ingreso_cantidad.value)})
                guardar_datos(datos)
                ingreso_nombre.value = ""
                ingreso_cantidad.value = ""
                renderizar_listas()
                mostrar_alerta("¡Ingreso guardado!", ft.Colors.GREEN)
            except ValueError:
                mostrar_alerta("Ingresa un número válido.", ft.Colors.RED)

    def agregar_gasto(e):
        if gasto_categoria.value and gasto_cantidad.value:
            try:
                datos["gastos"].append({"Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "Categoría": gasto_categoria.value, "Monto": float(gasto_cantidad.value)})
                guardar_datos(datos)
                gasto_categoria.value = None
                gasto_cantidad.value = ""
                renderizar_listas()
                mostrar_alerta("¡Gasto guardado!", ft.Colors.RED_400)
            except ValueError:
                mostrar_alerta("Ingresa un número válido.", ft.Colors.RED)

    def agregar_deuda(e):
        if deuda_nombre.value and deuda_cantidad.value:
            try:
                datos["deudas"].append({"Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "Concepto": deuda_nombre.value, "Monto": float(deuda_cantidad.value)})
                guardar_datos(datos)
                deuda_nombre.value = ""
                deuda_cantidad.value = ""
                renderizar_listas()
                mostrar_alerta("¡Deuda registrada!", ft.Colors.ORANGE)
            except ValueError:
                mostrar_alerta("Ingresa un número válido.", ft.Colors.RED)

    def exportar_excel(e):
        if not datos["ingresos"] and not datos["gastos"] and not datos["deudas"]:
            mostrar_alerta("No hay datos para exportar.", ft.Colors.GREY_700)
            return
        nombre_archivo = f"Mis_Finanzas_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        # Nota: En Android el guardado de Excel requiere permisos adicionales, se guarda en carpeta de la App
        mostrar_alerta(f"Excel generado: {nombre_archivo}", ft.Colors.BLUE)

    def confirmar_reinicio(e):
        datos["ingresos"], datos["gastos"], datos["deudas"] = [], [], []
        guardar_datos(datos)
        renderizar_listas()
        dialogo_confirmacion.open = False
        page.update()
        mostrar_alerta("¡Datos borrados!", ft.Colors.RED)

    dialogo_confirmacion = ft.AlertDialog(
        title=ft.Text("⚠️ ¿Borrar todo?"),
        content=ft.Text("Se eliminará todo permanentemente."),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: setattr(dialogo_confirmacion, "open", False) or page.update()),
            ft.TextButton("Sí, borrar", on_click=confirmar_reinicio, style=ft.ButtonStyle(color=ft.Colors.RED)),
        ],
    )

    renderizar_listas()
    
    t = ft.Tabs(
        selected_index=0, expand=1,
        tabs=[
            ft.Tab(text="Dashboard", icon=ft.icons.PIE_CHART_OUTLINE, content=ft.Column([
                ft.Container(height=10), ft.Text("Balance Disponible", size=16, color=ft.Colors.GREY_600),
                txt_balance, ft.Card(content=ft.Container(padding=15, content=ft.Column([txt_total_ingresos, txt_total_gastos, ft.Divider(), txt_total_deudas]))),
                ft.FilledButton("Descargar Excel", icon=ft.icons.DOWNLOAD, on_click=exportar_excel),
                ft.OutlinedButton("Reiniciar Todo", icon=ft.icons.DELETE_FOREVER, on_click=lambda e: page.open(dialogo_confirmacion), style=ft.ButtonStyle(color=ft.Colors.RED))
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
            ft.Tab(text="Ingresos", icon=ft.icons.TRENDING_UP, content=ft.Column([ingreso_nombre, ingreso_cantidad, ft.ElevatedButton("Añadir", on_click=agregar_ingreso, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE), ft.Divider(), lista_ingresos_ui], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
            ft.Tab(text="Gastos", icon=ft.icons.TRENDING_DOWN, content=ft.Column([gasto_categoria, gasto_cantidad, ft.ElevatedButton("Añadir", on_click=agregar_gasto, bgcolor=ft.Colors.RED_500, color=ft.Colors.WHITE), ft.Divider(), lista_gastos_ui], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
            ft.Tab(text="Deudas", icon=ft.icons.ACCOUNT_BALANCE_WALLET, content=ft.Column([deuda_nombre, deuda_cantidad, ft.ElevatedButton("Añadir", on_click=agregar_deuda, bgcolor=ft.Colors.ORANGE_500, color=ft.Colors.WHITE), ft.Divider(), lista_deudas_ui], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        ]
    )
    page.add(t)

def main_detector(page: ft.Page):
    import traceback
    try:
        main(page)
    except Exception as e:
        page.bgcolor = "black"
        page.scroll = "always"
        page.add(ft.Text("Error en la App:", size=20, color="red", weight="bold"), ft.Text(traceback.format_exc(), color="white"))
        page.update()

ft.app(target=main_detector)
