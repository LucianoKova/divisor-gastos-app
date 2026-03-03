import streamlit as st
from gastos import DivisorGastos
import pandas as pd

app = DivisorGastos()

st.set_page_config(page_title="Divisor de Gastos", page_icon="💰")

st.title("💰 Divisor de Gastos - Luciano & Mirko")

menu = st.sidebar.selectbox(
    "Menú",
    ["Agregar gasto", "Ver balance", "Ver gastos", "Eliminar gasto"]
)

# ---------------------------------------
# AGREGAR GASTO
# ---------------------------------------
if menu == "Agregar gasto":

    st.subheader("Agregar nuevo gasto")

    descripcion = st.text_input("Descripción")
    monto = st.number_input("Monto", min_value=0.0, step=1000.0)
    pagador = st.selectbox("Quién pagó", app.personas)

    if st.button("Agregar"):
        if descripcion and monto > 0:
            app.agregar_gasto(descripcion, monto, pagador)
            st.success("Gasto agregado correctamente")
        else:
            st.error("Complete todos los campos correctamente")


# ---------------------------------------
# VER BALANCE
# ---------------------------------------
elif menu == "Ver balance":

    st.subheader("Balance actual")

    balance = app.calcular_balance()

    persona1, persona2 = app.personas
    monto1 = balance[persona1]
    monto2 = balance[persona2]

    if monto1 > 0:
        st.info(f"👉 {persona2} le debe ${monto1:,.2f} a {persona1}")
    elif monto2 > 0:
        st.info(f"👉 {persona1} le debe ${monto2:,.2f} a {persona2}")
    else:
        st.success("Están saldados. No hay deudas.")


# ---------------------------------------
# VER GASTOS
# ---------------------------------------
elif menu == "Ver gastos":

    st.subheader("Lista de gastos")

    if not app.gastos:
        st.warning("No hay gastos registrados.")
    else:
       df = pd.DataFrame(app.gastos)
df["fecha"] = pd.to_datetime(df["fecha"])
st.dataframe(df.sort_values("fecha", ascending=False))
 st.subheader("Total pagado por persona")
        totales = df.groupby("pagador")["monto"].sum()
        st.bar_chart(totales)
        st.subheader("Distribución porcentual")
st.pyplot(totales.plot.pie(autopct="%1.1f%%", ylabel="").figure)


# ---------------------------------------
# ELIMINAR GASTO
# ---------------------------------------
elif menu == "Eliminar gasto":

    st.subheader("Eliminar gasto")

    if not app.gastos:
        st.warning("No hay gastos para eliminar.")
    else:
        opciones = [
            f"{i+1}. {g['descripcion']} - ${g['monto']} - {g['pagador']}"
            for i, g in enumerate(app.gastos)
        ]

        seleccion = st.selectbox("Seleccionar gasto", opciones)

        if st.button("Eliminar"):
            indice = opciones.index(seleccion)
            app.eliminar_gasto(indice)
            st.success("Gasto eliminado correctamente")
            import matplotlib.pyplot as plt

st.subheader("Distribución porcentual")

fig, ax = plt.subplots()
ax.pie(totales, labels=totales.index, autopct="%1.1f%%")
ax.set_title("Gastos por persona")

st.pyplot(fig)