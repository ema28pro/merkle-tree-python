from hashlib import sha256
from visualizador import recorrer_arbol, mostrar_arbol

def hash256(data: str) -> str:
    """Calcula el hash SHA-256 de un texto."""
    return sha256(data.encode('utf-8')).hexdigest()

class MerkleTree:
    recorrer_arbol, mostrar_arbol = recorrer_arbol, mostrar_arbol

    def __init__(self, transacciones):
        self.transacciones = transacciones
        self.niveles = []
        self.construir_arbol()

    def construir_arbol(self):
        nodos = [Nodo(valor = tx) for tx in self.transacciones] # Guardamos el primer nivel
        self.niveles.append(nodos)
        print(nodos) # Mostrar cada nivel
        while len(nodos) > 1:
            nuevas_nodos = []
            for i in range(0, len(nodos), 2): # Vamos recorriendo lso niveles para hacer el siguiente
                if i + 1 < len(nodos):
                    nuevas_nodos.append(Nodo(nodos[i], nodos[i+1]))
                else: # Para este caso el ultimo queda solo si es un numero impar de nodos/hojas
                    nuevas_nodos.append(Nodo(nodos[i], nodos[i]))
            nodos = nuevas_nodos
            self.niveles.append(nodos)
            print(nodos) # Mostrar cada nivel

    def obtener_raiz(self): return self.niveles[-1][0]   
    
    def mostrar_niveles(self):
        niveles = self.niveles
        for i in range(len(niveles)):
            j = niveles[i]
            print(f"nivel {i}")
            for k in j:
                print(" - ", k)
            print("\n")
    
    def generar_prueba_inclusion(self, indice):
        if isinstance(indice, list):
            return [self.generar_prueba_inclusion(item) for item in indice]
        elif isinstance(indice, str):
            for i in range(len(self.niveles[0])):
                if self.niveles[0][i] == hash256(indice):
                    indice = i
                    break
            if not isinstance(indice, int):
                print("No se encontro la transaccion")
                return -1
        elif not isinstance(indice, int) or indice < 0 or indice >= len(self.transacciones):
            print("Error al verificar la prueba")
            return -1

        hojas = self.niveles[0]
        prueba = []
        actual = hojas[indice]
        while actual.padre is not None:
            if actual == actual.padre.izquierda: # Si esta en la izquierda ponemos a su hermano a la derecha
                prueba.append(("derecha", actual.padre.derecha.valor))
            else: #Si esta a la derecha ponemos a su hermano a la izquierda
                prueba.append(("izquierda", actual.padre.izquierda.valor))
            actual = actual.padre
        return prueba
    
    def verificar_prueba(self, tx, prueba, esTransacion = False):
        raiz = self.obtener_raiz()
        if not esTransacion: # Se nos paso el indice del nodo que queremos verificar
            hash_actual = self.niveles[0][tx].valor
        elif esTransacion:
            hash_actual = hash256(tx) # Se nos paso la transaccion que queremos verificar
        else:
            print("Error al verificar la prueba")
        
        for dir, hash_hermano in prueba:
            if dir == "derecha":
                hash_actual = hash256(hash_actual + hash_hermano)
            else:
                hash_actual = hash256(hash_hermano + hash_actual)
        return hash_actual == raiz

class Nodo:
    def __init__(self, izquierda = None, derecha = None, valor = None): # Guardamos los hijos del nodo
        self.valor = hash256( (izquierda.valor + derecha.valor) if valor is None else valor) # Lo calculamos aca rapidamente
        self.izquierda = izquierda
        self.derecha = derecha
        self.padre = None
        self.asignar_padres()
    
    def asignar_padres(self): # Le asigna el padre a los hijos
        if self.izquierda is not None:
            self.izquierda.padre = self
        if self.derecha is not None:
            self.derecha.padre = self

    def __repr__(self): return f" {self.valor[:8]}... " # Mostramos los primeros 8 o 10 caracteres del hash para que sea legible. Cuando se imprime desde una lista se usa este

    def __str__(self): return self.valor # Cuando se imprime el elemneto se muestra asi

    def __eq__(self, other): return (self.valor == other.valor) if isinstance(other, Nodo) else (self.valor == other)
    # Permite comparar directamente contra un str

transacciones1 = ["Tomas paga 10 a Emanuel", "Emanuel paga 5 a Charlie", "Charlie paga 3 a David", "David paga 2 a Sofia", "Tomas paga 5 a Emanuel"]
transacciones2 = ["Tomas paga 10 a Emanuel", "Alejandro paga 5 a Charlie", "Charlie paga 3 a David", "David paga 2 a Sofia", "Tomas paga 5 a Emanuel"]

# Se cambio la segunda Transaccion
def app(): # Aca podemos probar lo que queramos con los arboles 
    print("Pasos Ejemplo 1")
    arbol1 = MerkleTree(transacciones1)
    print("Pasos Ejemplo 2")
    arbol2 = MerkleTree(transacciones2)
    print("\nComparacion")
    print("Ejemplo 1", arbol1.obtener_raiz())
    print("Ejemplo 2", arbol2.obtener_raiz())
    str1 = arbol1.obtener_raiz().valor
    str2 = arbol2.obtener_raiz().valor
    print("Diferencias:", sum(1 for a, b in zip(str1, str2) if a != b), "de", len(str1), "caracteres")

    # arbol1.recorrer_arbol()
    # a = arbol1.generar_prueba_inclusion(0)
    # print(a)
    # print(arbol1.verificar_prueba("Tomas paga 10 a Emanuel", a, True))
    # # Otras formas de ver el arbol
    # print("-"*60)
    # print(arbol1.transacciones)
    # arbol1.mostrar_niveles()
    # arbol1.recorrer_arbol()
    # arbol1.mostrar_arbol(hash_chars=14)

if __name__ == "__main__":
    # from test import test
    # test()
    app()