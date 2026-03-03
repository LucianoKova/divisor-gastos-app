import streamlit as st
from gastos import DivisorGastos
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Divisor de Gastos", page_icon="💰")

app = DivisorGastos()

# -----------------------------
# LOGIN SIMPLE
# -----------------------------
usuarios = {
    "luciano": "1234",
    "mirko": "1234"
}

if "usuario" not in st.session_state:
    st.session_state.usuario = None

# Pantalla de login
if st.session_state.usuario is None:
    st.title("🔐 Divisor de Gastos")
    st.subheader("Iniciar sesión")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar", use_container_width=True):
            if user in usuarios and usuarios[user] == password:
                st.session_state.usuario = user
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    st.stop()

# Si ya está logueado
st.sidebar.success(f"👤 Sesión: {st.session_state.usuario.capitalize()}")

if st.sidebar.button("🚪 Cerrar sesión"):
    st.session_state.usuario = None
    st.rerun()

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

    st.subheader("📋 Lista de gastos")

    if not app.gastos:
        st.warning("No hay gastos registrados.")
    else:
        df = pd.DataFrame(app.gastos)

        # Filtrar por usuario
        if "usuario" in df.columns:
            df = df[df["usuario"] == st.session_state.usuario]

        if df.empty:
            st.warning("No hay gastos para este usuario.")
        else:
            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha")

            # Filtro fechas
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

            st.download_button(
                label="📥 Descargar CSV",
                data=df_filtrado.to_csv(index=False),
                file_name="gastos_filtrados.csv",
                mime="text/csv"
            )

            # KPIs
            total_general = df_filtrado["monto"].sum()
            total_por_persona = df_filtrado.groupby("pagador")["monto"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total General", f"${total_general:,.0f}")

            for i, persona in enumerate(app.personas):
                valor = total_por_persona.get(persona, 0)
                col = col2 if i == 0 else col3
                col.metric(f"Pagado por {persona}", f"${valor:,.0f}")

            # -----------------------------
            # GRÁFICO POR CATEGORÍA
            # -----------------------------
            st.subheader("🧩 Gastos por categoría")

            if "categoria" in df_filtrado.columns:
                gastos_categoria = df_filtrado.groupby("categoria")["monto"].sum()

                fig2, ax2 = plt.subplots()
                ax2.pie(
                    gastos_categoria,
                    labels=gastos_categoria.index,
                    autopct="%1.1f%%"
                )
                ax2.set_title("Distribución por categoría")

                st.pyplot(fig2)

            # -----------------------------
            # GRÁFICO POR PERSONA
            # -----------------------------
            st.subheader("📊 Total pagado por persona")
            st.bar_chart(total_por_persona)

            # -----------------------------
            # EVOLUCIÓN MENSUAL
            # -----------------------------
            st.subheader("📈 Evolución mensual")

            df_filtrado["mes"] = df_filtrado["fecha"].dt.to_period("M")
            mensual = df_filtrado.groupby("mes")["monto"].sum()
            mensual.index = mensual.index.astype(str)

            st.line_chart(mensual)

# ---------------------------------------
# ELIMINAR GASTO
# ---------------------------------------
elif menu == "Eliminar gasto":

    st.subheader("Eliminar gasto")

    if not app.gastos:
        st.warning("No hay gastos para eliminar.")
    else:
        df = pd.DataFrame(app.gastos)

        if "usuario" in df.columns:
            df = df[df["usuario"] == st.session_state.usuario]

        if df.empty:
            st.warning("No hay gastos para este usuario.")
        else:
            opciones = [
                f"{i+1}. {g['descripcion']} - ${g['monto']} - {g['pagador']}"
                for i, g in df.iterrows()
            ]

            seleccion = st.selectbox("Seleccionar gasto", opciones)

            if st.button("Eliminar"):
                indice = opciones.index(seleccion)
                app.eliminar_gasto(indice)
                st.success("Gasto eliminado correctamente")