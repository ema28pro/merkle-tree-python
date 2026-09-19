import numpy as np
from hashlib import sha256

h = lambda x: sha256(str(x).encode()).hexdigest()

class MerkleTreeNP:
    def __init__(self, txs):
        # Nivel 0 con los hashes de las transacciones
        self.niveles = [np.array([h(t) for t in txs])]
        while len(self.niveles[-1]) > 1:
            n = self.niveles[-1]
            if len(n) % 2:  # Regla del impar: duplicar último
                n = np.append(n, n[-1])
            # Generar siguiente nivel combinando pares usando slicing de NumPy [0::2] y [1::2]
            self.niveles.append(np.array([h(a + b) for a, b in zip(n[0::2], n[1::2])]))
        self.raiz = self.niveles[-1][0]

    def prueba(self, idx):
        """Genera la prueba de inclusión subiendo por los niveles con idx // 2."""
        p = []
        for n in self.niveles[:-1]:
            herm = idx - 1 if idx % 2 else (idx + 1 if idx + 1 < len(n) else idx)
            p.append(("izquierda" if idx % 2 else "derecha", str(n[herm])))
            idx //= 2
        return p

    def verificar(self, tx, prueba):
        """Verifica una prueba recalculando la raíz."""
        act = h(tx)
        for d, hm in prueba:
            act = h(hm + act) if d == "izquierda" else h(act + hm)
        return act == self.raiz


# --- Ejemplo de uso ---
if __name__ == "__main__":
    txs = ["Tomas paga 10", "Emanuel paga 5", "Charlie paga 3", "David paga 2", "Tomas paga 5"]
    arbol = MerkleTreeNP(txs)
    
    print("Merkle Root:        ", arbol.raiz)
    prueba_tx3 = arbol.prueba(2)
    print("¿Tx 3 válida?:      ", arbol.verificar(txs[2], prueba_tx3))
    print("¿Dato falso falla?: ", not arbol.verificar("Tx 3 adulterada", prueba_tx3))
