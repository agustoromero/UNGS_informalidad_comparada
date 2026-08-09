# ARGENTINA
# Argentina

## Objetivo

Este documento describe la implementación específica de Argentina dentro del proyecto de armonización de estructura ocupacional e informalidad para América Latina.

Argentina constituye el caso de referencia utilizado para diseñar gran parte del pipeline común.

---

# Fuente oficial

Instituto Nacional de Estadística y Censos (INDEC)

Encuesta Permanente de Hogares (EPH)

https://www.indec.gob.ar/

---

# Cobertura temporal

Objetivo final

- 2007
- 2018
- 2023

Actualmente implementado

- 2018
- 2023

La incorporación de 2007 constituye una de las próximas etapas del proyecto.

---

# Cobertura geográfica

La EPH releva únicamente población urbana.

Por lo tanto Argentina permitirá construir:

- Total urbano
- Urbano desagregado

No será posible construir:

- Total rural
- Rural desagregado
- Urbano + Rural

Estas limitaciones deberán documentarse explícitamente en las comparaciones internacionales.

---

# Unidad de análisis

Personas.

Se trabaja siempre sobre la ocupación principal.

---

# Rango etario

Se consideran personas entre

15 y 65 años.

Todo cálculo de estructura ocupacional e informalidad utiliza este universo.

---

# Denominadores

El proyecto producirá indicadores utilizando distintos universos.

Entre ellos:

- PET
- PEA
- Ocupados

Según corresponda al indicador.

---

# Estructura ocupacional

Se construyen los siguientes grupos.

## Total

- Ocupados

## Sector formal

- Asalariados privados
- Asalariados públicos
- Autónomos profesionales
- Patrones

## Sector informal

- Patrones micro
- Asalariados privados micro
- Autónomos no profesionales
- Trabajo familiar
- Empleo doméstico

Además se conservarán los totales correspondientes.

---

# Definición de informalidad

El proyecto utiliza una definición productivista.

No se basa exclusivamente en:

- registro laboral
- aportes
- seguridad social

La clasificación considera simultáneamente múltiples dimensiones.

Entre ellas:

- tamaño del establecimiento
- categoría ocupacional
- educación
- características del empleo

Las reglas completas se documentan en:

11_METODOLOGIA.md

---

# Cambios metodológicos

## Tamaño del establecimiento

Versión anterior

Menor a 5 personas.

Versión actual

Menor a 10 personas.

Esta regla afecta especialmente la identificación de:

- patrones informales
- asalariados privados informales

---

## Autónomos

Versión anterior

Clasificación basada en calificación ocupacional.

Versión actual

La distinción profesional / no profesional se realiza utilizando:

Educación terciaria o universitaria completa.

---

# Indicadores adicionales

Además de la estructura ocupacional se construirán indicadores sobre:

## Subocupación

- Subocupado demandante
- Subocupado no demandante
- Totales

## Contrato laboral

Siempre que la encuesta lo permita.

Se distinguirá:

- contrato escrito
- contrato verbal

y

- permanente
- temporal

---

# Sector público

Se buscará identificar la composición del empleo público en:

- Administración pública
- Educación
- Salud

Si la información no estuviera disponible directamente se evaluará utilizar variables auxiliares.

---

# Salarios

Posteriormente se incorporará:

Salario real de la ocupación principal.

Para ello será necesario incorporar series de IPC compatibles.

Actualmente esta etapa todavía no forma parte del pipeline.

---

# Scripts

Actualmente existen:

scripts/argentina/

- argentina_2018.py
- argentina_2023.py

En el futuro se agregará:

- argentina_2007.py

---

# Datos

Los microdatos se almacenan en:

data/argentina/

Los archivos armonizados se exportan hacia:

outputs/harmonized/

---

# Observaciones

Argentina constituye el país de referencia utilizado para desarrollar gran parte del pipeline común.

Las nuevas funcionalidades deberán implementarse procurando mantener compatibilidad con la estructura ya utilizada para este país.