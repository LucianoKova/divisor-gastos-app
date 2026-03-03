import sqlite3
from datetime import datetime


class DivisorGastos:
    def __init__(self, db_name="gastos.db"):
        self.db_name = db_name
        self.personas = ["Luciano", "Mirko"]
        self._crear_tabla()

    def _conectar(self):
        return sqlite3.connect(self.db_name)

    def _crear_tabla(self):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT,
                monto REAL,
                pagador TEXT,
                categoria TEXT,
                usuario TEXT,
                fecha TEXT
            )
        """)

        conn.commit()
        conn.close()

    def agregar_gasto(self, descripcion, monto, pagador, categoria, usuario):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO gastos (descripcion, monto, pagador, categoria, usuario, fecha)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            descripcion,
            monto,
            pagador,
            categoria,
            usuario,
            datetime.now().strftime("%Y-%m-%d")
        ))

        conn.commit()
        conn.close()

    def obtener_gastos(self):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM gastos")
        datos = cursor.fetchall()

        conn.close()
        return datos

    def eliminar_gasto(self, id_gasto):
        conn = self._conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM gastos WHERE id = ?", (id_gasto,))
        conn.commit()
        conn.close()

    def calcular_balance(self):
        conn = self._conectar()
        cursor = conn.cursor()

        total_pagado = {persona: 0 for persona in self.personas}

        cursor.execute("SELECT pagador, SUM(monto) FROM gastos GROUP BY pagador")
        resultados = cursor.fetchall()

        for pagador, total in resultados:
            total_pagado[pagador] = total if total else 0

        total_general = sum(total_pagado.values())
        deuda_individual = total_general / len(self.personas)

        balance = {}
        for persona in self.personas:
            balance[persona] = total_pagado[persona] - deuda_individual

        conn.close()
        return balance