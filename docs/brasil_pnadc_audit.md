# Auditoría PNADC (Brasil) y propuesta de capa de metadatos

## A) Estructura PNADC observada en el repositorio

### 1) Lectura de microdatos en `PNADcIBGE-master`
- `read_pnadc()` **no reconstruye VD***: lee columnas desde archivo fijo (`readr::read_fwf`) usando un layout generado desde `input_txt` (script SAS oficial). La función calcula `start/end` a partir de líneas que empiezan con `@` y arma `fwf_positions(start, end, X2)`. Luego lee con `col_types` derivado de `$` (carácter) vs numérico.  
- Si se pide `vars`, igualmente preserva variables de diseño (Año, Trimestre, UPA, V1008, V1014, V2003, pesos y replicados, etc.).
- Conclusión: **VD4002/VD4009 se leen directamente del microdato** si están en `input_txt`; no se recalculan dentro del paquete.

### 2) Etiquetado (`pnadc_labeller`)
- `pnadc_labeller()` abre el XLS diccionario y asume estructura tabular (renombra a `X__1..X__n`).
- Usa `X__3` como nombre de variable y (`X__6`,`X__7`) como `(código, etiqueta)` de categorías.
- Forward-fill de `X__3` para bloques donde sólo cambia código/etiqueta.
- Sólo etiqueta variables de clase `character` no incluidas en `notlabel`.
- Implicación clave: si el pipeline Python carga numérico, **no habrá etiquetas**, pero los códigos siguen siendo válidos.

### 3) ¿Etiquetas separadas?
- Sí: los **value labels viven en el XLS** (diccionario), no en el TXT de microdatos.
- El `input_txt` define layout/tipos; el XLS define semántica de categorías.

## B) Familias de variables (mapa operativo)
- `V*`: variables base del cuestionario (domicilio, persona, trabajo, ingresos, etc.).
- `VD*`: variables derivadas/publicadas por IBGE (ej. condición de ocupación, posición ocupacional). En este repo se usan como variables de análisis, no reconstruidas.
- Identificación hogar/persona usada en repo:
  - Hogar/entorno muestral: `UF`, `UPA`, `V1008`, `V1014`
  - Persona: `V2003`
  - ID compuesto operativo: `UF + UPA + V1008 + V1014 + V2003`
- Pesos: `V1028` (peso principal), potencialmente con replicados `V1028***` en flujos de diseño complejo.

## C) Diagnóstico del pipeline actual (`scripts/common_pipeline.py`)

### Hallazgos
1. Brasil carga columnas mínimas (`Ano`, `Trimestre`, IDs, `V1028`, `VD4002`, `VD4009`, `VD4012`, `V4018`) y luego clasifica empleo/informalidad por códigos.  
2. El pipeline **no utiliza diccionario XLS** ni adjunta labels; trabaja con códigos crudos.  
3. Si en parquet `VD4002` o `VD4009` llegan como texto etiquetado (p.ej. por pasos previos), la coerción numérica a `NaN` puede colapsar tasas.  
4. El antecedente en `precariedad.mundial/scripts/Brasil.R` usa explícitamente etiquetas de texto (`"Pessoas ocupadas"`, etc.), lo cual sugiere coexistencia de dos representaciones posibles en el repo.

### Hipótesis para anomalía (ocupado≈7%, informal≈0%)
- **Desalineación de representación**: el pipeline espera códigos numéricos en `VD4002/VD4009`, pero parte de los datos puede estar en etiquetas (o viceversa).
- **No necesariamente error conceptual**: puede ser error de interpretación tipo/encoding/origen de parquet.

## D) Propuesta de capa `metadata_brasil` (centralizada)

Schema recomendado:
- `variable` (str)
- `description` (str)
- `type` (`numeric`|`character`)
- `position` (int, 1-indexed)
- `width` (int)
- `categories` (json/dict code->label)
- `na_rules` (json/list: códigos especiales/blank/NIU)
- `derived` (bool, `variable.startswith("VD")`)
- `notes` (str: versión/año/diccionario/origen)

### Estrategia de extracción robusta
1. Parsear `input_txt` para `position`, `width`, `type` y universo de variables reales del TXT.
2. Parsear XLS diccionario para `description`, categorías y notas.
3. Resolver bloques repetidos de encabezado y forward-fill de nombre de variable.
4. Versionar metadatos por `(año, trimestre, fuente_diccionario)`.
5. Exponer utilidades:
   - `coerce_using_metadata(df, vars)`
   - `attach_labels(df, vars)` opcional
   - `validate_expected_codes(df, variable, metadata)`

## E) Script de diagnóstico recomendado
- Nuevo script: `scripts/brasil/diagnose_pnadc_types.py` (adjunto en este PR).
- Objetivo: sin tocar pipeline, inspeccionar parquet bruto y reportar por variable:
  - dtype real
  - top valores observados
  - share de `NA`
  - comparación contra códigos esperados configurables

## F) Cambios mínimos sugeridos (después del diagnóstico)
1. Agregar validación previa de tipo/valores de `VD4002` y `VD4009` antes de `build_core()` para detectar si vienen etiquetadas en texto.
2. Centralizar mapa de códigos Brasil en un único módulo de metadatos (evitar hardcode disperso).
3. Mantener outputs estables: activar sólo warnings/errores diagnósticos al inicio.

## Recomendación
Sí: conviene **centralizar parsing de diccionario** (input + xls) en una capa reutilizable. `PNADcIBGE-master` ya resuelve buena parte en R; se puede replicar en Python de forma mínima para validación y tipado, sin reescribir la lógica de armonización de otros países.
