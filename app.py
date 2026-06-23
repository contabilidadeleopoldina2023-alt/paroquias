import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Ranking Diocesano 2026", layout="wide")

st.title("⛪ Sistema de Avaliação - Ranking Diocesano 2026 ☁️")
st.markdown("Monitoramento, histórico mensal e ranking dinâmico em tempo real.")

# Configurações de links
SPREADSHEET_ID = "1QzKhdsqMv4lZp06jfZ_bYXz4_1kA7qYaD2PUuQ_3k80"
URL_LEITURA = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Dados"
URL_GRAVACAO = "https://script.google.com/macros/s/AKfycbwHpWJPxvpxpV5pLZH6MX06yZUHureAhawc5zhipW18HihVd1hac4G-89-SYWHgUXCP/exec"

LISTA_PAROQUIAS = [
    "2. Paróquia do Sr Bom Jesus - ARGIRITA", "3. Paróquia de Santo Antônio - ASTOLFO DUTRA",
    "4. Paróquia de São Franc de Paula - BOA FAMILIA", "5. Paróquia de São Sebastião - CACHOEIRA ALEGRE",
    "6. Paróquia Santa Rita de Cássia - CATAGUASES", "7. Paróquia de N. S. do Rosário - CATAGUASES",
    "8. Paróquia de São José Operário - CATAGUASES", "9. Seminário N. S. da Conceição - BOA VISTA",
    "10. Paróquia de N. S. das Dores - DORES DA VITORIA", "11. Paróquia de São Sebastião - EUGENOPOLIS",
    "12. Paróquia do Div Espírito Santo - GUARANI", "13. Paróquia de Sant'Ana - GUIDOVAL",
    "14. Paróquia de N. S. da Encarnação - GUIRICEMA", "15. Paróquia de N S da Glória - ITAMURI",
    "16. Paróquia de N S das Dores - ITAPIRUÇU", "17. Paróquia de N. S. da Conceição - LARANJAL",
    "18. Curato da Catedral - LEOPOLDINA", "19. Paróquia de N. S. do Rosário - LEOPOLDINA",
    "20. Paróquia de São José Operário - LEOPOLDINA", "21. Paróquia de Sta Rita de Cássia - MIRADOURO",
    "22. Paróquia de Sto Antônio - MIRAÍ", "23. Paróquia de São Paulo - MURIAÉ",
    "24. Paróquia de N. S da Conceição - MURIAÉ", "25. Paróquia de N S Aparecida - MURIAÉ",
    "26. Paróquia de São Franc de Assis - PALMA", "27. Paróquia de N. S do Patrocínio - PATROCÍNIO DO MURIAÉ",
    "28. Paróquia de N. S da Piedade - PIACATUBA", "29. Paróquia de São Sebastião - PIRAÚBA",
    "30. Paróquia de Santo Antônio - PROVIDÊNCIA", "31. Paróquia Jesus Menino Deus - RECREIO",
    "32. Paróquia de São Sebastião - RODEIRO", "33. Paróquia de N. S do Rosário - ROSÁRIO DA LIMEIRA",
    "34. Paróquia de Santana - SANTANA DE CATAGUASES", "35. Paróquia de São Sebastião - SÃO GERALDO",
    "36. Paróquia de Santo Antônio - TEBAS", "37. Paróquia de São José - TOCANTINS",
    "38. Paróquia de Santo Antônio - TUIUTINGA", "39. Paróquia de São Januário - UBÁ",
    "40. Paróquia de N S do Rosário - UBÁ", "41. Paróquia do Div Espírito Santo - UBÁ",
    "42. Paróquia de São João Batista - VISCONDE RIO BRANCO", "43. Curato de São Franc de Paula - VISTA ALEGRE",
    "44. Paróquia do Sr Bom Jesus - VIEIRAS", "45. Paróquia de São José - ALÉM PARAÍBA",
    "46. Paróquia Madre de Deus - ANGUSTURA", "47. Paróquia de N. S. da Conceição - ESTRELA DALVA",
    "48. Paróquia de Santana - PIRAPETINGA", "49. Paróquia de Santo Antônio - SANTO ANTONIO AVENTUREIRO",
    "50. Paróquia de São Sebastião - VOLTA GRANDE", "51. Paróquia Sr Bom Jesus dos Aflitos - ITAMARATI DE MINAS",
    "52. Paróquia de São Sebastião - UBÁ", "53. Paróquia N. S. Sagrado Coração - MURIAÉ",
    "54. Paróquia Santo Antônio - BELISÁRIO", "55. Paróquia São Benedito - LEOPOLDINA",
    "56. Paróquia São Sebastião - VISCONDE RIO BRANCO", "57. Seminário M. N. S. Guadalupe - JUIZ DE FORA",
    "58. Paróquia N. S. da Consolação - ALÉM PARAÍBA", "59. Paróquia N S das Dores - DONA EUZÉBIA",
    "60. Paroqui N S Divino pranto - MURIAÉ", "61. Paróquia de Sta Bernadete - UBÁ",
    "62. P. São Crist e Imac Conceição - CATAGUASES", "63. Paróquia Santa Cruz - MURIAÉ",
    "64. Paróquia de Santo Antônio - VISCONDE RIO BRANCO", "65. Paróquia São José Operário - UBÁ"
]

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
ORDEM_RANKING = ["E", "D", "C", "B", "A", "A+"]

def converter_pontos_em_nota(pontos):
    if pontos >= 5: return "A"
    elif pontos == 4: return "A"
    elif pontos == 3: return "B"
    elif pontos == 2: return "C"
    elif pontos == 1: return "D"
    return "E"

def calcular_ranking_regras(row):
    # Pega as notas mensais com base nas colunas de pontos existentes
    notas_por_mes = []
    for m in MESES:
        col = f"{m}_Pontos"
        if col in row and not pd.isna(row[col]):
            notas_por_mes.append(converter_pontos_em_nota(int(row[col])))
        else:
            notas_por_mes.append("E") # Padrão inicial
            
    # Aplica a regra de blocos de 2 meses (Bimestres acumulados)
    rank_atual = "E"
    manter_sempre_A = True
    
    # Avalia os bimestres: (Jan, Fev), (Mar, Abr), (Mai, Jun)...
    for i in range(0, 12, 2):
        n1 = notas_por_mes[i]
        n2 = notas_por_mes[i+1]
        
        # Se algum mês do ano não foi nota Máxima (A), perde a chance de ser A+ no final
        if n1 != "A" or n2 != "A":
            manter_sempre_A = False
            
        idx1 = ORDEM_RANKING.index(n1)
        idx2 = ORDEM_RANKING.index(n2)
        
        if n1 == n2:
            rank_atual = n1 # Se forem iguais, assume a nota deles
        elif idx1 > idx2:
            # Primeiro mês alto, segundo baixo -> CAI (Pega o pior ou mantém baixo)
            rank_atual = n2
        elif idx1 < idx2:
            # Primeiro mês baixo, segundo alto -> SOBE (Assume o melhor)
            rank_atual = n2
            
    # Regra bônus: Quem permanecer "A" de Janeiro a Dezembro vira A+
    if manter_sempre_A and any(f"{m}_Pontos" in row for m in MESES):
        return "A+"
        
    return rank_atual

def criar_fallback_df():
    df = pd.DataFrame({"Paróquia / Instituição": LISTA_PAROQUIAS})
    for m in MESES:
        df[f"{m}_Pontos"] = 0
    df["Ranking_Geral"] = "E"
    return df

@st.cache_data(ttl=2)
def carregar_dados():
    try:
        df = pd.read_csv(URL_LEITURA)
        if df.empty or "Paróquia / Instituição" not in df.columns:
            return criar_fallback_df()
        return df
    except Exception:
        return criar_fallback_df()

df_atual = carregar_dados()

# Interface Gráfica
col_form, col_ranking = st.columns([1.1, 1.4])

with col_form:
    st.subheader("📝 Votação Mensal Coletiva")
    
    # Seleção de Mês e Paróquia
    mes_selecionado = st.selectbox("Selecione o Mês da Avaliação:", MESES)
    paroquia_selecionada = st.selectbox("Selecione a Paróquia:", LISTA_PAROQUIAS)
    
    # Tenta resgatar os dados salvos específicos desse mês para não apagar o histórico
    filtro = df_atual[df_atual["Paróquia / Instituição"] == paroquia_selecionada]
    v1 = v2 = v3 = v4 = v5 = False
    if len(filtro) > 0:
        row = filtro.iloc[0]
        v1 = bool(row.get(f"{mes_selecionado}_C1", False))
        v2 = bool(row.get(f"{mes_selecionado}_C2", False))
        v3 = bool(row.get(f"{mes_selecionado}_C3", False))
        v4 = bool(row.get(f"{mes_selecionado}_C4", False))
        v5 = bool(row.get(f"{mes_selecionado}_C5", False))
        
    c1 = st.checkbox("1° Saldo em conformidade", value=v1, key="c1")
    c2 = st.checkbox("2° Anexos em dia", value=v2, key="c2")
    c3 = st.checkbox("3° MPM em dia", value=v3, key="c3")
    c4 = st.checkbox("4° Arquivamento físico em dia", value=v4, key="c4")
    c5 = st.checkbox("5° Tudo pronto até o quinto dia útil", value=v5, key="c5")
    
    if st.button("Salvar Avaliação Mensal", use_container_width=True):
        nova_pontuacao = sum([c1, c2, c3, c4, c5])
        
        # Simula a alteração local na memória para calcular o novo ranking geral correto
        idx_p = df_atual[df_atual["Paróquia / Instituição"] == paroquia_selecionada].index
        if len(idx_p) > 0:
            df_atual.loc[idx_p[0], f"{mes_selecionado}_Pontos"] = nova_pontuacao
            novo_ranking = calcular_ranking_regras(df_atual.loc[idx_p[0]])
        else:
            novo_ranking = converter_pontos_em_nota(nova_pontuacao)
            
        payload = {
            "paroquia": paroquia_selecionada,
            "mes": mes_selecionada,
            "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5,
            "pontos": int(nova_pontuacao),
            "ranking": novo_ranking
        }
        
        with st.spinner("Computando voto mensal..."):
            try:
                resposta = requests.post(URL_GRAVACAO, data=json.dumps(payload))
                if "Sucesso" in resposta.text:
                    st.success(f"Voto de {mes_selecionado} gravado! Rank Geral atualizado.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Erro no painel do Google: {resposta.text}")
            except Exception:
                st.error("Erro na conexão com o servidor da nuvem.")

with col_ranking:
    st.subheader("📊 Placar Geral Acumulado 2026")
    
    # Calcula os Rankings Finais de todas com base nas regras de bimestres/oscilação
    df_exibicao = df_atual.copy()
    df_exibicao["Ranking_Calculado"] = df_exibicao.apply(calcular_ranking_regras, axis=1)
    
    # Cria uma nota numérica invisível para ordenar a tabela de forma correta (A+ no topo)
    df_exibicao["_ordem"] = df_exibicao["Ranking_Calculado"].apply(lambda x: ORDEM_RANKING.index(x))
    df_ordenado = df_exibicao.sort_values(by=["_ordem", "Paróquia / Instituição"], ascending=[False, True])
    
    st.dataframe(
        df_ordenado[["Paróquia / Instituição", "Ranking_Calculado"]],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Paróquia / Instituição": st.column_config.TextColumn("Paróquia / Instituição"),
            "Ranking_Calculado": st.column_config.TextColumn("Rank Consolidado 🏆")
        }
    )
