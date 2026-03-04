# Bio-Monitor 5.0

> **Taller:** Gestión de la Innovación y Marcos Regulatorios en Software IoT

---

## PARTE 1 — Descripción del Proyecto

### ¿Qué es?

Bio-Monitor 5.0 es un sistema IoT vestible (*wearable*) que monitorea signos vitales en tiempo real y usa **Inteligencia Artificial en el Borde (Edge AI)** para detectar arritmias directamente en el dispositivo, sin enviar datos a internet. Todo el software implementa en código los marcos regulatorios exigidos: **GDPR, IEC 62443, ISO/IEC 27403 y criterios CE/FDA**.

Incluye una **interfaz web interactiva (Flask)** donde se puede demostrar cada módulo de seguridad en el navegador.

---

### Stack tecnológico

| Tecnología | Uso |
|---|---|
| **Python 3.10+** | Lenguaje principal |
| **Flask 3.x** | Dashboard web interactivo |
| **cryptography ≥42.0** | AES-256-GCM cifrado en reposo · RSA-2048 firma OTA |
| **PyJWT ≥2.8** | OAuth2 / OpenID Connect con tokens JWT |
| **scikit-learn ≥1.4** | Modelo Random Forest para detección de arritmias |
| **numpy ≥2.0** | Procesamiento de datos ECG |
| **Bootstrap 5.3** | UI responsive (CDN) |

---

### Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/Sebastian1499/Proyecto-Bio-Monitor-5.0.git
cd Proyecto-Bio-Monitor-5.0

# 2. (Recomendado) Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4a. Ejecutar la interfaz WEB (recomendado)
python web_app/app.py
# → Abrir http://localhost:5000

# 4b. O ejecutar la demo en terminal
python main.py
```

**Usuarios de prueba para el dashboard web:**

| Usuario | Contraseña | Rol |
|---|---|---|
| `dr.garcia` | `pass123` | Médico |
| `paciente1` | `mipass` | Paciente |
| `device-007` | `devicepass` | Dispositivo IoT |
| `admin` | `adminpass` | Administrador |

---

### Estructura del proyecto

```
Proyecto-Bio-Monitor-5.0/
├── main.py                        ← Demo terminal + menú interactivo
├── requirements.txt
├── web_app/
│   ├── app.py                     ← Servidor Flask (backend)
│   └── templates/                 ← 8 pantallas HTML
├── crypto_module/crypto_module.py ← AES-256-GCM + TLS 1.3
├── secure_erase/secure_erase.py   ← Borrado Seguro DoD 5220.22-M
├── auth_service/auth_service.py   ← OAuth2 + OpenID Connect + JWT
├── edge_ai/edge_ai_model.py       ← Edge AI + XAI (95.8% precisión)
├── ota_updater/ota_updater.py     ← OTA con firma RSA-2048
└── blockchain_logs/blockchain_logger.py ← Logs inmutables
```

---
---

## PARTE 2 — Entregables del Taller

### 2.1 Identificación del Proyecto e Innovación Propuesta

**Nombre del proyecto:** Bio-Monitor 5.0
**Sector:** Salud digital / MedTech / IoT
**Equipo:** Startup de ingeniería de software

**Problema identificado:**
Los dispositivos médicos IoT existentes transmiten datos de salud del paciente a servidores en la nube sin protección adecuada, sin transparencia algorítmica y sin mecanismos de cumplimiento regulatorio integrados directamente en el software. Esto genera riesgos de privacidad, accesos no autorizados y falta de auditabilidad.

**Innovación propuesta:**
Un wearable IoT con diagnóstico de arritmias completamente local (Edge AI), donde cada componente del software implementa en código —no solo en documentación— los marcos regulatorios de salud digital: cifrado certificado, borrado seguro, autenticación estándar internacional, IA explicable y auditoría inmutable.

**Tipo de innovación:**

| Dimensión | Clasificación | Justificación |
|---|---|---|
| **Por objeto** | Innovación de producto | Nuevo dispositivo con capacidades de IA en el borde |
| **Por origen** | Innovación tecnológica | Integración de 6 tecnologías de seguridad en un solo sistema |
| **Por grado** | Innovación incremental-radical | Mejora sobre wearables existentes con ruptura en privacidad y transparencia |
| **Por impacto** | Innovación de mercado | Primer wearable médico con cumplimiento regulatorio integrado en código |

---

### 2.2 Propuesta de Valor (Canvas simplificado)

| Elemento | Descripción |
|---|---|
| **Segmento** | Pacientes con riesgo cardíaco · Hospitales y clínicas · Aseguradoras de salud |
| **Problema** | Dispositivos actuales: datos en la nube sin garantías, IA no explicable, sin GDPR |
| **Solución** | Edge AI local + cifrado certificado + logs auditables + cumplimiento GDPR/CE/FDA nativo |
| **Diferenciador** | El cumplimiento regulatorio no es un añadido posterior — está programado en el núcleo del sistema |
| **Canales** | Venta directa a hospitales · Partnership con fabricantes de wearables · SaaS para clínicas |
| **Ingresos** | Licencia de software + soporte regulatorio + certificación CE/FDA como servicio |

---

### 2.3 Matriz de Ansoff — Posicionamiento Estratégico

La Matriz de Ansoff identifica la estrategia de crecimiento según si el producto y el mercado son nuevos o existentes.

```
                     PRODUCTO EXISTENTE    PRODUCTO NUEVO
                    ┌──────────────────────────────────────┐
MERCADO             │  Penetración de  │  Desarrollo de   │
EXISTENTE           │     mercado      │    producto  ✓   │
                    ├──────────────────┼──────────────────┤
MERCADO             │  Desarrollo de   │                  │
NUEVO               │     mercado      │ Diversificación  │
                    └──────────────────────────────────────┘
```

**Estrategia seleccionada: Desarrollo de Producto**

Bio-Monitor 5.0 introduce un **producto nuevo** (wearable con IA en el borde + cumplimiento regulatorio integrado en código) dirigido a un **mercado existente** (salud digital, hospitales, pacientes cardíacos), compitiendo con dispositivos actuales como Holter digitales o smartwatches médicos sin IA local ni cumplimiento regulatorio nativo.

**Justificación:**
- Los competidores actuales ya tienen el mercado establecido.
- La innovación no está en crear un mercado nuevo, sino en ofrecer un producto radicalmente mejor en seguridad, privacidad y transparencia algorítmica para el mismo mercado.
- Estrategia de diferenciación: el factor regulatorio (GDPR nativo, CE/FDA) actúa como barrera de entrada y ventaja competitiva sostenible.

---

### 2.4 Modelo TRL (Technology Readiness Level) + Gates de Desarrollo

El modelo TRL (NASA/ESA) mide la madurez tecnológica de TRL 1 (concepto básico) a TRL 9 (sistema probado en operación real).

#### Estado actual del proyecto

| Nivel TRL | Descripción | Estado en Bio-Monitor 5.0 |
|---|---|---|
| TRL 1 | Principios básicos observados | ✅ Investigación sobre ECG, arritmias, criptografía médica |
| TRL 2 | Concepto tecnológico formulado | ✅ Diseño de arquitectura de 6 módulos interdependientes |
| TRL 3 | Prueba de concepto experimental | ✅ Cada módulo probado individualmente con datos sintéticos |
| **TRL 4** | **Validación en laboratorio** | ✅ **Sistema integrado funcionando — 8 requisitos [OK]** |
| TRL 5 | Validación en entorno relevante | 🔄 Pendiente: pruebas con sensores físicos reales |
| TRL 6 | Demostración en entorno relevante | 🔄 Pendiente: prototipo de hardware integrado |
| TRL 7 | Demostración en entorno operacional | ⏳ Pendiente: ensayo clínico piloto |
| TRL 8 | Sistema completo y calificado | ⏳ Pendiente: certificación CE/FDA oficial |
| TRL 9 | Sistema probado en operación real | ⏳ Pendiente: lanzamiento comercial |

**Nivel alcanzado: TRL 4** — Software completamente funcional, todos los módulos de seguridad integrados y validados.

#### Gates de Desarrollo Superados

| Gate | Criterio Técnico | Criterio Regulatorio | Resultado |
|---|---|---|---|
| **Gate 1** — Concepto | Arquitectura del sistema definida | Licencias de software: solo permisivas (Apache, MIT, BSD) sin dependencias GPL | ✅ cryptography=Apache · PyJWT=MIT · scikit-learn=BSD · numpy=BSD |
| **Gate 2** — Desarrollo | IA con precisión ≥ 95% en detección de arritmias | Transparencia algorítmica — XAI requerido por CE/FDA | ✅ **95.8% precisión** · XAI por importancia de features implementado |
| **Gate 3** — Lanzamiento | Sistema estable · Actualización OTA segura | Certificación de ciberseguridad IEC 62443 | ✅ RSA-2048-PSS · SHA-256 · rechazo automático de firmware adulterado |

---

### 2.5 Marcos Regulatorios Aplicados

#### GDPR — Reglamento General de Protección de Datos

Aplicable porque el sistema procesa **datos de salud** de pacientes — categoría especial bajo el Art. 9 del GDPR.

| Artículo GDPR | Requisito | Implementación en el código |
|---|---|---|
| **Art. 17** — Derecho al olvido | El paciente puede exigir borrado total de sus datos | `secure_erase.py`: DoD 5220.22-M, 3 pasadas de sobreescritura + eliminación del archivo |
| **Art. 25** — Privacidad desde el diseño | La protección de datos por defecto, no como añadido | `crypto_module.py`: AES-256-GCM cifra los datos *antes* de guardarlos · TLS 1.3 en tránsito |
| **Art. 30** — Registro de actividades | Registro auditable de quién accedió a qué y cuándo | `blockchain_logger.py`: blockchain local con SHA-256 encadenado, inmutable |
| **Art. 35** — DPIA | Análisis de Impacto de Protección de Datos | Ver sección 2.6 |

#### IEC 62443 — Seguridad en Sistemas IoT

| Zona | Nivel de Seguridad | Implementación |
|---|---|---|
| Autenticación | SL-2 | `auth_service.py`: OAuth2 + OpenID Connect + JWT firmados HMAC-SHA256 |
| Autorización | SL-2 (RBAC) | 4 roles con permisos distintos (médico, paciente, dispositivo, admin) |
| Integridad del software | SL-3 | `ota_updater.py`: RSA-2048-PSS firma todo firmware |
| Auditoría | SL-2 | `blockchain_logger.py`: registro completo con detección de accesos denegados |

#### ISO/IEC 27403 — Seguridad en Ecosistemas IoT

| Control | Implementación |
|---|---|
| Control de acceso de dispositivos | OAuth2 con token específico para rol `dispositivo` |
| Actualizaciones seguras de firmware | OTA firmado RSA-2048 · rechazo automático si firma inválida |
| Registro de eventos | Blockchain de logs inmutable · SHA-256 encadenado |
| Cifrado en reposo y en tránsito | AES-256-GCM + TLS 1.3 |

#### CE/FDA — Certificación de Dispositivos Médicos

| Requisito | Implementación |
|---|---|
| Algoritmos de IA explicables (XAI) | `edge_ai_model.py`: cada predicción devuelve las 3 variables más influyentes con porcentaje |
| Precisión clínica documentada | **95.8%** en 4 clases: Normal, Taquicardia, Bradicardia, Fibrilación Auricular |
| Trazabilidad de decisiones | Cada diagnóstico queda registrado en blockchain con timestamp y usuario |
| Actualización de software segura | Firma digital RSA-2048 en cada paquete OTA |

---

### 2.6 DPIA — Análisis de Impacto de Protección de Datos

Requerido por GDPR Art. 35 cuando se procesan datos sensibles (categoría: datos de salud).

**Datos que se procesan:**
- Señales ECG (BPM, variabilidad RR, amplitud QRS, intervalo PR)
- SpO2 (nivel de oxígeno en sangre)
- Identificador interno del paciente (nunca nombre ni DNI)
- Registros de acceso (usuario, timestamp, acción)

**Análisis de riesgos de privacidad:**

| Riesgo | Probabilidad | Impacto | Nivel | Medida implementada |
|---|---|---|---|---|
| Filtración de datos en reposo | Media | Crítico | 🔴 Alto | AES-256-GCM: datos ilegibles sin la clave |
| Intercepción en tránsito | Alta | Crítico | 🔴 Crítico | TLS 1.3: comunicación completamente cifrada |
| Acceso con rol incorrecto | Media | Alto | 🟠 Alto | OAuth2 RBAC: token no concede acceso a recursos de otro rol |
| Imposibilidad de borrar datos | Media | Alto | 🟠 Alto | DoD 5220.22-M: 3 pasadas de sobreescritura irrecuperable |
| IA no explicable (CE/FDA) | Media | Crítico | 🔴 Crítico | XAI integrado: toda predicción incluye importancia de variables |
| Manipulación de logs de auditoría | Baja | Crítico | 🟠 Alto | Blockchain: hash SHA-256 encadenado — alteración retroactiva detectable |

**Resultado de la DPIA:** Todos los riesgos tienen medidas técnicas implementadas en código. El sistema cumple *Privacy by Design* (GDPR Art. 25).

---

### 2.7 Matriz de Riesgos del Proyecto

| # | Riesgo | Probabilidad | Impacto | Nivel | Mitigación implementada |
|---|---|---|---|---|---|
| R01 | Firmware malicioso inyectado vía OTA | Media | Catastrófico | 🔴 **CRÍTICO** | RSA-2048-PSS: dispositivo rechaza firmware sin firma válida automáticamente |
| R02 | Fuga de datos de salud | Media | Catastrófico | 🔴 **CRÍTICO** | AES-256-GCM en reposo · TLS 1.3 en tránsito · blockchain de logs |
| R03 | Acceso no autorizado a registros de otro paciente | Alta | Grave | 🟠 **ALTO** | OAuth2 RBAC — token de paciente no accede a datos de otros |
| R04 | IA toma decisión sin explicación (CE/FDA) | Media | Grave | 🟠 **ALTO** | XAI integrado en cada predicción — importancia de features documentada |
| R05 | Precisión IA < 95% (Gate 2 rechazado) | Media | Grave | 🟠 **ALTO** | Validación automática en código — el sistema no avanza si no supera 95% |
| R06 | Imposibilidad de cumplir Derecho al Olvido | Media | Grave | 🟠 **ALTO** | DoD 5220.22-M: borrado de 3 pasadas — datos irrecuperables |
| R07 | Dependencia con vulnerabilidad CVE | Baja | Moderado | 🟡 **MEDIO** | Solo librerías activamente mantenidas · versiones mínimas en requirements.txt |
| R08 | Datos de diagnóstico procesados fuera del dispositivo | Alta | Moderado | 🟡 **MEDIO** | Edge AI: diagnóstico en el dispositivo, datos crudos nunca salen |

---

### 2.8 Estrategia de Propiedad Intelectual y Licencias

**Auditoría de licencias (Gate 1):**

| Librería | Licencia | Compatible con uso comercial | Restricción |
|---|---|---|---|
| `cryptography` | Apache License 2.0 | ✅ Sí | Ninguna para uso comercial |
| `PyJWT` | MIT License | ✅ Sí | Ninguna |
| `scikit-learn` | BSD 3-Clause | ✅ Sí | Solo mantener aviso de copyright |
| `numpy` | BSD 3-Clause | ✅ Sí | Solo mantener aviso de copyright |
| `Flask` | BSD 3-Clause | ✅ Sí | Solo mantener aviso de copyright |

✅ **Gate 1 superado:** Ninguna dependencia impone restricciones GPL. El proyecto puede distribuirse como software propietario sin conflictos de licencia.

**Estrategia de PI recomendada:**
- Registrar como secreto industrial el modelo IA entrenado y los parámetros de configuración de seguridad
- Solicitar patente de utilidad para el método de integración de Edge AI + cumplimiento regulatorio en el mismo pipeline
- Open source selectivo en módulos genéricos (borrado seguro, blockchain de logs) para visibilidad en la comunidad

---

### 2.9 Resumen de Cumplimiento Regulatorio

| Requisito del Taller | Marco Regulatorio | Módulo | Resultado |
|---|---|---|---|
| Cifrado AES-256 en reposo | GDPR Art. 25 | `crypto_module.py` | ✅ AES-256-GCM |
| Cifrado en tránsito | GDPR Art. 25 | `crypto_module.py` | ✅ TLS 1.3 forzado |
| Borrado seguro GDPR | GDPR Art. 17 | `secure_erase.py` | ✅ DoD 5220.22-M 3 pasadas |
| Autenticación y control de acceso | IEC 62443 / ISO 27403 | `auth_service.py` | ✅ OAuth2 + JWT + RBAC |
| IA precisión > 95% | Gate 2 | `edge_ai_model.py` | ✅ **95.8%** |
| IA explicable (XAI) | CE / FDA | `edge_ai_model.py` | ✅ Importancia de features |
| Firmware firmado digitalmente | Gate 3 / IEC 62443 | `ota_updater.py` | ✅ RSA-2048-PSS + SHA-256 |
| Logs de acceso inmutables | ISO/IEC 27403 / GDPR | `blockchain_logger.py` | ✅ Blockchain SHA-256 |

---

*Repositorio: https://github.com/Sebastian1499/Proyecto-Bio-Monitor-5.0 · Python 3.10+ · Flask 3.x*
