import os
import psycopg2
import bcrypt
from datetime import datetime


class DivisorGastos:
    def __init__(self):
        self.personas = ["Luciano", "Mirko"]
        self._crear_tablas()

    # ----------------------------
    # CONEXIÓN POSTGRESQL
    # ----------------------------
    def _conectar(self):
        database_url = os.getenv("DATABASE_URL")
        return psycopg2.connect(database_url)

    # ----------------------------
    # CREAR TABLAS
    # ----------------------------
    def _crear_tablas(self):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id SERIAL PRIMARY KEY,
                descripcion TEXT,
                monto REAL,
                pagador TEXT,
                categoria TEXT,
                usuario TEXT,
                fecha DATE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS presupuestos (
                id SERIAL PRIMARY KEY,
                usuario TEXT,
                mes TEXT,
                monto REAL
            )
        """)

        conn.commit()
        conn.close()

    # ----------------------------
    # USUARIOS
    # ----------------------------
    def crear_usuario(self, username, password):
        conn = self._conectar()
        cursor = conn.cursor()

        password_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()

        cursor.execute("""
            INSERT INTO usuarios (username, password_hash)
            VALUES (%s, %s)
            ON CONFLICT (username) DO NOTHING
        """, (username, password_hash))

        conn.commit()
        conn.close()

    def validar_usuario(self, username, password):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT password_hash FROM usuarios
            WHERE username = %s
        """, (username,))

        resultado = cursor.fetchone()
        conn.close()

        if not resultado:
            return False

        password_hash = resultado[0].encode()
        return bcrypt.checkpw(password.encode(), password_hash)

    # ----------------------------
    # GASTOS
    # ----------------------------
    def agregar_gasto(self, descripcion, monto, pagador, categoria, usuario):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO gastos (descripcion, monto, pagador, categoria, usuario, fecha)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            descripcion,
            monto,
            pagador,
            categoria,
            usuario,
            datetime.now().date()
        ))

        conn.commit()
        conn.close()

    def obtener_gastos(self):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, descripcion, monto, pagador, categoria, usuario, fecha
            FROM gastos
            ORDER BY fecha ASC
        """)

        datos = cursor.fetchall()
        conn.close()
        return datos

    def eliminar_gasto(self, id_gasto):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM gastos WHERE id = %s",
            (id_gasto,)
        )

        conn.commit()
        conn.close()

    def calcular_balance(self, usuario):
        conn = self._conectar()
        cursor = conn.cursor()

        total_pagado = {persona: 0 for persona in self.personas}

        cursor.execute("""
            SELECT pagador, SUM(monto)
            FROM gastos
            WHERE usuario = %s
            GROUP BY pagador
        """, (usuario,))

        resultados = cursor.fetchall()

        for pagador, total in resultados:
            total_pagado[pagador] = float(total) if total else 0

        total_general = sum(total_pagado.values())

        if total_general == 0:
            conn.close()
            return {persona: 0 for persona in self.personas}

        deuda_individual = total_general / len(self.personas)

        balance = {
            persona: total_pagado[persona] - deuda_individual
            for persona in self.personas
        }

        conn.close()
        return balance

    # ----------------------------
    # PRESUPUESTO
    # ----------------------------
    def guardar_presupuesto(self, usuario, mes, monto):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM presupuestos
            WHERE usuario = %s AND mes = %s
        """, (usuario, mes))

        cursor.execute("""
            INSERT INTO presupuestos (usuario, mes, monto)
            VALUES (%s, %s, %s)
        """, (usuario, mes, monto))

        conn.commit()
        conn.close()

    def obtener_presupuesto(self, usuario, mes):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT monto FROM presupuestos
            WHERE usuario = %s AND mes = %s
        """, (usuario, mes))

        resultado = cursor.fetchone()
        conn.close()

        return float(resultado[0]) if resultado else None