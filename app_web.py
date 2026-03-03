import streamlit as st
from gastos import DivisorGastos
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Divisor de Gastos", page_icon="💰")

app = DivisorGastos()

# -----------------------------
# LOGIN
# -----------------------------
usuarios = {
    "luciano": "1234",
    "mirko": "1234"
}

if "usuario" not in st.session_state:
    st.session_state.usuario = None

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
            st.rerun()
        else:
            st.error("Complete todos los campos correctamente")

# ---------------------------------------
# VER BALANCE
# ---------------------------------------
elif menu == "Ver balance":

    st.subheader("Balance actual")

    balance = app.calcular_balance(st.session_state.usuario)

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

    datos = app.obtener_gastos()

    if not datos:
        st.warning("No hay gastos registrados.")
    else:
        df = pd.DataFrame(datos, columns=[
            "id", "descripcion", "monto",
            "pagador", "categoria", "usuario", "fecha"
        ])

        df = df[df["usuario"] == st.session_state.usuario]

        if df.empty:
            st.warning("No hay gastos para este usuario.")
        else:
            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha")

                        # ---------------------------------------
            # PRESUPUESTO MENSUAL
            # ---------------------------------------
            st.subheader("💰 Presupuesto mensual")

            meses_disponibles = sorted(
                df["fecha"].dt.to_period("M").astype(str).unique()
            )

            if meses_disponibles:

                mes_seleccionado = st.selectbox(
                    "Seleccionar mes",
                    meses_disponibles,
                    index=len(meses_disponibles) - 1
                )

                presupuesto_actual = app.obtener_presupuesto(
                    st.session_state.usuario,
                    mes_seleccionado
                )

                nuevo_presupuesto = st.number_input(
                    "Definir / editar presupuesto del mes",
                    min_value=0.0,
                    value=float(presupuesto_actual) if presupuesto_actual else 0.0,
                    step=50000.0
                )

                if st.button("Guardar presupuesto"):
                    app.guardar_presupuesto(
                        st.session_state.usuario,
                        mes_seleccionado,
                        nuevo_presupuesto
                    )
                    st.success("Presupuesto actualizado")
                    st.rerun()

                df_mes = df[
                    df["fecha"].dt.to_period("M").astype(str) == mes_seleccionado
                ]

                gasto_mes = df_mes["monto"].sum()

                if presupuesto_actual and presupuesto_actual > 0:

                    porcentaje = gasto_mes / presupuesto_actual
                    st.progress(min(porcentaje, 1.0))

                    restante = presupuesto_actual - gasto_mes

                    if restante > 0:
                        st.success(f"Te quedan ${restante:,.0f}")
                    else:
                        st.error(f"⚠ Excediste el presupuesto en ${abs(restante):,.0f}")

            # ---------------------------------------
            # TABLA
            # ---------------------------------------
            st.dataframe(df)

            # ---------------------------------------
            # KPIs
            # ---------------------------------------
            total_general = df["monto"].sum()
            total_por_persona = df.groupby("pagador")["monto"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total General", f"${total_general:,.0f}")

            for i, persona in enumerate(app.personas):
                valor = total_por_persona.get(persona, 0)
                col = col2 if i == 0 else col3
                col.metric(f"Pagado por {persona}", f"${valor:,.0f}")

            # ---------------------------------------
            # GRÁFICO CATEGORÍA
            # ---------------------------------------
            st.subheader("🧩 Gastos por categoría")
            gastos_categoria = df.groupby("categoria")["monto"].sum()

            fig2, ax2 = plt.subplots()
            ax2.pie(
                gastos_categoria,
                labels=gastos_categoria.index,
                autopct="%1.1f%%"
            )
            ax2.set_title("Distribución por categoría")
            st.pyplot(fig2)

            # ---------------------------------------
            # EVOLUCIÓN MENSUAL
            # ---------------------------------------
            st.subheader("📈 Evolución mensual")

            df["mes"] = df["fecha"].dt.to_period("M")
            mensual = df.groupby("mes")["monto"].sum()
            mensual.index = mensual.index.astype(str)

            st.line_chart(mensual)

# ---------------------------------------
# ELIMINAR GASTO
# ---------------------------------------
elif menu == "Eliminar gasto":

    st.subheader("Eliminar gasto")

    datos = app.obtener_gastos()

    if not datos:
        st.warning("No hay gastos para eliminar.")
    else:
        df = pd.DataFrame(datos, columns=[
            "id", "descripcion", "monto",
            "pagador", "categoria", "usuario", "fecha"
        ])

        df = df[df["usuario"] == st.session_state.usuario]

        if df.empty:
            st.warning("No hay gastos para este usuario.")
        else:
            opciones = [
                f"{row['id']} - {row['descripcion']} - ${row['monto']}"
                for _, row in df.iterrows()
            ]

            seleccion = st.selectbox("Seleccionar gasto", opciones)

            if st.button("Eliminar"):
                id_gasto = int(seleccion.split(" - ")[0])
                app.eliminar_gasto(id_gasto)
                st.success("Gasto eliminado correctamente")
                st.rerun()