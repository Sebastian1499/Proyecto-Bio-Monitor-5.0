# Bio-Monitor 5.0

Proyecto del taller **"Gestión de la Innovación y Marcos Regulatorios en Software IoT"**.

Sistema IoT vestible (*wearable*) que monitorea signos vitales y usa **Inteligencia Artificial en el Borde** para detectar arritmias, cumpliendo con los marcos regulatorios GDPR, IEC 62443, ISO/IEC 27403 y certificación CE/FDA.

---

## ¿Con qué está hecho?

| Tecnología | Uso |
|---|---|
| **Python 3.10+** | Lenguaje principal |
| **cryptography** | AES-256-GCM y RSA-2048 (cifrado y firma digital) |
| **PyJWT** | Tokens JWT para OAuth2 / OpenID Connect |
| **scikit-learn** | Modelo Random Forest para detección de arritmias |
| **numpy** | Procesamiento numérico para los datos del ECG |

---

## Estructura del proyecto

```
Proyecto-Bio-Monitor-5.0/
│
├── main.py                              ← Punto de entrada: demo de integración completa
├── requirements.txt                     ← Dependencias del proyecto
│
├── crypto_module/
│   └── crypto_module.py                 ← Módulo 1: AES-256-GCM + TLS 1.3
│
├── secure_erase/
│   └── secure_erase.py                  ← Módulo 2: Borrado Seguro (Derecho al Olvido)
│
├── auth_service/
│   └── auth_service.py                  ← Módulo 3: OAuth2 / OpenID Connect con JWT
│
├── edge_ai/
│   └── edge_ai_model.py                 ← Módulo 4: IA en el Borde (detección arritmias)
│
├── ota_updater/
│   └── ota_updater.py                   ← Módulo 5: Actualización OTA con firma digital
│
└── blockchain_logs/
    └── blockchain_logger.py             ← Módulo 6: Logs de acceso inmutables
```

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Sebastian1499/Proyecto-Bio-Monitor-5.0.git
cd Proyecto-Bio-Monitor-5.0
```

### 2. (Opcional) Crear un entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## ¿Cómo se ejecuta?

### Demo completa (todos los módulos integrados)

```bash
python main.py
```

Esto simula un ciclo de vida completo del sistema:

1. Inicializa todos los subsistemas
2. Entrena el modelo de IA (debería lograr ≥ 95% de precisión)
3. El dispositivo IoT se autentica con OAuth2
4. Captura datos del paciente y los cifra con AES-256
5. El modelo de IA detecta la arritmia y muestra la explicación XAI
6. Si hay emergencia, envía alerta usando TLS 1.3
7. El médico accede a los datos con su propio token
8. Se realiza una actualización OTA firmada con RSA-2048
9. El paciente ejerce el Derecho al Olvido (Borrado Seguro)
10. Se audita toda la blockchain de logs

### Módulos individuales

Cada módulo también se puede probar por separado:

```bash
python crypto_module/crypto_module.py
python secure_erase/secure_erase.py
python auth_service/auth_service.py
python edge_ai/edge_ai_model.py
python ota_updater/ota_updater.py
python blockchain_logs/blockchain_logger.py
```

---

## ¿Qué hace cada módulo?

### Módulo 1 — `crypto_module.py` (AES-256 + TLS 1.3)
Cifra los datos de salud del paciente **antes de guardarlos** en la memoria Flash del dispositivo usando AES-256-GCM. También muestra la configuración correcta de TLS 1.3 para el envío seguro a la nube.
- Cumple: **GDPR Art. 25 — Privacidad desde el diseño**

### Módulo 2 — `secure_erase.py` (Borrado Seguro)
Implementa el algoritmo **DoD 5220.22-M** (3 pasadas: ceros, unos, aleatorio) para sobreescribir y eliminar datos de forma irrecuperable cuando el paciente lo solicita.
- Cumple: **GDPR Art. 17 — Derecho al olvido**

### Módulo 3 — `auth_service.py` (OAuth2 / OpenID Connect)
Sistema completo de autenticación y autorización con roles (paciente, médico, administrador, dispositivo). Emite **tokens JWT firmados** y soporta revocación de tokens.
- Cumple: **IEC 62443 — Control de acceso en sistemas IoT**

### Módulo 4 — `edge_ai_model.py` (IA en el Borde)
Modelo **Random Forest** que clasifica lecturas de ECG en: Normal, Taquicardia, Bradicardia o Fibrilación Auricular. Incluye **XAI** (explicabilidad): muestra qué variables influyeron en el diagnóstico.
- Precisión alcanzada: **~95.8%** (supera el Gate 2)
- Cumple: **CE/FDA — Algoritmos auditables y explicables**

### Módulo 5 — `ota_updater.py` (OTA Seguro)
El servidor firma cada actualización de firmware con **RSA-2048**. El dispositivo verifica la firma antes de instalar. Si el firmware fue adulterado (ataque), el dispositivo lo rechaza.
- Cumple: **Gate 3 — Certificación de Ciberseguridad**

### Módulo 6 — `blockchain_logger.py` (Logs Inmutables)
Cadena de bloques local donde cada evento (login, lectura, borrado, etc.) queda registrado con el **hash del bloque anterior**. Si alguien modifica un registro, la verificación de integridad lo detecta.
- Cumple: **ISO/IEC 27403 — Auditoría en ecosistema IoT**

---

## Cumplimiento Regulatorio Implementado

| Requisito | Regulación | Estado |
|---|---|---|
| Cifrado AES-256 en reposo | GDPR Art. 25 / HSPD | ✅ |
| Cifrado TLS 1.3 en tránsito | GDPR Art. 25 / HSPD | ✅ |
| Borrado Seguro | GDPR Art. 17 | ✅ |
| Autenticación OAuth2/OpenID Connect | IEC 62443 | ✅ |
| IA con precisión > 95% | Gate 2 | ✅ ~95.8% |
| Algoritmo explicable (XAI) | CE/FDA | ✅ |
| Firma digital OTA (RSA-2048) | Gate 3 | ✅ |
| Logs de acceso inmutables | ISO/IEC 27403 | ✅ |

---

## Usuarios de prueba

Disponibles en `auth_service/auth_service.py`:

| Usuario | Contraseña | Rol |
|---|---|---|
| `dr.garcia` | `pass123` | médico |
| `paciente1` | `mipass` | paciente |
| `device-007` | `devicepass` | dispositivo IoT |
| `admin` | `adminpass` | administrador |

---

## Taller

**Asignatura:** Gestión de la Innovación y Marcos Regulatorios en Software IoT  
**Proyecto:** Bio-Monitor 5.0 — Dispositivo wearable de monitoreo de signos vitales con IA en el borde
