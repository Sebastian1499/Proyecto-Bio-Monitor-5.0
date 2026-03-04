"""
MODULO 2: Borrado Seguro (Secure Erase) - Derecho al Olvido
=============================================================
Proyecto Bio-Monitor 5.0 - Cumplimiento GDPR Art. 17 (Seccion 2A)

El GDPR exige que los usuarios puedan pedir borrar sus datos.
En un dispositivo IoT con memoria Flash NO basta con "delete" normal,
porque el archivo queda en disco hasta que se sobreescribe.

Solucion: Sobreescribir los datos con patrones aleatorios antes de eliminar.

Este modulo simula ese proceso como lo haria un nodo IoT real.
"""

import os
import struct
import hashlib


class AlmacenamientoFlashSimulado:
    """
    Simula el sistema de archivos de la memoria Flash de un dispositivo IoT.
    En un dispositivo real, esto seria escritura directa a sectores de memoria.
    """

    def __init__(self, ruta_base: str = "flash_storage"):
        self.ruta_base = ruta_base
        os.makedirs(ruta_base, exist_ok=True)
        print(f"  [Flash] Almacenamiento inicializado en: '{ruta_base}/'")

    def _ruta_archivo(self, id_paciente: str) -> str:
        # Usamos hash del ID para no exponer el ID directamente en el nombre de archivo
        nombre_hash = hashlib.sha256(id_paciente.encode()).hexdigest()[:16]
        return os.path.join(self.ruta_base, f"datos_{nombre_hash}.bin")

    def guardar(self, id_paciente: str, datos: bytes):
        """Guarda datos del paciente en la Flash simulada."""
        ruta = self._ruta_archivo(id_paciente)
        with open(ruta, "wb") as f:
            f.write(datos)
        print(f"  [Flash] Datos guardados para paciente '{id_paciente}' ({len(datos)} bytes)")
        return ruta

    def existe(self, id_paciente: str) -> bool:
        return os.path.exists(self._ruta_archivo(id_paciente))

    def borrado_seguro(self, id_paciente: str, pasadas: int = 3) -> bool:
        """
        Borrado Seguro de datos del paciente.
        
        Algoritmo: DoD 5220.22-M (estandar del Departamento de Defensa de EE.UU.)
        - Pasada 1: Sobreescribir con 0x00 (todos ceros)
        - Pasada 2: Sobreescribir con 0xFF (todos unos)  
        - Pasada 3: Sobreescribir con bytes ALEATORIOS
        - Final: Eliminar el archivo

        En dispositivos IoT reales (Flash NAND) se hace a nivel de sector/bloque.
        
        pasadas: numero de sobreescrituras (minimo 3 para cumplir GDPR)
        """
        ruta = self._ruta_archivo(id_paciente)

        if not os.path.exists(ruta):
            print(f"  [BorradoSeguro] No se encontraron datos para '{id_paciente}'")
            return False

        tamano = os.path.getsize(ruta)
        print(f"\n  [BorradoSeguro] Iniciando borrado de {tamano} bytes para '{id_paciente}'")
        print(f"  [BorradoSeguro] Algoritmo: DoD 5220.22-M ({pasadas} pasadas)")

        patrones = []
        for i in range(pasadas):
            if i == 0:
                patron = b'\x00' * tamano        # Pasada 1: ceros
                nombre_patron = "0x00 (ceros)"
            elif i == 1:
                patron = b'\xFF' * tamano        # Pasada 2: unos
                nombre_patron = "0xFF (unos)"
            else:
                patron = os.urandom(tamano)      # Pasada 3+: aleatorio
                nombre_patron = "aleatorio"

            with open(ruta, "r+b") as f:
                f.seek(0)
                f.write(patron)
                f.flush()
                os.fsync(f.fileno())             # Forzar escritura fisica al disco

            print(f"  [BorradoSeguro]   Pasada {i+1}/{pasadas}: {nombre_patron} - OK")

        # Ultimo paso: eliminar el archivo
        os.remove(ruta)
        print(f"  [BorradoSeguro] Archivo eliminado del sistema de archivos.")
        print(f"  [BorradoSeguro] BORRADO COMPLETADO - Derecho al Olvido cumplido.")
        return True

    def verificar_borrado(self, id_paciente: str) -> bool:
        """Verifica que el archivo ya no existe (auditoria post-borrado)."""
        existe = self.existe(id_paciente)
        if not existe:
            print(f"  [Verificacion] Datos de '{id_paciente}': NO EXISTEN (borrado confirmado)")
        else:
            print(f"  [Verificacion] ADVERTENCIA: Datos de '{id_paciente}' aun presentes")
        return not existe


# ==============================================================
# DEMO RAPIDA
# ==============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  MODULO BORRADO SEGURO - Derecho al Olvido GDPR")
    print("=" * 55)

    flash = AlmacenamientoFlashSimulado(ruta_base="flash_storage")

    # Simular datos de paciente guardados en la Flash
    id_paciente = "P-00123"
    datos_ejemplo = b'{"bpm": 98, "spo2": 97.5, "historial": "30 dias de lecturas..."}'

    print(f"\n[1] Guardando datos del paciente '{id_paciente}'...")
    flash.guardar(id_paciente, datos_ejemplo)

    print(f"\n[2] Verificando existencia antes del borrado:")
    print(f"    Datos existen: {flash.existe(id_paciente)}")

    print(f"\n[3] Paciente solicita 'Derecho al Olvido' (GDPR Art.17):")
    flash.borrado_seguro(id_paciente, pasadas=3)

    print(f"\n[4] Auditoria post-borrado:")
    flash.verificar_borrado(id_paciente)

    print("\n[OK] Modulo Borrado Seguro funcionando correctamente.\n")
