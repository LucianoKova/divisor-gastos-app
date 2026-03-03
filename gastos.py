import json
import os
from datetime import datetime


class DivisorGastos:
    def __init__(self, archivo="data.json"):
        self.archivo = archivo
        self.personas = ["Luciano", "Mirko"]
        self.gastos = []
        self.cargar_datos()

    def cargar_datos(self):
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, "r") as f:
                    self.gastos = json.load(f)
            except json.JSONDecodeError:
                self.gastos = []
        else:
            self.gastos = []

    def guardar_datos(self):
        with open(self.archivo, "w") as f:
            json.dump(self.gastos, f, indent=4)

def agregar_gasto(self, descripcion, monto, pagador, categoria):
    gasto = {
        "descripcion": descripcion,
        "monto": monto,
        "pagador": pagador,
        "categoria": categoria,
        "fecha": datetime.now().strftime("%Y-%m-%d")
    }
    self.gastos.append(gasto)
    self.guardar_datos()

    def calcular_balance(self):
        total_pagado = {persona: 0 for persona in self.personas}

        for gasto in self.gastos:
            total_pagado[gasto["pagador"]] += gasto["monto"]

        total_general = sum(total_pagado.values())
        deuda_individual = total_general / len(self.personas)

        balance = {}
        for persona in self.personas:
            balance[persona] = total_pagado[persona] - deuda_individual

        return balance

    def eliminar_gasto(self, indice):
        if 0 <= indice < len(self.gastos):
            self.gastos.pop(indice)
            self.guardar_datos()
            return True
        return False

    def resetear_gastos(self):
        self.gastos = []
        self.guardar_datos()