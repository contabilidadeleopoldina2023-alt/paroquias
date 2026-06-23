import streamlit as st
import pandas as pd
import requests
import json

# Configuração da página do sistema
st.set_page_config(page_title="Ranking Diocesano - Nuvem", layout="wide")

st.title("⛪ Sistema de Avaliação Diocesano - Nuvem ☁️")
st.markdown("Monitoramento e ranking colaborativo de paróquias em tempo real.")

# Links de Leitura e Gravação da sua Planilha Google
SPREADSHEET_ID = "1QzKhdsqMv4lZp06jfZ_bYXz4_1kA7qYaD2PUuQ_3k80"
URL_LEITURA = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Dados"
URL_GRAVACAO = "https://script.google.com/macros/s/AKfycbwHpWJPxvpxpV5pLZH6MX06yZUHureAhawc5zhipW18HihVd1hac4G-89-SYWHgUXCP/exec"

# Carregar dados em tempo real da planilha (com atualização rápida)
@st.cache_data(ttl=2)
def carregar_dados():
    try:
        df = pd.read_csv(URL_LEITURA)
        colunas_bool = ["Saldo em Conformidade", "Anexos em Dia", "MPM em Dia", "Arquivamento Físico em Dia", "Tudo Pronto até 5º DU"]
        for col in colunas_bool:
            if col in df.columns:
                df[col] = df[col].fillna(False).astype(bool)
        return df
    except Exception:
        st.error("Erro ao conectar com a planilha do Google. Verifique a internet.")
        st.stop()

df_atual = carregar_dados()

def calcular_ranking(pontos):
    if pontos == 5: return "A+"
    elif pontos == 4: return "A"
    elif pontos == 3: return "B"
    elif pontos == 2: return "C"
    elif pontos == 1: return "D"
    else: return "F"

# Divisão da tela (Formulário na esquerda | Painel Geral na direita)
col_form, col_ranking = st.columns([1.1, 1.4])

with col_form:
    st.subheader("📝 Atualizar Avaliação")
    lista_opcoes = df_atual["Paróquia / Instituição"].tolist()
    paroquia_selecionada = st.selectbox("Selecione a Paróquia:", lista_opcoes)
    
    filtro = df_atual[df_atual["Paróquia / Instituição"] == paroquia_selecionada]
    if len(filtro) > 0:
        dados_p = filtro.iloc[0]
        v1 = bool(dados_p.get("Saldo em Conformidade", False))
        v2 = bool(dados_p.get("Anexos em Dia", False))
        v3 = bool(dados_p.get("MPM em Dia", False))
        v4 = bool(dados_p.get("Arquivamento Físico em Dia", False))
        v5 = bool(dados_p.get("Tudo Pronto até 5º DU", False))
    else:
        v1 = v2 = v3 = v4 = v5 = False
    
    c1 = st.checkbox("1° Saldo em conformidade", value=v1)
    c2 = st.checkbox("2° Anexos em dia", value=v2)
    c3 = st.checkbox("3° MPM em dia", value=v3)
    c4 = st.checkbox("4° Arquivamento físico em dia", value=v4)
    c5 = st.checkbox("5° Tudo pronto até o quinto dia útil", value=v5)
    
    if st.button("Salvar Avaliação na Nuvem", use_container_width=True):
        nova_pontuacao = sum([c1, c2, c3, c4, c5])
        novo_ranking = calcular_ranking(nova_pontuacao)
        
        # Envia os dados REAIS para a planilha do Google via API do Script
        payload = {
            "paroquia": paroquia_selecionada,
            "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5,
            "pontos": int(nova_pontuacao), "ranking": novo_ranking
        }
        
        with st.spinner("Gravando na nuvem..."):
            try:
                resposta = requests.post(URL_GRAVACAO, data=json.dumps(payload))
                if "Sucesso" in resposta.text:
                    st.success(f"Salvo diretamente na Planilha! Classificação: {novo_ranking}")
                    st.cache_data.clear() # Limpa o cache para ler o dado novo na hora
                    st.rerun()
                else:
                    st.error(f"O Google Sheets respondeu com um erro: {resposta.text}")
            except Exception as e:
                st.error("Falha de rede ao enviar os dados para a nuvem.")

with col_ranking:
    st.subheader("📊 Placar Geral Diocesano")
    df_ordenado = df_atual.sort_values(by=["Pontuação", "Paróquia / Instituição"], ascending=[False, True])
    st.dataframe(
        df_ordenado[["Paróquia / Instituição", "Ranking", "Pontuação"]],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Ranking": st.column_config.TextColumn("Classificação ⭐"),
            "Pontuação": st.column_config.ProgressColumn("Critérios Atendidos", min_value=0, max_value=5, format="%d")
        }
    )
