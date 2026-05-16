**Informe de Revisión de Código – `sar.py`**  
*Fecha: 2026‑05‑16*  

---  

## 1. Resumen Ejecutivo  

| Métrica | Valor |
|--------|-------|
| **Puntuación de calidad global (0‑10)** | **5.8** |
| **Veredicto breve** | El código funciona, pero contiene vulnerabilidades críticas (deserialización con `pickle`), errores lógicos que pueden provocar excepciones y varios problemas de rendimiento y estilo que afectan a la mantenibilidad y a la eficiencia en producción. Se requiere una serie de correcciones antes de permitir el merge. |

---  

## 2. Problemas Críticos (DEBEN corregirse antes del merge)

| # | Área | Descripción | Acción requerida |
|---|------|-------------|------------------|
| 1 | **Seguridad** | Uso de `pickle.load()` / `pickle.dump()` para persistir datos → ejecución de código arbitrario. | Sustituir por JSON (o por un *restricted unpickler*) y actualizar `save_info` / `load_info`. |
| 2 | **Lógica** | `create_semantic_model` no devuelve el modelo en el caso `"Spacy"` (falta `return`). | Añadir `return` y reemplazar `assert` por `ValueError`. |
| 3 | **Lógica / Crash** | `self.semantic_threshold` inicializado a `None` y usado en comparaciones numéricas → `TypeError`. | Inicializar con un valor numérico por defecto (p.ej. `0.0`) y validar antes de usar. |
| 4 | **Seguridad / Robustez** | `index_dir` accede a `args['positional']` y `args['semantic']` sin validar → `KeyError`. | Usar `args.get(..., False)` y validar tipos. |
| 5 | **Seguridad / ReDoS** | Expresión regular sin límite de longitud en `solve_query`. | Imponer `MAX_QUERY_LEN` y validar antes de ejecutar `re.findall`. |
| 6 | **Robustez** | Argumento mutable por defecto `prev:Dict={}` en `solve_query`. | Cambiar a `prev: Optional[Dict] = None`. |
| 7 | **Funcionalidad incompleta** | `solve_and_show` está sin implementar (`pass`). | Implementar la lógica o eliminar la función del API público. |

---  

## 3. Hallazgos de Seguridad  

| # | Tipo | Severidad | Descripción | Corrección propuesta |
|---|------|-----------|-------------|----------------------|
| 1 | Deserialización insegura (`pickle`) | **CRÍTICA** | `pickle.load()` permite ejecutar código arbitrario. | Reemplazar por JSON (ver ejemplo en la tabla) o usar `SafeUnpickler`. |
| 2 | Validación de argumentos con `assert` | **MEDIA** | `assert` puede desactivarse con `-O`. | Cambiar a `if …: raise ValueError`. |
| 3 | Falta de validación de parámetros (`args['positional']`) | **BAJA** | `KeyError` si el parámetro falta. | Usar `args.get('positional', False)`. |
| 4 | Posible ReDoS en la regex de `solve_query` | **MEDIA** | `re.findall(r'"[^"]*"|\S+', query)` sin límite de longitud. | Definir `MAX_QUERY_LEN` (p.ej. 4096) y lanzar `ValueError` si se supera. |
| 5 | Exposición de IDs internos en `reverse_posting` | **BAJA** | Devuelve la lista completa de `artid` no presentes, permitiendo enumeración. | Añadir paginación (`limit`) y devolver sólo la diferencia necesaria. |
| 6 | Uso de `print` para logging | **BAJA** | Mezcla salida con lógica, dificulta auditoría. | Sustituir por el módulo `logging`. |

---  

## 4. Hallazgos de Rendimiento  

| # | Fragmento | Problema | Impacto | Optimización sugerida |
|---|-----------|----------|---------|-----------------------|
| 1 | Concatenación de strings en bucle (`txt_secs += …`) | O(n²) por creación de nuevos objetos `str`. | Alto (parseo lento en colecciones grandes). | Construir una lista de partes y `''.join()` al final. |
| 2 | `sorted(self.articles.keys())` en cada llamada a `reverse_posting`. | Ordenación O(N log N) repetida. | Medio‑alto. | Cachear la lista ordenada (`self._sorted_artids`). |
| 3 | `reverse_posting` genera la lista completa de IDs no presentes. | Uso de memoria O(N). | Medio. | Limitar resultados con parámetro `limit`. |
| 4 | Búsqueda posicional con bucles `while` anidados. | Complejidad potencial O(p·q) → lento para vocabulario frecuente. | Medio. | Convertir postings a `set` y usar intersección de conjuntos. |
| 5 | Bucle que vuelve a lanzar consultas al modelo semántico (`self.model.query`) con tamaños crecientes. | Multiplica el coste de consultas costosas (BERT, etc.). | Alto. | Duplicar `k` progresivamente y romper el bucle tan pronto como el umbral se cumpla. |
| 6 | Tokenización repetida en `solve_query` y `get_posting`. | Trabajo O(L) innecesario por token. | Bajo‑medio. | Cachear tokenizaciones dentro de la llamada. |
| 7 | `sorted(files)` en `index_dir`. | Ordenación innecesaria por directorio. | Bajo. | Iterar sin ordenar. |
| 8 | Creación de árbol k‑d sin idempotencia (`create_kdtree`). | Re‑entrenamiento costoso si se llama varias veces. | Medio. | Marcar con bandera `_kdtree_built`. |
| 9 | Uso de `print` para logging en `load_semantic_model`. | Afecta pruebas y rendimiento de I/O. | Bajo. | Reemplazar por `logging`. |

---  

## 5. Hallazgos de Estilo y Calidad  

| # | Problema | Severidad | Corrección sugerida |
|---|----------|-----------|---------------------|
| 1 | `assert` para validar entrada de usuario. | Mayor | Reemplazar por `raise ValueError`. |
| 2 | Argumento mutable por defecto (`prev:Dict={}`). | Mayor | Cambiar a `prev: Optional[Dict] = None`. |
| 3 | Nombre tipográfico `all_atribs`. | Menor | Renombrar a `ALL_ATTRS`. |
| 4 | `self.semantic_threshold = None` → comparaciones numéricas. | Mayor | Inicializar con `0.0`. |
| 5 | Acceso directo a `args['positional']` / `args['semantic']`. | Menor | Usar `args.get(..., False)`. |
| 6 | Método sin implementar (`solve_and_show`). | Menor | Implementar o eliminar. |
| 7 | Mezcla de tabs y spaces, indentación inconsistente. | Menor | Uniformizar a 4 espacios. |
| 8 | Uso de `pickle` (seguridad). | Mayor | Cambiar a JSON o *restricted unpickler*. |
| 9 | Nombres con errores tipográficos (`chuncks`, `chunck_index`). | Menor | Renombrar a `chunks`, `chunk_index`. |
|10| Uso de `print` para logging. | Menor | Adoptar módulo `logging`. |
|11| Valores “mágicos” (`200`, `4096`) codificados en el cuerpo. | Sugerencia | Definir como constantes de clase. |
|12| Falta de docstrings estructurados (PEP 257). | Sugerencia | Añadir docstrings con `Args`, `Returns`, `Raises`. |
|13| No se valida la salida de `split('\t')` en `solve_and_test`. | Menor | Capturar `ValueError` y registrar. |
|14| `solve_query` devuelve tupla aunque solo se usa la lista. | Sugerencia | Cambiar firma a devolver solo la lista. |
|15| Falta de tipado estático en varias funciones. | Sugerencia | Añadir anotaciones de tipo (`-> List[int]`, etc.). |
|16| Uso de `print` en `load_semantic_model`. | Sugerencia | Reemplazar por `logger.info`. |
|17| Algoritmo posicional complejo y poco legible. | Sugerencia | Reescribir usando intersección de conjuntos (ver tabla). |
|18| No se valida la longitud de la consulta antes de la regex. | Sugerencia | Añadir límite (`MAX_QUERY_LEN`). |
|19| Constantes definidas dentro de `__init__` (`MAX_EMBEDDINGS`). | Sugerencia | Declararlas como atributos de clase. |
|20| Falta de manejo de errores al abrir archivos. | Sugerencia | Capturar `FileNotFoundError`, `IOError`. |

---  

## 6. Plan de Acción Recomendado  

1. **Seguridad primero**  
   1.1. Reemplazar `pickle` por JSON (o implementar `SafeUnpickler`).  
   1.2. Cambiar todas las validaciones con `assert` a `raise ValueError`.  
   1.3. Añadir límite de longitud a la consulta y validar antes de la regex.  

2. **Corregir errores lógicos críticos**  
   2.1. Añadir `return` faltante en `create_semantic_model` y usar `ValueError` para nombres no soportados.  
   2.2. Inicializar `self.semantic_threshold` con `0.0` y validar su tipo en `solve_semantic_query`.  
   2.3. Reemplazar argumentos mutables por `None` en `solve_query`.  

3. **Mejorar robustez de la API**  
   3.1. Modificar `index_dir` para usar `args.get` con valores por defecto.  
   3.2. Implementar `solve_and_show` (o eliminarla).  
   3.3. Sustituir `print` por `logging` en todo el módulo.  

4. **Optimizar rendimiento**  
   4.1. Refactorizar concatenaciones de strings en `parse_article` usando listas y `''.join()`.  
   4.2. Cachear la lista ordenada de `article` IDs (`self._sorted_artids`).  
   4.3. Limitar resultados en `reverse_posting` con parámetro `limit`.  
   4.4. Reescribir la búsqueda posicional con intersección de conjuntos.  
   4.5. Optimizar el bucle de consultas semánticas: duplicar `k` y romper temprano.  
   4.6. Cachear tokenizaciones dentro de `solve_query` / `get_posting`.  
   4.7. Eliminar `sorted(files)` en `index_dir`.  
   4.8. Hacer `create_kdtree` idempotente (bandera `_kdtree_built`).  

5. **Estilo y calidad**  
   5.1. Renombrar variables con errores tipográficos (`all_atribs`, `chuncks`, `chunck_index`).  
   5.2. Definir todas las constantes como atributos de clase (`MAX_QUERY_LEN`, `DEFAULT_SEMANTIC_MODEL`, etc.).  
   5.3. Añadir docstrings y anotaciones de tipo a todas las funciones.  
   5.4. Uniformizar indentación a 4 espacios.  
   5.5. Revisar y eliminar código muerto o no usado.  

6. **Pruebas y CI**  
   6.1. Añadir pruebas unitarias que cubran los casos de error (p.ej. carga de archivo inexistente, línea de test sin tabulador, `None` en `semantic_threshold`).  
   6.2. Integrar análisis estático (`flake8`, `mypy`, `bandit`) en la pipeline CI.  

---  

## 7. Puntos Positivos  

| Aspecto | Comentario |
|---------|------------|
| **Arquitectura modular** | El código separa claramente la indexación, la búsqueda posicional y la búsqueda semántica, lo que facilita la extensión. |
| **Uso de modelos avanzados** | Integra varios modelos de embeddings (SBERT, Beto, Spacy) ofreciendo flexibilidad al usuario. |
| **Soporte de consultas booleanas** | Implementa operadores `AND`, `OR`, `NOT` y manejo de frases entre comillas. |
| **Persistencia de estado** | La capacidad de guardar y cargar el índice permite reutilizar trabajos costosos. |
| **Documentación parcial** | Algunas funciones ya incluyen docstrings que describen su propósito. |
| **Uso de typing** | Emplea anotaciones de tipo en varios lugares, lo que ayuda a los IDE y a `mypy`. |
| **Manejo de stop‑words y stemming** | Ofrece opciones configurables (`positional`, `semantic`) para adaptar la indexación a diferentes casos de uso. |

---  

*Fin del informe.*  

---  

**Generación del PDF**  

```json
{
  "md_path": "reports/review_sar.py.md"
}
```  

---  