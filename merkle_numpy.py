import numpy as np
from hashlib import sha256
import time


def hash256(data: str) -> str:
    """Calcula el hash SHA-256 en formato hexadecimal."""
    return sha256(data.encode("utf-8")).hexdigest()


class MerkleTreeNumPy:
    """Implementación optimizada y simplificada de Árbol de Merkle con NumPy.
    
    A diferencia de la versión enlazada con objetos `Nodo` y punteros bidireccionales,
    esta versión almacena cada nivel como un arreglo NumPy 1D contiguo (dtype='<U64').
    
    Toda la navegación se realiza por ARITMÉTICA DE ÍNDICES en tiempo O(1):
      - Padre en nivel superior:  padre_idx = i // 2
      - Hermano en el nivel:      hermano_idx = (i + 1) si es izquierdo, (i - 1) si es derecho
      - Dirección de concatenar:  "derecha" si (i % 2 == 0) else "izquierda"
    """

    def __init__(self, transacciones):
        self.transacciones = list(transacciones)
        self.niveles = []  # Lista de arreglos 1D de numpy (uno por cada nivel)
        self.construir_arbol()

    def construir_arbol(self):
        """Construye el árbol nivel por nivel usando arreglos de NumPy."""
        if not self.transacciones:
            raise ValueError("La lista de transacciones no puede estar vacía.")

        # Nivel 0 (Hojas): Convertir transacciones a hashes y almacenar en array de NumPy
        hojas = np.array([hash256(tx) for tx in self.transacciones], dtype="<U64")
        self.niveles.append(hojas)

        actual = hojas
        while len(actual) > 1:
            n = len(actual)
            num_padres = (n + 1) // 2
            padres = np.empty(num_padres, dtype="<U64")

            # Combinar en parejas de dos
            for i in range(0, n, 2):
                izq = actual[i]
                # Regla del impar: si el último no tiene pareja, se duplica a sí mismo
                der = actual[i + 1] if (i + 1 < n) else actual[i]
                padres[i // 2] = hash256(izq + der)

            self.niveles.append(padres)
            actual = padres

    def obtener_raiz(self) -> str:
        """Retorna el hash de la raíz (Merkle Root) en O(1)."""
        return str(self.niveles[-1][0])

    def generar_prueba_inclusion(self, indice):
        """Genera la prueba de inclusión mediante aritmética de índices en O(log N).
        
        Admite:
          - Índice entero (int).
          - Texto de la transacción (str).
          - Lista de transacciones o índices (list) para procesamiento por lote.
        """
        # Procesamiento por lote (batch)
        if isinstance(indice, list):
            return [self.generar_prueba_inclusion(item) for item in indice]

        # Búsqueda si se pasa una cadena
        if isinstance(indice, str):
            h_buscado = hash256(indice)
            coincidencias = np.where(self.niveles[0] == h_buscado)[0]
            if len(coincidencias) == 0:
                print("No se encontro la transaccion")
                return -1
            indice = int(coincidencias[0])

        elif not isinstance(indice, (int, np.integer)) or indice < 0 or indice >= len(self.transacciones):
            print("Error al verificar la prueba")
            return -1

        prueba = []
        pos = int(indice)

        # Subir nivel por nivel mediante cálculo aritmético de índices
        for l in range(len(self.niveles) - 1):
            nivel_actual = self.niveles[l]
            n = len(nivel_actual)

            if pos % 2 == 0:
                # Nodo izquierdo: hermano a la derecha (si existe, o duplicado)
                hermano_hash = nivel_actual[pos + 1] if (pos + 1 < n) else nivel_actual[pos]
                prueba.append(("derecha", str(hermano_hash)))
            else:
                # Nodo derecho: hermano a la izquierda
                hermano_hash = nivel_actual[pos - 1]
                prueba.append(("izquierda", str(hermano_hash)))

            # Subir al padre en el siguiente nivel: pos // 2
            pos = pos // 2

        return prueba

    def verificar_prueba(self, tx, prueba, esTransaccion=False) -> bool:
        """Verifica una prueba de inclusión recalculando la raíz paso a paso."""
        if prueba == -1 or not isinstance(prueba, list):
            return False

        if esTransaccion:
            hash_actual = hash256(tx)
        else:
            if not isinstance(tx, (int, np.integer)) or tx < 0 or tx >= len(self.transacciones):
                return False
            hash_actual = str(self.niveles[0][tx])

        for direccion, hash_hermano in prueba:
            if direccion == "derecha":
                hash_actual = hash256(hash_actual + hash_hermano)
            else:
                hash_actual = hash256(hash_hermano + hash_actual)

        return hash_actual == self.obtener_raiz()

    def mostrar_resumen(self):
        """Imprime un resumen tabular de los niveles almacenados en NumPy."""
        print("\n" + "=" * 60)
        print("         ARBOL DE MERKLE (VERSION NUMPY / ARREGLOS)        ")
        print("=" * 60)
        print(f"Total de niveles: {len(self.niveles)}")
        print(f"Merkle Root:      {self.obtener_raiz()}\n")
        for i, nivel in enumerate(self.niveles):
            etiqueta = "Hojas (Base)" if i == 0 else ("Raiz" if i == len(self.niveles) - 1 else f"Nivel {i}")
            hashes_cortos = [f"{h[:6]}.." for h in nivel]
            print(f" [{i}] {etiqueta:<14} ({len(nivel)} nodos): {hashes_cortos}")
        print("=" * 60 + "\n")


# =====================================================================
# Demostración y Benchmark Comparativo
# =====================================================================
if __name__ == "__main__":
    txs = [
        "Tomas paga 10 a Emanuel",
        "Emanuel paga 5 a Charlie",
        "Charlie paga 3 a David",
        "David paga 2 a Sofia",
        "Tomas paga 5 a Emanuel",
    ]

    print("\n--- 1. Construcción con NumPy ---")
    arbol_np = MerkleTreeNumPy(txs)
    arbol_np.mostrar_resumen()

    print("--- 2. Prueba de Inclusión para Transacción 3 ---")
    prueba_tx3 = arbol_np.generar_prueba_inclusion(2)
    print(f"Prueba generada ({len(prueba_tx3)} pasos):")
    for paso, (dir, h) in enumerate(prueba_tx3, 1):
        print(f"  Paso {paso}: Hermano a la {dir:<9} -> {h[:16]}...")

    valida = arbol_np.verificar_prueba(txs[2], prueba_tx3, esTransaccion=True)
    print(f"\n¿Verificación válida (Tx 3)?: {valida}")

    invalida = arbol_np.verificar_prueba("Charlie paga 9999 a David", prueba_tx3, esTransaccion=True)
    print(f"¿Verificación con dato falso?: {invalida}")

    # Benchmark: 10,000 transacciones
    print("\n" + "-" * 60)
    print("  BENCHMARK: 10,000 transacciones (NumPy vs Nodos Dinámicos)")
    print("-" * 60)
    txs_grandes = [f"Tx {i}: Usuario_{i} paga {i * 1.5} a Destino_{i}" for i in range(10000)]

    # Test NumPy
    t0 = time.time()
    t_np = MerkleTreeNumPy(txs_grandes)
    t_np_total = time.time() - t0
    print(f"  * Versión NumPy:            {t_np_total:.4f} s | Raíz: {t_np.obtener_raiz()[:16]}...")

    # Test Nodos ligados (main.py)
    try:
        from main import MerkleTree as MerkleTreeOriginal
        import io, contextlib
        t0 = time.time()
        with contextlib.redirect_stdout(io.StringIO()):
            t_orig = MerkleTreeOriginal(txs_grandes)
        t_orig_total = time.time() - t0
        print(f"  * Versión Nodos Dinámicos:  {t_orig_total:.4f} s | Raíz: {t_orig.obtener_raiz().valor[:16]}...")
        
        # Comparación de integridad
        coinciden = (t_np.obtener_raiz() == t_orig.obtener_raiz().valor)
        print(f"\n  >> ¿Ambas versiones producen exactamente la misma raíz?: {coinciden}")
    except Exception as e:
        print(f"  No se pudo comparar con main.py: {e}")
