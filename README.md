# Bio-Monitor 5.0

> **Taller:** Gestión de la Innovación y Marcos Regulatorios en Software IoT

Sistema IoT vestible (*wearable*) que monitorea signos vitales y usa **Inteligencia Artificial en el Borde** para predecir arritmias — implementando en código todos los marcos regulatorios exigidos: GDPR, IEC 62443, ISO/IEC 27403 y certificación CE/FDA.

---

## Índice

1. [Contexto del Proyecto](#1-contexto-del-proyecto)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Tecnologías utilizadas](#3-tecnologías-utilizadas)
4. [Estructura del proyecto](#4-estructura-del-proyecto)
5. [Instalación](#5-instalación)
6. [Cómo se ejecuta](#6-cómo-se-ejecuta)
7. [Qué hace cada módulo](#7-qué-hace-cada-módulo)
8. [Salida real del sistema](#8-salida-real-del-sistema)
9. [Cumplimiento regulatorio](#9-cumplimiento-regulatorio)
10. [Evolución TRL y Gates](#10-evolución-trl-y-gates)
11. [Matriz de riesgos y mitigaciones implementadas](#11-matriz-de-riesgos-y-mitigaciones-implementadas)
12. [Usuarios de prueba](#12-usuarios-de-prueba)

---

## 1. Contexto del Proyecto

Una Startup de ingeniería busca innovar con un dispositivo IoT vestible que:
- Monitorea signos vitales en tiempo real (frecuencia cardíaca, SpO2, temperatura, ECG)
- Usa **Inteligencia Artificial en el Borde** (Edge AI) para predecir arritmias sin enviar datos a internet
- Debe cumplir regulaciones estrictas de **protección de datos de salud** y **certificaciones de dispositivos médicos** antes de ser comercializado

**El reto:** el software no puede ser una "caja negra". Debe ser auditable, explicable, seguro y respetuoso con la privacidad del paciente desde el primer día.

---

## 2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    DISPOSITIVO IoT (Wearable)                │
│                                                             │
│  Sensores ECG/SpO2  ──►  Modelo IA (Edge AI)  ──►  Alerta  │
│         │                     │                             │
│         ▼                     ▼                             │
│   AES-256-GCM            Explicación XAI                    │
│   (cifrado Flash)        (CE/FDA)                           │
│         │                                                   │
│   Borrado Seguro                                            │
│   (GDPR Art.17)                                             │
└──────────────┬──────────────────────────────────────────────┘
               │  TLS 1.3 (cifrado en tránsito)
               ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR / NUBE                           │
│                                                             │
│  OAuth2 / OpenID Connect  ──►  Control de Acceso por Roles  │
│  (autenticación JWT)            (médico / paciente / admin) │
│                                                             │
│  Servidor OTA  ──►  RSA-2048  ──►  Firmware firmado         │
│                                                             │
│  Blockchain de Logs  ──►  Auditoría inmutable               │
│  (SHA-256 encadenado)      (ISO/IEC 27403)                  │
└─────────────────────────────────────────────────────────────┘
```

**Flujo completo de un ciclo:**
1. El dispositivo se autentica con OAuth2 → recibe token JWT
2. Captura señales vitales del paciente
3. El modelo de IA analiza los datos **en el dispositivo** (no salen a internet)
4. Los datos se cifran con AES-256 antes de guardarse en memoria Flash
5. Si hay emergencia, envía alerta al médico por TLS 1.3
6. El médico accede con su propio token (rol `medico`)
7. Todo evento queda registrado en la blockchain de logs
8. Las actualizaciones de firmware se verifican con firma RSA antes de instalar
9. Si el paciente pide borrar sus datos, se aplica Borrado Seguro (3 pasadas)

---

## 3. Tecnologías utilizadas

| Tecnología | Versión | Uso en el proyecto |
|---|---|---|
| **Python** | 3.10+ | Lenguaje principal de todos los módulos |
| **cryptography** | ≥42.0 | AES-256-GCM (cifrado en reposo) + RSA-2048 (firma OTA) |
| **PyJWT** | ≥2.8 | Generación y verificación de tokens JWT para OAuth2 |
| **scikit-learn** | ≥1.4 | Modelo Random Forest para clasificación de arritmias |
| **numpy** | ≥2.0 | Generación y procesamiento de datos ECG |
| **ssl** (stdlib) | — | Configuración de contexto TLS 1.3 (módulo estándar de Python) |
| **hashlib** (stdlib) | — | SHA-256 para integridad de bloques y hashing de contraseñas |

---

## 4. Estructura del proyecto

```
Proyecto-Bio-Monitor-5.0/
│
├── main.py                              ← Punto de entrada: demo de integración completa
├── requirements.txt                     ← Dependencias (pip install -r requirements.txt)
├── .gitignore
│
├── crypto_module/
│   └── crypto_module.py                 ← Módulo 1: AES-256-GCM + TLS 1.3
│
├── secure_erase/
│   └── secure_erase.py                  ← Módulo 2: Borrado Seguro DoD 5220.22-M
│
├── auth_service/
│   └── auth_service.py                  ← Módulo 3: OAuth2 + OpenID Connect + JWT
│
├── edge_ai/
│   └── edge_ai_model.py                 ← Módulo 4: IA en el Borde + XAI
│
├── ota_updater/
│   └── ota_updater.py                   ← Módulo 5: Firmware OTA con firma RSA-2048
│
└── blockchain_logs/
    └── blockchain_logger.py             ← Módulo 6: Logs de acceso inmutables
```

---

## 5. Instalación

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/Sebastian1499/Proyecto-Bio-Monitor-5.0.git
cd Proyecto-Bio-Monitor-5.0
```

### Paso 2 — (Recomendado) Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Paso 3 — Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 6. Cómo se ejecuta

### Demo completa — todos los módulos integrados

```bash
python main.py
```

### Módulos individuales — para ver cada uno por separado

```bash
python crypto_module/crypto_module.py      # AES-256 + TLS 1.3
python secure_erase/secure_erase.py        # Borrado Seguro
python auth_service/auth_service.py        # OAuth2 / OpenID Connect
python edge_ai/edge_ai_model.py            # IA detección arritmias
python ota_updater/ota_updater.py          # Actualización OTA segura
python blockchain_logs/blockchain_logger.py # Blockchain de logs
```

---

## 7. Qué hace cada módulo

### Módulo 1 — `crypto_module.py` · Cifrado AES-256 + TLS 1.3

**Problema que resuelve:** los datos de salud del paciente (BPM, SpO2, temperatura) no pueden guardarse en texto plano en la memoria del dispositivo. Si el dispositivo es robado o hackeado, los datos deben ser ilegibles.

**Solución implementada:**
- **AES-256-GCM:** cifra los datos antes de escribirlos en la Flash. GCM (Galois/Counter Mode) no solo cifra, también verifica integridad — si alguien altera los datos cifrados, la descifrada falla.
- **PBKDF2-SHA256:** la clave AES se deriva de un password usando 100.000 iteraciones, haciendo ataques de fuerza bruta inviables.
- **TLS 1.3:** configuración del contexto SSL para el canal de comunicación con la nube, forzando solo TLS 1.3 con verificación de certificado obligatoria.

**Regulación:** GDPR Art. 25 (Privacidad desde el diseño), HSPD (datos de salud)

---

### Módulo 2 — `secure_erase.py` · Borrado Seguro

**Problema que resuelve:** cuando un paciente pide borrar sus datos (GDPR Art. 17 — Derecho al Olvido), el `delete` normal no es suficiente. El archivo sigue en disco hasta que el sistema operativo lo sobreescribe. En memoria Flash esto puede tardar mucho tiempo.

**Solución implementada:**
- Algoritmo **DoD 5220.22-M** (Departamento de Defensa EE.UU.):
  - Pasada 1: sobreescribir con `0x00` (todos ceros)
  - Pasada 2: sobreescribir con `0xFF` (todos unos)
  - Pasada 3: sobreescribir con bytes aleatorios
- `os.fsync()` fuerza que cada pasada quede escrita físicamente en el disco
- Finalmente se elimina el archivo del sistema de archivos
- El sistema simula la Flash del dispositivo con archivos nombrados por hash del ID del paciente (no se expone el ID directamente)

**Regulación:** GDPR Art. 17 (Derecho al olvido)

---

### Módulo 3 — `auth_service.py` · OAuth2 / OpenID Connect

**Problema que resuelve:** el sistema tiene múltiples actores (dispositivo IoT, paciente, médico, administrador) con distintos niveles de acceso. Es necesario verificar identidad y controlar permisos.

**Solución implementada:**
- **OAuth2:** protocolo de autorización — define *quién puede hacer qué*
- **OpenID Connect:** capa de identidad sobre OAuth2 — define *quién eres*
- Tokens **JWT** (JSON Web Token) firmados con HMAC-SHA256
- Sistema de **roles y permisos:** cada rol tiene un conjunto de acciones permitidas
- **Revocación de tokens:** lista negra para invalidar tokens de dispositivos robados o usuarios dados de baja
- Contraseñas almacenadas como hash SHA-256 (nunca en texto plano)

**Roles disponibles:**

| Rol | Permisos |
|---|---|
| `paciente` | leer sus propios datos |
| `medico` | leer datos de pacientes, ver alertas |
| `admin` | todo lo anterior + administrar usuarios |
| `dispositivo` | enviar datos, recibir configuración |

**Regulación:** IEC 62443 (seguridad en sistemas de control), ISO/IEC 27403

---

### Módulo 4 — `edge_ai_model.py` · IA en el Borde + XAI

**Problema que resuelve:** detectar arritmias en tiempo real sin enviar datos del paciente a internet. La IA debe correr *en el dispositivo*, ser precisa (>95%) y explicable (CE/FDA exige saber *por qué* el algoritmo tomó una decisión).

**Solución implementada:**
- Modelo **Random Forest** — ideal para Edge AI porque es:
  - Liviano (no requiere GPU)
  - Rápido en inferencia (milisegundos)
  - Naturalmente explicable (importancia de features)
- **4 clases de diagnóstico:** Normal, Taquicardia (BPM >100), Bradicardia (BPM <60), Fibrilación Auricular (ritmo irregular)
- **6 features del ECG:** BPM, intervalo RR, variabilidad RR, amplitud QRS, intervalo PR, SpO2
- **XAI:** cada predicción incluye las 3 variables más influyentes en la decisión con su porcentaje de importancia
- **Precisión alcanzada: 95.8%** — supera el requisito del Gate 2

**Regulación:** CE/FDA (algoritmos auditables y explicables — XAI), Gate 2

---

### Módulo 5 — `ota_updater.py` · Actualización OTA con Firma Digital

**Problema que resuelve:** si un atacante intercepta una actualización de firmware y manda código malicioso al dispositivo médico, puede tomar control total. Esto es crítico en un dispositivo que monitorea signos vitales.

**Solución implementada:**
- El servidor genera un par de claves **RSA-2048**
- Antes de distribuir un firmware: calcula su hash **SHA-256** y lo **firma con la clave privada**
- El dispositivo tiene embebida la **clave pública** del servidor (en fábrica)
- Al recibir una actualización: verifica la firma RSA y el hash SHA-256
- Si cualquier bit del firmware fue modificado → la verificación falla → **la actualización es rechazada automáticamente**
- En la demo se simula un ataque: el atacante modifica el firmware pero no puede re-firmarlo (no tiene la clave privada) → el dispositivo lo bloquea

**Regulación:** Gate 3 (certificación de ciberseguridad), IEC 62443

---

### Módulo 6 — `blockchain_logger.py` · Logs Inmutables

**Problema que resuelve:** si el sistema es hackeado y se filtran datos, los reguladores y auditores necesitan saber *quién accedió a qué y cuándo*. El atacante no puede borrar su rastro.

**Solución implementada:**
- Cadena de bloques local (sin criptomonedas, sin red P2P):
  - Cada evento de acceso es un **bloque**
  - Cada bloque contiene el **hash SHA-256 del bloque anterior**
  - Si alguien modifica un bloque viejo → todos los hashes siguientes se rompen → la verificación de integridad lo detecta
- Cada bloque registra: usuario, rol, acción, recurso accedido, IP de origen, resultado (permitido/denegado), timestamp UTC
- Funciones de búsqueda: por usuario, por accesos fallidos (detección de ataques)
- Función de exportación completa para auditores externos

**Regulación:** ISO/IEC 27403 (seguridad en ecosistema IoT), GDPR (derecho de auditoría)

---

## 8. Salida real del sistema

Esta es la salida completa al ejecutar `python main.py`:

```
############################################################
  BIO-MONITOR 5.0 - DEMO INTEGRACION COMPLETA
############################################################

============================================================
  PASO 1: Inicializando subsistemas
============================================================
  [Flash] Almacenamiento inicializado en: 'flash_datos/'
  [Servidor OTA] Generando par de claves RSA-2048...
  [Servidor OTA] Claves RSA-2048 generadas.
  [+] Servidor de autenticacion OAuth2: OK
  [+] Almacenamiento Flash cifrado: OK
  [+] Blockchain de logs: OK
  [+] Servidor OTA con firma RSA: OK

============================================================
  PASO 2: Entrenando modelo IA (Edge AI)
============================================================
  [IA] Modelo entrenado con 960 muestras
  [IA] Precision en test: 95.8%
  [IA] Gate 2 SUPERADO: Precision >= 95%

============================================================
  PASO 3: Autenticacion del dispositivo IoT (OAuth2)
============================================================
  [Auth] Login exitoso para 'device-007' (rol: dispositivo)
  Dispositivo autenticado. Rol: dispositivo

============================================================
  PASO 4: Cifrado AES-256 de datos del paciente
============================================================
  Datos originales: {"bpm": 140, "spo2": 95.2, "temp": 37.1, "variabilidad_rr": 12}
  [Flash] Datos guardados para paciente 'P-00123' (188 bytes)
  Datos cifrados y guardados en Flash.
  Cifrado AES-256 activo: 5NL30CKnNeRtZW8zu6EY5/3NkbTBm1...

============================================================
  PASO 5: Analisis de arritmias (Edge AI + XAI)
============================================================
  Diagnostico: Taquicardia
  Confianza:   100.0%
  Emergencia:  True
  Explicacion XAI (CE/FDA):
    - bpm: 27.0% de importancia
    - variabilidad_rr: 25.3% de importancia
    - intervalo_rr: 25.3% de importancia

  !!! ALERTA: Posible Taquicardia detectada.
  !!! Enviando alerta al medico via TLS 1.3...
  [TLS 1.3] Contexto SSL configurado correctamente
  [TLS 1.3] Version minima: TLSv1_3
  [TLS 1.3] Version maxima: TLSv1_3
  [TLS 1.3] Verificacion de certificado: ACTIVADA
  [TLS 1.3] Listo para conectar a 'api.biomonitor.cloud:443'

============================================================
  PASO 6: Medico accede a datos del paciente (OAuth2)
============================================================
  [Auth] Login exitoso para 'dr.garcia' (rol: medico)
  Medico autenticado: dr.garcia (rol: medico)
  Datos descifrados para el medico: {"bpm": 140, "spo2": 95.2, "temp": 37.1, "variabilidad_rr": 12}

============================================================
  PASO 7: Actualizacion OTA con firma digital (Gate 3)
============================================================
  [Dispositivo BM-007] Iniciado con firmware v1.0.0
  [Servidor OTA] Paquete v2.1.0 creado y firmado.
  [Servidor OTA] Hash SHA-256: f0459e189efb361e...
  [Servidor OTA] Firma: 4f1946e01cb8b1ac51a9...

  [OTA] Recibiendo paquete de actualizacion v2.1.0...
  [OTA] Firma RSA: VALIDA
  [OTA] Integridad SHA-256: VERIFICADA
  [OTA] Instalando firmware v2.1.0 (235 bytes)...
  [OTA] [################] 100%
  [OTA] Dispositivo actualizado: v1.0.0 -> 2.1.0
  [OTA] ACTUALIZACION EXITOSA

============================================================
  PASO 8: Borrado Seguro - Derecho al Olvido (GDPR Art.17)
============================================================
  [BorradoSeguro] Iniciando borrado de 188 bytes para 'P-00123'
  [BorradoSeguro] Algoritmo: DoD 5220.22-M (3 pasadas)
  [BorradoSeguro]   Pasada 1/3: 0x00 (ceros) - OK
  [BorradoSeguro]   Pasada 2/3: 0xFF (unos) - OK
  [BorradoSeguro]   Pasada 3/3: aleatorio - OK
  [BorradoSeguro] Archivo eliminado del sistema de archivos.
  [BorradoSeguro] BORRADO COMPLETADO - Derecho al Olvido cumplido.
  [Verificacion] Datos de 'P-00123': NO EXISTEN (borrado confirmado)

============================================================
  PASO 9: Auditoria final de logs blockchain
============================================================
  Total de eventos registrados: 10
  Integridad de la cadena: VALIDA
  Todos los 10 bloques son integros e inmutables.

  Historial de accesos auditado:
    [01] SISTEMA      | ENTRENAMIENTO_IA       | PERMITIDO
    [02] device-007   | LOGIN                  | PERMITIDO
    [03] device-007   | ESCRITURA              | PERMITIDO
    [04] device-007   | PREDICCION_IA          | PERMITIDO
    [05] device-007   | ALERTA_ENVIADA         | PERMITIDO
    [06] dr.garcia    | LECTURA                | PERMITIDO
    [07] SERVIDOR_OTA | ACTUALIZACION_OTA      | PERMITIDO
    [08] paciente1    | SOLICITUD_BORRADO      | PERMITIDO
    [09] SISTEMA      | BORRADO_COMPLETADO     | PERMITIDO

############################################################
  RESUMEN DE CUMPLIMIENTO REGULATORIO
############################################################
  [OK]  AES-256 cifrado en reposo
  [OK]  TLS 1.3 cifrado en transito
  [OK]  Borrado Seguro (GDPR Art.17)
  [OK]  OAuth2/OpenID Connect
  [OK]  IA precision > 95% (95.8%)
  [OK]  Explicabilidad XAI (CE/FDA)
  [OK]  Firma digital OTA (RSA-2048)
  [OK]  Logs inmutables blockchain

  Bio-Monitor 5.0 listo para revision regulatoria.
############################################################
```

---

## 9. Cumplimiento Regulatorio

| Requisito del Taller | Marco Regulatorio | Módulo que lo implementa | Resultado |
|---|---|---|---|
| Cifrado AES-256 en reposo (Flash) | GDPR Art. 25 / HSPD | `crypto_module.py` | ✅ AES-256-GCM |
| Cifrado TLS 1.3 en tránsito | GDPR Art. 25 / HSPD | `crypto_module.py` | ✅ TLS 1.3 forzado |
| Borrado Seguro (Derecho al Olvido) | GDPR Art. 17 | `secure_erase.py` | ✅ DoD 5220.22-M 3 pasadas |
| Autenticación y autorización | IEC 62443 / ISO 27403 | `auth_service.py` | ✅ OAuth2 + OpenID Connect |
| IA precisión > 95% | Gate 2 | `edge_ai_model.py` | ✅ 95.8% |
| Algoritmo auditable y explicable | CE/FDA (XAI) | `edge_ai_model.py` | ✅ Importancia de features |
| Firma digital de firmware OTA | Gate 3 | `ota_updater.py` | ✅ RSA-2048-PSS-SHA256 |
| Logs de acceso inmutables | ISO/IEC 27403 | `blockchain_logger.py` | ✅ Blockchain con SHA-256 |

---

## 10. Evolución TRL y Gates

| Nivel / Gate | Requisito Técnico | Requisito Regulatorio | Estado en el código |
|---|---|---|---|
| **TRL 4** (Validación Técnica) | Software funciona | DPIA — Análisis de Impacto de Protección de Datos | Módulos 1-6 operativos |
| **Gate 1** (Concepto) | Arquitectura definida | Evaluación de licencias (cryptography=Apache, PyJWT=MIT, scikit-learn=BSD) | ✅ Solo librerías permisivas |
| **Gate 2** (Desarrollo) | IA precisión > 95% | Transparencia algorítmica / XAI | ✅ 95.8% + explicación por feature |
| **TRL 6** (Prototipo) | Pentesting externo | Verificación de no backdoors | Módulo 5: firma digital bloquea firmware no autorizado |
| **Gate 3** (Lanzamiento) | Sistema estable | Certificación de ciberseguridad — OTA segura | ✅ RSA-2048 + rechazo de firmware adulterado |
| **TRL 8** (Cumplimiento Total) | Homologación | Registro ante reguladores (Superintendencia de Salud, entes de protección de datos) | Base técnica implementada |

---

## 11. Matriz de Riesgos y Mitigaciones Implementadas

| Riesgo | Descripción | Mitigación implementada en el código |
|---|---|---|
| **Fallo del Software** | El dispositivo no reporta una emergencia a tiempo | Módulo 4: detección local (Edge AI), sin dependencia de red para el diagnóstico |
| **Fuga de Datos** | El sistema es hackeado y se filtran datos médicos | Módulo 6: blockchain de logs inmutables — el atacante no puede borrar su rastro. Módulo 1: datos cifrados con AES-256 hacen ilegible cualquier filtración |
| **Soberanía de Datos** | Datos guardados en servidores fuera del país | Módulo 4 (Edge AI): el diagnóstico ocurre *en el dispositivo*, los datos no salen |
| **Firmware Malicioso** | Atacante inyecta código malicioso vía actualización OTA | Módulo 5: firma RSA-2048 — el dispositivo rechaza cualquier firmware no firmado por el servidor legítimo |
| **Acceso No Autorizado** | Usuario sin permisos accede a datos de otro paciente | Módulo 3: OAuth2 con roles — un paciente no puede acceder a datos de otro aunque tenga token válido |

---

## 12. Usuarios de prueba

Definidos en `auth_service/auth_service.py`:

| Usuario | Contraseña | Rol | Permisos |
|---|---|---|---|
| `dr.garcia` | `pass123` | médico | leer datos de pacientes, ver alertas |
| `paciente1` | `mipass` | paciente | leer solo sus propios datos |
| `device-007` | `devicepass` | dispositivo IoT | enviar datos, recibir configuración |
| `admin` | `adminpass` | administrador | todos los permisos anteriores + administrar usuarios |

---

*Proyecto desarrollado en Python 3 · Repositorio: https://github.com/Sebastian1499/Proyecto-Bio-Monitor-5.0*
