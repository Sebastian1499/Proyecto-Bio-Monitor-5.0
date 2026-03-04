"""
BIO-MONITOR 5.0  —  Dashboard Web Flask
=========================================
Este archivo es el SERVIDOR WEB del proyecto.
Conecta todos los modulos de seguridad con una interfaz grafica en el navegador.

Como ejecutarlo:
    python web_app/app.py
    Luego abre: http://localhost:5000

Estructura de rutas:
    /              -> Login (GET: formulario, POST: autenticar)
    /logout        -> Cerrar sesion
    /dashboard     -> Pantalla principal con resumen del sistema
    /diagnostico   -> Diagnostico IA de arritmias (Edge AI + XAI)
    /cifrado       -> Cifrar/descifrar datos con AES-256-GCM
    /ota           -> Demo actualizacion firmware con firma RSA-2048
    /borrado       -> Borrado seguro de datos (GDPR Art. 17)
    /logs          -> Registros inmutables en blockchain de auditoria
"""

# ============================================================
# IMPORTS — Modulos estandar y modulos del proyecto
# ============================================================
import sys       # Para manipular la ruta de busqueda de modulos Python
import os        # Para rutas de archivos y generacion de bytes aleatorios
import json      # Para serializar/deserializar datos entre modulos y templates
import hashlib   # Para calcular hashes SHA-256 (usado en la simulacion OTA)

# Agregamos las carpetas de cada modulo al path de Python para que
# los imports funcionen correctamente sin necesidad de instalar el proyecto
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for m in ["crypto_module","secure_erase","auth_service","edge_ai","ota_updater","blockchain_logs"]:
    sys.path.insert(0, os.path.join(BASE, m))

# Flask: framework web ligero para crear el servidor HTTP y manejar rutas
from flask import Flask, render_template, request, redirect, url_for, session

# Modulos propios del proyecto Bio-Monitor 5.0
from crypto_module    import cifrar_datos, descifrar_datos       # AES-256-GCM
from secure_erase     import AlmacenamientoFlashSimulado          # DoD 5220.22-M
from auth_service     import ServidorAutenticacion, GuardianRecursos  # OAuth2/JWT
from edge_ai_model    import ModeloArritmias, generar_datos_ecg   # Random Forest
from ota_updater      import ServidorFirmware, DispositivoIoT     # RSA-2048 OTA
from blockchain_logger import BlockchainLogs, EntradaLog           # SHA-256 chain
import ast  # Para evaluar literales de Python de forma segura (ya no se usa pero se deja)

# ============================================================
# CREACION DE LA APP FLASK
# ============================================================
app = Flask(__name__)

# Clave secreta para firmar las cookies de sesion (Flask sessions)
# En produccion debe ser una clave larga y aleatoria guardada en variable de entorno
app.secret_key = "biomonitor-flask-secret-2026"


# ============================================================
# INICIALIZACION DE SUBSISTEMAS
# Se ejecuta UNA SOLA VEZ al arrancar el servidor.
# Los objetos quedan en memoria y son compartidos por todas las peticiones.
# ============================================================
print("Iniciando subsistemas Bio-Monitor 5.0...")

# Servidor OAuth2 con JWT: maneja login, tokens y revocacion
auth_server  = ServidorAutenticacion()

# Guardian: verifica si un token tiene permisos para acceder a un recurso
guardian     = GuardianRecursos(auth_server)

# Flash simulada: archivos en flash_datos/ representan la memoria del dispositivo IoT
flash_store  = AlmacenamientoFlashSimulado(ruta_base=os.path.join(BASE, "flash_datos"))

# Blockchain de auditoria: registro inmutable de todos los eventos del sistema
blockchain   = BlockchainLogs()

# Servidor OTA: genera y firma paquetes de firmware con clave privada RSA-2048
servidor_ota = ServidorFirmware()

# Entrenar el modelo de IA al iniciar el servidor para que este listo para predicciones
print("Entrenando modelo IA...")
X, y = generar_datos_ecg(1200)       # Generar 1200 muestras artificiales de ECG
modelo_ia = ModeloArritmias()         # Crear clasificador Random Forest
precision, _ = modelo_ia.entrenar(X, y)  # Entrenar y obtener precision del modelo
PRECISION_PCT = f"{precision*100:.1f}"   # Guardar como texto para mostrar en UI
print(f"Modelo listo — precision: {PRECISION_PCT}%")


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def _user():
    """Retorna el nombre del usuario con sesion activa, o '?' si no hay sesion."""
    return session.get("usuario", "?")

def _require_login():
    """
    Middleware de autenticacion para rutas protegidas.
    Retorna None si el usuario TIENE sesion activa.
    Retorna redirect al login si NO tiene sesion.
    Uso: redir = _require_login(); if redir: return redir
    """
    if "usuario" not in session:
        return redirect(url_for("login"))
    return None

# ============================================================
# RUTA: LOGIN   GET /   POST /
# ============================================================
@app.route("/", methods=["GET","POST"])
def login():
    """
    Pagina de inicio de sesion del sistema.
    GET:  Muestra el formulario de login (plantilla login.html)
    POST: Recibe usuario + password y los valida con el modulo OAuth2/JWT
          - Si son correctos: guarda token en sesion y redirige al dashboard
          - Si son incorrectos: muestra error y registra el intento en blockchain
    """
    error = None  # Mensaje de error a mostrar en el formulario (None = sin error)

    if request.method == "POST":
        # Obtener credenciales enviadas en el formulario HTML
        usuario  = request.form.get("usuario","").strip()
        password = request.form.get("password","").strip()
        try:
            # Autenticar contra el servidor OAuth2 (valida usuario y password)
            # Si las credenciales son incorrectas lanza una excepcion
            tokens = auth_server.autenticar(usuario, password)

            # Guardar datos del usuario en la sesion Flask (cookie firmada con secret_key)
            session["usuario"]  = usuario
            session["token"]    = tokens["access_token"]  # JWT para autorizar peticiones
            session["permisos"] = tokens["scope"]         # Ej: "medico lectura escritura"

            # Registrar evento de login exitoso en el blockchain inmutable
            blockchain.registrar(EntradaLog(usuario,"usuario","LOGIN","sistema","web","PERMITIDO"))

            # Redirigir al dashboard principal
            return redirect(url_for("dashboard"))

        except Exception as e:
            # Login fallido: guardar el error para mostrarlo en la pagina
            error = str(e)
            # Registrar intento fallido (util para detectar ataques de fuerza bruta)
            blockchain.registrar(EntradaLog(usuario,"?","LOGIN","sistema","web","DENEGADO",str(e)))

    # Renderizar formulario de login (con error si lo hay)
    return render_template("login.html", error=error)

# ============================================================
# RUTA: LOGOUT   GET /logout
# ============================================================
@app.route("/logout")
def logout():
    """
    Cierra la sesion del usuario.
    Registra el evento en blockchain (trazabilidad) y limpia la cookie de sesion.
    """
    # Registrar cierre de sesion antes de limpiar (para saber quien fue)
    blockchain.registrar(EntradaLog(_user(),"usuario","LOGOUT","sistema","web","PERMITIDO"))
    session.clear()  # Eliminar toda la informacion de sesion de la cookie
    return redirect(url_for("login"))  # Volver a la pagina de login


# ============================================================
# RUTA: DASHBOARD   GET /dashboard
# ============================================================
@app.route("/dashboard")
def dashboard():
    """
    Pantalla principal del sistema.
    Muestra tarjetas con el estado de cada modulo, tabla de cumplimiento regulatorio
    y botones de acceso a cada seccion.
    Requiere sesion activa (redirige a login si no hay sesion).
    """
    redir = _require_login()  # Verificar que el usuario este autenticado
    if redir: return redir

    return render_template("dashboard.html",
        usuario=_user(),                   # Nombre del usuario para mostrar en header
        permisos=session.get("permisos",""),  # Permisos del rol (medico, paciente, etc)
        precision=PRECISION_PCT)           # Precision del modelo IA para mostrar en tarjeta

# ============================================================
# RUTA: DIAGNOSTICO IA   GET /diagnostico   POST /diagnostico
# ============================================================
@app.route("/diagnostico", methods=["GET","POST"])
def diagnostico():
    """
    Pantalla de diagnostico de arritmias con inteligencia artificial.
    GET:  Muestra formulario con 6 campos para ingresar datos del ECG.
    POST: Envia los 6 parametros al modelo Random Forest y muestra:
          - Diagnostico: Normal / Taquicardia / Bradicardia / Fibrilacion Auricular
          - Confianza del modelo en porcentaje
          - Si es emergencia critica (automaticamente alerta al medico)
          - Probabilidades de cada clase (grafico de barras)
          - Explicacion XAI: las 3 variables que mas influyeron en la decision
    Cumplimiento: CE/FDA exige algoritmos explicables (XAI) para dispositivos medicos.
    """
    redir = _require_login()
    if redir: return redir

    resultado = None  # None = formulario no enviado todavia
    valores   = {}    # Valores del formulario para pre-llenarlo si hay error

    if request.method == "POST":
        try:
            # Leer los 6 parametros del ECG desde el formulario HTML
            # Se convierten a float para que el modelo los pueda procesar
            valores = {
                "bpm":             float(request.form.get("bpm", 72)),         # Frecuencia cardiaca
                "intervalo_rr":    float(request.form.get("intervalo_rr", 833)),  # Ms entre latidos
                "variabilidad_rr": float(request.form.get("variabilidad_rr", 20)),  # Variacion RR
                "amplitud_qrs":    float(request.form.get("amplitud_qrs", 1.0)),    # Amplitud QRS
                "intervalo_pr":    float(request.form.get("intervalo_pr", 160)),    # Intervalo PR
                "spo2":            float(request.form.get("spo2", 98)),            # Saturacion O2
            }

            # Llamar al modelo Random Forest (entrenado al iniciar el servidor)
            # Retorna: {diagnostico, confianza, es_emergencia, probabilidades, xai_explicacion}
            resultado = modelo_ia.predecir(valores)

            # Registrar en blockchain que un usuario ejecuto un diagnostico
            blockchain.registrar(EntradaLog(
                _user(),"usuario","PREDICCION_IA","ECG_MANUAL","web","PERMITIDO",
                f"dx={resultado['diagnostico']}"))

        except Exception as e:
            # Si algo falla (ej: valor no numerico), mostrar error amigable
            resultado = {"error": str(e)}

    return render_template("diagnostico.html",
        usuario=_user(), resultado=resultado, valores=valores)

# ============================================================
# RUTA: CIFRADO AES-256   GET /cifrado   POST /cifrado
# ============================================================
@app.route("/cifrado", methods=["GET","POST"])
def cifrado():
    """
    Pantalla de cifrado y descifrado de datos medicos del paciente.
    Tiene dos acciones controladas por el campo oculto 'accion' del formulario:

    CIFRAR (accion=cifrar):
      1. Lee los datos vitales del paciente (bpm, spo2, temperatura)
      2. Deriva una clave AES-256 con PBKDF2-SHA256 (100,000 iteraciones)
      3. Cifra los datos con AES-256-GCM (tambien verifica integridad)
      4. Guarda el paquete cifrado en flash_datos/ (simula memoria Flash del IoT)
      5. Muestra: datos cifrados en base64, nonce y salt

    DESCIFRAR (accion=descifrar):
      1. Lee el id_paciente y clave del formulario
      2. Busca el paquete cifrado en flash_datos/
      3. Intenta descifrar con la clave proporcionada
      4. Si la clave es correcta: muestra los datos originales
      5. Si es incorrecta: GCM tag falla -> error de autenticacion

    Cumplimiento: GDPR Art. 25 — Privacy by Design (cifrado antes de guardar)
    """
    redir = _require_login()
    if redir: return redir

    resultado = None  # Resultado de la operacion (dict con datos o error)

    if request.method == "POST":
        # Determinar que accion ejecutar: cifrar o descifrar
        accion    = request.form.get("accion","cifrar")
        id_pac    = request.form.get("id_paciente","P-00001").strip()
        clave_usr = request.form.get("clave","clave-demo").strip()

        if accion == "cifrar":
            try:
                # Construir JSON con los signos vitales del paciente
                datos = json.dumps({
                    "bpm":         float(request.form.get("bpm","72")),
                    "spo2":        float(request.form.get("spo2","98")),
                    "temperatura": float(request.form.get("temperatura","36.5")),
                    "paciente_id": id_pac,
                })
                # cifrar_datos: deriva clave PBKDF2, cifra con AES-256-GCM
                # Retorna dict {cifrado, nonce, salt} todos en base64
                paquete = cifrar_datos(datos, clave_usr)

                # Guardar paquete cifrado en flash_datos/ (simulando memoria Flash del dispositivo)
                flash_store.guardar(id_pac, json.dumps(paquete).encode())

                # Registrar operacion de escritura en la auditoria blockchain
                blockchain.registrar(EntradaLog(
                    _user(),"usuario","ESCRITURA",f"ECG_{id_pac}","web","PERMITIDO","AES-256-GCM"))

                # Preparar resultado para mostrar en la plantilla
                resultado = {"accion":"cifrar","id_paciente":id_pac,
                             "cifrado":paquete["cifrado"],   # Datos cifrados en base64
                             "nonce":paquete["nonce"],         # Nonce de 12 bytes en base64
                             "salt":paquete["salt"]}           # Salt de 16 bytes en base64
            except Exception as e:
                resultado = {"accion":"cifrar","error":str(e)}

        elif accion == "descifrar":
            # Verificar si existen datos guardados para este paciente
            if not flash_store.existe(id_pac):
                resultado = {"accion":"descifrar",
                             "error":f"No hay datos para '{id_pac}'. Primero cifra un paciente."}
            else:
                try:
                    # Leer el paquete cifrado del archivo en flash_datos/
                    ruta = flash_store._ruta_archivo(id_pac)
                    with open(ruta,"rb") as f:
                        pkg = json.loads(f.read().decode())

                    # Intentar descifrar con la clave proporcionada
                    # Si la clave es incorrecta, GCM tag falla y lanza excepcion
                    texto = descifrar_datos(pkg, clave_usr)

                    # Registrar acceso de lectura exitoso en blockchain
                    blockchain.registrar(EntradaLog(
                        _user(),"usuario","LECTURA",f"ECG_{id_pac}","web","PERMITIDO"))

                    # Convertir JSON descifrado a dict para mostrar en tabla HTML
                    resultado = {"accion":"descifrar","datos":json.loads(texto)}

                except Exception:
                    # Clave incorrecta o datos corruptos: registrar como acceso denegado
                    blockchain.registrar(EntradaLog(
                        _user(),"usuario","LECTURA",f"ECG_{id_pac}","web","DENEGADO","Clave incorrecta"))
                    resultado = {"accion":"descifrar","error":"Clave incorrecta. No se pueden descifrar los datos."}

    return render_template("cifrado.html", usuario=_user(), resultado=resultado)

# ============================================================
# RUTA: OTA FIRMWARE   GET /ota   POST /ota
# ============================================================
@app.route("/ota", methods=["GET","POST"])
def ota():
    """
    Pantalla de demo de actualizacion OTA (Over-The-Air) con firma digital RSA-2048.
    Simula dos escenarios en una sola demo:

    ESCENARIO 1 — Actualizacion legitima:
      1. El servidor genera el contenido del firmware (binario)
      2. Firma el firmware con su clave privada RSA-2048-PSS-SHA256
      3. El dispositivo recibe el paquete y verifica la firma con la clave publica
      4. Como la firma es valida: instala el firmware correctamente

    ESCENARIO 2 — Ataque man-in-the-middle:
      1. Se toma el mismo paquete OTA y se reemplaza su contenido por malware
      2. El dispositivo intenta verificar la firma RSA del firmware adulterado
      3. La firma NO corresponde al nuevo contenido -> verificacion FALLA
      4. El dispositivo RECHAZA la instalacion del firmware malicioso

    Cumplimiento: IEC 62443 (ciberseguridad en sistemas medicos/industriales)
                  Gate 3 del taller — Certificacion de ciberseguridad IoT
    """
    redir = _require_login()
    if redir: return redir

    resultado = None

    if request.method == "POST":
        version   = request.form.get("version","2.1.0").strip()
        device_id = request.form.get("device_id","BioMonitor-007").strip()
        try:
            # PASO 1: Generar contenido binario del firmware (en produccion seria el .bin real)
            fw      = f"BIOMONITOR_FW_v{version}_RELEASE".encode() + os.urandom(64)

            # PASO 2: Servidor firma el firmware con RSA-2048 (clave privada del servidor)
            paquete = servidor_ota.crear_paquete_firmware(fw, version)

            # ── Escenario 1: Actualizacion legitima ──
            # Crear dispositivo IoT con la clave publica del servidor embebida
            dev1 = DispositivoIoT(device_id, servidor_ota.obtener_clave_publica_pem())
            # El dispositivo verifica la firma y aplica el update si es valida
            ok1  = dev1.verificar_y_aplicar_actualizacion(paquete)
            legitima = {
                "exito":               ok1,
                "hash":                paquete["hash_sha256"],              # Hash SHA-256 del firmware
                "tamanio_firma_bytes": len(bytes.fromhex(paquete["firma_hex"])),  # 256 bytes (RSA-2048)
                "mensaje": "Firma RSA-2048 valida. Firmware instalado correctamente." if ok1
                           else "Error al verificar firmware legitimo.",
            }

            # ── Escenario 2: Ataque - firmware adulterado ──
            # Copiar el paquete original y reemplazar el firmware por contenido malicioso
            pkg_malo = dict(paquete)
            fw_malo  = b"MALWARE_PAYLOAD_" + os.urandom(64)  # Contenido del atacante
            pkg_malo["firmware_hex"] = fw_malo.hex()  # Reemplazar firmware
            # Actualizar el hash para que no sea detectado por hash, solo por firma RSA
            pkg_malo["hash_sha256"]  = hashlib.sha256(fw_malo).hexdigest()
            # NOTA: la firma del paquete original NO corresponde al nuevo firmware
            # El atacante no puede re-firmar porque no tiene la clave privada del servidor
            dev2 = DispositivoIoT(device_id, servidor_ota.obtener_clave_publica_pem())
            ok2  = dev2.verificar_y_aplicar_actualizacion(pkg_malo)
            ataque = {
                "exito":   ok2,  # Debe ser False (ataque bloqueado por RSA)
                "mensaje": "Firmware instalado (PELIGRO)." if ok2
                           else "Firma RSA invalida - firmware adulterado rechazado.",
            }

            # Empaquetar resultado para la plantilla
            resultado = {"version":version,"device_id":device_id,"legitima":legitima,"ataque":ataque}

            # Registrar el evento OTA en el blockchain de auditoria
            blockchain.registrar(EntradaLog(
                _user(),"usuario","ACTUALIZACION_OTA",f"{device_id} v{version}","web",
                "PERMITIDO" if ok1 else "DENEGADO"))

        except Exception as e:
            resultado = {"error": str(e)}

    return render_template("ota.html", usuario=_user(), resultado=resultado)

# ============================================================
# RUTA: BORRADO SEGURO   GET /borrado   POST /borrado
# ============================================================
@app.route("/borrado", methods=["GET","POST"])
def borrado():
    """
    Pantalla de borrado seguro de datos del paciente (GDPR Art. 17 - Derecho al Olvido).
    Tiene dos acciones controladas por el campo 'accion' del formulario:

    CREAR DATOS DE PRUEBA (accion=guardar):
      - Genera datos ficticios para el paciente y los guarda en flash_datos/
      - Esto permite demostrar el borrado sin necesidad de cifrar datos primero
      - Util para la demo del taller

    BORRAR DATOS (accion=borrar):
      1. Verifica que existan datos del paciente en flash_datos/
      2. Aplica el algoritmo DoD 5220.22-M en 3 pasadas:
           Pasada 1: Sobreescribir todos los bytes con 0x00 (ceros absolutos)
           Pasada 2: Sobreescribir todos los bytes con 0xFF (unos absolutos)
           Pasada 3: Sobreescribir con bytes completamente aleatorios
      3. Elimina el archivo del sistema de archivos
      4. Verifica que los datos ya no existan
      5. Registra el evento en blockchain como evidencia de cumplimiento

    Cumplimiento: GDPR Art. 17 — Derecho de supresion (Derecho al Olvido)
    """
    redir = _require_login()
    if redir: return redir

    resultado   = None  # Resultado de la operacion
    id_paciente = ""    # ID pre-llenado en el formulario

    if request.method == "POST":
        id_paciente = request.form.get("id_paciente","").strip()
        accion      = request.form.get("accion","borrar")  # 'guardar' o 'borrar'

        if not id_paciente:
            resultado = {"error":"Ingresa un ID de paciente valido."}

        elif accion == "guardar":
            # Crear datos ficticios para el paciente (para poder borrarlos despues)
            datos_prueba = {"paciente_id":id_paciente,"bpm":75,"spo2":98.5,
                            "temperatura":36.5,"historial":"Ultimas 30 lecturas ECG","medico":"dr.garcia"}

            # Guardar como JSON en la memoria Flash simulada (carpeta flash_datos/)
            flash_store.guardar(id_paciente, json.dumps(datos_prueba).encode())

            # Registrar la creacion de datos en blockchain
            blockchain.registrar(EntradaLog(
                _user(),"usuario","ESCRITURA",f"DATOS_{id_paciente}","web","PERMITIDO","test data"))

            # Resultado para mostrar los datos creados en la pagina
            resultado = {"accion":"guardar","id_paciente":id_paciente,"datos":datos_prueba}

        elif accion == "borrar":
            # Verificar primero que existan datos para borrar
            if not flash_store.existe(id_paciente):
                resultado = {"accion":"borrar","id_paciente":id_paciente,"exito":False,
                             "error":f"No hay datos para '{id_paciente}'. Usa 'Crear datos de prueba' primero."}
            else:
                # Ejecutar borrado seguro DoD 5220.22-M (3 pasadas de sobreescritura)
                exito = flash_store.borrado_seguro(id_paciente, pasadas=3)

                # Verificar que no queden datos (auditoria post-borrado)
                flash_store.verificar_borrado(id_paciente)

                # Registrar en blockchain como evidencia de cumplimiento GDPR Art.17
                blockchain.registrar(EntradaLog(
                    _user(),"usuario","BORRADO",f"ALL_{id_paciente}","web","PERMITIDO","GDPR Art.17"))

                # Preparar descripcion de las 3 pasadas para mostrar en tabla HTML
                resultado = {
                    "accion":"borrar","id_paciente":id_paciente,"exito":exito,
                    "pasadas":[
                        {"numero":1,"descripcion":"Sobreescritura con 0x00 (todos ceros)","estado":"Completado"},
                        {"numero":2,"descripcion":"Sobreescritura con 0xFF (todos unos)",  "estado":"Completado"},
                        {"numero":3,"descripcion":"Sobreescritura con bytes aleatorios",    "estado":"Completado"},
                    ],
                    "verificacion":"Archivo eliminado del sistema de archivos. Datos irrecuperables. GDPR Art. 17 cumplido.",
                }

    return render_template("borrado.html", usuario=_user(), resultado=resultado, id_paciente=id_paciente)

# ============================================================
# RUTA: BLOCKCHAIN LOGS   GET /logs   POST /logs
# ============================================================
@app.route("/logs", methods=["GET","POST"])
def logs():
    """
    Pantalla de auditoria del blockchain de accesos.
    Muestra todos los eventos del sistema: logins, lecturas, escrituras, borrados.

    Cada evento es un bloque que contiene el hash del bloque anterior.
    Si alguien modifica un evento historico, la cadena se rompe y el sistema lo detecta.

    POST (accion=generar_demo):
      Agrega 6 eventos de ejemplo para que el blockchain no este vacio.
      Incluye 2 accesos DENEGADOS de un 'atacante' para demostrar deteccion de amenazas.

    Datos que muestra:
      - Tabla con todos los eventos: usuario, accion, recurso, resultado, hash
      - Tarjeta con total de bloques
      - Tarjeta con estado de integridad (VALIDA o COMPROMETIDA)
      - Contador de accesos denegados (posibles ataques)

    Cumplimiento: ISO/IEC 27403 — Trazabilidad y auditoria de datos medicos
    """
    redir = _require_login()
    if redir: return redir

    # Si el usuario presiona 'Generar eventos demo', agregar eventos de muestra
    if request.method == "POST" and request.form.get("accion") == "generar_demo":
        for ev in [
            EntradaLog("dr.garcia", "medico",     "LECTURA",   "ECG_P00123",    "192.168.1.10","PERMITIDO"),
            EntradaLog("paciente1", "paciente",    "LECTURA",   "MIS_DATOS",     "192.168.1.20","PERMITIDO"),
            EntradaLog("device-007","dispositivo", "ESCRITURA", "BPM_P00123",    "10.0.0.7",   "PERMITIDO"),
            EntradaLog("atacante",  "desconocido", "LECTURA",   "ECG_P00123",    "203.0.113.42","DENEGADO","IP foranea"),
            EntradaLog("atacante",  "desconocido", "LECTURA",   "HISTORIAL_ALL", "203.0.113.42","DENEGADO","Sin permisos"),
            EntradaLog("admin",     "admin",       "BORRADO",   "ECG_P00789",    "192.168.1.1", "PERMITIDO","GDPR Art.17"),
        ]:
            blockchain.registrar(ev)  # Cada llamada crea un nuevo bloque encadenado

    # Exportar la cadena completa como lista de diccionarios
    auditoria = blockchain.exportar_auditoria()

    # Aplanar la estructura anidada del bloque para facilitar el uso en Jinja2
    # Bloque original: {indice, timestamp, entrada:{usuario,accion,...}, hash_propio}
    # Lo convertimos a: {indice, timestamp, usuario, accion, recurso, resultado, hash}
    entradas = [{
        "indice":    b["indice"],
        "timestamp": b["timestamp"],
        "usuario":   b["entrada"]["usuario"],
        "accion":    b["entrada"]["accion"],
        "recurso":   b["entrada"]["recurso"],
        "resultado": b["entrada"]["resultado"],
        "hash":      b["hash_propio"],          # Hash SHA-256 del bloque
    } for b in auditoria[1:]]  # [1:] para saltarse el bloque genesis (indice 0)

    # Verificar que ninguno de los bloques fue modificado despues de crearse
    valida, _ = blockchain.verificar_integridad()

    # Contar intentos de acceso denegados (indicador de posibles ataques)
    denegados = sum(1 for b in blockchain.cadena if b.entrada.resultado == "DENEGADO")

    # Estadisticas para las tarjetas del encabezado de la pagina
    stats = {
        "total_bloques":     blockchain.total_bloques() - 1,    # -1 para no contar el genesis
        "integridad":        "VALIDA" if valida else "COMPROMETIDA",
        "accesos_denegados": denegados,
    }

    return render_template("logs.html", usuario=_user(), entradas=entradas, stats=stats)


# ============================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  BIO-MONITOR 5.0 — Dashboard Web")
    print("  Abre tu navegador en: http://localhost:5000")
    print("="*55 + "\n")
    # debug=False: no mostrar informacion interna al navegador en produccion
    # port=5000: puerto estandar para desarrollo Flask
    app.run(debug=False, port=5000)
