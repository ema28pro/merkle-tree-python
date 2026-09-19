# Explicación de Funciones y Clases Principales (`main.py`)

Este documento describe las responsabilidades y funcionamiento detallado de las clases y funciones implementadas en [main.py](main.py), el núcleo del Arbol de Merkle.


## 1. Función Criptográfica Base

### `hash256(data: str) -> str`
Calcula el resumen criptográfico **SHA-256** de una cadena de texto.

* **Parámetros:** `data` (cadena de texto a procesar, por ejemplo una transacción o la concatenación de dos hashes).
* **Retorno:** Una cadena hexadecimal de 64 caracteres.
* **Funcionamiento interno:**
  ```python
  def hash256(data: str) -> str:
      return sha256(data.encode('utf-8')).hexdigest()
  ```
  Codifica el texto en bytes bajo codificación UTF-8 y aplica la función hash estándar de la librería `hashlib`.


## 2. Clase `Nodo`

Modela un **nodo binario con enlaces bidireccionales** (punteros hacia hijos y hacia el padre). A diferencia de guardar solo listas de texto plano, esta clase representa físicamente el arbol en memoria.

### Atributos:
* `self.valor`: Hash SHA-256 almacenado en el nodo.
* `self.izquierda`: Referencia al nodo hijo izquierdo (o `None` si es hoja).
* `self.derecha`: Referencia al nodo hijo derecho (o `None` si es hoja).
* `self.padre`: Referencia al nodo ascendente directo (o `None` si es la raíz).

### Métodos principales:

#### `__init__(self, izquierda=None, derecha=None, valor=None)`
Constructor de clase que permite crear dos tipos de nodos:
1. **Nodos Hoja (Base):** Se les pasa un bloque de datos en `valor` (por ejemplo, el texto de la transacción). Calcula:
   $$\text{valor} = \text{hash256}(\text{transacción})$$
2. **Nodos Internos / Padres:** Se les pasan dos hijos (`izquierda` y `derecha`). Concatena los hashes de ambos y calcula el hash del padre:
   $$\text{valor} = \text{hash256}(\text{izquierda.valor} + \text{derecha.valor})$$

#### `asignar_padres(self)`
Establece la relación inversa asignándole a los hijos su referencia `padre = self`:
```python
if self.izquierda is not None:
    self.izquierda.padre = self
if self.derecha is not None:
    self.derecha.padre = self
```
> [!NOTE]
> Esta asignación es fundamental para la **prueba de inclusión**, ya que permite a una hoja ascender directamente hacia la raíz sin tener que buscar recursivamente desde la cima.

#### `__repr__(self)`, `__str__(self)` y `__eq__(self, other)` - Métodos especiales de clase
* `__repr__`: Retorna una versión recortada (`f" {self.valor[:8]}... "`) para que al imprimir listas de nodos en la consola sea legible.
* `__str__`: Retorna el hash completo de 64 caracteres cuando el nodo se imprime o se convierte a string.
* `__eq__`: Sobrecarga el operador de igualdad (`==`) para permitir comparar un `Nodo` tanto contra otro `Nodo` como directamente contra un `str`:
  ```python
  def __eq__(self, other):
      return (self.valor == other.valor) if isinstance(other, Nodo) else (self.valor == other)
  ```
  > [!TIP]
  > Gracias a este método, expresiones como `arbol.obtener_raiz() == hash_esperado` funcionan de forma transparente sin necesidad de extraer manualmente `.valor`.


## 3. Clase `MerkleTree`

Gestiona el ciclo de vida del arbol: construcción nivel por nivel, consulta de la raíz, generación de pruebas criptográficas y verificación de integridad.

### Atributos:
* `self.transacciones`: Lista con los bloques de datos originales.
* `self.niveles`: Lista de listas (`list[list[Nodo]]`), donde `self.niveles[0]` contiene las hojas y `self.niveles[-1]` contiene la raíz única.


### Métodos detallados:

### A. `construir_arbol(self)`
Construye el arbol de abajo hacia arriba (*bottom-up*).

1. **Nivel 0 (Hojas):** Transforma cada transacción de texto en un objeto `Nodo(valor=tx)`:
   ```python
   nodos = [Nodo(valor=tx) for tx in self.transacciones]
   self.niveles.append(nodos)
   ```
2. **Niveles superiores:** Mientras exista más de un nodo en el nivel actual:
   * Recorre la lista de dos en dos (`range(0, len(nodos), 2)`).
   * **Caso par:** Si tiene compañero (`i + 1 < len(nodos)`), crea el padre con `Nodo(nodos[i], nodos[i+1])`.
   * **Regla del nodo impar:** Si el último elemento queda solo, se duplica a sí mismo para formar pareja: `Nodo(nodos[i], nodos[i])`.
   * Agrega la nueva capa a `self.niveles` hasta llegar a una lista de longitud 1 (la raíz).


### B. `obtener_raiz(self) -> Nodo`
Retorna directamente el objeto **`Nodo` raíz** de la cima del arbol:
```python
def obtener_raiz(self):
    return self.niveles[-1][0]
```
Acceso instantáneo $O(1)$. Retornar el objeto `Nodo` en lugar de solo su string `.valor` resulta mucho más útil:
* Otorga acceso a la estructura completa del arbol y sus ramas (`raiz.izquierda`, `raiz.derecha`).
* Se imprime directamente como hash gracias a `__str__` y `__repr__`.
* Se compara directamente contra strings gracias a `__eq__`.


### C. `generar_prueba_inclusion(self, indice: int | str | list) -> list[tuple[str, str]] | list[list[tuple[str, str]]]`
Genera la ruta criptográfica de hashes hermanos necesaria para demostrar que una transacción pertenece al conjunto. Admite:
* Un **índice numérico** (`int`) de la hoja.
* Directamente el **texto plano de la transacción** (`str`).
* Una **lista** (`list`) de índices o transacciones para generar múltiples pruebas en lote (*batch*).

* **Funcionamiento:**
  1. **Procesamiento por lote:** Si `indice` es una lista (`list`), aplica recursión generando y retornando una lista con la prueba de cada elemento: `[self.generar_prueba_inclusion(item) for item in indice]`.
  2. **Detección de transacción por texto:** Si `indice` es una cadena (`str`), busca automáticamente la hoja cuyo hash coincida con `hash256(indice)`. Si no se encuentra en el arbol, imprime `"No se encontro la transaccion"` y retorna `-1`.
  3. **Control de rango y tipos inválidos:** Si el valor no es entero tras la búsqueda o se encuentra fuera del rango válido (`indice < 0 or indice >= len(self.transacciones)`), notifica `"Error al verificar la prueba"` y retorna `-1`.
  4. **Ubicación de la hoja:** Obtiene `actual = self.niveles[0][indice]`.
  5. Mediante un bucle `while actual.padre is not None`, sube por el arbol:
     * Si el nodo actual es el hijo **izquierdo**, su hermano necesario para concatenar está a la **derecha**:
       ```python
       prueba.append(("derecha", actual.padre.derecha.valor))
       ```
     * Si el nodo actual es el hijo **derecho**, su hermano necesario está a la **izquierda**:
       ```python
       prueba.append(("izquierda", actual.padre.izquierda.valor))
       ```
     * Sube un nivel: `actual = actual.padre`.
* **Retorno:** Una lista de tuplas `[("direccion", "hash_hermano"), ...]`.
* **Complejidad:** $O(\log N)$ pasos, requiriendo un número mínimo de hashes.


### D. `verificar_prueba(self, tx, prueba, esTransacion=False) -> bool`
Valida matemáticamente si una transacción pertenece al arbol recalculando la raíz a partir de la prueba.

* **Parámetros:**
  * `tx`: Puede ser el texto de la transacción (si `esTransacion=True`) o el índice de la hoja en el arbol (si `esTransacion=False`).
  * `prueba`: La lista de tuplas generada por `generar_prueba_inclusion`.
* **Lógica de verificación:**
  1. Obtiene el hash inicial `hash_actual = hash256(tx)`.
  2. Itera paso a paso combinando estrictamente según la posición del hermano:
     ```python
     for dir, hash_hermano in prueba:
         if dir == "derecha":
             hash_actual = hash256(hash_actual + hash_hermano)
         else:
             hash_actual = hash256(hash_hermano + hash_actual)
     ```
  3. Compara el resultado acumulado con la raíz del arbol:
     ```python
     return hash_actual == raiz
     ```

> [!IMPORTANT]
> **¿Por qué es indispensable respetar la dirección de concatenación?**
> La concatenación de texto **no es conmutativa**:
> $$\text{hash}(A + B) \neq \text{hash}(B + A)$$
> En una función criptográfica como SHA-256, invertir el orden de los hashes hermanos genera una entrada completamente distinta, y por el **efecto avalancha**, el hash resultante del padre será totalmente erróneo. Por ello, la prueba debe especificar con precisión si el hermano se concatena a la `"derecha"` o a la `"izquierda"` para reproducir fielmente la raíz original. Si un solo carácter de la transacción, un hash hermano o el orden se desordena o altera, la verificación retornará `False`.


### E. Métodos Visualizadores enlazados
La clase enlaza directamente las funciones gráficas del módulo [visualizador.py](visualizador.py):
* `arbol.recorrer_arbol()`: Muestra el recorrido en profundidad (DFS) en formato de ramas jerárquicas con conectores (`├──`, `└──`).
* `arbol.mostrar_arbol(hash_chars=6)`: Dibuja el arbol simétrico completo horizontalmente, con la raíz centrada en la cima y nodos centrado.


## 4. Función de Entrada Interactiva (`app()`)

Ubicada al final de [main.py](main.py), sirve como zona de pruebas local para instanciar arboles, comparar raíces entre transacciones legítimas y alteradas, calcular diferencias de caracteres por efecto avalancha e invocar el visualizador vertical.
