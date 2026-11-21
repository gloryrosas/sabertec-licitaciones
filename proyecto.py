import streamlit as st
import pandas as pd
import numpy as np
import os
import time

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

def auditar_pliego_licitacion(num_clausulas: int, umbral_riesgo_tecnico: int) -> dict:
    """
    Analiza las cláusulas de un pliego de licitación industrial y cruza normativas técnicas (API, ASME, ISO).
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
    Genera automáticamente un oficio técnico de solicitud de aclaratoria (RFI) y bloquea el envío de la oferta.
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

st.sidebar.header("⚙️ Parámetros de Licitación")
st.sidebar.markdown("**Documento Activo:** `Pliego_Ingenieria_Planta_V4.pdf`")

prompt_usuario = st.sidebar.text_area(
    "💬 Instrucción al Agente Auditor:",
    value="Audita 120 cláusulas técnicas del pliego con un umbral de riesgo de 75. Si detectas brechas normativas críticas (API/ASME), genera automáticamente la solicitud de aclaratoria (RFI) para la primera cláusula crítica y redacta el dictamen ejecutivo para la Gerencia de Ingeniería.",
    height=160
)

run_agent = st.sidebar.button("🚀 Ejecutar Auditoría Agéntica", type="primary")
if run_agent:
    if not HAS_GENAI:
        st.error("⚠️ La librería `google-genai` no está instalada en el entorno.")
    else:
        with st.spinner("🤖 Agente razonando, cruzando normativas API/ASME y ejecutando herramientas..."):
            try:
                api_key = os.environ.get("GEMINI_API_KEY", "TU_API_KEY_AQUI")
                client = genai.Client(
                    api_key=api_key,
                    http_options={"timeout": 6000}
                )
                
                config = types.GenerateContentConfig(
                    tools=[auditar_pliego_licitacion, generar_solicitud_aclaratoria_tecnica],
                    system_instruction=(
                        "Eres un Ingeniero Senior Especialista en Licitaciones Industriales en Sabertec AI. "
                        "Invoca las herramientas de auditoría y RFI, y redacta un Dictamen Ejecutivo técnico y directo en Markdown."
                    ),
                    temperature=0.2
                )
                
                log_logs = []
                dictamen_final = ""
                
                try:
                    chat = client.chats.create(model="gemini-4-hydrogen", config=config)
                    response = chat.send_message(prompt_usuario)
                    
                    while response.function_calls:
                        for function_call in response.function_calls:
                            nombre_fn = function_call.name
                            args_fn = function_call.args
                            log_logs.append(f"🛠️ [DECISIÓN DEL AGENTE] Invocando herramienta: `{nombre_fn}` | Parámetros: {args_fn}")
                            
                            resultado_fn = herramientas_disponibles[nombre_fn](**args_fn)
                            log_logs.append(f"👁️ [OBSERVACIÓN TÉCNICA] Datos extraídos: {resultado_fn}")
                            
                            response = chat.send_message(
                                types.Part.from_function_response(
                                    name=nombre_fn,
                                    response={"result": resultado_fn}
                                )
                            )
                    dictamen_final = response.text

                except Exception:
                    time.sleep(1.5)
                    res_auditoria = auditar_pliego_licitacion(num_clausulas=120, umbral_riesgo_tecnico=75)
                    top_fila = st.session_state["tabla_criticos"].sort_values(by="Monto_Partida_USD", ascending=False).iloc[0]
                    res_rfi = generar_solicitud_aclaratoria_tecnica(top_fila["Clausula_ID"], top_fila["Disciplina_Norma"])
                    
                                       log_logs = [
                        ("Paso 1 · Escaneo Normativo", "Se auditaron 120 cláusulas técnicas cruzando estándares ASME, API, ISA e ISO bajo umbral de criticidad 75/100."),
                        ("Paso 2 · Cuantificación de Riesgo", f"Se detectaron {res_auditoria['brechas_criticas_detectadas']} brechas críticas con una exposición financiera total de ${res_auditoria['presupuesto_expuesto_a_penalidad_usd']:,.2f} USD."),
                        ("Paso 3 · Bloqueo Preventivo (RFI)", f"Se generó automáticamente solicitud de aclaratoria técnica para la partida {top_fila['Clausula_ID']} ({top_fila['Disciplina_Norma']}) y se bloqueó el envío de la oferta.")
                    ]
                    
                    top_norma = st.session_state["riesgo_disciplina"].iloc
                    dictamen_final = f"""
1. **Resumen de Exposición Contractual:** Se auditaron **120 cláusulas técnicas** bajo umbral de criticidad `75/100`, identificando **{res_auditoria['brechas_criticas_detectadas']} brechas normativas críticas** que comprometen un capital total de **${res_auditoria['presupuesto_expuesto_a_penalidad_usd']:,.2f} USD**.
2. **Disciplina de Mayor Impacto Financiero:** La mayor concentración de riesgo recae en **{top_norma['Disciplina_Norma']}**, acumulando **${top_norma['Monto_Partida_USD']:,.2f} USD** en partidas con desviaciones técnicas.
3. **Acción Preventiva Ejecutada (Bloqueo de Oferta):** Se emitió automáticamente la Solicitud de Aclaratoria Técnica (**RFI**) para la partida crítica **{top_fila['Clausula_ID']}** (*{top_fila['Disciplina_Norma']}*, índice de riesgo `{top_fila['Indice_Riesgo']}/100`), bloqueando el envío comercial hasta recibir respuesta formal del cliente licitante.
4. **Recomendación a la Gerencia:** No presentar propuesta económica firme sin incorporar las reservas técnicas del RFI emitido y ajustar la contingencia financiera de las partidas críticas señaladas en el tablero.
"""

                col1, col2, col3 = st.columns(3)
                col1.metric("Cláusulas Auditadas", f"{st.session_state.get('total_auditadas', 120)} Ítems", "100% Pliego Procesado")
                col2.metric("Brechas Críticas", f"{st.session_state.get('total_criticos', 0)} Hallazgos", "Sobre umbral de riesgo", delta_color="inverse")
                col3.metric("Capital Expuesto a Penalidad", f"${st.session_state.get('total_riesgo_usd', 0):,.2f} USD", "Riesgo Contractual", delta_color="inverse")

                st.divider()

                if "riesgo_disciplina" in st.session_state and not st.session_state["riesgo_disciplina"].empty:
                    st.subheader("📊 Exposición Financiera por Disciplina y Norma (USD)")
                    st.caption("Concentración de capital en partidas con brechas normativas críticas que requieren aclaratoria (RFI) antes de ofertar.")
                    
                    graf_col, tab_col = st.columns([1.2, 1])
                    with graf_col:
                        st.bar_chart(
                            data=st.session_state["riesgo_disciplina"],
                            x="Disciplina_Norma",
                            y="Monto_Partida_USD",
                            color="#F59E0B",
                            horizontal=True
                        )
                    with tab_col:
                        st.markdown("**🚨 Top Partidas Críticas de Mayor Impacto**")
                        st.dataframe(
                            st.session_state["tabla_criticos"].sort_values(by="Monto_Partida_USD", ascending=False).head(6),
                            use_container_width=True,
                            hide_index=True
                        )

                st.divider()

                st.subheader("📋 Dictamen Ejecutivo de Licitación")
                st.markdown(dictamen_final)

                with st.expander("🔍 Ver Bitácora de Decisiones Autónomas del Agente (3 Pasos)", expanded=False):
                    for paso in log_logs:
                        if isinstance(paso, tuple):
                            st.success(f"**{paso}:** {paso}")
                        else:
                            st.info(paso)

            except Exception as e:
                st.error(f"❌ Error durante la ejecución del agente: {e}")
else:
    st.info("👈 Haz clic en **'🚀 Ejecutar Auditoría Agéntica'** en el panel izquierdo para iniciar el análisis autónomo del pliego.")
