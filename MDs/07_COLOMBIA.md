# COLOMBIA
# Colombia

## Objetivo

Implementar un pipeline reproducible para Colombia que permita construir microdatos armonizados compatibles con el resto de los países del proyecto.

La prioridad es obtener una base armonizada que preserve la comparabilidad internacional antes que maximizar el uso de variables exclusivas de Colombia.

---

# Cobertura temporal

Actualmente implementado:

* 2018
* 2023

Objetivo final:

* 2007
* 2018
* 2023

Los tres años deberán coexistir.

---

# Fuente

Gran Encuesta Integrada de Hogares (GEIH).

Debe documentarse exactamente:

* fuente oficial
* años utilizados
* módulos empleados
* diseño muestral
* factores de expansión
* universo de referencia

---

# Universo de análisis

Personas de:

* 15 años o más
* hasta 65 años inclusive

Debe existir una justificación metodológica documentada.

---

# Cobertura geográfica

Siempre que sea posible deberán generarse indicadores para:

## Total nacional

## Urbano

## Rural

## Urbano + Rural

Siempre manteniendo la comparabilidad internacional.

Si alguna apertura no fuera posible deberá documentarse.

---

# Unidad de análisis

Persona ocupada.

Posteriormente también deberán incorporarse indicadores para:

* PEA
* PET
* tasa de actividad
* tasa de empleo

---

# Clasificación ocupacional

Debe construirse exactamente la misma estructura que para todos los países.

## Sector formal

* Asalariados privados
* Asalariados públicos
* Autónomos profesionales
* Patrones

## Sector informal

* Asalariados privados en establecimientos menores a 10 personas
* Patrones en establecimientos menores a 10 personas
* Autónomos no profesionales
* Trabajo familiar
* Servicio doméstico

La estructura debe ser idéntica para todos los países.

---

# Criterios de informalidad

La definición utilizada es productivista.

No depende únicamente de:

* aportes
* seguridad social
* registro laboral

La clasificación incorpora simultáneamente distintas características del puesto.

Siempre deberá privilegiarse la armonización internacional.

---

# Autónomos profesionales

La clasificación ya no utilizará calificación ocupacional.

El nuevo criterio será:

Educación terciaria o universitaria completa.

Si Colombia no dispone exactamente de esa variable deberá buscarse la mejor proxy posible.

Nunca reemplazar automáticamente por missing.

---

# Tamaño del establecimiento

Nuevo criterio:

Formal:

10 trabajadores o más.

Informal:

menos de 10 trabajadores.

Debe identificarse la variable equivalente utilizada por GEIH.

---

# Variables adicionales

Además de la estructura ocupacional deberán incorporarse:

## Subocupación

* voluntaria
* involuntaria (demandante)

## Contrato

* escrito
* verbal

## Duración

* permanente
* temporal
* plazo fijo
* equivalente disponible

Siempre documentando equivalencias.

---

# Sector público

Se requiere identificar dentro del empleo público:

* Salud
* Educación
* Administración pública

Si la información no estuviera disponible deberá buscarse la mejor clasificación equivalente.

---

# Salarios

Más adelante deberán incorporarse:

* ingreso laboral principal
* salario real

La deflactación será común para todos los países utilizando índices oficiales.

Ese componente todavía no forma parte del pipeline.

---

# Variables armonizadas

Cada nueva variable deberá incorporarse también al esquema general del proyecto.

No crear variables locales incompatibles con el resto de los países.

---

# Pipeline

Actualmente Colombia posee scripts específicos de normalización.

En el largo plazo la idea es migrar gradualmente hacia un pipeline propio por país.

Mientras tanto continuará utilizando el common_pipeline.py.

---

# Documentación obligatoria

Cada decisión metodológica deberá quedar registrada.

Especialmente:

* variables originales
* variables armonizadas
* proxies utilizadas
* diferencias respecto del resto de los países
* limitaciones

Nunca asumir equivalencias sin documentarlas.

---

# Prioridad metodológica

El objetivo principal es mantener la comparabilidad internacional.

Ante varias alternativas deberá priorizarse:

1. comparabilidad internacional;
2. consistencia con el resto del pipeline;
3. aprovechamiento de información adicional propia de Colombia.

Toda excepción deberá quedar explícitamente documentada.
