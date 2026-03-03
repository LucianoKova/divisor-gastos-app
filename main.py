from gastos import DivisorGastos

app = DivisorGastos()

while True:
    print("\n--- DIVISOR DE GASTOS ---")
    print("1. Agregar gasto")
    print("2. Ver balance")
    print("3. Ver gastos")
    print("4. Eliminar gasto")
    print("5. Salir")

    opcion = input("Elegí una opción: ")

    if opcion == "1":
        descripcion = input("Descripción del gasto: ")

        try:
            monto = float(input("Monto: "))
        except ValueError:
            print("Monto inválido.")
            continue

        pagador = input("Quién pagó (Luciano/Mirko): ")

        if pagador not in app.personas:
            print("Nombre inválido.")
            continue

        app.agregar_gasto(descripcion, monto, pagador)
        print("Gasto agregado correctamente.")

    elif opcion == "2":
        balance = app.calcular_balance()

        print("\n--- BALANCE ---")

        persona1, persona2 = app.personas
        monto1 = balance[persona1]
        monto2 = balance[persona2]

        if monto1 > 0:
            print(f"{persona2} le debe ${monto1:.2f} a {persona1}")
        elif monto2 > 0:
            print(f"{persona1} le debe ${monto2:.2f} a {persona2}")
        else:
            print("Están saldados. No hay deudas.")

    elif opcion == "3":
        print("\n--- LISTA DE GASTOS ---")

        if not app.gastos:
            print("No hay gastos registrados.")
        else:
            for i, gasto in enumerate(app.gastos, start=1):
                print(f"{i}. {gasto['descripcion']} - ${gasto['monto']} - Pagó: {gasto['pagador']}")

    elif opcion == "4":
        print("\n--- ELIMINAR GASTO ---")

        if not app.gastos:
            print("No hay gastos para eliminar.")
            continue

        for i, gasto in enumerate(app.gastos, start=1):
            print(f"{i}. {gasto['descripcion']} - ${gasto['monto']} - Pagó: {gasto['pagador']}")

        try:
            numero = int(input("Número del gasto a eliminar: "))
            eliminado = app.eliminar_gasto(numero - 1)

            if eliminado:
                print("Gasto eliminado correctamente.")
            else:
                print("Número inválido.")
        except ValueError:
            print("Entrada inválida.")

    elif opcion == "5":
        print("Saliendo...")
        break

    else:
        print("Opción inválida.")