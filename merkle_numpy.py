import numpy as np
from hashlib import sha256

h = lambda x: sha256(str(x).encode()).hexdigest()

class MerkleTreeNP:
    """Árbol de Merkle implementado sobre un único arreglo estático de NumPy (tipo montículo/heap).
    
    Estructura en memoria contigua (tamaño fijo 2*M):
      - Raíz:          índice 1
      - Hijos de i:    2*i (izq) y 2*i + 1 (der)
      - Padre de pos:  pos // 2
      - Hermano:       pos ^ 1 (operador bitwise XOR)
      - Hojas:         índices desde M hasta 2*M - 1
    """

    def __init__(self, txs):
        self.n = len(txs)
        self.M = 1 << (self.n - 1).bit_length()  # Próxima potencia de 2 (ej. 5 -> 8)
        self.tree = np.empty(2 * self.M, dtype="<U64")  # Único arreglo estático de tamaño fijo

        # 1. Hojas en el rango [M, 2M-1] con duplicación estática del último elemento
        for i in range(self.M):
            self.tree[self.M + i] = h(txs[min(i, self.n - 1)])

        # 2. Construcción bottom-up de abajo hacia arriba en O(M)
        for i in range(self.M - 1, 0, -1):
            self.tree[i] = h(self.tree[2 * i] + self.tree[2 * i + 1])

        self.raiz = str(self.tree[1])

    def prueba(self, idx):
        """Genera la prueba de inclusión mediante aritmética de índices pura (XOR y // 2)."""
        p, pos = [], self.M + idx
        while pos > 1:
            dir_hermano = "derecha" if pos % 2 == 0 else "izquierda"
            p.append((dir_hermano, str(self.tree[pos ^ 1])))  # pos ^ 1 da el hermano directo
            pos //= 2  # Subir al padre
        return p

    def verificar(self, tx, prueba):
        """Verifica la prueba recalculando el camino hasta la raíz."""
        act = h(tx)
        for d, hm in prueba:
            act = h(act + hm) if d == "derecha" else h(hm + act)
        return act == self.raiz


# --- Demostración ---
if __name__ == "__main__":
    txs = [
        "Tomas paga 10 a Emanuel",
        "Emanuel paga 5 a Charlie",
        "Charlie paga 3 a David",
        "David paga 2 a Sofia",
        "Tomas paga 5 a Emanuel",
    ]

    arbol = MerkleTreeNP(txs)
    print("Merkle Root:", arbol.raiz)

    prueba_tx3 = arbol.prueba(2)
    print("Prueba Tx 3:", prueba_tx3)
    print("¿Tx 3 válida?:", arbol.verificar(txs[2], prueba_tx3))
    print("¿Dato adulterado falla?:", not arbol.verificar("Charlie paga 9999 a David", prueba_tx3))
