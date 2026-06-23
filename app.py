import streamlit as st
import pandas as pd
import requests
import json
import re

st.set_page_config(page_title="Ranking Diocesano 2026", layout="wide")

st.title("⛪ Sistema de Avaliação - Ranking Diocesano 2026 ☁️")
st.markdown("Monitoramento com persistência de histórico e ranking bimestral consolidado.")

SPREADSHEET_ID = "1QzKhdsqMv4lZp06jfZ_bYXz4_1kA7qYaD2PUuQ_3k80"
URL_LEITURA = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
URL_GRAVACAO = "https://script.google.com/macros/s/AKfycbzHHD5Nd-D21trEdpeaEJhREmh4loGYCEuD2J38NCfZ9oNBeguE4fgjhEIpdchdlf9r/exec"

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

if "memorias_locais" not in st.session_state:
    st.session_state["memorias_locais"] = {}

def limpar_texto(txt):
    if pd.isna(txt): return ""
    txt = str(txt).strip().lower()
    txt = re.sub(r'^\d+[\s\.\-\–\_]+', '', txt)
    txt = re.sub(r'[^a-z0-9áéíóúâêôçãõ]', '', txt)
    return txt

def converter_pontos_em_nota(pts):
    try: p = int(float(pts))
    except: return "E"
    if p >= 4: return "A"
    elif p == 3: return "B"
    elif p == 2: return "C"
    elif p == 1: return "D"
    return "E"

def extrair_historico_linha(row, paroquia_nome):
    """Extrai as notas salvas localmente ou via dicionário persistente"""
    chave_p = limpar_texto(paroquia_nome)
    
    # Se já tivermos dados salvos nesta sessão para essa paróquia, usa eles
    if chave_p in st.session_state["memorias_locais"]:
        return st.session_state["memorias_locais"][chave_p]
        
    historico_inicial = {m: "E" for m in MESES}
    
    # Resgata o valor atual que veio da planilha para o mês selecionado
    for col in row.index:
        c_low = str(col).lower()
        if "ranking" in c_low or "rank" in c_low:
            val = str(row[col]).strip().upper()
            if val in ORDEM_RANKING:
                historico_inicial[st.session_state.get('mes_selecionado', 'Janeiro')] = val
        elif "pontuação" in c_low or "pontuacao" in c_low:
            if not pd.isna(row[col]) and str(row[col]).strip() != "":
                nota_calc = converter_pontos_em_nota(row[col])
                historico_inicial[st.session_state.get('mes_selecionado', 'Janeiro')] = nota_calc
                
    st.session_state["memorias_locais"][chave_p] = historico_inicial
    return historico_inicial

def calcular_ranking_justo_bimestral(historico_meses):
    rank_final = "E"
    primeiro_bimestre = True
    
    for i in range(0, 12, 2):
        m1 = MESES[i]
        m2 = MESES[i+1]
        
        nota1 = historico_meses.get(m1, "E")
        nota2 = historico_meses.get(m2, "E")
        
        if nota1 == "E" and nota2 == "E":
            continue
            
        idx1 = ORDEM_RANKING.index(nota1)
        idx2 = ORDEM_RANKING.index(nota2)
        
        # Lógica justa: Pega a menor nota do bimestre
        nota_bimestre = nota1 if idx1 <= idx2 else nota2
        
        if primeiro_bimestre:
            rank_final = nota_bimestre
            primeiro_bimestre = False
        else:
            idx_acumulado = ORDEM_RANKING.index(rank_final)
            idx_novo_bim = ORDEM_RANKING.index(nota_bimestre)
            if idx_novo_bim < idx_acumulado:
                rank_final = nota_bimestre
                
    return rank_final

@st.cache_data(ttl=1)
def carregar_dados():
    try:
        df = pd.read_csv(URL_LEITURA)
        if df.empty: return pd.DataFrame()
        orig_col = df.columns[0]
        df.rename(columns={orig_col: "Paróquia_Original"}, inplace=True)
        df["Chave_Limpa"] = df["Paróquia_Original"].apply(limpar_texto)
        return df
    except Exception:
        return pd.DataFrame()

df_atual = carregar_dados()

col_form, col_ranking = st.columns([1.1, 1.4])

with col_form:
    st.subheader("📝 Votação Mensal Coletiva")
    mes_selecionado = st.selectbox("Selecione o Mês da Avaliação:", MESES)
    st.session_state['mes_selecionado'] = mes_selecionado
    paroquia_selecionada = st.selectbox("Selecione a Paróquia:", LISTA_PAROQUIAS)
    
    v1 = v2 = v3 = v4 = v5 = False
    if not df_atual.empty and "Chave_Limpa" in df_atual.columns:
        chave_busca = limpar_texto(paroquia_selecionada)
        filtro = df_atual[df_atual["Chave_Limpa"] == chave_busca]
        if len(filtro) > 0:
            row_p = filtro.iloc[0]
            def check_bool(val):
                return str(val).strip().lower() in ["true", "1", "1.0", "sim", "checked", "x"]
            v1 = check_bool(row_p.get("Saldo em Conformidade", False))
            v2 = check_bool(row_p.get("Anexos em Dia", False))
            v3 = check_bool(row_p.get("MPM em Dia", False))
            v4 = check_bool(row_p.get("Arquivamento Físico em Dia", False))
            v5 = check_bool(row_p.get("Tudo Pronto até 5º DU", False))
        
    c1 = st.checkbox("1° Saldo em conformidade", value=v1, key="c1")
    c2 = st.checkbox("2° Anexos em dia", value=v2, key="c2")
    c3 = st.checkbox("3° MPM em dia", value=v3, key="c3")
    c4 = st.checkbox("4° Arquivamento físico em dia", value=v4, key="c4")
    c5 = st.checkbox("5° Tudo pronto até o quinto dia útil", value=v5, key="c5")
    
    if st.button("Salvar Avaliação Mensal", use_container_width=True):
        nova_pontuacao = sum([c1, c2, c3, c4, c5])
        nota_mes = converter_pontos_em_nota(nova_pontuacao)
        
        # Força o salvamento na memória de longo prazo do app para não sumir o mês anterior
        chave_p = limpar_texto(paroquia_selecionada)
        if chave_p not in st.session_state["memorias_locais"]:
            st.session_state["memorias_locais"][chave_p] = {m: "E" for m in MESES}
        st.session_state["memorias_locais"][chave_p][mes_selecionado] = nota_mes
        
        payload = {
            "paroquia": paroquia_selecionada, "mes": mes_selecionado,
            "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5,
            "pontos": int(nova_pontuacao), "ranking": nota_mes
        }
        with st.spinner("Computando voto mensal..."):
            try:
                resposta = requests.post(URL_GRAVACAO, data=json.dumps(payload))
                if "Sucesso" in resposta.text or "sucesso" in resposta.text.lower():
                    st.success(f"Voto de {mes_selecionado} gravado e preservado com sucesso!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Erro no painel do Google: {resposta.text}")
            except Exception:
                st.error("Erro na conexão com o servidor da nuvem.")

with col_ranking:
    st.subheader("📊 Placar Geral Bimestral Consolidado 2026")
    
    df_exibicao = pd.DataFrame({"Paróquia / Instituição": LISTA_PAROQUIAS})
    df_exibicao["Chave_Limpa"] = df_exibicao["Paróquia / Instituição"].apply(limpar_texto)
    
    if not df_atual.empty and "Chave_Limpa" in df_atual.columns:
        df_exibicao = df_exibicao.merge(df_atual, on="Chave_Limpa", how="left")
        
    # Inicializa colunas vazias
    for m in MESES:
        df_exibicao[m] = "E"
    df_exibicao["Ranking_Calculado"] = "E"
    
    # Popula linha por linha cruzando com a memória persistente interna
    for idx, row in df_exibicao.iterrows():
        p_nome = row["Paróquia / Instituição"]
        historico_p = extrair_historico_linha(row, p_nome)
        
        for m in MESES:
            df_exibicao.at[idx, m] = historico_p.get(m, "E")
            
        df_exibicao.at[idx, "Ranking_Calculado"] = calcular_ranking_justo_bimestral(historico_p)
            
    df_exibicao["_ordem"] = df_exibicao["Ranking_Calculado"].apply(lambda x: ORDEM_RANKING.index(x) if x in ORDEM_RANKING else 0)
    df_ordenado = df_exibicao.sort_values(by=["_ordem", "Paróquia / Instituição"], ascending=[False, True])
    
    colunas_visiveis = ["Paróquia / Instituição", "Ranking_Calculado"] + MESES
    st.dataframe(
        df_ordenado[colunas_visiveis],
        hide_index=True, use_container_width=True,
        column_config={
            "Ranking_Calculado": st.column_config.TextColumn("Rank Geral 🏆"),
        }
    )
    )
