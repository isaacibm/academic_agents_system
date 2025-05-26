import streamlit as st
from main import run_compliance_assistant

st.title("Assistente de IA para cáculo")
st.write("Esta IA auxilia a compreender recursos de Cálculo e Álgebra Linear")

with st.sidebar:
    st.header("Selecione uma tarefa")
    tipo_tarefa = "Responder uma pergunta sobre Ciências Exatas"

    pergunta_usuario = st.text_area("Digite sua pergunta: ")

if st.button("Executar"):
    if not pergunta_usuario.strip():
        st.warning("Por favor, digite sua pergunta antes de executar")
    else:
        st.markdown("Processando solicitação... Aguarde, por favor")

        resultado = run_compliance_assistant(pergunta_usuario)
        st.subheader("Resposta IA")
        st.markdown(f'<p style="color: black !important;">{resultado}</p>', unsafe_allow_html=True)
