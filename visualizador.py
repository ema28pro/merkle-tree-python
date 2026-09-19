def recorrer_arbol(self, nodo=None, prefijo="", es_izq=None):
    """Recorre el arbol mostrando todas sus ramas y hojas en consola."""
    # Si no se pasa nodo, empezamos desde la raíz del arbol
    if nodo is None:
        nodo = self.niveles[-1][0]
        print(f"Raiz: {nodo.valor[:12]}...")
        if nodo.izquierda:
            self.recorrer_arbol(nodo.izquierda, "", es_izq=True)
        if nodo.derecha:
            self.recorrer_arbol(nodo.derecha, "", es_izq=False)
        return
    # Dibujar ramas con conectores bonitos compatibles con Windows
    conector = "├── [Izq] " if es_izq else "└── [Der] "
    # conector = "|-- [Izq] " if es_izq else "\\-- [Der] " # Si no funciona el de arriba usa estos
    tipo = "(Hoja)" if nodo.izquierda is None else "(Rama)"
    print(prefijo + conector + f"{tipo} {nodo.valor[:10]}...")
    # nuevo_prefijo = prefijo + ("|   " if es_izq else "    ")
    nuevo_prefijo = prefijo + ("│   " if es_izq else "    ") # Lo mismo aca
    if nodo.izquierda:
        self.recorrer_arbol(nodo.izquierda, nuevo_prefijo, es_izq=True)
    if nodo.derecha:
        self.recorrer_arbol(nodo.derecha, nuevo_prefijo, es_izq=False)


def armar_fila(elementos):
    """Arma una fila directamente: recibe lista de tuplas (posicion_x, texto)"""
    linea, cursor = "", 0
    for pos, texto in elementos:
        ini = pos - len(texto) // 2
        linea += " " * (ini - cursor) + texto
        # print(linea)
        cursor = ini + len(texto)
    return linea


def mostrar_arbol(self, hash_chars=6, usa_unicode=True):
    """Muestra el arbol de forma vertical centrada con la raíz en la cima y espacios calculados,
    expandiendo completamente las ramas duplicadas cuando cualquier nivel es impar."""
    niveles = self.niveles
    if not niveles:
        print("Arbol vacío.")
        return

    import sys
    # Detectar compatibilidad con caracteres unicode de dibujo de cajas
    if usa_unicode:
        try:
            "┌─┴─┐│".encode(sys.stdout.encoding or "utf-8")
        except Exception:
            usa_unicode = False

    c_izq_sym = "┌" if usa_unicode else "+" # esquina izquierda
    c_der_sym = "┐" if usa_unicode else "+" # esquina derecha
    c_padre_sym = "┴" if usa_unicode else "^" # union
    c_horiz = "─" if usa_unicode else "-"
    c_vert = "│" if usa_unicode else "|"

    # 1. Obtener la jerarquía completa del arbol desde la raíz (BFS)
    root = niveles[-1][0]
    curr = [root]
    levels_down = []
    while curr:
        levels_down.append(curr)
        nxt = []
        has_children = False
        for n in curr:
            if n and (n.izquierda or n.derecha):
                has_children = True
                nxt.append(n.izquierda)
                nxt.append(n.derecha)
                # Cuando un nodo viene de un duplicado, sus hijos son el mismo duplicado, asi que no tenemos que duplicarlos en nxt
        if not has_children:
            break
        curr = nxt
    print(levels_down)

    # Niveles invertidos: índice 0 son las hojas (base) y el último es la raíz
    niveles_completos = list(reversed(levels_down))
    num_hojas = len(niveles_completos[0])
    slot_w = max(11, hash_chars + 5) # Ancho minimo mas espacio parentesis, espaciado y len(hash_mostrado)
    total_w = num_hojas * slot_w

    # 2. Calcular coordenadas centrales de cada nodo en la pantalla
    posiciones = []
    pos_0 = [i * slot_w + slot_w // 2 for i in range(num_hojas)]
    posiciones.append(pos_0)

    for l in range(1, len(niveles_completos)):
        pos_l = []
        hijos_pos = posiciones[l - 1]
        # print(pos_l, hijos_pos)
        for k in range(len(niveles_completos[l])):
            c_izq = hijos_pos[2 * k]
            c_der = hijos_pos[2 * k + 1]
            # print("-", c_izq, c_der)
            pos_l.append((c_izq + c_der) // 2)
        # print(pos_l, hijos_pos)
        posiciones.append(pos_l)

    print("\n" + "=" * total_w)
    print("VISUALIZACION DEL ARBOL DE MERKLE".center(total_w))
    print("=" * total_w + "\n")

    # 3. Imprimir de arriba (raíz) hacia abajo (hojas)
    for l in range(len(niveles_completos) - 1, -1, -1):
        if l == len(niveles_completos) - 1:
            tag = "(Raiz)"
            print(armar_fila([(posiciones[l][0], tag)]))

        # Fila de nodos (posicion, hash_reducido)
        items = [(posiciones[l][k], f"[{nodo.valor[:hash_chars]}]") for k, nodo in enumerate(niveles_completos[l])]
        print(armar_fila(items))

        # Conectores hacia el nivel inferior (ramas y verticales directas)
        # Ayuda de la IA
        if l > 0:
            hijos_pos = posiciones[l - 1]
            linea_c1, linea_c2 = "", ""
            cur1, cur2 = 0, 0
            for k in range(len(niveles_completos[l])):
                c_p = posiciones[l][k]
                c_izq = hijos_pos[2 * k]
                c_der = hijos_pos[2 * k + 1]

                # Rama horizontal con unión al padre
                rama = c_izq_sym + c_horiz * (c_p - c_izq - 1) + c_padre_sym + c_horiz * (c_der - c_p - 1) + c_der_sym
                linea_c1 += " " * (c_izq - cur1) + rama
                cur1 = c_izq + len(rama)

                # Caídas verticales
                linea_c2 += " " * (c_izq - cur2) + c_vert + " " * (c_der - c_izq - 1) + c_vert
                cur2 = c_der + 1

            print(linea_c1)
            print(linea_c2)

    # 4. Fila de transacciones debajo de las hojas
    num_orig = len(self.transacciones) # Sin los duplicados
    # Como ya estan calculadas las posiciones de las hojas solo tenemos que construir las tuplas
    items_tx = [(posiciones[0][i], f"Tx {i + 1}" if i < num_orig else f"Tx {num_orig}D") for i in range(num_hojas)]
    # print(items_tx)
    print(armar_fila(items_tx))
    print("-" * total_w + "\n")

recorrer_arbol_horizontal = mostrar_arbol