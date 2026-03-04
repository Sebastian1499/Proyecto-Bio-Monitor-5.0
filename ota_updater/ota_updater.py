"""
MODULO 5: Actualizador OTA con Firma Digital
==============================================
Proyecto Bio-Monitor 5.0 - Gate 3: Certificacion de Ciberseguridad

OTA = Over-The-Air: actualizar el firmware del dispositivo de forma inalambrica.

El problema de seguridad: si un atacante intercepta la actualizacion y manda
un firmware malicioso, puede tomar control del dispositivo medico.

Solucion: FIRMA DIGITAL con RSA-2048
- El servidor firma el firmware con su CLAVE PRIVADA (solo el servidor la conoce)
- El dispositivo verifica la firma con la CLAVE PUBLICA (embebida en el dispositivo)
- Si la firma no es valida -> el dispositivo RECHAZA la actualizacion

Flujo:
  [Servidor] Genera firmware -> Firma con clave privada -> Publica firma + firmware
  [Dispositivo] Descarga -> Verifica firma con clave publica -> Instala si OK

Libreria: cryptography
"""

import os
import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from datetime import datetime, timezone


class ServidorFirmware:
    """
    Representa el servidor de actualizaciones de Bio-Monitor.
    Firma cada nuevo firmware antes de distribuirlo.
    """

    def __init__(self):
        print("  [Servidor OTA] Generando par de claves RSA-2048...")
        # Generamos el par de claves (en produccion estas estarian en un HSM)
        self._clave_privada: RSAPrivateKey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.clave_publica: RSAPublicKey = self._clave_privada.public_key()
        print("  [Servidor OTA] Claves RSA-2048 generadas.")

    def obtener_clave_publica_pem(self) -> bytes:
        """Exporta la clave publica en formato PEM para distribuir a los dispositivos."""
        return self.clave_publica.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def crear_paquete_firmware(self, contenido_firmware: bytes, version: str) -> dict:
        """
        Crea un paquete de firmware firmado digitalmente.
        
        El hash SHA-256 del firmware se calcula y luego se firma.
        Esto garantiza:
        1. AUTENTICIDAD: solo el servidor con la clave privada pudo firmar
        2. INTEGRIDAD: si el firmware cambia 1 bit, el hash cambia y la verificacion falla
        """
        # 1. Calcular hash SHA-256 del firmware
        hash_firmware = hashlib.sha256(contenido_firmware).hexdigest()

        # 2. Firmar el hash con la clave privada (RSA-PSS + SHA-256)
        firma = self._clave_privada.sign(
            contenido_firmware,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        paquete = {
            "version":          version,
            "fecha_emision":    datetime.now(timezone.utc).isoformat(),
            "tamano_bytes":     len(contenido_firmware),
            "hash_sha256":      hash_firmware,
            "firma_hex":        firma.hex(),
            "firmware_hex":     contenido_firmware.hex(),
            "algoritmo_firma":  "RSA-2048-PSS-SHA256",
        }

        print(f"  [Servidor OTA] Paquete v{version} creado y firmado.")
        print(f"  [Servidor OTA] Hash SHA-256: {hash_firmware[:16]}...")
        print(f"  [Servidor OTA] Firma: {firma.hex()[:20]}...")

        return paquete


class DispositivoIoT:
    """
    Simula el dispositivo Bio-Monitor wearable.
    Tiene embebida la clave publica del servidor para verificar actualizaciones.
    """

    def __init__(self, id_dispositivo: str, clave_publica_pem: bytes):
        self.id_dispositivo = id_dispositivo
        self.firmware_actual = "v1.0.0"
        self.clave_publica: RSAPublicKey = serialization.load_pem_public_key(clave_publica_pem)
        print(f"  [Dispositivo {id_dispositivo}] Iniciado con firmware {self.firmware_actual}")

    def verificar_y_aplicar_actualizacion(self, paquete: dict) -> bool:
        """
        Proceso completo de actualizacion OTA segura:
        
        1. Verificar la firma digital del paquete
        2. Verificar que el hash del firmware sea correcto
        3. Si todo OK -> simular instalacion
        4. Si algo falla -> rechazar completamente
        """
        version = paquete.get("version", "desconocida")
        print(f"\n  [OTA] Recibiendo paquete de actualizacion v{version}...")

        # Paso 1: Reconstruir datos originales
        firmware_bytes = bytes.fromhex(paquete["firmware_hex"])
        firma_bytes    = bytes.fromhex(paquete["firma_hex"])

        # Paso 2: Verificar firma RSA
        try:
            self.clave_publica.verify(
                firma_bytes,
                firmware_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            print(f"  [OTA] Firma RSA: VALIDA")
        except Exception as e:
            print(f"  [OTA] FIRMA INVALIDA: {e}")
            print(f"  [OTA] ACTUALIZACION RECHAZADA - Posible firmware malicioso!")
            return False

        # Paso 3: Verificar integridad con hash SHA-256
        hash_calculado = hashlib.sha256(firmware_bytes).hexdigest()
        if hash_calculado != paquete["hash_sha256"]:
            print(f"  [OTA] HASH INCORRECTO: firmware corrompido!")
            print(f"  [OTA] ACTUALIZACION RECHAZADA")
            return False

        print(f"  [OTA] Integridad SHA-256: VERIFICADA")

        # Paso 4: Simulacion de instalacion
        print(f"  [OTA] Instalando firmware v{version} ({paquete['tamano_bytes']} bytes)...")
        print(f"  [OTA] [################] 100%")
        firmware_anterior = self.firmware_actual
        self.firmware_actual = version
        print(f"  [OTA] Dispositivo actualizado: {firmware_anterior} -> {self.firmware_actual}")
        print(f"  [OTA] ACTUALIZACION EXITOSA")
        return True


# ==============================================================
# DEMO RAPIDA
# ==============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  MODULO OTA - Firmware con Firma Digital RSA")
    print("=" * 55)

    # 1. Servidor genera claves y firma un nuevo firmware
    print("\n[1] Inicializando servidor de actualizaciones:")
    servidor = ServidorFirmware()

    print("\n[2] Servidor crea nuevo firmware v2.1.0:")
    # Simulamos el contenido binario del firmware
    firmware_nuevo = b"BIOMONITOR_FIRMWARE_v2.1.0_" + os.urandom(256)
    paquete_legit = servidor.crear_paquete_firmware(firmware_nuevo, version="2.1.0")

    # 2. Dispositivo recibe la clave publica del servidor (en fabrica)
    print("\n[3] Dispositivo IoT recibe la clave publica del servidor:")
    dispositivo = DispositivoIoT("BM-007", servidor.obtener_clave_publica_pem())

    # 3. Actualizacion legitima
    print("\n[4] Instalando actualizacion LEGITIMA v2.1.0:")
    exito = dispositivo.verificar_y_aplicar_actualizacion(paquete_legit)
    print(f"    Resultado: {'EXITO' if exito else 'FALLIDO'}")

    # 4. Intento de firmware malicioso (atacante modifica el firmware)
    print("\n[5] Simulando ataque: firmware modificado por atacante:")
    paquete_malicioso = dict(paquete_legit)
    firmware_malicioso = b"MALWARE_" + os.urandom(256)
    # El atacante cambia el firmware pero NO puede re-firmar (no tiene la clave privada)
    paquete_malicioso["firmware_hex"] = firmware_malicioso.hex()
    paquete_malicioso["hash_sha256"]  = hashlib.sha256(firmware_malicioso).hexdigest()
    exito = dispositivo.verificar_y_aplicar_actualizacion(paquete_malicioso)
    print(f"    Resultado: {'EXITO' if exito else 'ATAQUE BLOQUEADO'}")

    print("\n[OK] Modulo OTA funcionando correctamente.\n")
