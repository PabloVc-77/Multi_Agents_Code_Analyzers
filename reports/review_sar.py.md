**Informe de Revisión de Código – `sar.py`**  
*Fecha: 16‑05‑2026*  

---  

## 1. Resumen Ejecutivo  

| Métrica | Valor |
|--------|-------|
| **Puntuación de calidad global (0‑10)** | **5.2** |
| **Veredicto** | El código funciona pero presenta **vulnerabilidades críticas**, **deficiencias de rendimiento** y **varios problemas de estilo y robustez** que impiden un merge seguro. Se requiere una refactorización importante antes de considerarlo listo para producción. |

---  

## 2. Problemas Críticos (DEBEN corregirse antes de merge)

| # | Área | Descripción | Impacto | Acción requerida |
|---|------|-------------|---------|------------------|
| C1 | **Deserialización insegura** (`pickle`) | `save_info`/`load_info` usan `pickle.dump/load` sobre datos que pueden ser controlados por terceros. Permite ejecución arbitraria de código. | **CRÍTICA** | Sustituir por JSON (o por un *restricted unpickler*). |
| C2 | **Uso de `assert` para validar entrada** (`create_semantic_model`) | En modo optimizado (`python -O`) los `assert` desaparecen, dejando la función sin validación. | **ALTA** | Reemplazar por comprobación explícita que lance `ValueError`. |
| C3 | **Acceso directo a `args['positional']` / `args['semantic']`** (`index_dir`) | Provoca `KeyError` si el llamador omite esas claves, exponiendo trazas de pila. | **ALTA** | Usar `args.get(..., False)` y validar tipos. |
| C4 | **Uso de objetos no inicializados** (`create_kdtree`) | Si `self.model` es `None`, `self.model.fit()` lanza `AttributeError`. | **ALTA** | Comprobar que el modelo está cargado y lanzar `RuntimeError` controlado. |
| C5 | **Métodos sin implementar** (`solve_and_show`, `update_chunks`, `create_kdtree` placeholders) | Devuelven `None` o `pass`, lo que puede generar errores inesperados en tiempo de ejecución. | **MEDIA** | Implementar la lógica o lanzar `NotImplementedError`. |

---  

## 3. Hallazgos de Seguridad  

| # | Fragmento / línea | Tipo | Severidad | Descripción | Corrección propuesta |
|---|-------------------|------|-----------|-------------|----------------------|
| S1 | `save_info` / `load_info` (pickle) | Deserialización insegura | **CRÍTICA** | Reemplazar por JSON (ver tabla de correcciones) o usar `RestrictedUnpickler`. |
| S2 | `assert modelname in (…)` en `create_semantic_model` | Validación con `assert` | **MEDIA** | Reemplazar por `if modelname not in allowed: raise ValueError`. |
| S3 | Falta de validación de `args['positional']` y `args['semantic']` | Parámetros externos | **BAJA** | Usar `args.get('positional', False)` y validar tipos. |
| S4 | `self.model` puede ser `None` antes de `fit()` | Uso de objeto no inicializado | **BAJA** | Añadir guardia `if self.model is None: raise RuntimeError`. |
| S5 | `solve_and_test` → `line.split('\t')` sin captura de excepción | Entrada no controlada | **BAJA** | Envolver en `try/except ValueError` y registrar línea inválida. |
| S6 | `load_info` y `save_info` no verifican rutas ni permisos | Acceso a fichero | **BAJA** | Validar que la ruta sea absoluta y que el proceso tenga permisos de lectura/escritura. |

---  

## 4. Hallazgos de Rendimiento  

| # | Fragmento / línea | Problema | Impacto | Solución recomendada |
|---|-------------------|----------|---------|----------------------|
| R1 | Concatenación de cadenas en bucle (`parse_article`) | Complejidad **O(n²)** | **ALTO** | Construir una lista de fragmentos y `'\n'.join()` al final. |
| R2 | Llamadas repetidas a `self.model.query` en `solve_semantic_query` | Re‑cálculo costoso | **ALTO** | Incrementar `top_k` exponencialmente y romper cuando se supera el umbral. |
| R3 | `sorted(self.articles.keys())` en cada `reverse_posting` | Re‑cálculo O(N log N) | **MEDIO** | Cachear la lista ordenada (`self._sorted_artids`). |
| R4 | `sorted(files)` en cada directorio de `index_dir` | Orden innecesario | **MEDIO** | Eliminar `sorted`, iterar directamente. |
| R5 | Búsqueda lineal `p+offset in positions2` en `get_positionals` | O(p·q) | **MEDIO** | Convertir `positions2` a `set` y usar intersección. |
| R6 | Compilación repetida de regex en `solve_query` y bucles de pruebas | Overhead menor | **BAJO** | Compilar una vez (`TOKEN_RE = re.compile(...)`). |
| R7 | `get_posting` tokeniza siempre el término | Overhead menor | **BAJO** | Normalizar con `lower()` directamente. |
| R8 | `solve_and_count` / `solve_and_test` crean listas de resultados sin pre‑asignar | Pequeña ineficiencia | **BAJO** | Opcional: usar list comprehensions. |

---  

## 5. Hallazgos de Estilo y Calidad  

| # | Tipo | Severidad | Comentario | Mejora sugerida |
|---|------|-----------|------------|-----------------|
| E1 | Nomenclatura | MENOR | `all_atribs`, `chuncks` → `all_attrs`, `chunks`. | Renombrar y actualizar referencias. |
| E2 | Constantes “mágicas” | MENOR | `10`, `200`, `2` aparecen como literales. | Declarar constantes (`DEFAULT_SHOW_MAX`, `MAX_EMBEDDINGS`, `INITIAL_MULTIPLIER`). |
| E3 | Docstrings insuficientes | MENOR | Falta descripción de parámetros `**args` y tipos de retorno. | Completar docstrings siguiendo PEP‑257. |
| E4 | Mutable defaults (`prev:Dict={}`) | MENOR | Compartir estado entre llamadas. | Cambiar a `prev: Optional[Dict]=None`. |
| E5 | Indentación mixta (tabs + spaces) | MAYOR | `create_kdtree` contiene tabulaciones que pueden generar `IndentationError`. | Uniformizar a 4 espacios. |
| E6 | Importaciones desordenadas | MENOR | No siguen orden PEP‑8. | Re‑ordenar: stdlib → terceros → locales. |
| E7 | Uso de `print` para logging | SUGERENCIA | No se controla nivel de verbosidad. | Reemplazar por módulo `logging`. |
| E8 | Métodos `set_showall`, `set_semantic_threshold` sin snake_case descriptivo. | MENOR | Renombrar a `set_show_all`, `set_semantic_threshold`. |
| E9 | Falta de anotaciones de tipo en varios métodos. | MENOR | Añadir `-> None` o tipos concretos. |
| E10 | Duplicación de lógica en `solve_and_count` / `solve_and_test`. | MENOR | Extraer método privado `_process_query_line`. |

---  

## 6. Plan de Acción Recomendado  

1. **Eliminar la vulnerabilidad crítica de deserialización**  
   * Reemplazar `pickle` por JSON (o implementar `RestrictedUnpickler`).  
   * Actualizar `save_info` / `load_info` y ejecutar pruebas de compatibilidad.  

2. **Corregir validaciones de entrada**  
   * Sustituir `assert` por comprobación explícita en `create_semantic_model`.  
   * Modificar `index_dir` para usar `args.get(..., False)` y validar tipos.  

3. **Garantizar inicialización de objetos críticos**  
   * Añadir guardas en `create_kdtree` y en cualquier método que use `self.model`.  

4. **Implementar los métodos pendientes** (`solve_and_show`, `update_chunks`, `create_kdtree` placeholders) o, si no se usan, lanzar `NotImplementedError`.  

5. **Optimizar rendimiento**  
   * Refactorizar `parse_article` usando listas y `join`.  
   * Re‑escribir `solve_semantic_query` con crecimiento exponencial de `top_k`.  
   * Cachear `sorted(self.articles.keys())` en `reverse_posting`.  
   * Cambiar `sorted(files)` por iteración directa en `index_dir`.  
   * Mejorar `get_positionals` usando `set` y operaciones de intersección.  
   * Compilar regex una sola vez (`TOKEN_RE`).  

6. **Aplicar mejoras de estilo y calidad**  
   * Renombrar variables y métodos según PEP‑8.  
   * Declarar todas las constantes al inicio del módulo.  
   * Completar docstrings y añadir anotaciones de tipo.  
   * Reemplazar `print` por `logging` (opcional, pero recomendado).  
   * Uniformizar indentación a 4 espacios.  

7. **Ejecutar pruebas de regresión**  
   * Añadir pruebas unitarias que cubran los caminos de error (p.ej., carga de modelo fallida, archivo JSON corrupto).  
   * Ejecutar `pytest --cov` y asegurar cobertura > 85 %.  

8. **Re‑ejecutar análisis estático** (Bandit, Flake8, MyPy) y validar que no queden nuevos hallazgos.  

---  

## 7. Puntos Positivos  

| Aspecto | Comentario |
|---------|------------|
| **Arquitectura modular** | La separación entre indexación, consultas booleanas y semánticas está bien definida. |
| **Uso de expresiones regulares** | La tokenización de consultas (`TOKEN_RE`) permite manejar frases entre comillas y operadores lógicos. |
| **Soporte para búsquedas posicionales** | Implementación de `get_positionals` muestra una visión avanzada del motor de búsqueda. |
| **Facilidad de extensión** | La fábrica `create_semantic_model` permite añadir nuevos modelos sin tocar el resto del código. |
| **Documentación inicial** | Existe una breve descripción del módulo y de la clase, lo que facilita la comprensión global. |
| **Uso de `Path` y `os.walk`** | Manejo correcto de rutas y recorrido de directorios. |
| **Separación de responsabilidades** | Métodos como `solve_query`, `solve_semantic_query` y `show_stats` están claramente delimitados. |

---  

*Fin del informe.*  

---  

**Generación del PDF**  

```json
{
  "md_path": "reports/review_sar.py.md"
}
```