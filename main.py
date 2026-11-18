import sys 
from herramientas import *

# =====================================================================
# Ejecución del menú y el sistema general
# =====================================================================
preparar_estructura_carpetas()
registrar_log("Inicio de sesión de la aplicación.")

registros_actuales = []
gestor_mongo = GestorMongoDB()

while True:
    print("\n" + "=" * 65)
    print("GESTIÓN Y MONITOREO BIOMÉDICO")
    print("=" * 65)
    print("1. Generar / Ingresar registros biomédicos aleatorios (50+)")
    print("2. Validar registros con Expresiones Regulares (Regex)")
    print("3. Ordenar por Frecuencia Cardíaca y Exportar a TXT, CSV y JSON")
    print("4. Importar y consultar datos desde JSON")
    print("5. Operaciones MongoDB Atlas (Conectar, Insertar, Consultar FC/SpO2 y Exportar)")
    print("6. Ver historial de acciones (log.txt)")
    print("7. Salir del programa")
    print("=" * 65)

    opcion = input("Seleccione una opción (1-7): ").strip()

    if opcion == "1":
        cant_str = input("Ingrese la cantidad de registros a generar [default 50]: ").strip()
        cant = int(cant_str) if cant_str.isdigit() and int(cant_str) > 0 else 50
        registros_actuales = generar_registros_aleatorios(cant)
        print(f"Se han generado {len(registros_actuales)} registros exitosamente.")
        print("\nMuestra de las 3 primeras entradas:")
        for r in registros_actuales[:3]:
            print(f"  • ID: {r['id']} | FR: {r['fr']} | FC: {r['fc']} | SpO2: {r['spo2']}")

    elif opcion == "2":
        if not registros_actuales:
            print("No hay registros cargados. Generando 50 por defecto...")
            registros_actuales = generar_registros_aleatorios(50)

        validos, invalidos = validar_lista_registros(registros_actuales)
        print(f"\n RESULTADO DE VALIDACIÓN REGEX:")
        print(f"  • Registros válidos   : {len(validos)}")
        print(f"  • Registros inválidos : {len(invalidos)}")

        if invalidos:
            print("\nDetalle de errores encontrados:")
            for inv, err in invalidos:
                print(f"  - {inv} -> {err}")
        else:
            print("¡Todos los registros cumplen estrictamente el formato Regex requerido!")

    elif opcion == "3":
        if not registros_actuales:
            print("No hay registros cargados. Generando 50 por defecto...")
            registros_actuales = generar_registros_aleatorios(50)

        validos, _ = validar_lista_registros(registros_actuales)
        ordenados = ordenar_por_frecuencia_cardiaca(validos)

        print("\nExportando archivos a la estructura /data/...")
        guardar_en_txt(ordenados)
        guardar_en_csv(ordenados)
        exportar_a_json(ordenados)
        print("Proceso de guardado y ordenamiento completado.")

    elif opcion == "4":
        registros_importados = importar_desde_json()
        if registros_importados:
            registros_actuales = registros_importados
            print(f"\nSe han cargado {len(registros_actuales)} registros a la memoria activa del programa.")

    elif opcion == "5":
        if not registros_actuales:
            print("Cargando datos desde JSON o generando nuevos para MongoDB...")
            registros_actuales = importar_desde_json()
            if not registros_actuales:
                registros_actuales = generar_registros_aleatorios(50)

        validos, _ = validar_lista_registros(registros_actuales)

        print("\n--- OPERACIONES CON MONGODB ---")
        uri = input("Ingrese la cadena de conexión de MongoDB Atlas (o presione ENTER para modo seguro/simulado): ").strip()
        if uri:
            gestor_mongo.connection_string = uri

        gestor_mongo.conectar()
        gestor_mongo.insertar_registros(validos)
        
        print("\n--- EJECUTANDO CONSULTAS REQUERIDAS ---")
        prom_fc = gestor_mongo.consultar_promedio_fc()
        spo2_baja = gestor_mongo.consultar_spo2_bajo(umbral=94)

        print(f"\nResumen de SpO2 < 94% ({len(spo2_baja)} pacientes):")
        for doc in spo2_baja[:5]:
            print(f"  • ID: {doc.get('id')} | SpO2: {doc.get('spo2')} | FC: {doc.get('fc')}")

        gestor_mongo.exportar_consultas_a_json()

    elif opcion == "6":
        if LOG_FILE.exists():
            print(f"\n --- HISTORIAL DE ACTIVIDADES ({LOG_FILE}) ---")
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lineas = f.readlines()
                for l in lineas[-15:]:  # Mostrar últimas 15 acciones
                    print(f"  {l.strip()}")
        else:
            print("Aún no se ha generado el archivo de log.")

    elif opcion == "7":
        print("\nSaliendo del sistema de gestión biomédica. ¡Hasta pronto!")
        registrar_log("Cierre de sesión de la aplicación.")
        break
    else:
        print("Opción no válida. Ingrese un número entre 1 y 7.")
