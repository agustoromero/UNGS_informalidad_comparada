# MEXICO
# México

## Objetivo

Implementar la armonización de microdatos de México dentro del proyecto comparativo de informalidad laboral y estructura ocupacional en América Latina.

El objetivo es construir estadísticas comparables entre países sobre:

* estructura ocupacional;
* informalidad;
* precariedad laboral;
* cambios estructurales del mercado de trabajo.

La prioridad es la armonización internacional y la consistencia metodológica.

---

# Cobertura temporal

Actualmente implementado:

* 2018
* 2023

Objetivo final:

* 2007
* 2018
* 2023

Los años deben mantenerse disponibles para análisis de evolución temporal.

---

# Fuente oficial

Instituto Nacional de Estadística y Geografía (INEGI).

Fuente principal:

Encuesta Nacional de Ocupación y Empleo (ENOE).

Sitio oficial:

https://www.inegi.org.mx/

Debe documentarse:

* versión de la encuesta utilizada;
* período;
* módulos utilizados;
* archivos descargados;
* factores de expansión;
* cambios metodológicos entre años.

---

# Universo de análisis

La población objetivo será:

Personas entre 15 y 65 años.

Toda la estructura ocupacional e indicadores derivados deberán calcularse sobre este universo.

---

# Cobertura geográfica

México permite potencialmente construir:

* Total nacional;
* Urbano;
* Rural;
* Urbano + Rural.

Siempre que las variables disponibles permitan mantener la comparabilidad.

Si una apertura geográfica no fuera posible deberá quedar documentada.

---

# Unidad de análisis

Persona.

La clasificación ocupacional se construye utilizando la ocupación principal.

---

# Denominadores

El proyecto incorporará distintos universos:

## PET

Población en edad de trabajar.

## PEA

Población económicamente activa.

## Ocupados

Base principal para la estructura ocupacional.

A partir de estos universos se calcularán:

* tasa de actividad;
* tasa de ocupación;
* estructura ocupacional;
* indicadores de informalidad.

---

# Estructura ocupacional

México deberá adaptarse a la estructura armonizada general.

## Sector formal

* Autónomos profesionales;
* Asalariados privados;
* Asalariados públicos;
* Patrones.

## Sector informal

* Patrones micro;
* Asalariados privados micro;
* Autónomos no profesionales;
* Trabajo familiar;
* Empleo doméstico.

El total de ocupados será siempre el denominador de la estructura ocupacional.

---

# Definición de informalidad

La definición utilizada es productivista.

No se limita únicamente a:

* registro laboral;
* acceso a seguridad social;
* condición legal del empleo.

La clasificación considera múltiples dimensiones:

* categoría ocupacional;
* tamaño del establecimiento;
* educación;
* características del vínculo laboral.

La metodología completa se encuentra en:

11_METODOLOGIA.md

---

# Tamaño del establecimiento

Criterio actualizado:

Establecimiento pequeño:

menos de 10 trabajadores.

Este criterio reemplaza la clasificación anterior basada en menos de 5 trabajadores.

Debe identificarse la variable equivalente disponible en ENOE.

---

# Autónomos profesionales

La clasificación será realizada mediante:

Educación terciaria o universitaria completa.

No se utilizará únicamente la calificación ocupacional.

Si ENOE no posee una variable idéntica deberá construirse una proxy documentada.

---

# Indicadores adicionales

Además de la estructura ocupacional se incorporarán indicadores sobre precariedad.

## Subocupación

Clasificación:

* subocupados voluntarios;
* subocupados involuntarios o demandantes de empleo.

---

## Contrato laboral

Cuando la encuesta lo permita:

* contrato escrito;
* contrato verbal.

---

## Temporalidad

Cuando exista información comparable:

* empleo permanente;
* empleo temporal;
* plazo determinado.

---

# Sector público

Se buscará desagregar el empleo público en:

* Administración pública;
* Educación;
* Salud.

La clasificación deberá realizarse mediante las variables disponibles en la encuesta.

---

# Salarios

En una etapa posterior se incorporará:

* ingreso de la ocupación principal;
* salario real.

Será necesario integrar:

* índices de precios oficiales;
* metodología común de deflactación.

Actualmente esta etapa no forma parte del pipeline principal.

---

# Scripts

Actualmente existen:

scripts/mexico/

* mexico_2018.py
* mexico_2023.py

En el futuro deberá incorporarse:

* mexico_2007.py

manteniendo la estructura común del proyecto.

---

# Datos

Los microdatos originales se almacenan en:

data/mexico/

Los datos armonizados se generan mediante el pipeline común y se almacenan en:

outputs/harmonized/

---

# Particularidades de México

México requiere especial atención debido a:

* cambios metodológicos de las encuestas;
* diferencias en módulos disponibles;
* necesidad de compatibilizar criterios de informalidad con otros países.

Toda diferencia respecto del esquema general deberá documentarse.

---

# Variables faltantes

Cuando una variable requerida no exista:

1. Revisar si existe una variable equivalente.
2. Evaluar una proxy conceptualmente válida.
3. Documentar la decisión.

Nunca asignar missing automáticamente sin análisis previo.

---

# Estado actual

México cuenta con una estructura inicial para 2018 y 2023.

Las próximas tareas son:

* incorporar 2007;
* revisar equivalencias metodológicas;
* generar parquets armonizados;
* validar indicadores frente al esquema internacional.

---

# Prioridad metodológica

Ante cualquier decisión se prioriza:

1. Comparabilidad internacional.
2. Consistencia con el pipeline común.
3. Uso de información adicional disponible en México.

Toda excepción debe quedar registrada.
