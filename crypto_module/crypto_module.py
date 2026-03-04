"""
MODULO 1: Cifrado AES-256 y Comunicacion Segura TLS 1.3
=========================================================
Proyecto Bio-Monitor 5.0 - Cumplimiento GDPR/HSPD (Seccion 2A)

Este modulo protege los datos de salud del paciente:
- AES-256-GCM: cifra los datos ANTES de guardarlos en la Flash del dispositivo
- TLS 1.3: se usa al enviar datos a la nube (simulado aqui con ejemplo de conexion)
- Clave derivada: usamos PBKDF2 para generar la clave desde una contrasena

Librerias: cryptography (pip install cryptography)
"""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# ==============================================================
# PARTE 1: AES-256-GCM - Cifrado en Reposo (datos en Flash)
# ==============================================================

def derivar_clave_desde_password(password: str, salt: bytes = None):
    """
    Convierte una contrasena legible en una clave AES-256 segura.
    Usa PBKDF2 con SHA-256 (estandar de la industria).
    
    - password: contrasena del usuario o ID del dispositivo
    - salt: bytes aleatorios para que dos passwords iguales den claves distintas
    """
    if salt is None:
        salt = os.urandom(16)  # 16 bytes aleatorios (nuevo cada vez)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,          # 32 bytes = 256 bits = AES-256
        salt=salt,
        iterations=100_000  # 100,000 iteraciones -> dificulta ataques de fuerza bruta
    )
    clave = kdf.derive(password.encode("utf-8"))
    return clave, salt


def cifrar_datos(datos: str, password: str):
    """
    Cifra datos de salud (ej: frecuencia cardiaca, SpO2) con AES-256-GCM.
    
    GCM = Galois/Counter Mode -> ademas de cifrar, VERIFICA integridad.
    Si alguien altera los datos cifrados, la descifrada falla. Perfecto para datos medicos.
    
    Retorna: diccionario con todo lo necesario para descifrar despues
    """
    clave, salt = derivar_clave_desde_password(password)

    aesgcm = AESGCM(clave)
    nonce = os.urandom(12)  # Numero unico por mensaje (12 bytes para GCM)

    datos_bytes = datos.encode("utf-8")
    datos_cifrados = aesgcm.encrypt(nonce, datos_bytes, None)

    # Guardamos todo lo necesario para descifrar
    paquete = {
        "salt":   base64.b64encode(salt).decode(),
        "nonce":  base64.b64encode(nonce).decode(),
        "cifrado": base64.b64encode(datos_cifrados).decode(),
    }
    return paquete


def descifrar_datos(paquete: dict, password: str):
    """
    Descifra los datos usando la misma contrasena.
    Si los datos fueron alterados o la password es incorrecta, lanza una excepcion.
    """
    salt   = base64.b64decode(paquete["salt"])
    nonce  = base64.b64decode(paquete["nonce"])
    cifrado = base64.b64decode(paquete["cifrado"])

    clave, _ = derivar_clave_desde_password(password, salt)
    aesgcm = AESGCM(clave)

    datos_originales = aesgcm.decrypt(nonce, cifrado, None)
    return datos_originales.decode("utf-8")


# ==============================================================
# PARTE 2: TLS 1.3 - Cifrado en Transito (envio a la nube)
# ==============================================================

def demostrar_tls13():
    """
    Muestra como se configura correctamente una conexion TLS 1.3 en Python.
    En un dispositivo IoT real, esto seria la capa de transporte al enviar datos al servidor.
    
    NOTA: Este codigo es un ejemplo de configuracion correcta.
    Para ejecutarlo necesitarias un servidor real. Aqui solo mostramos la configuracion.
    """
    import ssl

    contexto = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    # Forzamos solo TLS 1.3 (mas seguro que 1.2)
    contexto.minimum_version = ssl.TLSVersion.TLSv1_3
    contexto.maximum_version = ssl.TLSVersion.TLSv1_3

    # Verificamos el certificado del servidor (NUNCA desactivar en produccion)
    contexto.verify_mode = ssl.CERT_REQUIRED
    contexto.check_hostname = True
    contexto.load_default_certs()

    print("  [TLS 1.3] Contexto SSL configurado correctamente")
    print(f"  [TLS 1.3] Version minima: {contexto.minimum_version.name}")
    print(f"  [TLS 1.3] Version maxima: {contexto.maximum_version.name}")
    print("  [TLS 1.3] Verificacion de certificado: ACTIVADA")
    print("  [TLS 1.3] Listo para conectar a 'api.biomonitor.cloud:443'")

    return contexto


# ==============================================================
# DEMO RAPIDA
# ==============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  MODULO CRYPTO - AES-256 + TLS 1.3")
    print("=" * 55)

    # Simular datos de un paciente
    datos_paciente = '{"bpm": 98, "spo2": 97.5, "temp": 36.8, "paciente_id": "P-00123"}'
    password_dispositivo = "clave-secreta-dispositivo-007"

    print(f"\n[1] Datos originales:\n    {datos_paciente}")

    # Cifrar
    paquete_cifrado = cifrar_datos(datos_paciente, password_dispositivo)
    print(f"\n[2] Datos cifrados con AES-256-GCM:")
    print(f"    cifrado : {paquete_cifrado['cifrado'][:40]}...")
    print(f"    nonce   : {paquete_cifrado['nonce']}")
    print(f"    salt    : {paquete_cifrado['salt']}")

    # Descifrar
    datos_recuperados = descifrar_datos(paquete_cifrado, password_dispositivo)
    print(f"\n[3] Datos descifrados:\n    {datos_recuperados}")
    print(f"\n[4] Verificacion: {'CORRECTA' if datos_paciente == datos_recuperados else 'FALLIDA'}")

    # TLS
    print("\n[5] Configuracion TLS 1.3 para envio a la nube:")
    demostrar_tls13()

    print("\n[OK] Modulo Crypto funcionando correctamente.\n")
