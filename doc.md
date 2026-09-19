# Arbol de Merkle
Este laboratorio consiste en implementar una de las estructuras de datos criptográficas más importantes de la computación distribuida y blockchain (usada en Bitcoin, Git, etc.): el **Arbol de Merkle**.

A continuación tienes una explicación detallada de cómo funciona cada parte y qué te están pidiendo exactamente en el experimento.

---

### 1. ¿Qué es un Arbol de Merkle?

Un **Arbol de Merkle** es un arbol binario donde los datos reales solo están en la base (las hojas), y cada nodo superior es un resumen criptográfico (**hash SHA-256**) de sus hijos.

```
                  [ Merkle Root ]              <- Nivel 0 (Raíz única)
                     /         \
              [ Hash AB ]   [ Hash C_duplicado ] <- Nivel 1 (Nodos internos)
                /     \       /     \
             [H(A)]  [H(B)] [H(C)] [H(C)]      <- Nivel 2 (Hojas)
               |       |      |      |
             Tx_A    Tx_B   Tx_C   Tx_C        <- Datos base (Transacciones)
```

---

### 2. Desglose de las Especificaciones

1. **Cada hoja contiene el hash SHA-256 de un bloque de datos:**
   * Si tienes la transacción $T_1 = \text{"Alice paga 5 a Bob"}$, la hoja no guarda el texto, guarda:
     $$\text{Hoja}_1 = \text{SHA-256}(T_1)$$

2. **Cada nodo interno contiene el hash de la concatenación de sus dos hijos:**
   * Si un nodo padre tiene dos hijos con hashes $H_{\text{izq}}$ y $H_{\text{der}}$, el padre será:
     $$H_{\text{padre}} = \text{SHA-256}(H_{\text{izq}} + H_{\text{der}})$$

3. **Si el número de hojas o ramas es impar, la última se duplica:**
   * Para formar parejas en un arbol binario, necesitas un número par de elementos.
   * Si tienes 5 transacciones $[H_1, H_2, H_3, H_4, H_5]$, el elemento $H_5$ no tiene pareja. Por tanto, se duplica: $[H_1, H_2, H_3, H_4, H_5, \mathbf{H_5}]$.
   * Se combinan en parejas de dos:
     * Padre 1 = $\text{Hash}(H_1 + H_2)$
     * Padre 2 = $\text{Hash}(H_3 + H_4)$
     * Padre 3 = $\text{Hash}(H_5 + H_5)$
   * Ahora tienes 3 padres (vuelve a ser impar). Para el siguiente nivel, Padre 3 se vuelve a duplicar con sí mismo.

4. **La raíz (Merkle Root):**
   * Es el único hash que queda al final, en la cima del arbol.
   * Representa una **huella digital única de todo el conjunto de datos**. Gracias al *efecto avalancha* de SHA-256, si cambia un solo carácter en una sola transacción, todos los hashes hacia arriba cambian drásticamente y la raíz final será completamente distinta.

> [!NOTE]
> **Detalle de implementación en Python (`.encode()` y `.hexdigest()`):**
> * **`.encode()`:** Las funciones hash procesan secuencias de bytes binarios (`bytes`), no strings abstractos. `.encode()` traduce el texto a bytes (UTF-8 predeterminado) para que el algoritmo pueda procesarlo. Sin él, Python lanza `TypeError: Unicode-objects must be encoded before hashing`.
> * **`.hexdigest()`:** El resultado directo de SHA-256 son 32 bytes binarios no legibles (`.digest()`). `.hexdigest()` convierte esa salida a una cadena de texto (`str`) de 64 caracteres hexadecimales (`0-9, a-f`), permitiendo concatenar (`H_izq + H_der`), imprimir en consola y comparar directamente con `==`.

---

### 3. ¿Qué es una Prueba de Inclusión (Merkle Proof)?

Es la característica más potente de un Arbol de Merkle: **demostrar que una transacción pertenece al conjunto sin tener que descargar ni revisar todas las demás transacciones**.

Imagina que tienes 5 transacciones y quieres demostrarle a alguien que la **Transacción 3 ($T_3$)** existe en el arbol y es válida:
* La otra persona **solo conoce la Merkle Root**.
* Tú le entregas:
  1. El dato de $T_3$.
  2. La **ruta de prueba** (los hashes "hermanos" necesarios para subir por el arbol).
     * En este caso, necesitará el hash hermano de $H_3$ (que es $H_4$) y el hash hermano de su padre.
* El verificador hace los hashes hacia arriba paso a paso.
* Si el resultado final coincide exactamente con la **Merkle Root**, queda demostrado matemáticamente que $T_3$ forma parte del arbol.

---

### 4. Planteamiento de la solucion

1. **Crear 5 transacciones simuladas:**
   * Por ejemplo: strings simples como `"Tx1: Alice -> Bob 10"`, `"Tx2: Bob -> Charlie 5"`, etc.
2. **Construir el arbol y mostrar la raíz:**
   * Procesar las 5 transacciones (aplicando la regla del impar), calcular nivel por nivel hasta la raíz e imprimir el hash resultante (Merkle Root).
3. **Modificar una transacción y demostrar que la raíz cambia:**
   * Cambiar por ejemplo `"Tx1: Alice -> Bob 10"` por `"Tx1: Alice -> Bob 99"`.
   * Recalcular el arbol y mostrar que la nueva raíz es completamente diferente a la original (evidencia de no repudio / detección de alteraciones).
4. **Generar prueba de inclusión para la Transacción 3 y verificarla:**
   * Generar los hashes hermanos que acompañan a la Transacción 3.
   * Ejecutar una función `verificar(tx3, prueba, merkle_root)` que devuelva `True` (válida).
5. **Verificar con un dato incorrecto:**
   * Pasar una transacción falsa (ej. `"Tx3 falsa"`) con la misma prueba y la raíz original.
   * La función `verificar` debe recalcular una raíz errónea y devolver `False` (debe fallar).

---

### 5. Extensiones Modernas y Estado del Arte

En la computación distribuida y la criptografía moderna, el árbol de Merkle clásico ha evolucionado hacia estructuras más sofisticadas para resolver problemas de escalabilidad, almacenamiento y privacidad:

---

#### 5.1. Merkle Patricia Tries (MPT) — El motor de Ethereum
Mientras que Bitcoin utiliza un árbol de Merkle binario estático para transacciones dentro de cada bloque, **Ethereum** necesita gestionar el estado global dinámico de millones de cuentas (balances, almacenamiento de contratos inteligentes, noce de transacción).

* **Concepto:** Combina un *Radix/Patricia Trie* (árbol de prefijos optimizado para claves tipo diccionario `clave -> valor`) con hashes criptográficos de Merkle.
* **Aplicación:** Cada bloque de Ethereum incluye tres raíces de MPT:
  1. **State Root:** El estado de todas las cuentas y sus balances.
  2. **Transactions Root:** Lista de transacciones del bloque actual.
  3. **Receipts Root:** Recibos y eventos emitidos por los contratos.
* **Ventaja:** Permite autenticar cualquier dato tipo clave-valor (`¿Tiene Alicia 10 ETH?`) mediante una prueba criptográfica que recorre la clave hexadecimal.

---

#### 5.2. Verkle Trees — La frontera de la escalabilidad y clientes sin estado
Los **Verkle Trees** (creados por John Kuszmaul y adoptados en el roadmap de Ethereum por Vitalik Buterin) representan la mayor revolución sobre los árboles de Merkle en décadas:

* **El problema de Merkle:** En un árbol de Merkle binario con mil millones de elementos, la ruta de prueba requiere alrededor de 30 hashes ($\log_2 N$). Para verificar múltiples hojas a la vez, el tamaño de las pruebas crece a cientos de kilobytes, saturando el ancho de banda de la red.
* **La solución de Verkle:** Sustituye las funciones hash tradicionales por **compromisos vectoriales polinomiales** (como *KZG Polynomial Commitments* o *IPA/Inner Product Arguments*).
* **Impacto:**
  * Un nodo interno puede tener un factor de ramificación masivo (por ejemplo, 256 hijos en lugar de 2).
  * La prueba de inclusión para un conjunto de datos se comprime en un único compromiso de **tamaño constante sub-kilobyte** (~150 bytes), independiente de la cantidad de datos.
  * **Habilita los *Stateless Clients*:** Nodos ligeros en teléfonos móviles que pueden validar transacciones instantáneamente sin almacenar el historial de la blockchain.

---

#### 5.3. Pruebas de Merkle en Conocimiento Cero (zk-SNARKs / zk-Rollups)
En los sistemas de Capa 2 (L2 como *Starknet, zkSync, Scroll*) y protocolos de privacidad (como *Zcash* o *Tornado Cash*):

* **Verificación dentro de un circuito ZK:** La verificación de una prueba de inclusión se ejecuta matemáticamente dentro de un circuito aritmético de conocimiento cero.
* **Privacidad total (Anonimato):** Un usuario puede demostrar matemáticamente:
  $$\text{"Sé que pertenezco a la lista de usuarios válidos del árbol, pero no te diré qué hoja soy ni cuál es mi clave pública"}$$
* **Escalabilidad (Rollups):** Se agrupan miles de transacciones fuera de la cadena principal (*off-chain*), se calcula la nueva raíz de Merkle y se envía a la red principal únicamente una prueba criptográfica sucinta de validez de unos pocos cientos de bytes.

---

#### 5.4. Sparse Merkle Trees (SMT) y Pruebas de No-Inclusión
Un **Árbol de Merkle Disperso** es un árbol conceptualmente gigantesco de $2^{256}$ hojas (el mismo número de posibles hashes SHA-256), donde la inmensa mayoría de las hojas están vacías (con valor cero).

* **Prueba de No-Inclusión (*Non-membership proof*):** Permite demostrar con certeza matemática no solo que un registro **existe**, sino también que un registro **NO existe** en el conjunto de datos.
* **Optimización en memoria:** Los subárboles vacíos comparten hashes precalculados conocidos por defecto, por lo que solo se instancian en memoria los nodos con información real.

---

#### 5.5. Vulnerabilidad histórica: Maleabilidad por duplicación impar (CVE-2012-2459 de Bitcoin)
La regla de duplicar el último nodo cuando un nivel es impar (implementada en este laboratorio siguiendo el estándar clásico) causó un fallo histórico de seguridad en Bitcoin:

> [!WARNING]
> **Vulnerabilidad de Maleabilidad de Bloques (CVE-2012-2459):**
> Si se tienen las transacciones $[A, B, C]$, al aplicar la regla del impar se procesa como $[A, B, C, C]$.
> Si un atacante tomaba un bloque válido y agregaba intencionalmente la transacción $C$ repetida, $[A, B, C, C]$ generaba **exactamente la misma Merkle Root**.
> Esto permitía a atacantes mutar identificadores de bloques válidos e inyectar bloques huérfanos para provocar denegaciones de servicio (DoS) a nodos de la red.

* **Mitigación moderna:** En implementaciones modernas de alto rendimiento se utiliza **Separación de Dominios** (*Domain Separation*), prefijando los datos antes de hashear:
  * Hojas: $\text{Hash}(0x00 \ || \ \text{dato})$
  * Nodos internos: $\text{Hash}(0x01 \ || \ H_{\text{izq}} \ || \ H_{\text{der}})$
  Esto previene ataques de segunda preimagen y colisiones entre hojas y ramas.

---

#### 5.6. Tabla Comparativa

| Estructura | Complejidad Prueba | Tamaño de Prueba | Pruebas de No-Inclusión | Caso de Uso Principal |
| :--- | :---: | :---: | :---: | :--- |
| **Árbol de Merkle Estándar** | $O(\log_2 N)$ | Mediano (~1-2 KB) | No | Bitcoin, Git, Apache Cassandra |
| **Merkle Patricia Trie (MPT)** | $O(\log_{16} N)$ | Mediano (~3-5 KB) | Sí | Estado de Ethereum, IPFS |
| **Sparse Merkle Tree (SMT)** | $O(256)$ | Fijo (~8 KB) | Sí | Cuentas revocadas, Identity Trees |
| **Verkle Tree** | $O(\log_{256} N)$ | **Mínimo (~150 B)** | Sí | Ethereum Statelessness, Rollups |