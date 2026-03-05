import flet as ft
import pandas as pd
from datetime import datetime
import json
import os

# Archivo donde se guardará todo
ARCHIVO_DATOS = "mis_finanzas_datos.json"

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al leer datos: {e}")
            
    # Si no hay archivo o hay un error, empezamos de cero limpiamente
    return {"ingresos": [], "gastos": [], "deudas": []}

def guardar_datos(datos):
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4)
    except Exception as e:
        print(f"Error al guardar datos: {e}")

def main(page: ft.Page):
    # Configuración de la ventana
    page.title = "Mis Finanzas"
    page.window_width = 380
    page.window_height = 750
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # Cargar base de datos local
    datos = cargar_datos()
    
    categorias_gastos = [
        "🚌 Transporte", "🍛 Almuerzos", "🍔 Comida Rápida", 
        "🍫 Antojos", "🛒 Supermercado", "🎮 Entretenimiento", "💸 Otros"
    ]

    # --- ELEMENTOS DE LA INTERFAZ ---

    txt_total_ingresos = ft.Text("Ingresos: $0.00", size=16, color=ft.colors.GREEN_700, weight="bold")
    txt_total_gastos = ft.Text("Gastos: $0.00", size=16, color=ft.colors.RED_700, weight="bold")
    txt_total_deudas = ft.Text("Deudas Activas: $0.00", size=16, color=ft.colors.ORANGE_700, weight="bold")
    txt_balance = ft.Text("$0.00", size=40, weight="bold", color=ft.colors.BLUE_GREY_800)
    
    # Inputs Ingresos
    ingreso_nombre = ft.TextField(label="Descripción del Ingreso", width=300, prefix_icon=ft.icons.DESCRIPTION)
    ingreso_cantidad = ft.TextField(label="Monto ($)", width=300, keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.icons.ATTACH_MONEY)
    lista_ingresos_ui = ft.ListView(expand=1, spacing=10, padding=10)

    # Inputs Gastos
    gasto_categoria = ft.Dropdown(label="¿En qué gastaste?", width=300, options=[ft.dropdown.Option(cat) for cat in categorias_gastos], prefix_icon=ft.icons.CATEGORY)
    gasto_cantidad = ft.TextField(label="Monto ($)", width=300, keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.icons.MONEY_OFF)
    lista_gastos_ui = ft.ListView(expand=1, spacing=10, padding=10)

    # Inputs Deudas
    deuda_nombre = ft.TextField(label="¿A quién le debes / Qué debes?", width=300, prefix_icon=ft.icons.ACCOUNT_BALANCE_WALLET)
    deuda_cantidad = ft.TextField(label="Monto de Deuda ($)", width=300, keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.icons.WARNING_AMBER_ROUNDED)
    lista_deudas_ui = ft.ListView(expand=1, spacing=10, padding=10)


    # --- LÓGICA DE LA APLICACIÓN ---

    def mostrar_alerta(mensaje, color):
        snack = ft.SnackBar(ft.Text(mensaje, color=ft.colors.WHITE), bgcolor=color)
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
        
        txt_balance.color = ft.colors.GREEN_700 if balance >= 0 else ft.colors.RED_700
        page.update()

    def renderizar_listas():
        lista_ingresos_ui.controls.clear()
        lista_gastos_ui.controls.clear()
        lista_deudas_ui.controls.clear()

        for i in datos["ingresos"]:
            lista_ingresos_ui.controls.append(ft.ListTile(leading=ft.Icon(ft.icons.ARROW_UPWARD, color=ft.colors.GREEN), title=ft.Text(i["Concepto"], weight="bold"), subtitle=ft.Text(f"${i['Monto']:,.2f}", color=ft.colors.GREEN)))
        
        for g in datos["gastos"]:
            emoji = g["Categoría"].split(" ")[0]
            lista_gastos_ui.controls.append(ft.ListTile(leading=ft.Text(emoji, size=24), title=ft.Text(g["Categoría"][2:], weight="bold"), subtitle=ft.Text(f"-${g['Monto']:,.2f}", color=ft.colors.RED)))
            
        for d in datos["deudas"]:
            lista_deudas_ui.controls.append(ft.ListTile(leading=ft.Icon(ft.icons.WARNING_ROUNDED, color=ft.colors.ORANGE), title=ft.Text(d["Concepto"], weight="bold"), subtitle=ft.Text(f"-${d['Monto']:,.2f}", color=ft.colors.ORANGE)))

        actualizar_resumen()

    def agregar_ingreso(e):
        if ingreso_nombre.value and ingreso_cantidad.value:
            try:
                datos["ingresos"].append({
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Concepto": ingreso_nombre.value,
                    "Monto": float(ingreso_cantidad.value)
                })
                guardar_datos(datos)
                ingreso_nombre.value = ""
                ingreso_cantidad.value = ""
                renderizar_listas()
                mostrar_alerta("¡Ingreso guardado!", ft.colors.GREEN)
            except ValueError:
                mostrar_alerta("Ingresa un número válido.", ft.colors.RED)

    def agregar_gasto(e):
        if gasto_categoria.value and gasto_cantidad.value:
            try:
                datos["gastos"].append({
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Categoría": gasto_categoria.value,
                    "Monto": float(gasto_cantidad.value)
                })
                guardar_datos(datos)
                gasto_categoria.value = None
                gasto_cantidad.value = ""
                renderizar_listas()
                mostrar_alerta("¡Gasto guardado!", ft.colors.RED_400)
            except ValueError:
                mostrar_alerta("Ingresa un número válido.", ft.colors.RED)

    def agregar_deuda(e):
        if deuda_nombre.value and deuda_cantidad.value:
            try:
                datos["deudas"].append({
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Concepto": deuda_nombre.value,
                    "Monto": float(deuda_cantidad.value)
                })
                guardar_datos(datos)
                deuda_nombre.value = ""
                deuda_cantidad.value = ""
                renderizar_listas()
                mostrar_alerta("¡Deuda registrada!", ft.colors.ORANGE)
            except ValueError:
                mostrar_alerta("Ingresa un número válido.", ft.colors.RED)

    def exportar_excel(e):
        if not datos["ingresos"] and not datos["gastos"] and not datos["deudas"]:
            mostrar_alerta("No hay datos para exportar.", ft.colors.GREY_700)
            return
            
        df_ingresos = pd.DataFrame(datos["ingresos"])
        df_gastos = pd.DataFrame(datos["gastos"])
        df_deudas = pd.DataFrame(datos["deudas"])
        
        total_ing = sum([float(i["Monto"]) for i in datos["ingresos"]]) if datos["ingresos"] else 0
        total_gas = sum([float(g["Monto"]) for g in datos["gastos"]]) if datos["gastos"] else 0
        total_deu = sum([float(d["Monto"]) for d in datos["deudas"]]) if datos["deudas"] else 0
        
        df_balance = pd.DataFrame([{
            "Total Ingresos": total_ing, 
            "Total Gastos": total_gas, 
            "Total Deudas": total_deu,
            "Balance Final (Ingresos - Gastos)": total_ing - total_gas,
            "Fecha de Reporte": datetime.now().strftime("%Y-%m-%d")
        }])
        
        nombre_archivo = f"Mis_Finanzas_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        
        with pd.ExcelWriter(nombre_archivo) as writer:
            if not df_ingresos.empty: df_ingresos.to_excel(writer, sheet_name="Ingresos", index=False)
            if not df_gastos.empty: df_gastos.to_excel(writer, sheet_name="Gastos", index=False)
            if not df_deudas.empty: df_deudas.to_excel(writer, sheet_name="Deudas", index=False)
            df_balance.to_excel(writer, sheet_name="Balance", index=False)
        
        mostrar_alerta(f"¡Excel guardado: {nombre_archivo}!", ft.colors.BLUE)

    # --- LÓGICA PARA REINICIAR DATOS ---
    def confirmar_reinicio(e):
        datos["ingresos"] = []
        datos["gastos"] = []
        datos["deudas"] = []
        guardar_datos(datos)
        renderizar_listas()
        dialogo_confirmacion.open = False
        page.update()
        mostrar_alerta("¡Todos los datos han sido borrados!", ft.colors.RED)

    def cerrar_dialogo(e):
        dialogo_confirmacion.open = False
        page.update()

    dialogo_confirmacion = ft.AlertDialog(
        modal=True,
        title=ft.Text("⚠️ ¿Borrar todo?"),
        content=ft.Text("Esta acción eliminará todos los ingresos, gastos y deudas de forma permanente."),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo),
            ft.TextButton("Sí, borrar todo", on_click=confirmar_reinicio, style=ft.ButtonStyle(color=ft.colors.RED)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def abrir_dialogo_reinicio(e):
        page.dialog = dialogo_confirmacion
        dialogo_confirmacion.open = True
        page.update()


    # --- CONSTRUCCIÓN DE LAS PESTAÑAS ---
    
    # Renderizamos las listas al iniciar la app para mostrar datos guardados
    renderizar_listas()
    
    t = ft.Tabs(
        selected_index=0, animation_duration=300, expand=1,
        tabs=[
            ft.Tab(
                text="Dashboard", icon=ft.icons.PIE_CHART_OUTLINE,
                content=ft.Column(
                    [
                        ft.Container(height=10),
                        ft.Text("Mi Balance Disponible", size=16, color=ft.colors.GREY_600),
                        txt_balance,
                        ft.Card(
                            content=ft.Container(
                                padding=15,
                                content=ft.Column([txt_total_ingresos, txt_total_gastos, ft.Divider(), txt_total_deudas])
                            )
                        ),
                        ft.Container(height=10),
                        ft.FilledButton("Descargar Excel", icon=ft.icons.DOWNLOAD, on_click=exportar_excel),
                        ft.Container(height=10),
                        ft.OutlinedButton("Reiniciar Todo", icon=ft.icons.DELETE_FOREVER, on_click=abrir_dialogo_reinicio, style=ft.ButtonStyle(color=ft.colors.RED))
                    ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ),
            ft.Tab(
                text="Ingresos", icon=ft.icons.TRENDING_UP,
                content=ft.Column([ft.Container(height=10), ingreso_nombre, ingreso_cantidad, ft.ElevatedButton("Añadir Ingreso", on_click=agregar_ingreso, bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE), ft.Divider(), lista_ingresos_ui], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ),
            ft.Tab(
                text="Gastos", icon=ft.icons.TRENDING_DOWN,
                content=ft.Column([ft.Container(height=10), gasto_categoria, gasto_cantidad, ft.ElevatedButton("Añadir Gasto", on_click=agregar_gasto, bgcolor=ft.colors.RED_500, color=ft.colors.WHITE), ft.Divider(), lista_gastos_ui], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ),
            ft.Tab(
                text="Deudas", icon=ft.icons.ACCOUNT_BALANCE_WALLET,
                content=ft.Column([ft.Container(height=10), deuda_nombre, deuda_cantidad, ft.ElevatedButton("Añadir Deuda", on_click=agregar_deuda, bgcolor=ft.colors.ORANGE_500, color=ft.colors.WHITE), ft.Divider(), lista_deudas_ui], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        ]
    )
    
    page.add(t)


ft.app(target=main)



