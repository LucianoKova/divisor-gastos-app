import streamlit as st
from gastos import DivisorGastos
import pandas as pd
from datetime import datetime
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

st.set_page_config(page_title="Divisor de Gastos", page_icon="💰")

app = DivisorGastos()

# -----------------------------
# LOGIN REAL CON BASE
# -----------------------------
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:

    st.title("🔐 Divisor de Gastos")
    st.subheader("Iniciar sesión")

    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if app.verificar_usuario(user, password):
            st.session_state.usuario = user
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()

# -----------------------------
# SESIÓN ACTIVA
# -----------------------------
st.sidebar.success(f"👤 Sesión: {st.session_state.usuario}")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.usuario = None
    st.rerun()

st.title("💰 Divisor de Gastos")

menu = st.sidebar.selectbox(
    "Menú",
    ["Agregar gasto", "Ver balance", "Ver gastos", "Eliminar gasto"]
)

# -----------------------------
# FUNCION PDF
# -----------------------------
def generar_pdf(usuario, mes, gasto_mes, presupuesto, gasto_anterior):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("REPORTE MENSUAL DE GASTOS", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Usuario: {usuario}", styles["Normal"]))
    elements.append(Paragraph(f"Mes: {mes}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    data = [
        ["Concepto", "Monto"],
        ["Gasto del mes", f"${gasto_mes:,.0f}"],
        ["Presupuesto", f"${presupuesto if presupuesto else 0:,.0f}"],
        ["Mes anterior", f"${gasto_anterior:,.0f}"],
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------
# AGREGAR GASTO
# -----------------------------
if menu == "Agregar gasto":

    descripcion = st.text_input("Descripción")
    monto = st.number_input("Monto", min_value=0.0)
    pagador = st.selectbox("Quién pagó", app.personas)
    categoria = st.selectbox(
        "Categoría",
        ["Supermercado", "Alquiler", "Servicios", "Transporte", "Comida", "Otro"]
    )

    if st.button("Agregar"):
        if descripcion and monto > 0:
            app.agregar_gasto(
                descripcion,
                monto,
                pagador,
                categoria,
                st.session_state.usuario
            )
            st.success("Gasto agregado")
            st.rerun()

# -----------------------------
# VER BALANCE
# -----------------------------
elif menu == "Ver balance":

    balance = app.calcular_balance(st.session_state.usuario)
    p1, p2 = app.personas

    if balance[p1] > 0:
        st.info(f"{p2} le debe ${balance[p1]:,.0f} a {p1}")
    elif balance[p2] > 0:
        st.info(f"{p1} le debe ${balance[p2]:,.0f} a {p2}")
    else:
        st.success("Están saldados")

# -----------------------------
# VER GASTOS
# -----------------------------
elif menu == "Ver gastos":

    datos = app.obtener_gastos()

    if datos:
        df = pd.DataFrame(datos, columns=[
            "id", "descripcion", "monto",
            "pagador", "categoria", "usuario", "fecha"
        ])

        df = df[df["usuario"] == st.session_state.usuario]

        if not df.empty:

            df["fecha"] = pd.to_datetime(df["fecha"])
            st.dataframe(df)

            gasto_total = df["monto"].sum()
            st.metric("Total gastado", f"${gasto_total:,.0f}")

            # Resumen mensual
            hoy = datetime.now()
            mes_actual = hoy.strftime("%Y-%m")
            mes_anterior = (pd.Timestamp(hoy) - pd.DateOffset(months=1)).strftime("%Y-%m")

            df_actual = df[df["fecha"].dt.to_period("M").astype(str) == mes_actual]
            df_anterior = df[df["fecha"].dt.to_period("M").astype(str) == mes_anterior]

            gasto_actual = df_actual["monto"].sum()
            gasto_anterior = df_anterior["monto"].sum()

            st.subheader("Resumen mensual")
            st.write(f"Mes actual: ${gasto_actual:,.0f}")
            st.write(f"Mes anterior: ${gasto_anterior:,.0f}")

            pdf = generar_pdf(
                st.session_state.usuario,
                mes_actual,
                gasto_actual,
                0,
                gasto_anterior
            )

            st.download_button(
                "Descargar PDF",
                data=pdf,
                file_name=f"reporte_{mes_actual}.pdf",
                mime="application/pdf"
            )

# -----------------------------
# ELIMINAR GASTO
# -----------------------------
elif menu == "Eliminar gasto":

    datos = app.obtener_gastos()

    if datos:
        df = pd.DataFrame(datos, columns=[
            "id", "descripcion", "monto",
            "pagador", "categoria", "usuario", "fecha"
        ])

        df = df[df["usuario"] == st.session_state.usuario]

        if not df.empty:
            opciones = [
                f"{row['id']} - {row['descripcion']} - ${row['monto']}"
                for _, row in df.iterrows()
            ]

            seleccion = st.selectbox("Seleccionar gasto", opciones)

            if st.button("Eliminar"):
                id_gasto = int(seleccion.split(" - ")[0])
                app.eliminar_gasto(id_gasto)
                st.success("Eliminado")
                st.rerun()