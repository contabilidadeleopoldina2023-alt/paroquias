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
URL_GRAVACAO = "https://script.google.com/macros/s/AKfycbzG8HBTljt9RqSFz5Z6AUbkvCV19i1KYDzKWgaZlE502RR4PBM8qHtr1tvFf9MxKgCt/exec"

# Lista Oficial Padrão de Segurança (64 Paróquias / Instituições Oficiais)
LISTA_PAROQUIAS = [
    "2. Paróquia do Sr Bom Jesus - ARGIRITA",
    "3. Paróquia de Santo Antônio - ASTOLFO DUTRA",
    "4. Paróquia de São Franc de Paula - BOA FAMILIA",
    "5. Paróquia de São Sebastião - CACHOEIRA ALEGRE",
    "6. Paróquia Santa Rita de Cássia - CATAGUASES",
    "7. Paróquia de N. S. do Rosário - CATAGUASES",
    "8. Paróquia de São José Operário - CATAGUASES",
    "9. Seminário N. S. da Conceição - BOA VISTA",
    "10. Paróquia de N. S. das Dores - DORES DA VITORIA",
    "11. Paróquia de São Sebastião - EUGENOPOLIS",
    "12. Paróquia do Div Espírito Santo - GUARANI",
    "13. Paróquia de Sant'Ana - GUIDOVAL",
    "14. Paróquia de N. S. da Encarnação - GUIRICEMA",
    "15. Paróquia de N S da Glória - ITAMURI",
    "16. Paróquia de N S das Dores - ITAPIRUÇU",
    "17. Paróquia de N. S. da Conceição - LARANJAL",
    "18. Curato da Catedral - LEOPOLDINA",
    "19. Paróquia de N. S. do Rosário - LEOPOLDINA",
    "20. Paróquia de São José Operário - LEOPOLDINA",
    "21. Paróquia de Sta Rita de Cássia - MIRADOURO",
    "22. Paróquia de Sto Antônio - MIRAÍ",
    "23. Paróquia de São Paulo - MURIAÉ",
    "24. Paróquia de N. S da Conceição - MURIAÉ",
    "25. Paróquia de N S Aparecida - MURIAÉ",
    "26. Paróquia de São Franc de Assis - PALMA",
    "27. Paróquia de N. S do Patrocínio - PATROCÍNIO DO MURIAÉ",
    "28. Paróquia de N. S da Piedade - PIACATUBA",
    "29. Paróquia de São Sebastião - PIRAÚBA",
    "30. Paróquia de Santo Antônio - PROVIDÊNCIA",
    "31. Paróquia Jesus Menino Deus - RECREIO",
    "32. Paróquia de São Sebastião - RODEIRO",
    "33. Paróquia de N. S do Rosário - ROSÁRIO DA LIMEIRA",
    "34. Paróquia de Santana - SANTANA DE CATAGUASES",
    "35. Paróquia de São Sebastião - SÃO GERALDO",
    "36. Paróquia de Santo Antônio - TEBAS",
    "37. Paróquia de São José - TOCANTINS",
    "38. Paróquia de Santo Antônio - TUIUTINGA",
    "39. Paróquia de São Januário - UBÁ",
    "40. Paróquia de N S do Rosário - UBÁ",
    "41. Paróquia do Div Espírito Santo - UBÁ",
    "42. Paróquia de São João Batista - VISCONDE RIO BRANCO",
    "43. Curato de São Franc de Paula - VISTA ALEGRE",
    "44. Paróquia do Sr Bom Jesus - VIEIRAS",
    "45. Paróquia de São José - ALÉM PARAÍBA",
    "46. Paróquia Madre de Deus - ANGUSTURA",
    "47. Paróquia de N. S. da Conceição - ESTRELA DALVA",
    "48. Paróquia de Santana - PIRAPETINGA",
    "49. Paróquia de Santo Antônio - SANTO ANTONIO AVENTUREIRO",
    "50. Paróquia de São Sebastião - VOLTA GRANDE",
    "51. Paróquia Sr Bom Jesus dos Aflitos - ITAMARATI DE MINAS",
    "52. Paróquia de São Sebastião - UBÁ",
    "53. Paróquia N. S. Sagrado Coração - MURIAÉ",
    "54. Paróquia Santo Antônio - BELISÁRIO",
    "55. Paróquia São Benedito - LEOPOLDINA",
    "56. Paróquia São Sebastião - VISCONDE RIO BRANCO",
    "57. Seminário M. N. S. Guadalupe - JUIZ DE FORA",
    "58. Paróquia N. S. da Consolação - ALÉM PARAÍBA",
    "59. Paróquia N S das Dores - DONA EUZÉBIA",
    "60. Paroqui N S Divino pranto - MURIAÉ",
    "61. Paróquia de Sta Bernadete - UBÁ",
    "62. P. São Crist e Imac Conceição - CATAGUASES",
    "63. Paróquia Santa Cruz - MURIAÉ",
    "64. Paróquia de Santo Antônio - VISCONDE RIO BRANCO",
    "65. Paróquia São José Operário - UBÁ"
]

def criar_fallback_df():
    return pd.DataFrame({
        "Paróquia / Instituição": LISTA_PAROQUIAS,
        "Saldo em Conformidade": [False] * len(LISTA_PAROQUIAS),
        "Anexos em Dia": [False] * len(LISTA_PAROQUIAS),
        "MPM em Dia": [False] * len(LISTA_PAROQUIAS),
        "Arquivamento Físico em Dia": [False] * len(LISTA_PAROQUIAS),
        "Tudo Pronto até 5º DU": [False] * len(LISTA_PAROQUIAS),
        "Pontuação": [0] * len(LISTA_PAROQUIAS),
        "Ranking": ["F"] * len(LISTA_PAROQUIAS)
    })

# Carregar dados em tempo real da planilha com trava de segurança se estiver vazia
@st.cache_data(ttl=2)
def carregar_dados():
    try:
        df = pd.read_csv(URL_LEITURA)
        if df.empty or "Paróquia / Instituição" not in df.columns or len(df) < 5:
            return criar_fallback_df()
        
        colunas_bool = ["Saldo em Conformidade", "Anexos em Dia", "MPM em Dia", "Arquivamento Físico em Dia", "Tudo Pronto até 5º DU"]
        for col in colunas_bool:
            if col in df.columns:
                df[col] = df[col].fillna(False).astype(bool)
        return df
    except Exception:
        return criar_fallback_df()

df_atual = carregar_dados()

def calcular_ranking(pontos):
    if pontos == 5: return "A+"
    elif pontos == 4: return "A"
    elif pontos == 3: return "B"
    elif pontos == 2: return "C"
    elif pontos == 1: return "D"
    else: return "F"

# Divisão da tela
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
                    st.cache_data.clear()
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
