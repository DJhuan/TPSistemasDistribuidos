import streamlit as st
import requests
import os

# Configuração da Página
st.set_page_config(
    page_title="Têmis - Análise de Conduta",
    page_icon="⚖️",
    layout="wide"
)

# URL do API Gateway (Controller)
# No docker-compose, o nome do serviço será 'controller-service'
API_URL = os.getenv("API_URL", "http://controller-service:8000")

# Estilos CSS personalizados (Opcional, para dar um toque da "Marca")
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #FF4B4B;}
    .report-box {border: 1px solid #ddd; padding: 20px; border-radius: 10px; background-color: #f9f9f9;}
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.title("⚖️ Têmis - Assistente de Compliance")
st.markdown("Sistema inteligente para análise de conformidade da **Comp Júnior**.")

# Layout de Colunas
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Descrição da Ocorrência")
    texto_usuario = st.text_area(
        "Descreva a situação, ação ou dúvida detalhadamente:",
        height=300,
        placeholder="Ex: Um membro da diretoria utilizou o cartão corporativo para despesas pessoais..."
    )
    
    btn_analisar = st.button("🔍 Analisar Conduta", type="primary")

with col2:
    st.subheader("📋 Parecer do Sistema")
    
    if btn_analisar:
        if not texto_usuario.strip():
            st.warning("Por favor, insira uma descrição para análise.")
        else:
            with st.spinner("Consultando normas e gerando análise jurídica..."):
                try:
                    # Requisição para o API Gateway
                    response = requests.post(
                        f"{API_URL}/analisar_conduta", 
                        json={"descricao": texto_usuario},
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        analise = data.get("analise_completa")
                        acoes = data.get("acoes_sugeridas")
                        
                        # Exibição dos resultados
                        st.success("Análise concluída com sucesso!")
                        
                        st.markdown("### ✅ Ações Sugeridas")
                        st.warning(acoes)
                    else:
                        st.error(f"Erro na análise: {response.text}")
                
                except requests.exceptions.ConnectionError:
                    st.error("Não foi possível conectar ao servidor Têmis. Verifique se a API está online.")
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado: {e}")

# Rodapé
st.markdown("---")
st.caption("Sistema Têmis v1.0 | Comp Júnior - UFLA | Desenvolvido para Sistemas Distribuídos")