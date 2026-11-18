import os
import re
import csv
import json
import random
import datetime
from pathlib import Path

# Se intenta importar pymongo para MongoDB Atlas
try:
    import pymongo
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


# =====================================================================
# 1. Herramientas del sistema y registro de acciones (LOGS)
# =====================================================================
BASE_DIR = Path("data")
TXT_DIR = BASE_DIR / "txt"
CSV_DIR = BASE_DIR / "csv"
JSON_DIR = BASE_DIR / "json"
LOG_FILE = BASE_DIR / "log.txt"

def preparar_estructura_carpetas():
    """Crea la estructura de carpetas /data/txt, /data/csv, /data/json si no existen."""
    for directorio in [TXT_DIR, CSV_DIR, JSON_DIR]:
        directorio.mkdir(parents=True, exist_ok=True)
    registrar_log("Estructura de carpetas /data/ (txt, csv, json) creada/verificada.")

def registrar_log(accion):
    """Escribe un registro de la acción realizada con timestamp en log.txt."""
    try:
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {accion}\n")
    except Exception as e:
        print(f"Error al escribir en el log: {e}")


# =====================================================================
# 2. Validaciones
# =====================================================================
PATRON_ID = re.compile(r"^ID-\d{3}$")
PATRON_FR = re.compile(r"^\d{1,3}\sAños$")
PATRON_FC = re.compile(r"^\d{3}ppm$")
PATRON_SPO2 = re.compile(r"^\d{2,3}%$")

def validar_registro(registro):
    """
    Verifica que los campos (id, fr, fc, spo2) cumplan con los patrones Regex.
    Retorna (True, None) si es válido, o (False, mensaje_error) si falla.
    """
    if not PATRON_ID.match(str(registro.get("id", ""))):
        return False, f"ID inválido ({registro.get('id')}). Debe ser 'ID-XXX' (ej: ID-001)."
    if not PATRON_FR.match(str(registro.get("fr", ""))):
        return False, f"FR/Edad inválida ({registro.get('fr')}). Debe ser 'XX Años' (ej: 25 Años)."
    if not PATRON_FC.match(str(registro.get("fc", ""))):
        return False, f"FC inválida ({registro.get('fc')}). Debe ser 'XXXppm' (ej: 090ppm)."
    if not PATRON_SPO2.match(str(registro.get("spo2", ""))):
        return False, f"SpO2 inválida ({registro.get('spo2')}). Debe ser 'XX%' (ej: 95%)."
    return True, None

def validar_lista_registros(registros):
    """Valida una lista completa de registros e imprime reporte de inconsistencias."""
    validos = []
    invalidos = []
    for r in registros:
        es_valido, error = validar_registro(r)
        if es_valido:
            validos.append(r)
        else:
            invalidos.append((r, error))
    
    registrar_log(f"Validación Regex realizada: {len(validos)} válidos, {len(invalidos)} inválidos.")
    return validos, invalidos


# =====================================================================
# 3. GENERACIÓN, PROCESAMIENTO Y ORDENAMIENTO DE DATOS BIOMÉDICOS
# =====================================================================
def generar_registros_aleatorios(cantidad=50):
    """Genera una lista de al menos 'cantidad' registros biomédicos sintéticos."""
    registros = []
    for i in range(1, cantidad + 1):
        id_str = f"ID-{i:03d}"
        edad_num = random.randint(18, 90)
        fr_str = f"{edad_num} Años"
        fc_num = random.randint(50, 140)
        fc_str = f"{fc_num:03d}ppm"
        spo2_num = random.randint(88, 100)
        spo2_str = f"{spo2_num}%"

        registros.append({
            "id": id_str,
            "fr": fr_str,
            "fc": fc_str,
            "spo2": spo2_str
        })
    
    registrar_log(f"Generados {len(registros)} registros biomédicos aleatorios.")
    return registros

def extraer_valor_fc(fc_str):
    """Extrae el valor numérico de la frecuencia cardíaca a partir de '090ppm' -> 90."""
    match = re.search(r"\d+", fc_str)
    return int(match.group()) if match else 0

def extraer_valor_spo2(spo2_str):
    """Extrae el valor numérico de la SpO2 a partir de '95%' -> 95."""
    match = re.search(r"\d+", spo2_str)
    return int(match.group()) if match else 0

def ordenar_por_frecuencia_cardiaca(registros):
    """Ordena los registros de menor a mayor Frecuencia Cardíaca (fc)."""
    registros_ordenados = sorted(registros, key=lambda x: extraer_valor_fc(x["fc"]))
    registrar_log(f"Registros ordenados por Frecuencia Cardíaca ({len(registros_ordenados)} ítems).")
    return registros_ordenados


# =====================================================================
# 4. Gestión de archivos: TXT, CSV Y JSON con rutas y excepciones
# =====================================================================
def guardar_en_txt(registros, ruta_salida=TXT_DIR / "signos_vitales_ordenados.txt"):
    """Guarda los registros ordenados en formato plano .txt en /data/txt/."""
    try:
        preparar_estructura_carpetas()
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write("ID | Edad (FR) | Frecuencia Cardíaca (FC) | SpO2\n")
            f.write("-" * 50 + "\n")
            for r in registros:
                f.write(f"{r['id']} | {r['fr']} | {r['fc']} | {r['spo2']}\n")
        print(f"Archivo TXT guardado exitosamente en: '{ruta_salida}'")
        registrar_log(f"Archivo TXT guardado en '{ruta_salida}'.")
        return True
    except Exception as e:
        print(f"Error al guardar TXT: {e}")
        registrar_log(f"Error al guardar TXT: {e}")
        return False

def guardar_en_csv(registros, ruta_salida=CSV_DIR / "signos_vitales_ordenados.csv"):
    """Guarda los registros ordenados en formato .csv en /data/csv/."""
    try:
        preparar_estructura_carpetas()
        with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=["id", "fr", "fc", "spo2"])
            escritor.writeheader()
            escritor.writerows(registros)
        print(f"Archivo CSV guardado exitosamente en: '{ruta_salida}'")
        registrar_log(f"Archivo CSV guardado en '{ruta_salida}'.")
        return True
    except Exception as e:
        print(f"Error al guardar CSV: {e}")
        registrar_log(f"Error al guardar CSV: {e}")
        return False

def exportar_a_json(registros, ruta_salida=JSON_DIR / "signos_vitales.json"):
    """Exporta los registros a un archivo .json en /data/json/."""
    try:
        preparar_estructura_carpetas()
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(registros, f, indent=4, ensure_ascii=False)
        print(f"Archivo JSON exportado exitosamente en: '{ruta_salida}'")
        registrar_log(f"Archivo JSON exportado en '{ruta_salida}'.")
        return True
    except Exception as e:
        print(f"Error al exportar JSON: {e}")
        registrar_log(f"Error al exportar JSON: {e}")
        return False

def importar_desde_json(ruta_entrada=JSON_DIR / "signos_vitales.json"):
    """Importa y lee los registros desde un archivo .json."""
    if not Path(ruta_entrada).exists():
        print(f"El archivo '{ruta_entrada}' no existe.")
        return []
    try:
        with open(ruta_entrada, "r", encoding="utf-8") as f:
            datos = json.load(f)
        print(f"📖 {len(datos)} registros importados desde JSON ('{ruta_entrada}').")
        registrar_log(f"Importados {len(datos)} registros desde JSON ('{ruta_entrada}').")
        return datos
    except Exception as e:
        print(f"Error al importar JSON: {e}")
        registrar_log(f"Error al importar JSON: {e}")
        return []


# =====================================================================
# 5. Gestión de bases de datos NOSQL (MONGODB)
# =====================================================================
class GestorMongoDB:
    """Clase para manejar operaciones con MongoDB Atlas (o almacenamiento simulado si no está conectado)."""
    
    def __init__(self, connection_string=None):
        self.connection_string = connection_string or os.getenv("MONGO_URI", "mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority")
        self.client = None
        self.db = None
        self.coleccion = None
        self.usando_simulacion = False
        self._registros_simulados = []

    def conectar(self):
        """Intenta conectarse a MongoDB Atlas. Si falla o pymongo no está instalado, activa el modo simulación."""
        if not PYMONGO_AVAILABLE:
            print("Módulo 'pymongo' no instalado localmente. Se usará el modo de simulación de MongoDB.")
            self.usando_simulacion = True
            registrar_log("MongoDB: Activado modo de simulación (pymongo no instalado).")
            return False

        try:
            self.client = pymongo.MongoClient(self.connection_string, serverSelectionTimeoutMS=3000)
            self.client.admin.command('ping')
            self.db = self.client["laboratorio_biomedico"]
            self.coleccion = self.db["signos_vitales"]
            self.usando_simulacion = False
            print("Conexión exitosa a MongoDB Atlas.")
            registrar_log("MongoDB: Conexión exitosa a la base de datos 'laboratorio_biomedico'.")
            return True
        except Exception as e:
            print(f"No se pudo conectar a MongoDB Atlas ({e}). Se usará almacenamiento en memoria/simulación.")
            self.usando_simulacion = True
            registrar_log(f"MongoDB: Fallo de conexión ({e}). Modo simulación activado.")
            return False

    def insertar_registros(self, registros):
        """Inserta los registros validados en la colección 'signos_vitales'."""
        if not registros:
            print("No hay registros para insertar en MongoDB.")
            return 0

        if not self.usando_simulacion and self.coleccion is not None:
            try:
                resultado = self.coleccion.insert_many(registros)
                cant = len(resultado.inserted_ids)
                print(f"{cant} documentos insertados en la colección 'signos_vitales' (MongoDB Atlas).")
                registrar_log(f"MongoDB: Insertados {cant} documentos.")
                return cant
            except Exception as e:
                print(f"Error al insertar en MongoDB Atlas: {e}. Usando simulación.")
                self.usando_simulacion = True

        self._registros_simulados = [dict(r) for r in registros]
        cant = len(self._registros_simulados)
        print(f"[SIMULACIÓN MONGO] {cant} documentos guardados en la colección simulada 'signos_vitales'.")
        registrar_log(f"MongoDB (Simulación): Insertados {cant} documentos.")
        return cant

    def consultar_promedio_fc(self):
        """Calcula el promedio de la Frecuencia Cardíaca (fc)."""
        if not self.usando_simulacion and self.coleccion is not None:
            try:
                pipeline = [
                    {"$project": {"fc_num": {"$toInt": {"$substr": ["$fc", 0, 3]}}}},
                    {"$group": {"_id": None, "promedio_fc": {"$avg": "$fc_num"}}}
                ]
                res = list(self.coleccion.aggregate(pipeline))
                if res and "promedio_fc" in res[0]:
                    prom = round(res[0]["promedio_fc"], 2)
                    print(f"Promedio de Frecuencia Cardíaca en MongoDB Atlas: {prom} ppm")
                    registrar_log(f"MongoDB Consulta: Promedio FC = {prom} ppm.")
                    return prom
            except Exception as e:
                print(f"Error en agregación Atlas ({e}). Calculando localmente...")

        lista_fc = [extraer_valor_fc(r["fc"]) for r in self._registros_simulados if "fc" in r]
        if not lista_fc:
            print("No hay datos suficientes para calcular el promedio de FC.")
            return 0.0
        prom = round(sum(lista_fc) / len(lista_fc), 2)
        print(f"Promedio de Frecuencia Cardíaca: {prom} ppm")
        registrar_log(f"MongoDB Consulta (Simulación): Promedio FC = {prom} ppm.")
        return prom

    def consultar_spo2_bajo(self, umbral=94):
        """Consulta los documentos con SpO2 menor a 'umbral' (por defecto < 94)."""
        resultados = []
        if not self.usando_simulacion and self.coleccion is not None:
            try:
                docs = list(self.coleccion.find())
                for d in docs:
                    if "_id" in d:
                        d["_id"] = str(d["_id"])
                    if extraer_valor_spo2(d.get("spo2", "")) < umbral:
                        resultados.append(d)
                print(f"Se encontraron {len(resultados)} documentos con SpO2 < {umbral}% en MongoDB Atlas.")
                registrar_log(f"MongoDB Consulta: Encontrados {len(resultados)} docs con SpO2 < {umbral}%.")
                return resultados
            except Exception as e:
                print(f"Error en consulta Atlas ({e}). Filtrando localmente...")

        for r in self._registros_simulados:
            if extraer_valor_spo2(r.get("spo2", "")) < umbral:
                resultados.append(r)
        
        print(f"Se encontraron {len(resultados)} documentos con SpO2 < {umbral}% (Simulación).")
        registrar_log(f"MongoDB Consulta (Simulación): Encontrados {len(resultados)} docs con SpO2 < {umbral}%.")
        return resultados

    def exportar_consultas_a_json(self, ruta_salida=JSON_DIR / "resultados_mongo.json"):
        """Exporta los resultados de las consultas de MongoDB a 'resultados_mongo.json'."""
        try:
            promedio_fc = self.consultar_promedio_fc()
            docs_spo2_bajo = self.consultar_spo2_bajo(umbral=94)

            reporte = {
                "fecha_consulta": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "promedio_frecuencia_cardiaca_ppm": promedio_fc,
                "conteo_pacientes_spo2_bajo_94": len(docs_spo2_bajo),
                "pacientes_spo2_bajo_94": docs_spo2_bajo
            }

            preparar_estructura_carpetas()
            with open(ruta_salida, "w", encoding="utf-8") as f:
                json.dump(reporte, f, indent=4, ensure_ascii=False)
            
            print(f"Consultas de MongoDB exportadas correctamente a '{ruta_salida}'.")
            registrar_log(f"MongoDB: Consultas exportadas a '{ruta_salida}'.")
            return True
        except Exception as e:
            print(f"Error al exportar consultas de Mongo a JSON: {e}")
            registrar_log(f"Error al exportar consultas Mongo: {e}")
            return False
