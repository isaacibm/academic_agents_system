import streamlit as st
from main import (
    run_academic_assistant, 
    run_concept_explanation, 
    run_problem_solver,
    get_available_subjects,
    get_subject_documents_info
)
import time

# Configuração da página
st.set_page_config(
    page_title="Agente Acadêmico",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .subject-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
    .task-type-header {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .stAlert > div {
        background-color: #e8f4fd;
        border: 1px solid #b3d9ff;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🎓 Agente Acadêmico</h1>
    <p style="position: absolute; top: 1rem; right: 1rem;">
        <a href="https://cdnlogo.com/logo/ibm_37962.html"><img src="https://static.cdnlogo.com/logos/i/92/ibm.png" alt="IBM Logo" style="height: 120px; width: auto;"></a>
    </p>
    <p>Sistema inteligente para apoio acadêmico em múltiplas disciplinas</p>
</div>
""", unsafe_allow_html=True)

# Inicialização do estado da sessão
if 'current_subject' not in st.session_state:
    st.session_state.current_subject = "geral"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar para configurações
with st.sidebar:    
    # Informações sobre disciplinas disponíveis
    subjects_info = get_subject_documents_info()
    available_subjects = get_available_subjects()
    
    st.subheader("📚 Disciplinas Disponíveis")
    
    subject_options = {}
    for subject_id, subject_data in available_subjects.items():
        docs_count = subjects_info.get(subject_id, {}).get("documents_count", 0)
        status_icon = "✅" if docs_count > 0 else "⚠️"
        display_name = f"{status_icon} {subject_data['name']}"
        if docs_count > 0:
            display_name += f" ({docs_count} docs)"
        subject_options[display_name] = subject_id
    
    selected_subject_display = st.selectbox(
        "Selecione a disciplina:",
        options=list(subject_options.keys()),
        index=0
    )
    
    st.session_state.current_subject = subject_options[selected_subject_display]
    
    # Informações da disciplina selecionada
    current_subject_info = available_subjects.get(st.session_state.current_subject)
    if current_subject_info:
        st.markdown(f"""
        <div class="subject-card">
            <h4>{current_subject_info['name']}</h4>
            <p><small>{current_subject_info['description']}</small></p>
            <p><strong>Documentos:</strong> {subjects_info.get(st.session_state.current_subject, {}).get('documents_count', 0)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()


# Interface baseada no tipo de tarefa
st.markdown('<h2 class="task-type-header">💬 Como posso te ajudar hoje?</h2>', unsafe_allow_html=True)

pergunta = st.text_area(
    "Digite sua pergunta:",
    placeholder="Ex: Como calcular a derivada de uma função composta?",
    height=100,
    key="pergunta_input"
)

if st.button("🚀 Obter Resposta", type="primary"):
    if not pergunta.strip():
        st.warning("⚠️ Por favor, digite sua pergunta antes de executar")
    else:
        with st.spinner("🔍 Processando sua pergunta..."):
            try:
                resultado = run_academic_assistant(
                    pergunta, 
                    st.session_state.current_subject
                )
                
                st.markdown("### 📝 Resposta:")
                st.markdown(resultado) 
                
                # Adiciona ao histórico
                st.session_state.chat_history.append({
                    "tipo": "Pergunta",
                    "input": pergunta,
                    "output": resultado,
                    "disciplina": current_subject_info['name'],
                    "timestamp": time.strftime("%H:%M:%S")
                })
                
            except Exception as e:
                st.error(f"❌ Erro ao processar pergunta: {str(e)}")

# Footer com informações fixo
st.divider()
st.markdown("""
<div style="
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: #f8f9fa;
    border-top: 1px solid #ddd;
    text-align: center;
    color: #666;
    font-size: 0.9em;
    padding: 10px 0;
    z-index: 999;
">
    🎓 <strong>Agente Acadêmico</strong> | 
    Powered by CrewAI & IBM Watsonx 
</div>
<style>
    .main .block-container {
        padding-bottom: 60px;
    }
</style>
""", unsafe_allow_html=True)
