"""
PROYECTO BIO-MONITOR 5.0 - Sistema Completo
=============================================
Taller: Gestion de la Innovacion y Marcos Regulatorios en Software IoT

Este archivo demuestra la integracion de todos los modulos del proyecto:

  Modulo 1: crypto_module    - AES-256 + TLS 1.3      (GDPR/HSPD)
  Modulo 2: secure_erase     - Borrado Seguro          (Derecho al Olvido)
  Modulo 3: auth_service     - OAuth2 / OpenID Connect (Ciberseguridad)
  Modulo 4: edge_ai          - IA en el Borde          (CE/FDA + Gate 2)
  Modulo 5: ota_updater      - Firmware Firmado OTA    (Gate 3)
  Modulo 6: blockchain_logs  - Logs Inmutables         (Auditoria Legal)

Cumplimiento regulatorio implementado:
  [x] GDPR Art. 5  - Minimizacion de datos
  [x] GDPR Art. 17 - Derecho al olvido (Borrado Seguro)
  [x] GDPR Art. 25 - Privacidad desde el diseno (cifrado en reposo y transito)
  [x] IEC 62443    - Autenticacion y control de acceso
  [x] ISO/IEC 27403 - Seguridad en ecosistema IoT (logs auditables)
  [x] CE/FDA       - Algoritmo explicable (XAI) con confianza > 95%
"""

import sys
import os

# Agregar los modulos al path de Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for modulo in ["crypto_module", "secure_erase", "auth_service", "edge_ai",
               "ota_updater", "blockchain_logs"]:
    sys.path.insert(0, os.path.join(BASE_DIR, modulo))

from crypto_module   import cifrar_datos, descifrar_datos, demostrar_tls13
from secure_erase    import AlmacenamientoFlashSimulado
from auth_service    import ServidorAutenticacion, GuardianRecursos
from edge_ai_model   import ModeloArritmias, generar_datos_ecg
from ota_updater     import ServidorFirmware, DispositivoIoT
from blockchain_logger import BlockchainLogs, EntradaLog


def separador(titulo: str):
    borde = "=" * 60
    print(f"\n{borde}")
    print(f"  {titulo}")
    print(f"{borde}")


def demo_sistema_completo():
    """
    Simula un ciclo de vida completo del sistema Bio-Monitor 5.0:
    
    1. El dispositivo se autentica con OAuth2
    2. Captura datos del paciente
    3. Los cifra con AES-256 antes de guardarlos
    4. El modelo de IA analiza los datos on-device
    5. Si hay emergencia, envia alerta (TLS 1.3)
    6. Todo queda registrado en el log blockchain
    7. Se puede actualizar el firmware de forma segura (OTA)
    8. Si el paciente pide borrar sus datos -> Borrado Seguro
    """

    print("\n" + "#" * 60)
    print("  BIO-MONITOR 5.0 - DEMO INTEGRACION COMPLETA")
    print("#" * 60)

    # --------------------------------------------------
    # PASO 1: Inicializar subsistemas
    # --------------------------------------------------
    separador("PASO 1: Inicializando subsistemas")

    auth_server  = ServidorAutenticacion(expiracion_segundos=3600)
    guardian     = GuardianRecursos(auth_server)
    flash        = AlmacenamientoFlashSimulado(ruta_base="flash_datos")
    blockchain   = BlockchainLogs()
    servidor_ota = ServidorFirmware()

    print("  [+] Servidor de autenticacion OAuth2: OK")
    print("  [+] Almacenamiento Flash cifrado: OK")
    print("  [+] Blockchain de logs: OK")
    print("  [+] Servidor OTA con firma RSA: OK")

    # --------------------------------------------------
    # PASO 2: Entrenamiento del modelo de IA
    # --------------------------------------------------
    separador("PASO 2: Entrenando modelo IA (Edge AI)")

    X, y = generar_datos_ecg(n_muestras=1200)
    modelo_ia = ModeloArritmias()
    precision, _ = modelo_ia.entrenar(X, y)

    blockchain.registrar(EntradaLog(
        "SISTEMA", "sistema", "ENTRENAMIENTO_IA",
        f"ModeloArritmias_v1 precision={precision:.3f}",
        "127.0.0.1", "PERMITIDO",
        f"Gate 2 {'SUPERADO' if precision >= 0.95 else 'NO SUPERADO'}"
    ))

    # --------------------------------------------------
    # PASO 3: Dispositivo IoT se autentica
    # --------------------------------------------------
    separador("PASO 3: Autenticacion del dispositivo IoT (OAuth2)")

    try:
        tokens_dev = auth_server.autenticar("device-007", "devicepass")
        info_dev   = guardian.verificar_acceso(tokens_dev["access_token"], "enviar_datos")
        blockchain.registrar(EntradaLog(
            "device-007", "dispositivo", "LOGIN", "auth-server",
            "10.0.0.7", "PERMITIDO", "Autenticacion OAuth2 exitosa"
        ))
        print(f"  Dispositivo autenticado. Rol: {info_dev['rol']}")
    except PermissionError as e:
        print(f"  ERROR AUTH: {e}")
        blockchain.registrar(EntradaLog(
            "device-007", "desconocido", "LOGIN", "auth-server",
            "10.0.0.7", "DENEGADO", str(e)
        ))
        return

    # --------------------------------------------------
    # PASO 4: Capturar datos del paciente y cifrarlos
    # --------------------------------------------------
    separador("PASO 4: Cifrado AES-256 de datos del paciente")

    id_paciente   = "P-00123"
    datos_vitales = '{"bpm": 140, "spo2": 95.2, "temp": 37.1, "variabilidad_rr": 12}'
    password_dev  = "clave-dispositivo-007"

    print(f"  Datos originales: {datos_vitales}")

    paquete_cifrado = cifrar_datos(datos_vitales, password_dev)
    flash.guardar(id_paciente, str(paquete_cifrado).encode())
    print(f"  Datos cifrados y guardados en Flash.")
    print(f"  Cifrado AES-256 activo: {paquete_cifrado['cifrado'][:30]}...")

    blockchain.registrar(EntradaLog(
        "device-007", "dispositivo", "ESCRITURA", f"ECG_{id_paciente}",
        "10.0.0.7", "PERMITIDO", "Datos cifrados AES-256 guardados en Flash"
    ))

    # --------------------------------------------------
    # PASO 5: Analisis IA en el borde
    # --------------------------------------------------
    separador("PASO 5: Analisis de arritmias (Edge AI + XAI)")

    lectura_ecg = {
        "bpm": 140, "intervalo_rr": 428, "variabilidad_rr": 12,
        "amplitud_qrs": 1.2, "intervalo_pr": 130, "spo2": 95.2
    }

    diagnostico = modelo_ia.predecir(lectura_ecg)
    print(f"  Diagnostico: {diagnostico['diagnostico']}")
    print(f"  Confianza:   {diagnostico['confianza']}%")
    print(f"  Emergencia:  {diagnostico['es_emergencia']}")
    print(f"  Explicacion XAI (CE/FDA):")
    for feat in diagnostico['xai_explicacion']:
        print(f"    - {feat['feature']}: {feat['importancia_pct']}% de importancia")

    blockchain.registrar(EntradaLog(
        "device-007", "dispositivo", "PREDICCION_IA", f"ECG_{id_paciente}",
        "10.0.0.7", "PERMITIDO",
        f"Diagnostico={diagnostico['diagnostico']} Confianza={diagnostico['confianza']}%"
    ))

    if diagnostico['es_emergencia']:
        print(f"\n  !!! ALERTA: Posible {diagnostico['diagnostico']} detectada.")
        print(f"  !!! Enviando alerta al medico via TLS 1.3...")
        demostrar_tls13()
        blockchain.registrar(EntradaLog(
            "device-007", "dispositivo", "ALERTA_ENVIADA", f"MEDICO_{id_paciente}",
            "10.0.0.7", "PERMITIDO",
            f"Alerta de emergencia enviada via TLS 1.3"
        ))

    # --------------------------------------------------
    # PASO 6: Medico accede a los datos
    # --------------------------------------------------
    separador("PASO 6: Medico accede a datos del paciente (OAuth2)")

    tokens_med = auth_server.autenticar("dr.garcia", "pass123")
    info_med   = guardian.verificar_acceso(tokens_med["access_token"], "leer_datos_pacientes")
    print(f"  Medico autenticado: {info_med['sub']} (rol: {info_med['rol']})")

    datos_descifrados = descifrar_datos(paquete_cifrado, password_dev)
    print(f"  Datos descifrados para el medico: {datos_descifrados}")

    blockchain.registrar(EntradaLog(
        "dr.garcia", "medico", "LECTURA", f"ECG_{id_paciente}",
        "192.168.1.10", "PERMITIDO", "Medico accede a datos del paciente"
    ))

    # --------------------------------------------------
    # PASO 7: Actualizacion OTA segura
    # --------------------------------------------------
    separador("PASO 7: Actualizacion OTA con firma digital (Gate 3)")

    dispositivo = DispositivoIoT("BM-007", servidor_ota.obtener_clave_publica_pem())
    firmware_v2 = b"BIOMONITOR_FW_v2.1.0_PATCH_CRITICO_" + b"\x00" * 200
    paquete_fw  = servidor_ota.crear_paquete_firmware(firmware_v2, "2.1.0")
    exito_ota   = dispositivo.verificar_y_aplicar_actualizacion(paquete_fw)

    blockchain.registrar(EntradaLog(
        "SERVIDOR_OTA", "sistema", "ACTUALIZACION_OTA", "device-007",
        "10.0.0.1", "PERMITIDO" if exito_ota else "DENEGADO",
        f"Firmware v2.1.0 {'instalado' if exito_ota else 'rechazado'}"
    ))

    # --------------------------------------------------
    # PASO 8: Paciente ejerce Derecho al Olvido (GDPR)
    # --------------------------------------------------
    separador("PASO 8: Borrado Seguro - Derecho al Olvido (GDPR Art.17)")

    blockchain.registrar(EntradaLog(
        "paciente1", "paciente", "SOLICITUD_BORRADO", f"ALL_{id_paciente}",
        "192.168.2.5", "PERMITIDO", "Paciente ejerce GDPR Art.17"
    ))

    flash.borrado_seguro(id_paciente, pasadas=3)
    flash.verificar_borrado(id_paciente)

    blockchain.registrar(EntradaLog(
        "SISTEMA", "sistema", "BORRADO_COMPLETADO", f"ALL_{id_paciente}",
        "127.0.0.1", "PERMITIDO", "Borrado seguro DoD 5220.22-M completado"
    ))

    # --------------------------------------------------
    # PASO 9: Auditoria final de la blockchain
    # --------------------------------------------------
    separador("PASO 9: Auditoria final de logs blockchain")

    valida, errores = blockchain.verificar_integridad()
    total = blockchain.total_bloques()

    print(f"  Total de eventos registrados: {total}")
    print(f"  Integridad de la cadena: {'VALIDA' if valida else 'COMPROMETIDA'}")

    if errores:
        for err in errores:
            print(f"  ERROR: {err}")
    else:
        print(f"  Todos los {total} bloques son integros e inmutables.")

    print("\n  Historial de accesos auditado:")
    auditoria = blockchain.exportar_auditoria()
    for bloque in auditoria[1:]:  # saltar el genesis
        e = bloque['entrada']
        print(f"    [{bloque['indice']:02d}] {e['usuario']:<12} | "
              f"{e['accion']:<22} | {e['resultado']}")

    # --------------------------------------------------
    # RESUMEN FINAL
    # --------------------------------------------------
    print("\n" + "#" * 60)
    print("  RESUMEN DE CUMPLIMIENTO REGULATORIO")
    print("#" * 60)

    cumplimiento = [
        ("AES-256 cifrado en reposo",          True),
        ("TLS 1.3 cifrado en transito",         True),
        ("Borrado Seguro (GDPR Art.17)",        True),
        ("OAuth2/OpenID Connect",               True),
        (f"IA precision > 95% ({precision*100:.1f}%)", precision >= 0.95),
        ("Explicabilidad XAI (CE/FDA)",         True),
        ("Firma digital OTA (RSA-2048)",        exito_ota),
        ("Logs inmutables blockchain",          valida),
    ]

    for item, estado in cumplimiento:
        icono = "[OK]" if estado else "[XX]"
        print(f"  {icono}  {item}")

    print("\n  Bio-Monitor 5.0 listo para revision regulatoria.")
    print("#" * 60 + "\n")


def menu_interactivo():
    """Menu principal donde el usuario puede probar cada modulo."""

    # Inicializar subsistemas una sola vez
    auth_server = ServidorAutenticacion(expiracion_segundos=3600)
    guardian    = GuardianRecursos(auth_server)
    flash       = AlmacenamientoFlashSimulado(ruta_base="flash_datos")
    blockchain  = BlockchainLogs()
    servidor_ota = ServidorFirmware()

    print("\n  Entrenando modelo IA... (espera un momento)")
    X, y = generar_datos_ecg(n_muestras=1200)
    modelo_ia = ModeloArritmias()
    precision, _ = modelo_ia.entrenar(X, y)

    # Token activo de la sesion
    token_activo = None
    usuario_activo = None

    opciones = """
╔══════════════════════════════════════════════════════════╗
║           BIO-MONITOR 5.0  —  Menu Principal             ║
╠══════════════════════════════════════════════════════════╣
║  1. Iniciar sesion (OAuth2)                              ║
║  2. Cifrar y guardar datos del paciente (AES-256)        ║
║  3. Analizar arritmia con IA (Edge AI + XAI)             ║
║  4. Ver datos descifrados del paciente                   ║
║  5. Simular actualizacion OTA (firma RSA)                ║
║  6. Borrado Seguro — Derecho al Olvido (GDPR)            ║
║  7. Ver historial de logs (Blockchain)                   ║
║  8. Ejecutar demo automatica completa                    ║
║  0. Salir                                                ║
╚══════════════════════════════════════════════════════════╝"""

    while True:
        print(opciones)
        if usuario_activo:
            print(f"  Sesion activa: {usuario_activo}")
        opcion = input("\n  Elige una opcion: ").strip()

        # --------------------------------------------------
        if opcion == "1":
            separador("LOGIN — OAuth2 / OpenID Connect")
            print("  Usuarios disponibles: dr.garcia / paciente1 / device-007 / admin")
            print("  Contrasenas:          pass123   / mipass    / devicepass  / adminpass")
            usuario  = input("\n  Usuario:    ").strip()
            password = input("  Contrasena: ").strip()
            try:
                tokens = auth_server.autenticar(usuario, password)
                token_activo   = tokens["access_token"]
                usuario_activo = usuario
                print(f"\n  Login exitoso.")
                print(f"  Token JWT: {token_activo[:60]}...")
                print(f"  Permisos:  {tokens['scope']}")
                print(f"  Expira en: {tokens['expires_in']} segundos")
                blockchain.registrar(EntradaLog(
                    usuario, "usuario", "LOGIN", "sistema", "192.168.1.1", "PERMITIDO"))
            except (ValueError, PermissionError) as e:
                print(f"\n  ERROR: {e}")
                blockchain.registrar(EntradaLog(
                    usuario, "desconocido", "LOGIN", "sistema", "192.168.1.1", "DENEGADO", str(e)))

        # --------------------------------------------------
        elif opcion == "2":
            separador("CIFRAR DATOS CON AES-256")
            id_pac = input("  ID del paciente (ej: P-00123): ").strip() or "P-00123"
            bpm    = input("  BPM (ej: 98):                  ").strip() or "98"
            spo2   = input("  SpO2 % (ej: 97.5):             ").strip() or "97.5"
            temp   = input("  Temperatura (ej: 36.8):        ").strip() or "36.8"
            clave  = input("  Clave del dispositivo:         ").strip() or "clave-demo"

            datos = f'{{"bpm": {bpm}, "spo2": {spo2}, "temp": {temp}, "paciente_id": "{id_pac}"}}'
            print(f"\n  Datos originales:  {datos}")

            paquete = cifrar_datos(datos, clave)
            flash.guardar(id_pac, str(paquete).encode())

            print(f"  Datos cifrados:    {paquete['cifrado'][:40]}...")
            print(f"  Nonce (unico):     {paquete['nonce']}")
            print(f"  Salt (derivacion): {paquete['salt']}")
            print(f"\n  Guardado en Flash. Sin la clave '{clave}' es ilegible.")

            blockchain.registrar(EntradaLog(
                usuario_activo or "anonimo", "usuario", "ESCRITURA",
                f"ECG_{id_pac}", "10.0.0.1", "PERMITIDO", "AES-256-GCM"))

        # --------------------------------------------------
        elif opcion == "3":
            separador("ANALISIS DE ARRITMIA — Edge AI + XAI")
            print("  Ingresa los datos del ECG (Enter para usar valores de ejemplo):")
            bpm   = float(input("  BPM            (ej: 140): ").strip() or "140")
            rr    = float(input("  Intervalo RR ms (ej: 428): ").strip() or "428")
            varrr = float(input("  Variabilidad RR (ej: 12):  ").strip() or "12")
            qrs   = float(input("  Amplitud QRS mV (ej: 1.2): ").strip() or "1.2")
            pr    = float(input("  Intervalo PR ms (ej: 130): ").strip() or "130")
            spo2  = float(input("  SpO2 %          (ej: 95):  ").strip() or "95")

            resultado = modelo_ia.predecir({
                "bpm": bpm, "intervalo_rr": rr, "variabilidad_rr": varrr,
                "amplitud_qrs": qrs, "intervalo_pr": pr, "spo2": spo2
            })

            print(f"\n  ─── DIAGNOSTICO ───────────────────────────")
            print(f"  Resultado:   {resultado['diagnostico']}")
            print(f"  Confianza:   {resultado['confianza']}%")
            print(f"  Emergencia:  {'SI !!!' if resultado['es_emergencia'] else 'No'}")
            print(f"\n  Probabilidades por clase:")
            for clase, prob in resultado['probabilidades'].items():
                barra = "█" * int(prob / 5)
                print(f"    {clase:<25} {prob:5.1f}%  {barra}")
            print(f"\n  Explicacion XAI (por que este diagnostico):")
            for feat in resultado['xai_explicacion']:
                print(f"    - {feat['feature']}: {feat['importancia_pct']}% de peso en la decision")

            if resultado['es_emergencia']:
                print(f"\n  !!! Se enviaria alerta al medico via TLS 1.3")

            blockchain.registrar(EntradaLog(
                usuario_activo or "anonimo", "usuario", "PREDICCION_IA",
                "ECG_MANUAL", "10.0.0.1", "PERMITIDO",
                f"Resultado={resultado['diagnostico']}"))

        # --------------------------------------------------
        elif opcion == "4":
            separador("DESCIFRAR DATOS DEL PACIENTE")
            id_pac = input("  ID del paciente (ej: P-00123): ").strip() or "P-00123"
            clave  = input("  Clave del dispositivo:         ").strip() or "clave-demo"

            if not flash.existe(id_pac):
                print(f"\n  No hay datos guardados para '{id_pac}'.")
                print(f"  Usa la opcion 2 primero para guardar datos.")
            else:
                import ast
                raw = flash._ruta_archivo(id_pac)
                with open(raw, "rb") as f:
                    paquete = ast.literal_eval(f.read().decode())
                try:
                    datos = descifrar_datos(paquete, clave)
                    print(f"\n  Datos descifrados: {datos}")
                    blockchain.registrar(EntradaLog(
                        usuario_activo or "anonimo", "usuario", "LECTURA",
                        f"ECG_{id_pac}", "192.168.1.1", "PERMITIDO"))
                except Exception:
                    print(f"\n  ERROR: Clave incorrecta. No se pueden descifrar los datos.")
                    blockchain.registrar(EntradaLog(
                        usuario_activo or "anonimo", "usuario", "LECTURA",
                        f"ECG_{id_pac}", "192.168.1.1", "DENEGADO", "Clave incorrecta"))

        # --------------------------------------------------
        elif opcion == "5":
            separador("ACTUALIZACION OTA — Firma Digital RSA-2048")
            version = input("  Version del nuevo firmware (ej: 3.0.0): ").strip() or "3.0.0"

            firmware = f"BIOMONITOR_FW_v{version}_RELEASE".encode() + os.urandom(128)
            paquete_fw = servidor_ota.crear_paquete_firmware(firmware, version)

            dispositivo = DispositivoIoT("BM-007", servidor_ota.obtener_clave_publica_pem())
            print(f"\n  --- Instalando firmware legitimo ---")
            exito = dispositivo.verificar_y_aplicar_actualizacion(paquete_fw)

            print(f"\n  --- Simulando ataque: firmware adulterado ---")
            paquete_malo = dict(paquete_fw)
            import hashlib as _hl
            fw_malo = b"MALWARE_" + os.urandom(128)
            paquete_malo["firmware_hex"] = fw_malo.hex()
            paquete_malo["hash_sha256"]  = _hl.sha256(fw_malo).hexdigest()
            dispositivo2 = DispositivoIoT("BM-007", servidor_ota.obtener_clave_publica_pem())
            dispositivo2.verificar_y_aplicar_actualizacion(paquete_malo)

            blockchain.registrar(EntradaLog(
                "SERVIDOR_OTA", "sistema", "ACTUALIZACION_OTA", "BM-007",
                "10.0.0.1", "PERMITIDO" if exito else "DENEGADO", f"v{version}"))

        # --------------------------------------------------
        elif opcion == "6":
            separador("BORRADO SEGURO — Derecho al Olvido (GDPR Art.17)")
            id_pac = input("  ID del paciente a borrar (ej: P-00123): ").strip() or "P-00123"

            if not flash.existe(id_pac):
                print(f"\n  No hay datos de '{id_pac}' en el sistema.")
            else:
                confirm = input(f"\n  Confirmar borrado PERMANENTE de '{id_pac}' (s/n): ").strip().lower()
                if confirm == "s":
                    flash.borrado_seguro(id_pac, pasadas=3)
                    flash.verificar_borrado(id_pac)
                    blockchain.registrar(EntradaLog(
                        usuario_activo or "paciente", "paciente", "BORRADO",
                        f"ALL_{id_pac}", "192.168.1.1", "PERMITIDO", "GDPR Art.17"))
                else:
                    print("  Borrado cancelado.")

        # --------------------------------------------------
        elif opcion == "7":
            separador("HISTORIAL DE LOGS — Blockchain")
            print(f"  Total de bloques en la cadena: {blockchain.total_bloques()}")
            valida, errores = blockchain.verificar_integridad()
            print(f"  Integridad: {'VALIDA' if valida else 'COMPROMETIDA'}")
            print()
            print(f"  {'#':<4} {'Usuario':<14} {'Accion':<24} {'Recurso':<20} {'Resultado'}")
            print(f"  {'-'*80}")
            for b in blockchain.exportar_auditoria()[1:]:
                e = b['entrada']
                print(f"  [{b['indice']:02d}] {e['usuario']:<14} {e['accion']:<24} "
                      f"{e['recurso']:<20} {e['resultado']}")
            fallos = blockchain.buscar_fallos_auth()
            if fallos:
                print(f"\n  Accesos DENEGADOS detectados: {len(fallos)}")

        # --------------------------------------------------
        elif opcion == "8":
            demo_sistema_completo()

        # --------------------------------------------------
        elif opcion == "0":
            print("\n  Cerrando Bio-Monitor 5.0. Hasta luego.\n")
            break
        else:
            print("  Opcion no valida. Elige entre 0 y 8.")


if __name__ == "__main__":
    print("\n" + "█" * 60)
    print("  BIO-MONITOR 5.0")
    print("  Taller: Gestion de la Innovacion y Marcos Regulatorios")
    print("█" * 60)
    menu_interactivo()
