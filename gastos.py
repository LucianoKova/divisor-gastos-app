import os
import psycopg2
from datetime import datetime
from passlib.context import CryptContext


class DivisorGastos:

    # 🔐 Configuración de hash segura
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self):
        self.personas = ["Luciano", "Mirko"]
        self._crear_tablas()

    # -----------------------------
    # 🔌 CONEXIÓN POSTGRES (Railway)
    # -----------------------------
    def _conectar(self):
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise Exception("DATABASE_URL no configurada en Railway")

        return psycopg2.connect(database_url, sslmode="require")

    # -----------------------------
    # 📦 CREAR TABLAS
    # -----------------------------
    def _crear_tablas(self):
        conn = self._conectar()
        cursor = conn.cursor()

        # Tabla usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        """)

        # Tabla gastos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id SERIAL PRIMARY KEY,
                descripcion TEXT NOT NULL,
                monto NUMERIC NOT NULL,
                pagador TEXT NOT NULL,
                categoria TEXT NOT NULL,
                usuario TEXT NOT NULL,
                fecha TIMESTAMP NOT NULL
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()

    # -----------------------------
    # 👤 CREAR USUARIO
    # -----------------------------
    def crear_usuario(self, username, password):
        conn = self._conectar()
        cursor = conn.cursor()

        password_hash = self.pwd_context.hash(password)

        try:
            cursor.execute(
                "INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            conn.commit()
        except:
            pass  # Si ya existe, no rompe

        cursor.close()
        conn.close()

    # -----------------------------
    # 🔐 VERIFICAR LOGIN
    # -----------------------------
    def verificar_usuario(self, username, password):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password_hash FROM usuarios WHERE username = %s",
            (username,)
        )

        resultado = cursor.fetchone()

        cursor.close()
        conn.close()

        if resultado:
            return self.pwd_context.verify(password, resultado[0])

        return False

    # -----------------------------
    # ➕ AGREGAR GASTO
    # -----------------------------
    def agregar_gasto(self, descripcion, monto, pagador, categoria, usuario):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO gastos (descripcion, monto, pagador, categoria, usuario, fecha)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (descripcion, monto, pagador, categoria, usuario, datetime.now()))

        conn.commit()
        cursor.close()
        conn.close()

    # -----------------------------
    # 📋 OBTENER GASTOS
    # -----------------------------
    def obtener_gastos(self):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM gastos ORDER BY fecha DESC")
        datos = cursor.fetchall()

        cursor.close()
        conn.close()

        return datos

    # -----------------------------
    # ❌ ELIMINAR GASTO
    # -----------------------------
    def eliminar_gasto(self, id_gasto):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM gastos WHERE id = %s", (id_gasto,))

        conn.commit()
        cursor.close()
        conn.close()

    # -----------------------------
    # ⚖ CALCULAR BALANCE
    # -----------------------------
    def calcular_balance(self, usuario):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT pagador, SUM(monto) FROM gastos WHERE usuario = %s GROUP BY pagador",
            (usuario,)
        )

        resultados = cursor.fetchall()

        cursor.close()
        conn.close()

        balance = {persona: 0 for persona in self.personas}

        for pagador, total in resultados:
            balance[pagador] = float(total)

        diferencia = balance[self.personas[0]] - balance[self.personas[1]]

        if diferencia > 0:
            return {
                self.personas[0]: diferencia / 2,
                self.personas[1]: 0
            }
        elif diferencia < 0:
            return {
                self.personas[0]: 0,
                self.personas[1]: abs(diferencia) / 2
            }
        else:
            return {
                self.personas[0]: 0,
                self.personas[1]: 0
            }