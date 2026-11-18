# Taller3_Info1
Sistema de Gestión de Información y Monitoreo Biomédico (Unidades 3 y 4)

## Descripción del Proyecto 
Este trabajo consiste en un sistema integral desarrollado en **Python** para el procesamiento, validación, almacenamiento y análisis de **datos biomédicos sintéticos** (Frecuencia Cardíaca, Saturación de Oxígeno, Edad/Frecuencia Respiratoria e Identificación de Paciente). 
El sistema integra herramientas de manipulación de archivos multiformato (**TXT, CSV, JSON**), validación estricta mediante **Expresiones Regulares (Regex)**, un sistema automatizado de **auditoría (logs)** y persistencia en bases de datos NoSQL con **MongoDB Atlas**. 

## Funcionalidades Principales 
1. **Generación Sintética de Datos:** Creación automática de 50+ registros biomédicos aleatorios en los formatos requeridos.
3. **Validación Estricta con Regex:** Verificación mediante patrones de Expresiones Regulares para garantizar la integridad de los datos (`ID-XXX`, `XX Años`, `XXXppm`, `XX%`).
4. **Procesamiento y Ordenamiento:** Algoritmo que extrae el valor numérico de la Frecuencia Cardíaca (FC) y ordena los registros de menor a mayor.
5. **Persistencia Multiformato:** Almacenamiento organizado en estructura de carpetas `/data/`:
   * `/data/txt/`: Reporte tabulado plano.
   * `data/csv/`: Archivo delimitado por comas con encabezados estándar.
   * `/data/json/`: Exportación e importación en formato JSON.
6. **Integración con MongoDB Atlas (NoSQL):**
   * Conexión remota a clúster de MongoDB (con modo seguro de simulación local si no hay conexión).
   * Inserción masiva de documentos en la colección `signos\_vitales`.
   * Consulta agregada del **promedio de Frecuencia Cardíaca**.
   * Filtrado de alerta de pacientes con **\\(\text{SpO}_2 &lt; 94\%\\)**.
   * Exportación de resultados de consulta a `/data/json/resultados_mongo.json`.
7. **Sistema de Auditoría y Logs:** Registro automatizado de cada acción del sistema con marca de tiempo (`YYYY-MM-DD HH:MM:SS`) en `/data/log.txt`.

## Expresiones Regulares (Regex) Utilizadas 
| Campo | Patrón Regex | Ejemplo Válido | Descripción | 
| :--- | :--- | :--- | :--- | 
| **ID** | `^ID-\d{3}$` | `ID-001` | Prefijo 'ID-' seguido de 3 dígitos numéricos. | 
| **FR / Edad** | `^\d{1,3}\sAños$` | `25 Años` | De 1 a 3 dígitos seguidos de un espacio y la palabra 'Años'. | 
| **FC** | `^\d{3}ppm$` | `090ppm` | Exactamente 3 dígitos seguidos de la unidad 'ppm'. | 
| **SpO2** | `^\d{2,3}%$` | `95%` | De 2 a 3 dígitos seguidos del símbolo '%'. | 

## Estructura del Repositorio 
```text 
Informática1_Taller3/ 
│ 
├── taller3_Ana_Blandon.py   # Script principal de la aplicación 
├── README.md     # Documentación del proyecto 
└── data     # Carpeta de persistencia (generada automáticamente) 
  ├── log.txt     # Historial de auditoría con marcas de tiempo 
  ├── txt/ 
  │   └── signos_vitales_ordenados.txt 
  ├── csv/ 
  │   └── signos_vitales_ordenados.csv 
  └── json/ 
      ├── signos_vitales.json 
      └── resultados_mongo.json
