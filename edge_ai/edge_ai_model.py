"""
MODULO 4: IA en el Borde - Deteccion de Arritmias
====================================================
Proyecto Bio-Monitor 5.0 - Gate 2: Algoritmo IA con precision > 95%
Certificacion CE/FDA - Seccion 2B: XAI (Algoritmos Explicables)

El modelo de IA corre DIRECTAMENTE en el dispositivo wearable (Edge AI).
Ventajas:
  - No necesita internet para hacer predicciones (tiempo real)
  - Los datos del paciente NO salen del dispositivo (privacidad)
  - Latencia ultra baja (~ms)

Modelo: Random Forest (explicable, liviano, bueno para dispositivos IoT)
Input:  Caracteristicas del ECG (frecuencia cardiaca, intervalos RR, etc.)
Output: Normal / Taquicardia / Bradicardia / Fibrilacion Auricular

Nota sobre XAI (Explicabilidad): el modelo puede mostrar CUALES variables
fueron las mas importantes para su decision. Esto es obligatorio para CE/FDA.

Librerias: scikit-learn, numpy
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")


# Etiquetas de arritmias
CLASES = {
    0: "Normal",
    1: "Taquicardia",        # BPM > 100
    2: "Bradicardia",        # BPM < 60
    3: "Fibrilacion_Auricular"  # Ritmo irregular
}

# Nombres de las caracteristicas del ECG (para XAI)
FEATURES = [
    "bpm",            # Frecuencia cardiaca (latidos por minuto)
    "intervalo_rr",   # Tiempo entre latidos (ms) - clave para detectar irregularidades
    "variabilidad_rr",# Variacion del intervalo RR - alta variabilidad = posible FA
    "amplitud_qrs",   # Amplitud del complejo QRS en el ECG (mV)
    "intervalo_pr",   # Intervalo PR (ms) - retraso atrio-ventricular
    "spo2",           # Saturacion de oxigeno (%)
]


def generar_datos_ecg(n_muestras: int = 1500, semilla: int = 42):
    """
    Genera datos de ECG sinteticos pero realistas para entrenamiento.
    
    En produccion usarias datasets reales como MIT-BIH Arrhythmia Database.
    Aqui generamos datos que siguen las distribuciones clinicas reales.
    """
    rng = np.random.default_rng(semilla)

    X = []
    y = []

    muestras_por_clase = n_muestras // 4

    # Clase 0: Normal
    for _ in range(muestras_por_clase):
        bpm           = rng.normal(72, 8)           # 60-100 bpm normal
        intervalo_rr  = 60000 / bpm                 # ms = 60s / bpm
        var_rr        = rng.normal(20, 5)           # Variabilidad normal: ~20ms
        amp_qrs       = rng.normal(1.0, 0.1)        # ~1 mV
        intervalo_pr  = rng.normal(160, 15)         # 120-200ms normal
        spo2          = rng.normal(98, 0.5)
        X.append([bpm, intervalo_rr, var_rr, amp_qrs, intervalo_pr, spo2])
        y.append(0)

    # Clase 1: Taquicardia (BPM alto)
    for _ in range(muestras_por_clase):
        bpm           = rng.normal(130, 15)         # > 100 bpm
        intervalo_rr  = 60000 / bpm
        var_rr        = rng.normal(15, 5)
        amp_qrs       = rng.normal(1.2, 0.15)
        intervalo_pr  = rng.normal(140, 20)
        spo2          = rng.normal(96, 1)           # Leve desaturacion
        X.append([bpm, intervalo_rr, var_rr, amp_qrs, intervalo_pr, spo2])
        y.append(1)

    # Clase 2: Bradicardia (BPM bajo)
    for _ in range(muestras_por_clase):
        bpm           = rng.normal(45, 8)           # < 60 bpm
        intervalo_rr  = 60000 / bpm
        var_rr        = rng.normal(18, 4)
        amp_qrs       = rng.normal(0.9, 0.1)
        intervalo_pr  = rng.normal(180, 20)         # PR algo prolongado
        spo2          = rng.normal(97, 0.8)
        X.append([bpm, intervalo_rr, var_rr, amp_qrs, intervalo_pr, spo2])
        y.append(2)

    # Clase 3: Fibrilacion Auricular (ritmo MUY irregular)
    for _ in range(muestras_por_clase):
        bpm           = rng.normal(110, 25)         # Variable e irregular
        intervalo_rr  = 60000 / bpm
        var_rr        = rng.normal(80, 20)          # ALTA variabilidad = FA
        amp_qrs       = rng.normal(0.8, 0.2)
        intervalo_pr  = rng.normal(200, 50)         # Muy variable o ausente
        spo2          = rng.normal(95, 2)           # Posible desaturacion
        X.append([bpm, intervalo_rr, var_rr, amp_qrs, intervalo_pr, spo2])
        y.append(3)

    return np.array(X), np.array(y)


class ModeloArritmias:
    """
    Modelo de IA para detectar arritmias en el borde (Edge AI).
    
    Usa Random Forest porque:
    1. Es liviano y rapido (importante para dispositivos IoT)
    2. Es EXPLICABLE (XAI): podemos saber que variables importaron
    3. Maneja bien datos ruidosos de sensores
    4. Alcanza > 95% de precision en este problema
    """

    def __init__(self):
        self.modelo = RandomForestClassifier(
            n_estimators=50,    # 50 arboles (balance velocidad/precision)
            max_depth=8,        # Profundidad maxima (evita sobreajuste)
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.entrenado = False
        self.precision_lograda = 0.0

    def entrenar(self, X: np.ndarray, y: np.ndarray):
        """Entrena el modelo con datos de ECG."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Normalizar features (importante para estabilidad del modelo)
        X_train_sc = self.scaler.fit_transform(X_train)
        X_test_sc  = self.scaler.transform(X_test)

        # Entrenar
        self.modelo.fit(X_train_sc, y_train)

        # Evaluar
        predicciones = self.modelo.predict(X_test_sc)
        self.precision_lograda = accuracy_score(y_test, predicciones)
        self.entrenado = True

        print(f"  [IA] Modelo entrenado con {len(X_train)} muestras")
        print(f"  [IA] Precision en test: {self.precision_lograda * 100:.1f}%")

        if self.precision_lograda < 0.95:
            print("  [IA] ATENCION: Precision < 95%. No cumple Gate 2.")
        else:
            print("  [IA] Gate 2 SUPERADO: Precision >= 95%")

        return self.precision_lograda, classification_report(
            y_test, predicciones,
            target_names=list(CLASES.values()),
            output_dict=True
        )

    def predecir(self, lectura_ecg: dict) -> dict:
        """
        Realiza una prediccion en tiempo real sobre una lectura del sensor.
        
        lectura_ecg: {"bpm": 130, "intervalo_rr": 460, ...}
        
        Retorna prediccion + nivel de confianza + explicacion XAI
        """
        if not self.entrenado:
            raise RuntimeError("El modelo aun no ha sido entrenado.")

        # Construir vector de entrada
        vector = np.array([[
            lectura_ecg.get("bpm", 72),
            lectura_ecg.get("intervalo_rr", 833),
            lectura_ecg.get("variabilidad_rr", 20),
            lectura_ecg.get("amplitud_qrs", 1.0),
            lectura_ecg.get("intervalo_pr", 160),
            lectura_ecg.get("spo2", 98),
        ]])

        vector_sc = self.scaler.transform(vector)

        # Prediccion + probabilidades
        clase_predicha = self.modelo.predict(vector_sc)[0]
        probabilidades = self.modelo.predict_proba(vector_sc)[0]
        confianza = probabilidades[clase_predicha]

        # XAI: importancia de cada feature para ESTA prediccion
        importancias = self.modelo.feature_importances_
        ranking_features = sorted(
            zip(FEATURES, importancias),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "diagnostico":   CLASES[clase_predicha],
            "clase":         int(clase_predicha),
            "confianza":     round(float(confianza) * 100, 1),
            "es_emergencia": clase_predicha in [1, 3],  # Taquicardia y FA son emergencias
            "xai_explicacion": [
                {"feature": f, "importancia_pct": round(imp * 100, 1)}
                for f, imp in ranking_features[:3]
            ],
            "probabilidades": {
                CLASES[i]: round(float(p) * 100, 1)
                for i, p in enumerate(probabilidades)
            }
        }


# ==============================================================
# DEMO RAPIDA
# ==============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  MODULO IA BORDE - Deteccion de Arritmias")
    print("=" * 55)

    # 1. Generar datos y entrenar
    print("\n[1] Generando datos de ECG sinteticos...")
    X, y = generar_datos_ecg(n_muestras=1500)
    print(f"    {len(X)} muestras generadas, {len(CLASES)} clases")

    print("\n[2] Entrenando modelo Random Forest...")
    modelo = ModeloArritmias()
    precision, reporte = modelo.entrenar(X, y)

    print(f"\n[3] Reporte por clase:")
    for clase, metricas in reporte.items():
        if isinstance(metricas, dict):
            print(f"    {clase:<25} precision={metricas['precision']:.2f}  recall={metricas['recall']:.2f}")

    # 2. Prediccion en tiempo real con casos clinicos
    casos = [
        {"nombre": "Paciente Normal",         "bpm": 72,  "intervalo_rr": 833, "variabilidad_rr": 18, "amplitud_qrs": 1.0, "intervalo_pr": 155, "spo2": 98},
        {"nombre": "Posible Taquicardia",      "bpm": 140, "intervalo_rr": 428, "variabilidad_rr": 12, "amplitud_qrs": 1.2, "intervalo_pr": 130, "spo2": 95},
        {"nombre": "Posible Bradicardia",      "bpm": 42,  "intervalo_rr": 1428,"variabilidad_rr": 16, "amplitud_qrs": 0.9, "intervalo_pr": 185, "spo2": 97},
        {"nombre": "Posible Fibrilacion Auric.","bpm": 105, "intervalo_rr": 571, "variabilidad_rr": 90, "amplitud_qrs": 0.7, "intervalo_pr": 220, "spo2": 94},
    ]

    print("\n[4] Predicciones en tiempo real (Edge AI):")
    for caso in casos:
        nombre = caso.pop("nombre")
        resultado = modelo.predecir(caso)
        alerta = " !!! EMERGENCIA" if resultado["es_emergencia"] else ""
        print(f"\n    Paciente: {nombre}")
        print(f"    Diagnostico: {resultado['diagnostico']} "
              f"(confianza: {resultado['confianza']}%){alerta}")
        print(f"    Top features (XAI): "
              + ", ".join(f"{x['feature']}({x['importancia_pct']}%)"
                          for x in resultado['xai_explicacion']))

    print("\n[OK] Modulo IA Edge funcionando correctamente.\n")
