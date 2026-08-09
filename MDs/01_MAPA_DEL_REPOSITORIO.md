# MAPA DEL REPOSITORIO
# Mapa del repositorio

## Propósito

Este documento describe la organización del repositorio **UNGS_informalidad_comparada** y la función de cada directorio principal. No documenta la metodología de investigación ni el funcionamiento detallado del pipeline; únicamente establece dónde debe ubicarse cada componente del proyecto.

---

# Estructura general

```text
UNGS_informalidad_comparada/

├── config/
├── data/
├── docs/
├── logs/
├── MDs/
├── outputs/
├── scripts/
├── scripts_temporales/
├── estructura referencia/
├── otros repos/
├── .agents/
└── README.md
```

---

# Directorios principales

## config/

Contiene la configuración general utilizada por el pipeline.

Su contenido debe incluir únicamente archivos de configuración consumidos por el código (yaml, json u otros formatos equivalentes).

No debe contener documentación metodológica extensa.

Ejemplos actuales:

* country_mappings
* variables
* configuraciones generales

La documentación conceptual correspondiente se mantiene en la carpeta **MDs/**.

---

## data/

Almacena exclusivamente los datos de trabajo.

Cada país posee su propia carpeta.

Actualmente existen:

* argentina/
* brasil/
* chile/
* colombia/
* mexico/
* peru/

Dentro de cada carpeta se almacenan:

* microdatos originales
* archivos auxiliares
* diccionarios cuando corresponda

No deben almacenarse aquí resultados finales.

---

## docs/

Documentación oficial proveniente de los institutos estadísticos nacionales.

Cada país dispone de su propia carpeta documental.

Ejemplos:

* cuestionarios
* manuales
* diccionarios
* clasificadores
* documentación metodológica oficial

También se incluyen documentos internacionales utilizados por varios países (por ejemplo ISCO).

---

## MDs/

Documentación propia del proyecto.

Aquí se documentan:

* metodología
* decisiones de armonización
* variables
* pipeline
* descripción por país
* criterios utilizados

Estos documentos constituyen el contrato metodológico del proyecto.

---

## outputs/

Resultados generados automáticamente por el pipeline.

Ejemplos:

* bases armonizadas
* parquet finales
* tablas
* auditorías
* diagnósticos
* archivos Excel de salida

Todo el contenido de esta carpeta debe poder regenerarse ejecutando nuevamente el pipeline.

---

## scripts/

Código fuente principal del proyecto.

Se divide en módulos funcionales.

### scripts/argentina

Pipeline específico de Argentina.

### scripts/brasil

Pipeline específico de Brasil.

### scripts/chile

Pipeline específico de Chile (en desarrollo).

### scripts/colombia

Pipeline específico de Colombia.

### scripts/mexico

Pipeline específico de México.

### scripts/peru

Pipeline específico de Perú (en desarrollo).

### scripts/harmonization

Orquesta la armonización de todos los países.

Debe contener únicamente código relacionado con la construcción de la base armonizada.

### scripts/indicators

Genera indicadores a partir de la base armonizada.

Incluye:

* agregaciones
* tasas
* tablas
* medidas
* registros
* layouts

### scripts/checks

Rutinas de validación.

Se utilizan para detectar errores de consistencia antes o después de ejecutar el pipeline.

### common_pipeline.py

Archivo central del proyecto.

Contiene la lógica común utilizada por todos los países.

Mientras exista un pipeline compartido, cualquier modificación transversal debe implementarse aquí.

---

## scripts_temporales/

Scripts auxiliares utilizados durante el desarrollo.

No forman parte del pipeline oficial.

Pueden eliminarse o archivarse una vez finalizado el trabajo correspondiente.

---

## estructura referencia/

Material utilizado únicamente como referencia.

Incluye:

* scripts originales
* programas en R
* programas Stata
* implementaciones históricas

No forman parte del pipeline productivo.

---

## otros repos/

Repositorios externos utilizados como referencia metodológica o técnica.

No deben modificarse desde este proyecto.

---

## logs/

Registros generados durante la ejecución del pipeline.

Su contenido depende del proceso ejecutado.

---

## .agents/

Configuraciones específicas para asistentes o agentes automáticos.

No contienen lógica metodológica del proyecto.

---

# Organización del código

El objetivo de la estructura es separar claramente:

* datos
* documentación
* configuración
* código
* resultados

Cada componente debe tener una única responsabilidad.

Siempre que sea posible:

* la lógica común debe permanecer en el pipeline compartido;
* la lógica específica de un país debe permanecer únicamente en la carpeta correspondiente.

---

# Evolución prevista

El pipeline actual utiliza una arquitectura parcialmente compartida mediante `common_pipeline.py`.

A futuro se prevé migrar hacia pipelines independientes por país, manteniendo una etapa común únicamente para la armonización internacional y la construcción de los indicadores comparables.
