import streamlit as st
from gastos import DivisorGastos
import pandas as pd
import matplotlib.pyplot as plt

app = DivisorGastos()

st.set_page_config(page_title="Divisor de Gastos", page_icon="💰")

st.title("💰 Divisor de Gastos - Luciano & Mirko")

menu = st.sidebar.selectbox(
    "Menú",
    ["Agregar gasto", "Ver balance", "Ver gastos", "Eliminar gasto"]
)

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

elif menu == "Ver gastos":

    st.subheader("📋 Lista de gastos")

    if not app.gastos:
        st.warning("No hay gastos registrados.")
    else:
        df = pd.DataFrame(app.gastos)

        if "fecha" not in df.columns:
            df["fecha"] = None

        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha")

        # -----------------------------
        # FILTRO POR RANGO DE FECHAS
        # -----------------------------
        min_fecha = df["fecha"].min()
        max_fecha = df["fecha"].max()

        fecha_inicio, fecha_fin = st.date_input(
            "Filtrar por fecha",
            [min_fecha, max_fecha]
        )

        df_filtrado = df[
            (df["fecha"] >= pd.to_datetime(fecha_inicio)) &
            (df["fecha"] <= pd.to_datetime(fecha_fin))
        ]

        st.dataframe(df_filtrado.sort_values("fecha", ascending=False))

        # -----------------------------
        # KPIs
        # -----------------------------
        total_general = df_filtrado["monto"].sum()
        total_por_persona = df_filtrado.groupby("pagador")["monto"].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("💰 Total General", f"${total_general:,.0f}")

        for i, persona in enumerate(app.personas):
            valor = total_por_persona.get(persona, 0)
            col = col2 if i == 0 else col3
            col.metric(f"Pagado por {persona}", f"${valor:,.0f}")

        # -----------------------------
        # GRÁFICO DE BARRAS
        # -----------------------------
        st.subheader("📊 Total pagado por persona")
        st.bar_chart(total_por_persona)

        # -----------------------------
        # GRÁFICO DE TORTA
        # -----------------------------
        st.subheader("🥧 Distribución porcentual")

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.pie(total_por_persona, labels=total_por_persona.index, autopct="%1.1f%%")
        ax.set_title("Gastos por persona")
        st.pyplot(fig)

        # -----------------------------
        # EVOLUCIÓN TEMPORAL
        # -----------------------------
        st.subheader("📈 Evolución de gastos en el tiempo")

        evolucion = df_filtrado.groupby("fecha")["monto"].sum()
        st.line_chart(evolucion)

    st.subheader("Lista de gastos")

    if not app.gastos:
        st.warning("No hay gastos registrados.")
    else:
        df = pd.DataFrame(app.gastos)

        if "fecha" not in df.columns:
            df["fecha"] = None

        df["fecha"] = df["fecha"].fillna("2024-01-01")
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha", ascending=False)

        st.dataframe(df)

        st.subheader("Total pagado por persona")
        totales = df.groupby("pagador")["monto"].sum()
        st.bar_chart(totales)

        st.subheader("Distribución porcentual")

        fig, ax = plt.subplots()
        ax.pie(totales, labels=totales.index, autopct="%1.1f%%")
        ax.set_title("Gastos por persona")
        st.pyplot(fig)

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