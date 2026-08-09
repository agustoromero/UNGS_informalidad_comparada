# PIPELINE GENERAL
# Pipeline general

## Objetivo

Este documento describe el funcionamiento del pipeline principal del proyecto **UNGS_informalidad_comparada**.

El objetivo del pipeline es construir una base de datos armonizada internacionalmente que permita comparar la estructura ocupacional y la informalidad laboral entre distintos países y distintos años utilizando una metodología única.

---

# Arquitectura general

El pipeline sigue la siguiente secuencia:

```text
Microdatos nacionales
        │
        ▼
Pipeline específico del país
        │
        ▼
Variables armonizadas
        │
        ▼
Common Pipeline
        │
        ▼
Base armonizada internacional
        │
        ▼
Indicadores
        │
        ▼
Tablas
        │
        ▼
Auditorías
        │
        ▼
Outputs finales
```

---

# Etapa 1. Microdatos originales

Cada país posee sus propios archivos originales.

Los microdatos nunca deben modificarse.

La carpeta `data/` constituye la fuente primaria del proyecto.

---

# Etapa 2. Pipeline específico por país

Cada país posee un script propio.

Su función es:

* leer los microdatos originales;
* identificar las variables nacionales;
* transformarlas al esquema común del proyecto.

Los scripts específicos no deben producir estadísticas finales.

Su única responsabilidad consiste en construir una base armonizada para ese país.

---

# Etapa 3. Common Pipeline

Una vez armonizadas las variables nacionales, toda la lógica común se ejecuta mediante `common_pipeline.py`.

Esta etapa aplica reglas compartidas para todos los países.

Ejemplos:

* construcción de indicadores;
* clasificación ocupacional;
* identificación de formalidad e informalidad;
* cálculo de variables derivadas;
* filtros comunes.

Actualmente esta constituye el núcleo del proyecto.

---

# Etapa 4. Base armonizada

El resultado del Common Pipeline es una base armonizada con un esquema único para todos los países.

Esta base contiene exclusivamente variables comparables internacionalmente.

No incorpora variables particulares de un único país salvo que exista una justificación metodológica explícita.

---

# Etapa 5. Indicadores

A partir de la base armonizada se generan los distintos indicadores.

Esta etapa es independiente del país.

Los indicadores utilizan exclusivamente variables armonizadas.

Ejemplos:

* tasas;
* distribuciones;
* estructura ocupacional;
* informalidad;
* precariedad;
* agregaciones.

---

# Etapa 6. Auditoría

Antes de generar los productos finales deben ejecutarse las rutinas de auditoría.

Las auditorías verifican:

* existencia de variables;
* cobertura temporal;
* consistencia de categorías;
* tamaños muestrales;
* pérdidas de observaciones;
* consistencia entre países.

Toda anomalía debe documentarse.

---

# Etapa 7. Outputs

Los productos finales incluyen:

* bases armonizadas;
* archivos parquet;
* tablas;
* Excel;
* auditorías;
* diagnósticos.

Todo archivo ubicado en `outputs/` debe poder reconstruirse ejecutando nuevamente el pipeline.

---

# Flujo de responsabilidades

## Scripts por país

Responsables de:

* lectura;
* limpieza inicial;
* adaptación nacional;
* armonización primaria.

No calculan indicadores.

---

## Common Pipeline

Responsable de:

* armonización internacional;
* variables comunes;
* reglas metodológicas;
* integración entre países.

---

## Indicators

Responsable de:

* indicadores;
* tasas;
* tablas;
* agregaciones;
* salidas analíticas.

---

## Checks

Responsable de:

* validación;
* diagnóstico;
* control de calidad.

---

# Principios del pipeline

El pipeline sigue los siguientes principios.

## 1. Una única fuente de verdad

Cada variable armonizada debe construirse una sola vez.

No deben existir implementaciones duplicadas.

---

## 2. Prioridad de la armonización

Las decisiones metodológicas buscan maximizar la comparabilidad entre países.

Cuando una variable no exista exactamente en un país:

* primero debe buscarse un equivalente;
* luego una proxy;
* si ninguna alternativa resulta aceptable, el proceso debe detenerse para documentar la decisión.

Nunca debe imputarse automáticamente una variable.

---

## 3. Modularidad

Cada componente del pipeline posee una única responsabilidad.

No deben mezclarse:

* lectura;
* armonización;
* indicadores;
* auditoría.

---

## 4. Reproducibilidad

Todo resultado debe poder reproducirse ejecutando nuevamente el pipeline sobre los mismos microdatos.

No deben existir modificaciones manuales de resultados intermedios.

---

# Evolución prevista

Actualmente el proyecto utiliza un `common_pipeline.py` compartido para todos los países.

En una etapa posterior se prevé evolucionar hacia una arquitectura con pipelines independientes por país, manteniendo únicamente una etapa común para:

* integración internacional;
* armonización final;
* construcción de indicadores comparables.

Esta migración deberá realizarse sin modificar la metodología ni las definiciones armonizadas del proyecto.
