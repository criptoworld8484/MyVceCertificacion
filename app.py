import streamlit as st
import numpy as np
from PIL import Image
import json
import os
import sys
import time
import random
import copy
import re
import shutil

from src.paths import get_app_dir, get_data_dir
from src.api_key_manager import save_api_key, load_api_key, has_api_key

# ✅ CONFIGURACIÓN PROTEGIDA DE OPENCV
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "0"
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["MPLBACKEND"] = "Agg"

try:
    import cv2
    cv2.setNumThreads(1)
    OPENCV_AVAILABLE = True
except:
    OPENCV_AVAILABLE = False

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except:
    GENAI_AVAILABLE = False

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión de Preguntas", layout="wide", page_icon="📚")

# ✅ CSS ULTRA MEJORADO PARA CHECKBOXES Y ANIMACIONES
st.markdown("""
<style>
    /* ===== CHECKBOXES SUPER VISIBLES ===== */
    
    /* Contenedor del checkbox */
    div[data-testid="stCheckbox"] {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
        border: 2px solid #22c55e !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 8px 0 !important;
        box-shadow: 0 2px 6px rgba(34, 197, 94, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stCheckbox"]:hover {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important;
        border-color: #16a34a !important;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Input checkbox - SUPER GRANDE Y VERDE */
    div[data-testid="stCheckbox"] input[type="checkbox"] {
        width: 32px !important;
        height: 32px !important;
        accent-color: #10b981 !important;
        cursor: pointer !important;
        border: 3px solid #10b981 !important;
        border-radius: 6px !important;
    }
    
    /* Label del checkbox */
    div[data-testid="stCheckbox"] label {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #065f46 !important;
        cursor: pointer !important;
    }
    
    div[data-testid="stCheckbox"] label span {
        color: #065f46 !important;
        font-weight: 700 !important;
    }
    
    /* Cuando está checked */
    div[data-testid="stCheckbox"]:has(input:checked) {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        border-color: #047857 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important;
    }
    
    div[data-testid="stCheckbox"]:has(input:checked) label {
        color: white !important;
    }
    
    div[data-testid="stCheckbox"]:has(input:checked) label span {
        color: white !important;
    }
    
    /* ===== BOTONES MEJORADOS ===== */
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 14px 28px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.5) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: white !important;
        font-weight: 700 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4) !important;
    }
    
    .stButton > button:disabled {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        opacity: 1 !important;
    }
    
    /* ===== NUMBER INPUT ===== */
    .stNumberInput > div > div > input {
        font-size: 20px !important;
        font-weight: 700 !important;
        border: 3px solid #8b5cf6 !important;
        border-radius: 10px !important;
        text-align: center !important;
    }
    
    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #8b5cf6 0%, #6366f1 100%) !important;
        height: 12px !important;
    }
    
    /* ===== TEXT AREAS ===== */
    .stTextArea textarea {
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
        font-size: 15px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
    }
    
    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {
        font-size: 36px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader {
        font-weight: 700 !important;
        font-size: 16px !important;
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%) !important;
        border-radius: 8px !important;
        border: 2px solid #d1d5db !important;
    }
    
    /* ===== TOASTS (notificaciones) ===== */
    .stToast {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* ===== SPINNER PERSONALIZADO ===== */
    .stSpinner > div {
        border-top-color: #8b5cf6 !important;
        border-right-color: #6366f1 !important;
        border-bottom-color: #8b5cf6 !important;
        border-left-color: transparent !important;
        border-width: 4px !important;
    }
    
    /* Ocultar el texto del spinner por defecto */
    .stSpinner > div > div {
        color: #8b5cf6 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CONSTANTES ---
APP_DIR = get_app_dir()
DATA_DIR = get_data_dir()
os.makedirs(DATA_DIR, exist_ok=True)

ARCHIVO_JSON = os.path.join(DATA_DIR, "preguntas.json")
CARPETA_IMAGENES = os.path.join(DATA_DIR, "imagenes_preguntas")
os.makedirs(CARPETA_IMAGENES, exist_ok=True)


def _initialize_resources():
    """Copia recursos por defecto al directorio de datos si no existen."""
    app_json = os.path.join(APP_DIR, "preguntas.json")
    if os.path.exists(app_json) and not os.path.exists(ARCHIVO_JSON):
        shutil.copy2(app_json, ARCHIVO_JSON)
    
    app_img_dir = os.path.join(APP_DIR, "imagenes_preguntas")
    data_img_dir = CARPETA_IMAGENES
    if os.path.exists(app_img_dir) and os.path.isdir(app_img_dir):
        if not os.path.exists(data_img_dir) or not os.listdir(data_img_dir):
            if os.path.exists(data_img_dir):
                shutil.rmtree(data_img_dir)
            shutil.copytree(app_img_dir, data_img_dir)

_initialize_resources()

# --- PANTALLA DE CONFIGURACIÓN INICIAL ---
if "config_completed" not in st.session_state:
    saved_key = load_api_key()
    st.session_state.config_completed = saved_key is not None or has_api_key()
    st.session_state.api_key_ocr = saved_key or ""

if not st.session_state.config_completed:
    st.title("🎓 Simulador de Certificación")
    st.markdown("### Bienvenido al Simulador de Exámenes de Certificación F5 BIG-IP")
    
    st.markdown("---")
    st.markdown("#### Configuración Inicial")
    st.markdown("Para usar la funcionalidad de **OCR** (extracción de preguntas desde imágenes), necesitas configurar tu API Key de Google Gemini.")
    
    api_key_input = st.text_input(
        "API Key de Google Gemini",
        type="password",
        placeholder="Ingresa tu API Key...",
        key="api_key_setup_input"
    )
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("Guardar API Key", type="primary", use_container_width=True):
            if api_key_input:
                if save_api_key(api_key_input):
                    st.session_state.api_key_ocr = api_key_input
                    st.session_state.config_completed = True
                    st.success("API Key guardada correctamente. La funcionalidad OCR estará disponible.")
                    st.rerun()
                else:
                    st.error("Error al guardar la API Key. Asegúrate de tener cryptography instalado.")
            else:
                st.warning("Por favor, ingresa una API Key.")
    
    with col_btn2:
        if st.button("Continuar sin OCR", use_container_width=True):
            st.session_state.config_completed = True
            st.session_state.api_key_ocr = ""
            st.rerun()
    
    with st.expander("Como obtener una API Key?"):
        st.markdown("""
        1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Inicia sesión con tu cuenta de Google
        3. Crea una nueva API Key
        4. Copia la clave y pégala arriba
        """)
    
    st.markdown("---")
    st.info("Si no tienes API Key, puedes usar el simulador sin OCR. Podrás añadir preguntas manualmente.")
    
    st.stop()

st.title("📚 Centro de Gestión de Preguntas de Certificación")

# --- FUNCIONES DE CARGA/GUARDADO ---
@st.cache_data(ttl=10)
def load_questions():
    try:
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_questions(preguntas_actualizadas):
    with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(preguntas_actualizadas, f, indent=4, ensure_ascii=False)
    load_questions.clear()

preguntas = load_questions()

# --- FUNCIÓN DE ALEATORIZACIÓN ---
def aleatorizar_pregunta(pregunta):
    pregunta_aleatoria = copy.deepcopy(pregunta)
    
    opciones_originales = pregunta["opciones"]
    letras_disponibles = ["A", "B", "C", "D", "E", "F"][:len(opciones_originales)]
    
    mapa_opciones = {}
    for opcion in opciones_originales:
        letra = opcion[0]
        texto = opcion[3:].strip() if len(opcion) > 3 else opcion
        mapa_opciones[letra] = texto
    
    pares_originales = [(letra, mapa_opciones[letra]) for letra in letras_disponibles]
    random.shuffle(pares_originales)
    
    nuevas_opciones = []
    mapa_nuevas_letras = {}
    
    for idx, (letra_original, texto) in enumerate(pares_originales):
        nueva_letra = letras_disponibles[idx]
        nuevas_opciones.append(f"{nueva_letra}) {texto}")
        mapa_nuevas_letras[letra_original] = nueva_letra
    
    nuevas_correctas = [mapa_nuevas_letras[letra] for letra in pregunta["correctas"]]
    
    pregunta_aleatoria["opciones"] = nuevas_opciones
    pregunta_aleatoria["correctas"] = nuevas_correctas
    
    return pregunta_aleatoria

# --- FUNCIÓN OCR ---
def extract_text_from_image(image_path, api_key, modelo="gemini-2.5-flash", max_retries=2):
    if not GENAI_AVAILABLE:
        return {"error": "google.genai no está instalado. Ejecuta: pip install google-genai"}
    
    for intento in range(max_retries):
        try:
            client = genai.Client(api_key=api_key)
            
            img = Image.open(image_path)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            import io
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=95)
            img_bytes = img_byte_arr.getvalue()
            
            prompt = """
            Eres un asistente experto en analizar capturas de pantalla de exámenes de certificación.
            Extrae el texto de la imagen y devuélvelo ESTRICTAMENTE en este formato JSON:
            {
                "pregunta": "Aquí el texto de la pregunta completa",
                "respuestas": [
                    "A) texto de la primera opción (usa \\n para saltos de línea si la opción tiene múltiples líneas)",
                    "B) texto de la segunda opción",
                    ...
                ]
            }
            
            IMPORTANTE:
            - Si una opción tiene múltiples líneas (código, listas, texto largo), preserva el formato usando \\n
            - Ignora cualquier texto de interfaz (botones, logos, horas, etc.)
            - Si no hay opciones de respuesta, deja la lista "respuestas" vacía
            - Devuelve SOLO el JSON válido, sin markdown
            """
            
            response = client.models.generate_content(
                model=modelo,
                contents=[
                    prompt,
                    types.Part.from_bytes(
                        data=img_bytes,
                        mime_type='image/jpeg'
                    )
                ]
            )
            
            if not response or not response.text:
                return {"error": "Gemini no devolvió contenido."}
            
            texto_limpio = response.text.strip()
            if texto_limpio.startswith("```json"):
                texto_limpio = texto_limpio[7:].rstrip("```").strip()
            elif texto_limpio.startswith("```"):
                texto_limpio = texto_limpio[3:].rstrip("```").strip()
                
            data = json.loads(texto_limpio)
            
            if not isinstance(data, dict) or "pregunta" not in data or "respuestas" not in data:
                return {"error": "JSON inválido: debe contener 'pregunta' y 'respuestas'"}
                
            return data
            
        except json.JSONDecodeError as e:
            texto_error = response.text[:200] if response and hasattr(response, 'text') else 'Sin respuesta'
            return {"error": f"Error al parsear JSON: {str(e)}\n\nRespuesta: {texto_error}..."}
        
        except Exception as e:
            error_str = str(e)
            
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                retry_match = re.search(r'retry in (\d+(?:\.\d+)?)', error_str)
                wait_seconds = int(float(retry_match.group(1))) if retry_match else 30
                
                return {
                    "error": "cuota_excedida",
                    "mensaje": f"""🚫 **Cuota de API agotada**

Has excedido los límites gratuitos de Google Gemini.

**Soluciones:**
1. ⏳ Espera {wait_seconds} segundos y reintenta
2. 🔑 Crea una nueva API Key: https://makersuite.google.com/app/apikey
3. ✍️ Usa la pestaña "Ingesta Manual"
                    """.strip()
                }
            
            if intento < max_retries - 1:
                time.sleep(2 ** intento)
                continue
            
            return {"error": f"Error: {str(e)}"}
    
    return {"error": "Máximo de reintentos alcanzado"}

# --- FUNCIÓN PARA LIMPIAR FORMULARIO MANUAL ---
def limpiar_formulario_manual():
    st.session_state.manual_enunciado = ""
    st.session_state.manual_imagen = None
    for letra in ["A", "B", "C", "D", "E", "F"]:
        st.session_state[f"manual_texto_{letra}"] = ""
        st.session_state[f"manual_corr_{letra}"] = False

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3, tab4 = st.tabs(["✍️ Ingesta Manual", "📸 Extracción OCR", "📊 Ver Preguntas", "🎮 Simulador"])

# ========================================
# PESTAÑA 1: INGESTA MANUAL
# ========================================
with tab1:
    st.header("✍️ Añadir Pregunta Manualmente")
    st.markdown("Rellena el formulario para añadir una pregunta directamente.")
    
    if "manual_enunciado" not in st.session_state:
        st.session_state.manual_enunciado = ""
    if "manual_imagen" not in st.session_state:
        st.session_state.manual_imagen = None
    
    with st.form("form_manual", clear_on_submit=False):
        enunciado = st.text_area(
            "📝 Enunciado de la pregunta *", 
            height=120, 
            value=st.session_state.manual_enunciado,
            placeholder="Ejemplo: ¿Cuál de las siguientes opciones describe mejor...?",
            key="form_enunciado"
        )
        
        imagen_subida = st.file_uploader(
            "🖼️ Imagen adjunta (opcional)", 
            type=["png", "jpg", "jpeg"],
            key="img_upload_manual"
        )
        
        st.markdown("### Opciones de Respuesta")
        st.caption("⚠️ Rellena al menos 2 opciones y ✅ marca las correctas (puedes marcar múltiples).")
        
        letras = ["A", "B", "C", "D", "E", "F"]
        opciones_inputs = {}
        correctas_checks = {}
        
        for letra in letras:
            col1, col2 = st.columns([5, 1])
            with col1:
                if f"manual_texto_{letra}" not in st.session_state:
                    st.session_state[f"manual_texto_{letra}"] = ""
                
                opciones_inputs[letra] = st.text_input(
                    f"Opción {letra}", 
                    value=st.session_state[f"manual_texto_{letra}"],
                    key=f"form_texto_{letra}",
                    placeholder=f"Escribe la respuesta {letra}..."
                )
            with col2:
                st.write("")
                if f"manual_corr_{letra}" not in st.session_state:
                    st.session_state[f"manual_corr_{letra}"] = False
                
                correctas_checks[letra] = st.checkbox(
                    "✅ Correcta", 
                    value=st.session_state[f"manual_corr_{letra}"],
                    key=f"form_corr_{letra}"
                )
        
        col_submit, col_reset = st.columns([3, 1])
        
        with col_submit:
            submitted = st.form_submit_button("💾 Guardar Pregunta", type="primary", use_container_width=True)
        
        with col_reset:
            reset = st.form_submit_button("🔄 Limpiar", use_container_width=True)
        
        if reset:
            limpiar_formulario_manual()
            st.rerun()
        
        if submitted:
            st.session_state.manual_enunciado = enunciado
            for letra in letras:
                st.session_state[f"manual_texto_{letra}"] = opciones_inputs[letra]
                st.session_state[f"manual_corr_{letra}"] = correctas_checks[letra]
            
            if not enunciado.strip():
                st.error("❌ El enunciado es obligatorio.")
            else:
                opciones_capturadas = []
                correctas_capturadas = []
                
                for letra in letras:
                    texto = opciones_inputs[letra].strip()
                    if texto:
                        opciones_capturadas.append(f"{letra}) {texto}")
                        if correctas_checks[letra]:
                            correctas_capturadas.append(letra)
                
                if len(opciones_capturadas) < 2:
                    st.error("❌ Debes rellenar al menos 2 opciones.")
                elif not correctas_capturadas:
                    st.error("❌ Debes marcar al menos una respuesta correcta.")
                else:
                    with st.spinner("💾 Guardando pregunta..."):
                        preguntas_actuales = load_questions()
                        nuevo_id = 1 if not preguntas_actuales else max(p.get("id", 0) for p in preguntas_actuales) + 1
                        ruta_imagen = None
                        
                        if imagen_subida:
                            extension = imagen_subida.name.split(".")[-1]
                            nombre_archivo = f"img_q{nuevo_id}_{int(time.time())}.{extension}"
                            ruta_imagen = os.path.join(CARPETA_IMAGENES, nombre_archivo)
                            with open(ruta_imagen, "wb") as f:
                                f.write(imagen_subida.getbuffer())
                        
                        nueva_pregunta = {
                            "id": nuevo_id,
                            "pregunta": enunciado.strip(),
                            "imagen": ruta_imagen,
                            "opciones": opciones_capturadas,
                            "correctas": correctas_capturadas
                        }
                        
                        preguntas_actuales.append(nueva_pregunta)
                        save_questions(preguntas_actuales)
                    
                    st.success(f"✅ ¡Pregunta #{nuevo_id} guardada!")
                    st.balloons()
                    
                    limpiar_formulario_manual()
                    time.sleep(1)
                    st.rerun()

# ========================================
# PESTAÑA 2: EXTRACCIÓN OCR
# ========================================
with tab2:
    st.header("📸 Extracción Automática con OCR (Gemini)")
    
    if not GENAI_AVAILABLE:
        st.error("❌ El módulo `google.genai` no está instalado.")
        st.code("pip install google-genai", language="bash")
    else:
        st.markdown("Sube una captura y guarda directamente en la base de datos.")
        
        col_config1, col_config2 = st.columns([2, 1])
        
        with col_config1:
            with st.expander("🔑 Configurar API Key", expanded=True):
                saved_key = load_api_key()
                key_status = "✅ Configurada" if saved_key else "⚠️ No configurada"
                st.write(f"**Estado:** {key_status}")
                
                if saved_key:
                    st.session_state.api_key_ocr = saved_key
                    st.info("Tienes una API Key guardada. Puedes usarla o cambiarla.")
                
                new_key = st.text_input(
                    "API Key de Google Gemini",
                    value="",
                    type="password",
                    placeholder="Ingresa nueva API Key para actualizar...",
                    key="api_key_ocr_input"
                )
                
                col_save, col_clear = st.columns(2)
                with col_save:
                    if st.button("💾 Guardar Key", use_container_width=True):
                        if new_key:
                            if save_api_key(new_key):
                                st.session_state.api_key_ocr = new_key
                                st.success("API Key actualizada correctamente!")
                                st.rerun()
                            else:
                                st.error("Error al guardar la key.")
                        else:
                            st.warning("Ingresa una API Key.")
                with col_clear:
                    if st.button("🗑️ Eliminar Key", use_container_width=True):
                        from src.api_key_manager import delete_api_key
                        delete_api_key()
                        st.session_state.api_key_ocr = ""
                        st.info("API Key eliminada.")
                        st.rerun()
                
                st.caption("🔗 [Obtén tu API Key](https://makersuite.google.com/app/apikey)")
        
        with col_config2:
            with st.expander("⚙️ Modelo", expanded=False):
                modelo_seleccionado = st.selectbox(
                    "Modelo",
                    options=[
                        "gemini-2.5-flash",
                        "gemini-3-flash-preview",
                        "gemini-3.1-pro-preview"
                    ],
                    index=0
                )
        
        uploaded_file = st.file_uploader(
            "📤 Sube captura de pantalla",
            type=["png", "jpg", "jpeg"],
            key="img_upload_ocr"
        )
        
        if uploaded_file is not None:
            col_prev, col_full = st.columns([2, 1])
            
            with col_prev:
                st.image(uploaded_file, caption="Vista previa", width=400)
            
            with col_full:
                st.write("")
                with st.expander("🔍 Ver tamaño completo"):
                    st.image(uploaded_file, use_container_width=True)
            
            temp_path = "temp_capture_ocr.png"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("🚀 Procesar con OCR", type="primary", use_container_width=True):
                if not st.session_state.api_key_ocr.strip():
                    st.error("❌ Ingresa tu API Key arriba.")
                else:
                    with st.spinner(f"🧠 Analizando imagen con {modelo_seleccionado}..."):
                        resultado_texto = extract_text_from_image(
                            temp_path, 
                            st.session_state.api_key_ocr,
                            modelo=modelo_seleccionado
                        )
                        
                        st.session_state.resultado_ocr = resultado_texto
                        st.session_state.imagen_ocr_path = temp_path
                    
                    st.toast("✅ Análisis completado!", icon="✅")
            
            if "resultado_ocr" in st.session_state and st.session_state.resultado_ocr:
                resultado_texto = st.session_state.resultado_ocr
                
                st.success("✅ Procesamiento completado!")
                st.markdown("---")
                
                if "error" not in resultado_texto:
                    st.markdown("### ✏️ Revisar y Guardar")
                    
                    with st.expander("🖼️ Ver imagen capturada a tamaño completo", expanded=False):
                        if os.path.exists(st.session_state.imagen_ocr_path):
                            st.image(st.session_state.imagen_ocr_path, use_container_width=True)
                    
                    pregunta_editada = st.text_area(
                        "📝 Pregunta", 
                        resultado_texto.get("pregunta", ""), 
                        height=120, 
                        key="ocr_pregunta_editable"
                    )
                    
                    st.markdown("**Opciones de respuesta:**")
                    st.caption("✏️ Edita si es necesario y ✅ marca las correctas")
                    
                    respuestas = resultado_texto.get("respuestas", [])
                    opciones_guardadas = []
                    correctas_marcadas = []
                    
                    for idx, opcion in enumerate(respuestas):
                        letra = opcion[0] if opcion else chr(65 + idx)
                        texto_opcion = opcion[3:].strip() if len(opcion) > 3 else opcion
                        
                        col_opt, col_check = st.columns([5, 1])
                        
                        with col_opt:
                            texto_editado = st.text_area(
                                f"Opción {letra}",
                                value=texto_opcion,
                                height=90,
                                key=f"ocr_opcion_{idx}",
                                help="Edita si es necesario, puedes usar múltiples líneas"
                            )
                            
                            if texto_editado.strip():
                                opciones_guardadas.append(f"{letra}) {texto_editado.strip()}")
                        
                        with col_check:
                            st.write("")
                            st.write("")
                            es_correcta = st.checkbox(
                                f"✅ {letra}",
                                key=f"ocr_correcta_{idx}",
                                help=f"Marca si {letra} es correcta"
                            )
                            
                            if es_correcta and texto_editado.strip():
                                correctas_marcadas.append(letra)
                    
                    incluir_imagen = st.checkbox(
                        "📎 Guardar imagen adjunta",
                        value=True
                    )
                    
                    col_save, col_cancel = st.columns([3, 1])
                    
                    with col_save:
                        if st.button("💾 Guardar en Base de Datos", type="primary", use_container_width=True):
                            if not pregunta_editada.strip():
                                st.error("❌ La pregunta no puede estar vacía")
                            elif len(opciones_guardadas) < 2:
                                st.error("❌ Debe haber al menos 2 opciones")
                            elif not correctas_marcadas:
                                st.error("❌ Marca al menos una correcta")
                            else:
                                with st.spinner("💾 Guardando..."):
                                    preguntas_actuales = load_questions()
                                    nuevo_id = 1 if not preguntas_actuales else max(p.get("id", 0) for p in preguntas_actuales) + 1
                                    ruta_imagen = None
                                    
                                    if incluir_imagen and os.path.exists(st.session_state.imagen_ocr_path):
                                        import shutil
                                        nombre_archivo = f"img_q{nuevo_id}_ocr_{int(time.time())}.png"
                                        ruta_imagen = os.path.join(CARPETA_IMAGENES, nombre_archivo)
                                        shutil.copy(st.session_state.imagen_ocr_path, ruta_imagen)
                                    
                                    nueva_pregunta = {
                                        "id": nuevo_id,
                                        "pregunta": pregunta_editada.strip(),
                                        "imagen": ruta_imagen,
                                        "opciones": opciones_guardadas,
                                        "correctas": correctas_marcadas
                                    }
                                    
                                    preguntas_actuales.append(nueva_pregunta)
                                    save_questions(preguntas_actuales)
                                
                                st.success(f"🎉 ¡Pregunta #{nuevo_id} guardada!")
                                st.balloons()
                                st.toast("✅ Pregunta guardada exitosamente!", icon="🎉")
                                
                                del st.session_state.resultado_ocr
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                                
                                time.sleep(1)
                                st.rerun()
                    
                    with col_cancel:
                        if st.button("🔄 Nueva captura", use_container_width=True):
                            del st.session_state.resultado_ocr
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            st.rerun()
                
                elif resultado_texto.get("error") == "cuota_excedida":
                    st.error("🚫 Cuota agotada")
                    st.markdown(resultado_texto.get("mensaje", ""))
                else:
                    st.error(f"❌ {resultado_texto['error']}")

# ========================================
# PESTAÑA 3: VER PREGUNTAS
# ========================================
with tab3:
    st.header("📊 Base de Datos de Preguntas")
    
    preguntas = load_questions()
    
    if not preguntas:
        st.info("ℹ️ No hay preguntas guardadas.")
        
        st.markdown("### 📥 Importar preguntas desde archivo")
        
        archivo_importar = st.file_uploader(
            "Selecciona un archivo JSON con preguntas",
            type=["json"],
            help="Sube un archivo JSON con el formato correcto de preguntas",
            key="importar_inicial"
        )
        
        if archivo_importar is not None:
            try:
                contenido = json.load(archivo_importar)
                
                if isinstance(contenido, list) and len(contenido) > 0:
                    if all(isinstance(p, dict) and "pregunta" in p and "opciones" in p for p in contenido):
                        st.success(f"✅ Archivo válido: {len(contenido)} preguntas detectadas")
                        
                        with st.expander("👀 Vista previa de las preguntas"):
                            for i, p in enumerate(contenido[:5]):
                                st.markdown(f"**{i+1}.** {p['pregunta'][:80]}...")
                            if len(contenido) > 5:
                                st.caption(f"... y {len(contenido) - 5} preguntas más")
                        
                        if st.button("✅ Importar todas las preguntas", type="primary"):
                            with st.spinner("📥 Importando..."):
                                save_questions(contenido)
                            st.success(f"🎉 ¡{len(contenido)} preguntas importadas!")
                            st.toast("✅ Importación exitosa!", icon="🎉")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("❌ El archivo no tiene el formato correcto")
                else:
                    st.error("❌ El archivo está vacío")
            except json.JSONDecodeError:
                st.error("❌ El archivo no es un JSON válido")
    
    else:
        st.success(f"✅ {len(preguntas)} pregunta(s) guardada(s)")
        
        st.markdown("### 🔧 Herramientas")
        
        col_buscar, col_aleatorio = st.columns([3, 1])
        
        with col_buscar:
            buscar = st.text_input("🔍 Buscar", placeholder="Palabras clave...")
        
        with col_aleatorio:
            st.write("")
            mostrar_aleatorio = st.checkbox("🎲 Aleatorizar", value=False)
        
        with st.expander("📥 Importar / 📤 Exportar preguntas"):
            col_exp, col_imp = st.columns(2)
            
            with col_exp:
                st.markdown("**📤 Exportar**")
                st.download_button(
                    label="⬇️ Descargar JSON",
                    data=json.dumps(preguntas, indent=4, ensure_ascii=False),
                    file_name=f"preguntas_backup_{int(time.time())}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col_imp:
                st.markdown("**📥 Importar**")
                archivo_importar = st.file_uploader(
                    "Selecciona archivo JSON",
                    type=["json"],
                    key="importar_con_preguntas"
                )
        
        if archivo_importar is not None:
            try:
                contenido = json.load(archivo_importar)
                
                if isinstance(contenido, list) and len(contenido) > 0:
                    if all(isinstance(p, dict) and "pregunta" in p and "opciones" in p for p in contenido):
                        st.success(f"✅ Archivo válido: {len(contenido)} preguntas")
                        
                        col_merge, col_replace = st.columns(2)
                        
                        with col_merge:
                            if st.button("➕ Añadir", use_container_width=True):
                                with st.spinner("📥 Añadiendo..."):
                                    max_id = max((p.get("id", 0) for p in preguntas), default=0)
                                    for idx, p_nueva in enumerate(contenido):
                                        p_nueva["id"] = max_id + idx + 1
                                    preguntas.extend(contenido)
                                    save_questions(preguntas)
                                st.toast(f"✅ {len(contenido)} preguntas añadidas!", icon="✅")
                                time.sleep(1)
                                st.rerun()
                        
                        with col_replace:
                            if st.button("🔄 Reemplazar", type="secondary", use_container_width=True):
                                st.session_state.confirmar_reemplazo = True
                        
                        if st.session_state.get("confirmar_reemplazo", False):
                            st.warning("⚠️ Esto borrará todas las preguntas actuales")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("✅ Confirmar", type="primary"):
                                    with st.spinner("🔄 Reemplazando..."):
                                        save_questions(contenido)
                                    st.session_state.confirmar_reemplazo = False
                                    st.toast("✅ Base de datos reemplazada!", icon="🔄")
                                    time.sleep(1)
                                    st.rerun()
                            
                            with col2:
                                if st.button("❌ Cancelar"):
                                    st.session_state.confirmar_reemplazo = False
                                    st.rerun()
            except:
                st.error("❌ Error al leer el archivo")
        
        st.markdown("---")
        
        preguntas_filtradas = preguntas
        if buscar.strip():
            preguntas_filtradas = [p for p in preguntas if buscar.lower() in p['pregunta'].lower()]
            st.caption(f"🔍 {len(preguntas_filtradas)} resultado(s)")
        
        for q in preguntas_filtradas:
            p_mostrar = aleatorizar_pregunta(q) if mostrar_aleatorio else q
            
            with st.expander(f"❓ #{q['id']}: {q['pregunta'][:70]}..."):
                st.markdown(f"**{p_mostrar['pregunta']}**")
                
                if p_mostrar.get("imagen") and os.path.exists(p_mostrar["imagen"]):
                    st.image(p_mostrar["imagen"], use_container_width=True)
                
                st.markdown("**Opciones:**")
                for opt in p_mostrar["opciones"]:
                    letra = opt[0]
                    if letra in p_mostrar['correctas']:
                        st.markdown(f"✅ **{opt}**")
                    else:
                        st.markdown(f"- {opt}")
                
                if st.button(f"🗑️ Eliminar", key=f"del_{q['id']}"):
                    preguntas.remove(q)
                    save_questions(preguntas)
                    st.toast("✅ Pregunta eliminada", icon="🗑️")
                    st.rerun()

# ========================================
# PESTAÑA 4: SIMULADOR OPTIMIZADO SIN PARPADEOS
# ========================================
with tab4:
    st.header("🎮 Simulador de Examen")
    
    preguntas = load_questions()
    
    if not preguntas:
        st.info("ℹ️ No hay preguntas disponibles.")
    else:
        st.markdown(f"**📚 Banco:** {len(preguntas)} preguntas")
        
        # Inicializar estados
        if "simulador_activo" not in st.session_state:
            st.session_state.simulador_activo = False
        if "indice_actual" not in st.session_state:
            st.session_state.indice_actual = 0
        if "respuestas_usuario" not in st.session_state:
            st.session_state.respuestas_usuario = {}
        if "preguntas_simulador" not in st.session_state:
            st.session_state.preguntas_simulador = []
        if "mostrar_resultados" not in st.session_state:
            st.session_state.mostrar_resultados = False
        
        # ========================================
        # PANTALLA 1: CONFIGURACIÓN (CON SLIDER EN LUGAR DE NUMBER_INPUT)
        # ========================================
        if not st.session_state.simulador_activo:
            
            st.markdown("### ⚙️ Configurar Examen")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # ✅ SLIDER EN LUGAR DE NUMBER_INPUT (sin parpadeos)
                num_preguntas = st.slider(
                    "🎯 Número de preguntas del examen",
                    min_value=1,
                    max_value=len(preguntas),
                    value=min(10, len(preguntas)),
                    step=1,
                    help="Desliza para seleccionar cuántas preguntas quieres"
                )
                
                st.caption(f"📊 Seleccionadas: **{num_preguntas}** de {len(preguntas)} preguntas disponibles")
            
            with col2:
                st.write("")
                st.write("")
                st.write("")
                modo_aleatorio = st.checkbox("🎲 Orden aleatorio", value=True)
            
            st.markdown("---")
            
            if st.button("🚀 Iniciar Examen", type="primary", use_container_width=True):
                with st.spinner("🎮 Preparando tu examen personalizado..."):
                    preguntas_sel = random.sample(preguntas, num_preguntas) if modo_aleatorio else preguntas[:num_preguntas]
                    st.session_state.preguntas_simulador = [aleatorizar_pregunta(p) for p in preguntas_sel]
                    st.session_state.simulador_activo = True
                    st.session_state.indice_actual = 0
                    st.session_state.respuestas_usuario = {}
                    st.session_state.mostrar_resultados = False
                st.rerun()
        
        # ========================================
        # PANTALLA 2: VISTA DE CORRECCIÓN
        # ========================================
        elif st.session_state.mostrar_resultados:
            res = st.session_state.resultado_final
            
            st.markdown("## 🎯 Resultados del Examen")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("✅ Correctas", res['correctas'], delta=f"{res['correctas']}/{res['total']}")
            with col2:
                st.metric("🟡 Parciales", res['parciales'])
            with col3:
                st.metric("❌ Incorrectas", res['incorrectas'])
            with col4:
                st.metric("📊 Puntuación", f"{res['porcentaje']:.0f}%")
            
            if res['porcentaje'] >= 80:
                st.success("🎉 ¡Excelente! Has aprobado con nota alta")
            elif res['porcentaje'] >= 60:
                st.warning("😊 Aprobado - Puedes mejorar")
            else:
                st.error("😔 No aprobado - Sigue estudiando")
            
            st.markdown("---")
            st.markdown("### 📋 Revisión Detallada")
            
            col_filtro1, col_filtro2 = st.columns([3, 1])
            
            with col_filtro1:
                filtro = st.radio(
                    "Mostrar:",
                    ["Todas las preguntas", "Solo incorrectas", "Solo correctas"],
                    horizontal=True
                )
            
            with col_filtro2:
                st.write("")
                if st.button("🔄 Nuevo Examen", type="primary", use_container_width=True):
                    st.session_state.simulador_activo = False
                    st.session_state.mostrar_resultados = False
                    st.session_state.indice_actual = 0
                    st.session_state.respuestas_usuario = {}
                    st.rerun()
            
            st.markdown("---")
            
            # Preparar lista filtrada
            preguntas_revision = []
            for i, preg in enumerate(st.session_state.preguntas_simulador):
                resp_usuario = st.session_state.respuestas_usuario.get(i, [])
                if not isinstance(resp_usuario, list):
                    resp_usuario = [resp_usuario] if resp_usuario else []
                
                correctas_preg = set(preg["correctas"])
                respuestas_set = set(resp_usuario)
                
                if respuestas_set == correctas_preg:
                    estado = "correcta"
                elif respuestas_set.intersection(correctas_preg):
                    estado = "parcial"
                else:
                    estado = "incorrecta"
                
                if filtro == "Todas las preguntas":
                    preguntas_revision.append((i, preg, resp_usuario, estado))
                elif filtro == "Solo incorrectas" and estado == "incorrecta":
                    preguntas_revision.append((i, preg, resp_usuario, estado))
                elif filtro == "Solo correctas" and estado == "correcta":
                    preguntas_revision.append((i, preg, resp_usuario, estado))
            
            if not preguntas_revision:
                st.info(f"ℹ️ No hay preguntas con el filtro '{filtro}'")
            else:
                st.caption(f"📊 {len(preguntas_revision)} pregunta(s)")
                
                for idx_rev, (idx_orig, preg, resp_usuario, estado) in enumerate(preguntas_revision):
                    
                    st.markdown("---")
                    
                    if estado == "correcta":
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 16px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);'>
                            <h3 style='margin: 0; font-size: 20px;'>✅ Pregunta {idx_orig + 1} - CORRECTA</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    elif estado == "parcial":
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 16px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);'>
                            <h3 style='margin: 0; font-size: 20px;'>🟡 Pregunta {idx_orig + 1} - PARCIAL</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 16px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);'>
                            <h3 style='margin: 0; font-size: 20px;'>❌ Pregunta {idx_orig + 1} - INCORRECTA</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    col_pregunta, col_respuesta = st.columns([1, 1])
                    
                    with col_pregunta:
                        st.markdown("#### 📝 Enunciado")
                        
                        if preg.get("imagen") and os.path.exists(preg["imagen"]):
                            st.image(preg["imagen"], use_container_width=True)
                            st.markdown("---")
                        
                        st.markdown(f"**{preg['pregunta']}**")
                        st.markdown("---")
                        st.markdown("##### Opciones:")
                        
                        for opcion in preg["opciones"]:
                            letra = opcion[0]
                            texto = opcion[3:].strip() if len(opcion) > 3 else opcion
                            
                            if letra in preg["correctas"]:
                                st.markdown(f"""
                                <div style='background: #d1fae5; border-left: 4px solid #10b981; padding: 12px; margin-bottom: 8px; border-radius: 6px;'>
                                    <strong style='color: #065f46;'>{letra}) {texto}</strong>
                                    <span style='color: #059669; font-weight: 600;'> ← ✅ CORRECTA</span>
                                </div>
                                """, unsafe_allow_html=True)
                            elif letra in resp_usuario:
                                st.markdown(f"""
                                <div style='background: #fee2e2; border-left: 4px solid #ef4444; padding: 12px; margin-bottom: 8px; border-radius: 6px;'>
                                    <span style='color: #991b1b;'>{letra}) {texto}</span>
                                    <span style='color: #dc2626; font-weight: 600;'> ← ❌ Tu respuesta</span>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div style='background: #f9fafb; border-left: 4px solid #d1d5db; padding: 12px; margin-bottom: 8px; border-radius: 6px;'>
                                    <span style='color: #4b5563;'>{letra}) {texto}</span>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    with col_respuesta:
                        st.markdown("#### 🎯 Corrección")
                        
                        st.markdown("**Tu respuesta:**")
                        if resp_usuario:
                            if estado == "correcta":
                                st.success(f"✅ {', '.join(resp_usuario)}")
                            elif estado == "parcial":
                                st.warning(f"🟡 {', '.join(resp_usuario)}")
                            else:
                                st.error(f"❌ {', '.join(resp_usuario)}")
                        else:
                            st.error("❌ No respondida")
                        
                        st.markdown("---")
                        st.markdown("**Respuesta correcta:**")
                        st.success(f"✅ {', '.join(preg['correctas'])}")
                        
                        st.markdown("---")
                        st.markdown("**📚 Explicación:**")
                        
                        if len(preg['correctas']) > 1:
                            st.info(f"Requiere {len(preg['correctas'])} opciones")
                        else:
                            st.info("Respuesta única")
                
                st.markdown("---")
                col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
                with col_f2:
                    if st.button("🔄 Nuevo Examen", type="primary", use_container_width=True, key="final"):
                        st.session_state.simulador_activo = False
                        st.session_state.mostrar_resultados = False
                        st.session_state.indice_actual = 0
                        st.session_state.respuestas_usuario = {}
                        st.rerun()
        
        # ========================================
        # PANTALLA 3: SIMULADOR CON AVISO DESTACADO
        # ========================================
        else:
            idx = st.session_state.indice_actual
            preg = st.session_state.preguntas_simulador[idx]
            total = len(st.session_state.preguntas_simulador)
            
            st.progress((idx + 1) / total, text=f"📍 Pregunta {idx + 1} de {total}")
            
            st.markdown(f"### {preg['pregunta']}")
            
            if preg.get("imagen") and os.path.exists(preg["imagen"]):
                with st.expander("🔍 Ver imagen"):
                    st.image(preg["imagen"], use_container_width=True)
            
            st.markdown("---")
            
            num_correctas = len(preg.get("correctas", []))
            es_multiple = num_correctas > 1
            
            # ✅ AVISO ULTRA VISIBLE PARA SELECCIÓN MÚLTIPLE
            if es_multiple:
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
                    border: 4px solid #d97706;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 20px 0;
                    box-shadow: 0 8px 16px rgba(245, 158, 11, 0.4);
                    animation: pulse 2s infinite;
                '>
                    <div style='display: flex; align-items: center; gap: 16px;'>
                        <div style='
                            width: 60px;
                            height: 60px;
                            background: white;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 32px;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                        '>
                            ⚠️
                        </div>
                        <div style='flex: 1;'>
                            <div style='color: white; font-size: 22px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>
                                ⚠️ ATENCIÓN: SELECCIÓN MÚLTIPLE ⚠️
                            </div>
                            <div style='color: #ffffff; font-size: 18px; font-weight: 600;'>
                                Esta pregunta requiere seleccionar <strong style='font-size: 24px; background: white; color: #f59e0b; padding: 4px 12px; border-radius: 6px;'>{num_correctas}</strong> respuestas correctas
                            </div>
                        </div>
                    </div>
                </div>
                
                <style>
                    @keyframes pulse {{
                        0%, 100% {{
                            transform: scale(1);
                            box-shadow: 0 8px 16px rgba(245, 158, 11, 0.4);
                        }}
                        50% {{
                            transform: scale(1.02);
                            box-shadow: 0 12px 24px rgba(245, 158, 11, 0.6);
                        }}
                    }}
                </style>
                """, unsafe_allow_html=True)
            else:
                # Aviso para respuesta única (más discreto pero visible)
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                    border: 3px solid #1d4ed8;
                    border-radius: 10px;
                    padding: 16px;
                    margin: 16px 0;
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                '>
                    <div style='display: flex; align-items: center; gap: 12px;'>
                        <div style='
                            width: 48px;
                            height: 48px;
                            background: white;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 24px;
                        '>
                            ℹ️
                        </div>
                        <div style='flex: 1;'>
                            <div style='color: white; font-size: 18px; font-weight: 700;'>
                                📌 Selecciona UNA única respuesta correcta
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Obtener respuestas previas
            respuestas_previas = st.session_state.respuestas_usuario.get(idx, [])
            if not isinstance(respuestas_previas, list):
                respuestas_previas = [respuestas_previas] if respuestas_previas else []
            
            # Formulario para las opciones
            with st.form(key=f"form_pregunta_{idx}", clear_on_submit=False):
                
                opciones_seleccionadas = {}
                
                for i, opcion in enumerate(preg["opciones"]):
                    letra = opcion[0]
                    texto = opcion[3:].strip() if len(opcion) > 3 else opcion
                    
                    # Card visual
                    if letra in respuestas_previas:
                        st.markdown(f"""
                        <div style='
                            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                            border: 3px solid #047857;
                            border-radius: 12px;
                            padding: 16px;
                            margin-bottom: 12px;
                            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
                        '>
                            <div style='display: flex; align-items: center; gap: 12px;'>
                                <div style='
                                    width: 48px;
                                    height: 48px;
                                    border-radius: 50%;
                                    background: white;
                                    color: #10b981;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-weight: bold;
                                    font-size: 24px;
                                '>
                                    ✓
                                </div>
                                <div style='flex: 1; color: white;'>
                                    <div style='font-size: 14px; font-weight: 800; text-transform: uppercase;'>
                                        OPCIÓN {letra} SELECCIONADA
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='
                            background: white;
                            border: 2px solid #e5e7eb;
                            border-radius: 12px;
                            padding: 16px;
                            margin-bottom: 12px;
                        '>
                            <div style='display: flex; align-items: center; gap: 12px;'>
                                <div style='
                                    width: 48px;
                                    height: 48px;
                                    border-radius: 50%;
                                    background: #9ca3af;
                                    color: white;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-weight: bold;
                                    font-size: 22px;
                                '>
                                    {letra}
                                </div>
                                <div style='flex: 1;'>
                                    <div style='font-size: 12px; color: #6b7280; text-transform: uppercase; font-weight: 600;'>
                                        Opción {letra}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    col_txt, col_check = st.columns([4, 1])
                    
                    with col_txt:
                        if '\n' in texto or len(texto) > 70:
                            st.text(texto)
                        else:
                            st.markdown(texto)
                    
                    with col_check:
                        opciones_seleccionadas[letra] = st.checkbox(
                            f"✅ {letra}",
                            value=(letra in respuestas_previas),
                            key=f"opt_{idx}_{letra}"
                        )
                
                st.markdown("---")
                
                # Botones de navegación
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    btn_anterior = st.form_submit_button("⬅ Anterior", use_container_width=True) if idx > 0 else None
                
                with col2:
                    respondidas = len(st.session_state.respuestas_usuario)
                    st.metric("📊", f"{respondidas}/{total}")
                
                with col3:
                    if idx < total - 1:
                        btn_siguiente = st.form_submit_button("Siguiente ➡", use_container_width=True)
                    else:
                        btn_finalizar = st.form_submit_button("🏁 Finalizar", type="primary", use_container_width=True)
            
            # Procesar formulario
            respuestas_actuales = [letra for letra, seleccionada in opciones_seleccionadas.items() if seleccionada]
            
            if respuestas_actuales:
                st.session_state.respuestas_usuario[idx] = respuestas_actuales
                if es_multiple:
                    st.success(f"✓ Has marcado {len(respuestas_actuales)} de {num_correctas} opciones: {', '.join(respuestas_actuales)}")
                else:
                    st.success(f"✓ Seleccionada: {respuestas_actuales[0]}")
            else:
                if idx in st.session_state.respuestas_usuario:
                    del st.session_state.respuestas_usuario[idx]
                st.info("💡 Marca al menos una opción antes de continuar")
            
            # Navegación
            if idx > 0 and btn_anterior:
                st.session_state.indice_actual -= 1
                st.rerun()
            
            if idx < total - 1 and 'btn_siguiente' in locals() and btn_siguiente:
                st.session_state.indice_actual += 1
                st.rerun()
            
            if idx == total - 1 and 'btn_finalizar' in locals() and btn_finalizar:
                with st.spinner("📊 Calculando tus resultados finales..."):
                    correctas = 0
                    parciales = 0
                    
                    for i, p in enumerate(st.session_state.preguntas_simulador):
                        resp = st.session_state.respuestas_usuario.get(i, [])
                        if not isinstance(resp, list):
                            resp = [resp] if resp else []
                        
                        correctas_p = set(p["correctas"])
                        respuestas_s = set(resp)
                        
                        if respuestas_s == correctas_p:
                            correctas += 1
                        elif respuestas_s.intersection(correctas_p):
                            parciales += 1
                    
                    st.session_state.resultado_final = {
                        "correctas": correctas,
                        "parciales": parciales,
                        "incorrectas": total - correctas - parciales,
                        "total": total,
                        "porcentaje": (correctas / total) * 100
                    }
                    st.session_state.mostrar_resultados = True
                st.rerun()
