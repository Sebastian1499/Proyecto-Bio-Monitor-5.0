"""
MODULO 6: Blockchain para Logs de Acceso Inmutables
======================================================
Proyecto Bio-Monitor 5.0 - Seccion 5: Mitigacion de Fuga de Datos

Problema: Si el sistema es hackeado y se filtran datos medicos, necesitamos
poder AUDITAR quien accedio a que datos y cuando. El atacante no puede borrar
o modificar estos registros porque estan encadenados con hash.

Blockchain simplificada (sin criptomonedas, sin red P2P):
- Cada log de acceso es un BLOQUE
- Cada bloque contiene el HASH del bloque anterior
- Si alguien modifica un bloque viejo -> todos los hashes siguientes se rompen
- Esto garantiza INMUTABILIDAD: sabemos exactamente si el log fue alterado

Para cumplimiento legal (ISO/IEC 27403 + GDPR):
  - Quien accedio a los datos (usuario + rol)
  - Desde donde (IP del dispositivo)
  - Que dato accedio (ID paciente + tipo de dato)
  - Cuando (timestamp UTC)
  - Resultado (permitido o denegado)
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class EntradaLog:
    """Representa un evento de acceso a datos medicos."""
    usuario:       str
    rol:           str
    accion:        str          # "LECTURA", "ESCRITURA", "BORRADO", "LOGIN", "FALLO_AUTH"
    recurso:       str          # Que dato fue accedido (ej: "ECG_P00123")
    ip_origen:     str
    resultado:     str          # "PERMITIDO" o "DENEGADO"
    detalle:       str = ""     # Informacion adicional


class BloqueLog:
    """
    Un bloque en la cadena de logs.
    Contiene: datos del evento + hash del bloque anterior + su propio hash.
    """

    def __init__(self, indice: int, entrada: EntradaLog, hash_anterior: str):
        self.indice         = indice
        self.timestamp      = datetime.now(timezone.utc).isoformat()
        self.entrada        = entrada
        self.hash_anterior  = hash_anterior
        self.hash_propio    = self._calcular_hash()

    def _calcular_hash(self) -> str:
        """
        El hash depende de: indice + timestamp + datos + hash_anterior.
        Si cualquiera de estos cambia, el hash cambia completamente.
        """
        contenido = json.dumps({
            "indice":        self.indice,
            "timestamp":     self.timestamp,
            "entrada":       asdict(self.entrada),
            "hash_anterior": self.hash_anterior,
        }, sort_keys=True, ensure_ascii=False)

        return hashlib.sha256(contenido.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        return {
            "indice":        self.indice,
            "timestamp":     self.timestamp,
            "entrada":       asdict(self.entrada),
            "hash_anterior": self.hash_anterior,
            "hash_propio":   self.hash_propio,
        }


class BlockchainLogs:
    """
    Cadena de bloques para almacenar logs de acceso inmutables.
    
    Una vez que un log es registrado, no puede modificarse sin que
    la verificacion de integridad lo detecte.
    """

    GENESIS_HASH = "0" * 64  # Hash del bloque genesis (bloque cero)

    def __init__(self):
        self.cadena: List[BloqueLog] = []
        self._crear_bloque_genesis()

    def _crear_bloque_genesis(self):
        """El bloque genesis es el primero, no tiene padre."""
        entrada_genesis = EntradaLog(
            usuario  = "SISTEMA",
            rol      = "sistema",
            accion   = "INICIO",
            recurso  = "blockchain",
            ip_origen = "127.0.0.1",
            resultado = "PERMITIDO",
            detalle  = "Blockchain de logs iniciada - Bio-Monitor 5.0"
        )
        bloque = BloqueLog(0, entrada_genesis, self.GENESIS_HASH)
        self.cadena.append(bloque)

    def registrar(self, entrada: EntradaLog) -> BloqueLog:
        """
        Agrega un nuevo log a la cadena.
        El nuevo bloque referencia el hash del ultimo bloque (inmutabilidad).
        """
        hash_previo = self.cadena[-1].hash_propio
        nuevo_bloque = BloqueLog(len(self.cadena), entrada, hash_previo)
        self.cadena.append(nuevo_bloque)
        return nuevo_bloque

    def verificar_integridad(self) -> tuple[bool, List[str]]:
        """
        Recorre TODA la cadena y verifica que ningun bloque fue alterado.
        
        Un bloque esta corrupto si:
        1. Su hash_propio no coincide con el hash recalculado de su contenido
        2. Su hash_anterior no coincide con el hash del bloque previo
        
        Retorna: (es_valida, lista_de_errores)
        """
        errores = []

        for i, bloque in enumerate(self.cadena):
            # Verificar hash propio
            hash_recalculado = bloque._calcular_hash()
            if bloque.hash_propio != hash_recalculado:
                errores.append(f"Bloque {i}: hash_propio alterado")

            # Verificar enlace con bloque anterior
            if i > 0:
                hash_previo_real = self.cadena[i-1].hash_propio
                if bloque.hash_anterior != hash_previo_real:
                    errores.append(f"Bloque {i}: enlace con bloque {i-1} roto")

        es_valida = len(errores) == 0
        return es_valida, errores

    def buscar_por_usuario(self, usuario: str) -> List[dict]:
        """Filtra todos los eventos de acceso de un usuario especifico."""
        return [
            b.to_dict() for b in self.cadena
            if b.entrada.usuario == usuario
        ]

    def buscar_fallos_auth(self) -> List[dict]:
        """Retorna todos los intentos de acceso fallidos (util para detectar ataques)."""
        return [
            b.to_dict() for b in self.cadena
            if b.entrada.resultado == "DENEGADO"
        ]

    def exportar_auditoria(self) -> List[dict]:
        """Exporta toda la cadena para auditoria externa (reguladores)."""
        return [b.to_dict() for b in self.cadena]

    def total_bloques(self) -> int:
        return len(self.cadena)


# ==============================================================
# DEMO RAPIDA
# ==============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  MODULO BLOCKCHAIN - Logs de Acceso Inmutables")
    print("=" * 55)

    bc = BlockchainLogs()
    print(f"\n[1] Blockchain iniciada. Bloques: {bc.total_bloques()}")

    # Registrar eventos de acceso tipicos
    eventos = [
        EntradaLog("dr.garcia",  "medico",    "LOGIN",    "sistema",      "192.168.1.10", "PERMITIDO"),
        EntradaLog("dr.garcia",  "medico",    "LECTURA",  "ECG_P00123",   "192.168.1.10", "PERMITIDO"),
        EntradaLog("dr.garcia",  "medico",    "LECTURA",  "ECG_P00456",   "192.168.1.10", "PERMITIDO"),
        EntradaLog("device-007", "dispositivo","ESCRITURA","BPM_P00123",  "10.0.0.7",     "PERMITIDO"),
        EntradaLog("atacante",   "desconocido","LECTURA", "ECG_P00123",   "203.0.113.42", "DENEGADO",  "IP no autorizada"),
        EntradaLog("atacante",   "desconocido","LECTURA", "HISTORIAL_ALL","203.0.113.42", "DENEGADO",  "Sin permisos"),
        EntradaLog("admin",      "admin",      "BORRADO", "ECG_P00789",   "192.168.1.1",  "PERMITIDO", "Solicitud GDPR Art.17"),
    ]

    print("\n[2] Registrando eventos de acceso:")
    for evento in eventos:
        bloque = bc.registrar(evento)
        estado = "OK " if evento.resultado == "PERMITIDO" else "!!!"
        print(f"    [{estado}] Bloque {bloque.indice}: {evento.usuario} -> {evento.accion} {evento.recurso} [{evento.resultado}]")

    print(f"\n[3] Total bloques en la cadena: {bc.total_bloques()}")

    # Verificar integridad
    print("\n[4] Verificando integridad de toda la cadena:")
    valida, errores = bc.verificar_integridad()
    print(f"    Cadena valida: {valida}")
    if valida:
        print(f"    Todos los {bc.total_bloques()} bloques son integros.")

    # Detectar intentos de ataque
    fallos = bc.buscar_fallos_auth()
    print(f"\n[5] Intentos de acceso DENEGADOS (posibles ataques): {len(fallos)}")
    for f in fallos:
        print(f"    -> {f['entrada']['usuario']} desde {f['entrada']['ip_origen']} "
              f"intentó {f['entrada']['accion']} en {f['entrada']['recurso']}")

    # Simular tamper: modificar un bloque y detectarlo
    print("\n[6] Simulando ataque: atacante modifica log pasado:")
    bloque_atacado = bc.cadena[2]
    bloque_atacado.entrada.ip_origen = "127.0.0.1"  # El atacante cambia su IP para ocultarse
    bloque_atacado.entrada.resultado = "PERMITIDO"

    valida_post, errores_post = bc.verificar_integridad()
    print(f"    Cadena valida despues del ataque: {valida_post}")
    for err in errores_post:
        print(f"    DETECTADO: {err}")

    print("\n[OK] Modulo Blockchain funcionando correctamente.\n")
