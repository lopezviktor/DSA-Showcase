+----------------------+---------------------------+---------------------------+
| Feature              | Stack (Pila)              | Queue (Cola)              |
+----------------------+---------------------------+---------------------------+
| Tipo                 | LIFO                      | FIFO                      |
|                      | Last In, First Out        | First In, First Out       |
+----------------------+---------------------------+---------------------------+
| Uso típico           | Backtracking, undo/redo,  | Procesamiento en orden,   |
|                      | llamadas recursivas       | schedulers, buffers       |
+----------------------+---------------------------+---------------------------+
| Inserción            | push(item)                | enqueue(item)             |
|                      | O(1)                      | O(1) amortizado           |
+----------------------+---------------------------+---------------------------+
| Eliminación          | pop()                     | dequeue()                 |
|                      | O(1)                      | O(1) amortizado           |
+----------------------+---------------------------+---------------------------+
| Inspección           | peek() → top              | peek() → front            |
|                      | O(1)                      | O(1)                      |
+----------------------+---------------------------+---------------------------+
| Estructura interna   | Lista dinámica            | Lista + índice de _head   |
|                      | (_data stack)             | para evitar costes altos  |
+----------------------+---------------------------+---------------------------+
| Orden lógico         | De arriba a abajo         | De izquierda a derecha    |
|                      | [Bottom ... Top]          | [Front ... Back]          |
+----------------------+---------------------------+---------------------------+
| Errores              | EmptyStackError           | EmptyQueueError           |
+----------------------+---------------------------+---------------------------+
| Ejemplo visual       |        30                 |  Front → [10][20][30]     |
|                      |        20                 |                           |
|                      |        10                 |                           |
+----------------------+---------------------------+---------------------------+
| Cuándo usar          | Cuando lo último añadido  | Cuando respetar el orden  |
|                      | debe salir primero        | de llegada es crucial     |
+----------------------+---------------------------+---------------------------+