from hashlib import sha256

def h(x): return sha256(str(x).encode()).hexdigest()

class MerkleTree:
    def __init__(self, txs):
        self.niveles = [[h(t) for t in txs]] # Guarda en [0] los hashes de las hojas
        while len(self.niveles[-1]) > 1:
            n = self.niveles[-1] # n es el nivel actual
            if len(n) % 2: 
                n.append(n[-1])  # Regla del impar: duplicar último
            self.niveles.append([h(n[i] + n[i+1]) for i in range(0, len(n), 2)]) # Generar nivel superior combinando de 2 en 2
        self.raiz = self.niveles[-1][0]

    def prueba(self, idx):
        """Genera la prueba de inclusión subiendo niveles con división entera idx // 2."""
        p = [] # pruebas
        for n in self.niveles[:-1]: # recorremos la lista sin la raiz
            herm = idx - 1 if idx % 2 else (idx + 1 if idx + 1 < len(n) else idx) # Obtenemos el indice del hermano del actual
            p.append(("izquierda" if idx % 2 else "derecha", n[herm])) # guardamos la posicion y el hash del hermano
            idx //= 2 # actualizamos el indice para subir al siguiente nivel
        return p

    def verificar(self, tx, prueba):
        """Recalcula el camino para verificar la pertenencia."""
        act = h(tx) # hash de la transaccion a comprobar
        for d, hm in prueba:
            act = h(hm + act) if d == "izquierda" else h(act + hm) # se recalcula el hash con el hermano
        return act == self.raiz

# --- Ejemplo de uso ---
if __name__ == "__main__":
    txs = ["Tomas paga 10", "Emanuel paga 5", "Charlie paga 3", "David paga 2", "Tomas paga 5"]
    arbol = MerkleTree(txs)
    
    print("Merkle Root:       ", arbol.raiz)
    prueba_tx3 = arbol.prueba(2)
    dato_falso = "Charlie paga 0"
    print(txs[2], " >>  ¿Tx 3 válida?:      ", arbol.verificar(txs[2], prueba_tx3))
    print(dato_falso, " >>  ¿Dato falso falla?: ", not arbol.verificar(dato_falso, prueba_tx3))