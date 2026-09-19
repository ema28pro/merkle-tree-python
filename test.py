from main import MerkleTree, hash256

def test():
    print("\n" + "=" * 65)
    print("      LABORATORIO 2: ARBOL DE MERKLE Y PRUEBA DE INCLUSION      ")
    print("=" * 65)

    # -------------------------------------------------------------
    # 1. Crear 5 transacciones de datos simuladas
    # -------------------------------------------------------------
    print("\n[1] CREACION DE 5 TRANSACCIONES SIMULADAS:")
    txs_originales = [
        "Tomas paga 10 a Emanuel",   # Transaccion 1 (Indice 0)
        "Emanuel paga 5 a Charlie",  # Transaccion 2 (Indice 1)
        "Charlie paga 3 a David",    # Transaccion 3 (Indice 2)
        "David paga 2 a Sofia",      # Transaccion 4 (Indice 3)
        "Tomas paga 5 a Emanuel"     # Transaccion 5 (Indice 4)
    ]
    for i, tx in enumerate(txs_originales, start=1):
        print(f"  Tx {i}: '{tx}'")

    # -------------------------------------------------------------
    # 2. Construir el arbol y mostrar la raíz
    # -------------------------------------------------------------
    print("\n" + "-" * 65)
    input()
    print("[2] CONSTRUIR EL ARBOL Y MOSTRAR MERKLE ROOT:")
    arbol = MerkleTree(txs_originales)
    raiz_original = arbol.obtener_raiz().valor
    print(f"\nMerkle Root Original:\n>> {raiz_original}")
    print("\nDiagrama del arbol construido (estructura de ramas):")
    arbol.recorrer_arbol()
    print()

    # -------------------------------------------------------------
    # 3. Modificar una transacción y demostrar que la raíz cambia
    # -------------------------------------------------------------
    print("-" * 65)
    input()
    print("[3] MODIFICAR UNA TRANSACCION Y DEMOSTRAR CAMBIO DE RAIZ:")
    txs_modificadas = txs_originales.copy()
    txs_modificadas[1] = "Alejandro paga 5 a Charlie"  # Se modifica la Tx 2
    print(f"  Tx 2 original:  '{txs_originales[1]}'")
    print(f"  Tx 2 alterada:   '{txs_modificadas[1]}'")

    arbol_modificado = MerkleTree(txs_modificadas)
    raiz_modificada = arbol_modificado.obtener_raiz().valor
    print(f"\nNueva Merkle Root (con alteracion):\n>> {raiz_modificada}")
    print(f"\nSon iguales las raices? : {raiz_original == raiz_modificada}")
    print("    - Raiz Original =", raiz_original)
    print("    - Raiz Modificada =", raiz_modificada)
    diferencias = sum(1 for a, b in zip(raiz_original, raiz_modificada) if a != b)
    print(f"Caracteres diferentes entre ambas raices: {diferencias} de 64")
    print(">> EXITO: El error se dispersó por todo el arbol.")
    print()

    # -------------------------------------------------------------
    # 4. Generar prueba de inclusión para la transacción 3 y verificar
    # -------------------------------------------------------------
    print("-" * 65)
    input()
    print("[4] PRUEBA DE INCLUSION PARA LA TRANSACCION 3:")
    indice_tx3 = 2  # Tx 3 esta en indice 2
    tx3 = txs_originales[indice_tx3]
    print(f"  Transaccion objetivo: '{tx3}' (Indice: {indice_tx3})")

    prueba_tx3 = arbol.generar_prueba_inclusion(indice_tx3)
    print("\n  Pasos de la prueba de inclusion generada:")
    hash_actual = hash256(tx3)
    for paso, (direccion, hash_hermano) in enumerate(prueba_tx3, start=1):
        if paso == 1:
            print(f"    Paso {paso} (Nivel 1 / Hojas):")
            print(f"      * Hash hoja actual:                  {hash_actual[:16]}...")
            print(f"      * Hoja hermana a la {direccion.upper():<10}       -> {hash_hermano[:16]}...")
        else:
            print(f"\n    Paso {paso} (Nivel {paso}):")
            print(f"      * Hash anterior:                     {hash_actual[:16]}...")
            print(f"      * Hermano a la {direccion.upper():<15}      -> {hash_hermano[:16]}...")

        # Calcular el hash que sube al siguiente nivel
        if direccion == "derecha":
            hash_actual = hash256(hash_actual + hash_hermano)
        else:
            hash_actual = hash256(hash_hermano + hash_actual)
        
        es_raiz = (paso == len(prueba_tx3))
        etiqueta_res = "<> Hash resultante (Merkle Root):" if es_raiz else "<> Hash resultante:"
        print(f"      {etiqueta_res:<36} {hash_actual[:16]}...")

    # Verificacion
    es_valida = arbol.verificar_prueba(tx3, prueba_tx3, esTransacion=True)
    print(f"\n  Resultado de verificacion para Tx 3: {es_valida}")
    if es_valida:
        print("  >> EXITO: Prueba valida comprobada matematicamente (TRUE).")
    else:
        print("  >> ERROR: La prueba no coincidio.")
    print()

    # -------------------------------------------------------------
    # 5. Verificar con un dato incorrecto -> Debe fallar
    # -------------------------------------------------------------
    print("-" * 65)
    input()
    print("[5] VERIFICACION CON DATO INCORRECTO (DEBE FALLAR):")
    tx_falsa = "Charlie paga 9999 a David"  # Monto adulterado
    print(f"  Transaccion adulterada: '{tx_falsa}'")

    es_valida_falsa = arbol.verificar_prueba(tx_falsa, prueba_tx3, esTransacion=True)
    print(f"  Resultado de verificacion con dato falso: {es_valida_falsa}")
    if not es_valida_falsa:
        print("  >> EXITO: La verificacion fallo correctamente (FALSE) como se esperaba.")
    else:
        print("  >> ERROR: Se acepto un dato falso.")

    print()
    print("=" * 65 + "\n")

if __name__ == "__main__":
    test()