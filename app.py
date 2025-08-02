import os
import time
import streamlit as st
from main import run_academic_assistant  # fallback se AcademicCrew não tiver .run
from utils.document_processor import DocumentProcessor
from crew import AcademicCrew  # ajuste o path se estiver em outro módulo

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
    <p>Converse com seus documentos acadêmicos usando IBM Watsonx</p>
</div>
""", unsafe_allow_html=True)

# Inicialização do estado da sessão
if 'current_subject' not in st.session_state:
    st.session_state.current_subject = "geral"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar para escolha de disciplina
# helper
def human_readable_size(n_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n_bytes < 1024:
            return f"{n_bytes:.1f}{unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f}TB"

# CSS moderno para sidebar
st.markdown("""
<style>
.subject-pill-wrapper { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.subject-pill { padding: 6px 14px; border-radius: 999px; background: #f1f5fe; cursor: pointer; font-weight: 600; border: 1px solid transparent; transition: all .2s; font-size: 0.9rem; }
.subject-pill:hover { filter: brightness(1.05); }
.subject-pill.selected { background: linear-gradient(135deg,#667eea,#764ba2); color: white; box-shadow:0 8px 20px rgba(102,126,234,.35); }
.subject-card { background: #ffffff; border-radius: 12px; padding: 14px; box-shadow: 0 12px 30px rgba(0,0,0,0.05); margin-bottom: 14px; }
.pdf-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eef2f7; }
.pdf-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 0.9rem; }
.badge { background: #e7f1ff; padding: 2px 8px; border-radius: 8px; font-size: 0.55rem; margin-left: 6px; }
.small-muted { font-size: 0.7rem; color: #6b7280; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📚 Disciplinas Disponíveis")

    doc_proc = DocumentProcessor()
    raw_subjects = doc_proc.get_available_subjects()  # lista de IDs

    subject_options = {s: s.replace("_", " ").title() for s in raw_subjects}

    if not subject_options:
        st.info("Nenhuma disciplina encontrada na base de conhecimento.")
        selected_subject_id = st.session_state.current_subject
    else:
        # pills de seleção
        st.markdown('<div class="subject-pill-wrapper">', unsafe_allow_html=True)
        for sid, display in subject_options.items():
            is_selected = st.session_state.current_subject == sid
            if is_selected:
                st.markdown(f'<div class="subject-pill selected">{display}</div>', unsafe_allow_html=True)
            else:
                if st.button(display, key=f"select_{sid}"):
                    st.session_state.current_subject = sid
        st.markdown('</div>', unsafe_allow_html=True)

        selected_subject_id = st.session_state.current_subject if st.session_state.current_subject in subject_options else list(subject_options.keys())[0]
        st.divider()

        # Card da disciplina atual
        subject_info = doc_proc.get_subject_info(selected_subject_id)
        name = subject_info.get("name", selected_subject_id.replace("_", " ").title())
        description = subject_info.get("description", "Sem descrição disponível.")

        st.markdown(f"""
        <div class="subject-card">
            <h4 style="margin:4px 0;">{name}</h4>
            <p style="margin:4px 0;" class="small-muted">{description}</p>
        </div>
        """, unsafe_allow_html=True)

        # Documentos
        subject_path = doc_proc.knowledge_base_path / selected_subject_id
        pdf_path_objects = [
            p for p in subject_path.rglob("*")
            if p.is_file() and p.suffix.lower() == ".pdf"
        ]

        with st.expander("📄 Documentos", expanded=True):
            if pdf_path_objects:
                for p in sorted(pdf_path_objects):
                    rel = p.relative_to(doc_proc.knowledge_base_path)
                    try:
                        size = p.stat().st_size
                        hr_size = human_readable_size(size)
                    except Exception:
                        hr_size = "—"
                    st.markdown(
                        f'<div class="pdf-item"><div class="pdf-name">📄 {rel}</div>'
                        f'<div><span class="badge">{hr_size}</span></div></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("Nenhum PDF encontrado nesta disciplina.")

    st.divider()

# Área principal do chat
st.markdown("### 💬 No que você está pensando hoje?")

# Exibe histórico
for message in st.session_state.chat_history:
    role = message.get("role", "assistant")
    with st.chat_message(role):
        st.markdown(message.get("content", ""))

# Entrada de novo prompt
placeholder = f"Pergunte algo sobre {subject_options.get(st.session_state.current_subject, 'Geral')}..."
if prompt := st.chat_input(placeholder):
    # Registra input do usuário
    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt,
        "subject": st.session_state.current_subject,
        "timestamp": time.strftime("%H:%M:%S")
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 O agente está trabalhando nisso..."):
            crew_manager = AcademicCrew(subject_id=st.session_state.current_subject)
            try:
                response = crew_manager.run(question=prompt)
            except AttributeError:
                response = run_academic_assistant(prompt, st.session_state.current_subject)

            st.markdown(response)

            # Armazena resposta no histórico
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "subject": st.session_state.current_subject,
                "timestamp": time.strftime("%H:%M:%S")
            })

# Footer fixo
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
