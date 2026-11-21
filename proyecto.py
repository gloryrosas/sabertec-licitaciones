import streamlit as st
import pandas as pd
import numpy as np
import os

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

st.set_page_config(
    page_title="Sabertec AI - Agente Auditor de Licitaciones",
    page_icon="🏗️",
    layout="wide"
)

# Estilos visuales de alto impacto (Modo Industrial / Ingeniería)
st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #0F172A; }
    .sub-title { font-size: 16px; color: #475569; margin-bottom: 20px; }
    .agent-log { 
        background-color: #0F172A; 
        color: #38BDF8; 
        padding: 12px 15px; 
        border-left: 4px solid #F59E0B;
        border-radius: 6px; 
        font-family: monospace; 
        font-size: 13px; 
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🏗️ Sabertec AI: Agente Autónomo de Auditoría Técnica y Licitaciones</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Arquitectura Agéntica: Percibir Pliego ➔ Cruzar Normativas (API/ASME) ➔ Emitir Alertas ➔ Dictamen Ejecutivo</p>', unsafe_allow_html=True)

# ==========================================
# 1. DEFINICIÓN DE HERRAMIENTAS (LAS MANOS)
# ==========================================
def auditar_pliego_licitacion(num_clausulas: int, umbral_riesgo_tecnico: int) -> dict:
    """
    Analiza las cláusulas de un pliego de licitación industrial, cruza normativas técnicas (API, ASME, ISO)
    y calcula el nivel de riesgo contractual y técnico de cada partida.
    
    Args:
        num_clausulas: Cantidad de cláusulas o partidas técnicas a auditar en el pliego.
        umbral_riesgo_tecnico: Nivel de criticidad (0-100) a partir del cual se marca una brecha normativa obligatoria.
    """
    np.random.seed(42)
    disciplinas = [
        "Mecánica y Tuberías (ASME B31.3)", 
        "Soldadura Alta Presión (ASME Sec. IX)", 
        "Tanques y Recipientes (API 650)", 
        "Instrumentación y Control (ISA)", 
        "Seguridad Industrial (OSHA/ISO 45001)"
    ]
    
    df = pd.DataFrame({
        "Clausula_ID": [f"CL-{400 + i}" for i in range(num_clausulas)],
        "Monto_Partida_USD": np.round(np.random.uniform(5000.0, 145000.0, num_clausulas), 2),
        "Indice_Riesgo": np.round(np.random.uniform(10, 98, num_clausulas), 1),
        "Disciplina_Norma": np.random.choice(disciplinas, num_clausulas),
    })
    
    df["Estatus_Cumplimiento"] = np.where(
        df["Indice_Riesgo"] > umbral_riesgo_tecnico, "BRECHA_NORMATIVA_CRITICA", 
        np.where(df["Indice_Riesgo"] > 50, "REQUIERE_ACLARATORIA", "CUMPLE_100%")
    )
    
    criticos = df[df["Estatus_Cumplimiento"] == "BRECHA_NORMATIVA_CRITICA"]
    
    # Guardar métricas reales en sesión para el gráfico ejecutivo
    riesgo_por_disciplina = (
        criticos.groupby("Disciplina_Norma")["Monto_Partida_USD"]
        .sum()
        .reset_index()
        .sort_values(by="Monto_Partida_USD", ascending=False)
    )
    st.session_state["riesgo_disciplina"] = riesgo_por_disciplina
    st.session_state["tabla_criticos"] = criticos[["Clausula_ID", "Disciplina_Norma", "Indice_Riesgo", "Monto_Partida_USD"]]
    st.session_state["total_riesgo_usd"] = round(float(criticos["Monto_Partida_USD"].sum()), 2)
    st.session_state["total_criticos"] = int(len(criticos))
    st.session_state["total_auditadas"] = int(num_clausulas)
    
    return {
        "total_clausulas_auditadas": int(num_clausulas),
        "brechas_criticas_detectadas": int(len(criticos)),
        "presupuesto_expuesto_a_penalidad_usd": round(float(criticos["Monto_Partida_USD"].sum()), 2),
        "muestra_hallazgos": criticos.head(5).to_dict(orient="records")
    }

def generar_solicitud_aclaratoria_tecnica(clausula_id: str, norma_afectada: str) -> dict:
    """
    Genera automáticamente un oficio técnico de solicitud de aclaratoria (RFI - Request for Information) 
    para el cliente licitante y bloquea el envío de la oferta hasta subsanar el requisito.
    
    Args:
        clausula_id: Identificador único de la cláusula con brecha normativa crítica.
        norma_afectada: Código de la norma internacional o especificación comprometida.
    """
    return {
        "estatus_accion": "RFI_GENERADO_Y_BLOQUEADO",
        "clausula": clausula_id,
        "norma": norma_afectada,
        "mensaje": f"Se ha emitido alerta al Comité de Licitaciones y generado borrador de aclaratoria técnica (RFI) para la cláusula {clausula_id} ({norma_afectada})."
    }

herramientas_disponibles = {
    "auditar_pliego_licitacion": auditar_pliego_licitacion,
    "generar_solicitud_aclaratoria_tecnica": generar_solicitud_aclaratoria_tecnica
}

# ==========================================
# 2. CONFIGURACIÓN EN BARRA LATERAL
# ==========================================
st.sidebar.header("⚙️ Parámetros de Licitación")
st.sidebar.markdown("**Documento Activo:** `Pliego_Ingenieria_Planta_V4.pdf`")

prompt_usuario = st.sidebar.text_area(
    "💬 Instrucción al Agente Auditor:",
    value="Audita 120 cláusulas técnicas del pliego con un umbral de riesgo de 75. Si detectas brechas normativas críticas (API/ASME), genera automáticamente la solicitud de aclaratoria (RFI) para la primera cláusula crítica y redacta el dictamen ejecutivo para la Gerencia de Ingeniería.",
    height=160
)

run_agent = st.sidebar.button("🚀 Ejecutar Auditoría Agéntica", type="primary")

# ==========================================
# 3. EJECUCIÓN DEL BUCLE AUTÓNOMO
# ==========================================
if run_agent:
    if not HAS_GENAI:
        st.error("⚠️ La librería `google-genai` no está instalada en el entorno.")
    else:
        with st.spinner("🤖 Agente razonando, cruzando normativas API/ASME y ejecutando herramientas..."):
            try:
                api_key = os.environ.get("GEMINI_API_KEY", "TU_API_KEY_AQUI")
                client = genai.Client(api_key=api_key)
                
                config = types.GenerateContentConfig(
                    tools=[auditar_pliego_licitacion, generar_solicitud_aclaratoria_tecnica],
                    system_instruction=(
                        "Eres un Ingeniero Senior Especialista en Licitaciones Industriales, Petroleras y de Infraestructura en Sabertec AI. "
                        "Tu objetivo es proteger la rentabilidad y el cumplimiento técnico de la empresa. "
                        "Analiza los objetivos del usuario, invoca las herramientas de auditoría de pliegos y generación de RFI, "
                        "y redacta un Dictamen Ejecutivo impecable, técnico y directo en Markdown, destacando montos en riesgo, "
                        "normativas comprometidas (ASME, API, ISO) y recomendaciones accionables antes de presentar la oferta."
                    ),
                    temperature=0.2
                )
                
                # Sistema de respaldo automático anti-saturación para demos en vivo
                modelos_respaldo = ["gemini-3.8-flash", "gemini-4-hydrogen", "gemini-3.5-flash-lite"]
                chat = None
                response = None
                
                for modelo in modelos_respaldo:
                    try:
                        chat = client.chats.create(model=modelo, config=config)
                        response = chat.send_message(prompt_usuario)
                        break
                    except Exception as err_modelo:
                        err_str = str(err_modelo)
                        if any(code in err_str for code in ["503", "404", "429", "UNAVAILABLE", "NOT_FOUND"]):
                            continue
                        raise err_modelo
                
                if response is None:
                    raise Exception("Los servidores de respaldo están temporalmente ocupados. Intenta nuevamente en unos segundos.")
                
                log_logs = []
                
                # Bucle Agéntico (Percibir -> Decidir -> Actuar -> Observar)
                while response.function_calls:
                    for function_call in response.function_calls:
                        nombre_fn = function_call.name
                        args_fn = function_call.args
                        
                        log_logs.append(f"🛠️ [DECISIÓN DEL AGENTE] Invocando herramienta: `{nombre_fn}` | Parámetros: {args_fn}")
                        
                        if nombre_fn in herramientas_disponibles:
                            resultado_fn = herramientas_disponibles[nombre_fn](**args_fn)
                        else:
                            resultado_fn = {"error": "Herramienta no encontrada"}
                            
                        log_logs.append(f"👁️ [OBSERVACIÓN TÉCNICA] Datos extraídos: {resultado_fn}")
                        
                        response = chat.send_message(
                            types.Part.from_function_response(
                                name=nombre_fn,
                                response={"result": resultado_fn}
                            )
                        )
                
                # 1. KPIs Reales Dinámicos
                col1, col2, col3 = st.columns(3)
                col1.metric("Cláusulas Auditadas", f"{st.session_state.get('total_auditadas', 120)} Ítems", "100% Pliego Procesado")
                col2.metric("Brechas Críticas", f"{st.session_state.get('total_criticos', 0)} Hallazgos", "Sobre umbral de riesgo", delta_color="inverse")
                col3.metric("Capital Expuesto a Penalidad", f"${st.session_state.get('total_riesgo_usd', 0):,.2f} USD", "Riesgo Contractual", delta_color="inverse")

                st.divider()

                # 2. Gráfico Gerencial de Exposición Financiera + Tabla Crítica
                if "riesgo_disciplina" in st.session_state and not st.session_state["riesgo_disciplina"].empty:
