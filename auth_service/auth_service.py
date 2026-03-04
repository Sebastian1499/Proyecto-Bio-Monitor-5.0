"""
MODULO 3: Autenticacion con OAuth2 / OpenID Connect (OIDC)
=============================================================
Proyecto Bio-Monitor 5.0 - Entregable 1: Esquema de Ciberseguridad

OAuth2: Protocolo de AUTORIZACION (quien puede hacer que)
OpenID Connect: Capa encima de OAuth2 para AUTENTICACION (quien sos)

Flujo simplificado para Bio-Monitor:
  Dispositivo/App  -->  Auth Server  -->  Token JWT  -->  API de Datos

En produccion usarias Keycloak, Auth0 o Azure AD.
Aqui implementamos la logica central para entender como funciona.

Libreria: PyJWT (pip install PyJWT)
"""

import jwt          # PyJWT
import time
import secrets
import hashlib
from datetime import datetime, timezone


# Clave secreta del servidor de autenticacion (en produccion, usar RSA o ECDSA)
SECRET_KEY = "bio-monitor-secret-super-segura-2026"

# Roles disponibles en el sistema
ROLES = {
    "paciente":   ["leer_propios_datos"],
    "medico":     ["leer_propios_datos", "leer_datos_pacientes", "ver_alertas"],
    "admin":      ["leer_propios_datos", "leer_datos_pacientes", "ver_alertas", "administrar_usuarios"],
    "dispositivo": ["enviar_datos", "recibir_configuracion"],
}

# Base de datos simulada de usuarios
USUARIOS_DB = {
    "dr.garcia": {"password_hash": hashlib.sha256("pass123".encode()).hexdigest(), "rol": "medico"},
    "paciente1":  {"password_hash": hashlib.sha256("mipass".encode()).hexdigest(),  "rol": "paciente"},
    "device-007": {"password_hash": hashlib.sha256("devicepass".encode()).hexdigest(), "rol": "dispositivo"},
    "admin":      {"password_hash": hashlib.sha256("adminpass".encode()).hexdigest(), "rol": "admin"},
}


class ServidorAutenticacion:
    """
    Simula el Authorization Server de OAuth2 con soporte OpenID Connect.
    Emite tokens JWT firmados que los recursos (APIs) pueden verificar.
    """

    def __init__(self, secret: str = SECRET_KEY, expiracion_segundos: int = 3600):
        self.secret = secret
        self.expiracion = expiracion_segundos
        self.tokens_revocados = set()   # Lista negra de tokens

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def autenticar(self, usuario: str, password: str) -> dict:
        """
        Paso 1 de OAuth2: Verificar identidad del usuario.
        
        Retorna un Access Token (JWT) + ID Token (OpenID Connect).
        En OAuth2 real, esto seria el endpoint POST /token
        """
        if usuario not in USUARIOS_DB:
            raise ValueError(f"Usuario '{usuario}' no encontrado")

        usuario_db = USUARIOS_DB[usuario]
        if usuario_db["password_hash"] != self._hash_password(password):
            raise PermissionError("Contrasena incorrecta")

        rol = usuario_db["rol"]
        permisos = ROLES.get(rol, [])
        ahora = int(time.time())

        # ACCESS TOKEN: lo que permite hacer cosas en la API
        access_payload = {
            "sub":         usuario,                # Subject (quien es)
            "rol":         rol,
            "permisos":    permisos,
            "iss":         "biomonitor-auth-server",  # Issuer
            "aud":         "biomonitor-api",           # Audience
            "iat":         ahora,                      # Issued at
            "exp":         ahora + self.expiracion,    # Expira en
            "jti":         secrets.token_hex(16),      # ID unico del token
        }

        # ID TOKEN (OpenID Connect): informacion de identidad del usuario
        id_payload = {
            "sub":        usuario,
            "nombre":     f"Usuario {usuario.title()}",
            "rol":        rol,
            "iss":        "biomonitor-auth-server",
            "aud":        "biomonitor-app",
            "iat":        ahora,
            "exp":        ahora + self.expiracion,
            "auth_time":  ahora,
        }

        access_token = jwt.encode(access_payload, self.secret, algorithm="HS256")
        id_token     = jwt.encode(id_payload,     self.secret, algorithm="HS256")

        print(f"  [Auth] Login exitoso para '{usuario}' (rol: {rol})")

        return {
            "access_token": access_token,
            "id_token":     id_token,
            "token_type":   "Bearer",
            "expires_in":   self.expiracion,
            "scope":        " ".join(permisos),
        }

    def revocar_token(self, access_token: str):
        """
        Cierre de sesion: agrega el token a la lista negra.
        Util para cuando un dispositivo es robado o un medico es dado de baja.
        """
        try:
            payload = jwt.decode(access_token, self.secret, algorithms=["HS256"],
                                 audience="biomonitor-api")
            self.tokens_revocados.add(payload["jti"])
            print(f"  [Auth] Token revocado para usuario '{payload['sub']}'")
        except jwt.InvalidTokenError as e:
            print(f"  [Auth] No se pudo revocar: {e}")


class GuardianRecursos:
    """
    Simula el Resource Server de OAuth2.
    Cada endpoint de la API usa esto para verificar si el token es valido
    y si tiene los permisos necesarios.
    """

    def __init__(self, auth_server: ServidorAutenticacion):
        self.auth = auth_server

    def verificar_acceso(self, access_token: str, permiso_requerido: str) -> dict:
        """
        Valida el token JWT y verifica que tenga el permiso especifico.
        
        Lanza excepcion si:
        - El token esta expirado
        - La firma es invalida
        - El token fue revocado
        - No tiene el permiso requerido
        """
        try:
            payload = jwt.decode(access_token, self.auth.secret, algorithms=["HS256"],
                                 audience="biomonitor-api")
        except jwt.ExpiredSignatureError:
            raise PermissionError("Token expirado. Vuelva a iniciar sesion.")
        except jwt.InvalidTokenError as e:
            raise PermissionError(f"Token invalido: {e}")

        # Verificar lista negra
        if payload["jti"] in self.auth.tokens_revocados:
            raise PermissionError("Token revocado. Acceso denegado.")

        # Verificar permiso especifico
        if permiso_requerido not in payload.get("permisos", []):
            raise PermissionError(
                f"Sin permiso '{permiso_requerido}'. Rol '{payload['rol']}' no autorizado."
            )

        return payload


# ==============================================================
# DEMO RAPIDA
# ==============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  MODULO AUTH - OAuth2 / OpenID Connect")
    print("=" * 55)

    auth   = ServidorAutenticacion()
    guardian = GuardianRecursos(auth)

    # --- Login del medico ---
    print("\n[1] Medico inicia sesion:")
    tokens = auth.autenticar("dr.garcia", "pass123")
    print(f"    Access Token: {tokens['access_token'][:50]}...")
    print(f"    Expira en: {tokens['expires_in']} segundos")
    print(f"    Permisos: {tokens['scope']}")

    # --- Medico accede a datos de pacientes ---
    print("\n[2] Medico intenta ver datos de pacientes:")
    info = guardian.verificar_acceso(tokens["access_token"], "leer_datos_pacientes")
    print(f"    ACCESO CONCEDIDO - Usuario: {info['sub']}, Rol: {info['rol']}")

    # --- Paciente intenta ver datos de otros ---
    print("\n[3] Paciente intenta ver datos ajenos (no permitido):")
    tokens_pac = auth.autenticar("paciente1", "mipass")
    try:
        guardian.verificar_acceso(tokens_pac["access_token"], "leer_datos_pacientes")
    except PermissionError as e:
        print(f"    ACCESO DENEGADO: {e}")

    # --- Revocar token (logout o dispositivo robado) ---
    print("\n[4] Revocar sesion del medico (dispositivo robado):")
    auth.revocar_token(tokens["access_token"])
    try:
        guardian.verificar_acceso(tokens["access_token"], "leer_datos_pacientes")
    except PermissionError as e:
        print(f"    Token revocado: {e}")

    # --- Login del dispositivo IoT ---
    print("\n[5] Dispositivo IoT se autentica para enviar datos:")
    tokens_dev = auth.autenticar("device-007", "devicepass")
    info_dev = guardian.verificar_acceso(tokens_dev["access_token"], "enviar_datos")
    print(f"    DISPOSITIVO AUTORIZADO - Rol: {info_dev['rol']}")

    print("\n[OK] Modulo Auth funcionando correctamente.\n")
