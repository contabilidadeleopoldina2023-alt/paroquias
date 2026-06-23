import streamlit as st
import pandas as pd
import requests
import json
import re

st.set_page_config(page_title="Ranking Diocesano 2026", layout="wide")

st.title("⛪ Sistema de Avaliação - Ranking Diocesano 2026 ☁️")
st.markdown("Monitoramento anual contínuo com consolidação de travas bimestrais vigentes.")

SPREADSHEET_ID = "1QzKhdsqMv4lZp06jfZ_bYXz4_1kA7qYaD2PUuQ_3k80"
URL_LEITURA = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
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

def limpar_texto(txt):
    if pd.isna(txt): return ""
    txt = str(txt).strip().lower()
    txt = re.sub(r'^\d+[\s\.\-\–\_]+', '', txt)
    txt = re.sub(r'[^a-z0-9áéíóúâêôçãõ]', '', txt)
    return txt

def obter_nota_mes_planilha(row, mes):
    # Procura diretamente pela coluna exata "Mês_Ranking" (ex: Janeiro_Ranking, Março_Ranking)
    col_alvo = f"{mes}_Ranking"
    if col_alvo in row.index:
        val = str(row[col_alvo]).strip().upper()
        if val in ORDEM_RANKING:
            return val
            
    # Fallback caso a coluna na planilha use espaço ao invés de underline (ex: Janeiro Ranking)
    col_alvo_espaco = f"{mes} Ranking"
    if col_alvo_espaco in row.index:
        val = str(row[col_alvo_espaco]).strip().upper()
        if val in ORDEM_RANKING:
            return val
            
    return ""

def calcular_ranking_justo_bimestral(row):
    notas_bimestres = []
    
    for i in range(0, 12, 2):
        m1 = MESES[i]
        m2 = MESES[i+1]
        
        nota1 = obter_nota_mes_planilha(row, m1)
        nota2 = obter_nota_mes_planilha(row, m2)
        
        # Só calcula se pelo menos um dos meses do bimestre tiver nota lançada
        if nota1 == "" and nota2 == "":
            continue
            
        n1_valid = nota1 if nota1 != "" else "E"
        n2_valid = nota2 if nota2 != "" else "E"
        
        idx1 = ORDEM_RANKING.index(n1_valid)
        idx2 = ORDEM_RANKING.index(n2_valid)
        
        # Pega a menor nota do bimestre
        nota_do_bimestre = n1_valid if idx1 <= idx2 else n2_valid
        notas_bimestres.append(nota_do_bimestre)
        
    if not notas_bimestres:
        return "E"
        
    # O Rank Geral assume a menor nota de todos os bimestres já avaliados
    indices_finais = [ORDEM_RANKING.index(n) for n in notas_bimestres]
    return ORDEM_RANKING[min(indices_finais)]

@st.cache_data(ttl=0)
def carregar_dados():
    try:
        df = pd.read_csv(URL_LEITURA, dtype=str)
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
    paroquia_selecionada = st.selectbox("Selecione a Paróquia:", LISTA_PAROQUIAS)
    
    c1 = st.checkbox("1° Saldo em conformidade", value=False)
    c2 = st.checkbox("2° Anexos em dia", value=False)
    c3 = st.checkbox("3° MPM em dia", value=False)
    c4 = st.checkbox("4° Arquivamento físico em dia", value=False)
    c5 = st.checkbox("5° Tudo pronto até o quinto dia útil", value=False)
    
    if st.button("Salvar Avaliação Mensal", use_container_width=True):
        nova_pontuacao = sum([c1, c2, c3, c4, c5])
        
        if nova_pontuacao >= 4: nota_mes = "A"
        elif nova_pontuacao == 3: nota_mes = "B"
        elif nova_pontuacao == 2: nota_mes = "C"
        elif nova_pontuacao == 1: nota_mes = "D"
        else: nota_mes = "E"
        
        payload = {
            "paroquia": paroquia_selecionada, 
            "mes": mes_selecionado,
            "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5,
            "pontos": int(nova_pontuacao), 
            "ranking": nota_mes
        }
        with st.spinner("Conectando com o Google Sheets..."):
            try:
                resposta = requests.post(URL_GRAVACAO, data=json.dumps(payload))
                if "Sucesso" in resposta.text or "sucesso" in resposta.text.lower():
                    st.success(f"Avaliação de {mes_selecionado} enviada com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro de resposta: {resposta.text}")
            except Exception:
                st.error("Erro técnico na comunicação em nuvem.")

with col_ranking:
    st.subheader("📊 Placar Geral Anual - 65 Paróquias")
    
    df_exibicao = pd.DataFrame({"Paróquia / Instituição": LISTA_PAROQUIAS})
    df_exibicao["Chave_Limpa"] = df_exibicao["Paróquia / Instituição"].apply(limpar_texto)
    
    if not df_atual.empty and "Chave_Limpa" in df_atual.columns:
        df_exibicao = df_exibicao.merge(df_atual, on="Chave_Limpa", how="left")
        
    for m in MESES:
        df_exibicao[m] = df_exibicao.apply(lambda r: obter_nota_mes_planilha(r, m), axis=1)
        
    df_exibicao["Ranking_Calculado"] = df_exibicao.apply(calcular_ranking_justo_bimestral, axis=1)
    
    df_visual = df_exibicao.copy()
    for m in MESES:
        df_visual[m] = df_visual[m].apply(lambda x: x if x != "" else "-")
        
    df_visual["_ordem"] = df_visual["Ranking_Calculado"].apply(lambda x: ORDEM_RANKING.index(x) if x in ORDEM_RANKING else 0)
    df_ordenado = df_visual.sort_values(by=["_ordem", "Paróquia / Instituição"], ascending=[False, True])
    
    colunas_visiveis = ["Paróquia / Instituição", "Ranking_Calculado"] + MESES
    
    st.dataframe(
        df_ordenado[colunas_visiveis],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Ranking_Calculado": st.column_config.TextColumn("Rank Geral 🏆")
        }
    )
