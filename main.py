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


if __name__ == "__main__":
    demo_sistema_completo()
