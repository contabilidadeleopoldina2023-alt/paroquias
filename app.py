import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Ranking Diocesano 2026", layout="wide")

st.title("⛪ Sistema de Avaliação - Ranking Diocesano 2026 ☁️")
st.markdown("Monitoramento, histórico mensal e ranking dinâmico em tempo real.")

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

def calcular_pontos_linha_mes(row, mes):
    col_pts = f"{mes}_Pontos"
    if col_pts in row and not pd.isna(row[col_pts]) and str(row[col_pts]).strip() != "":
        try:
            return int(float(row[col_pts]))
        except:
            pass
            
    soma = 0
    for crit in ["C1", "C2", "C3", "C4", "C5"]:
        col_c = f"{mes}_{crit}"
        if col_c in row and not pd.isna(row[col_c]):
            val = str(row[col_c]).strip().lower()
            if val in ["true", "1", "1.0", "sim", "checked"]:
                soma += 1
    return soma

def converter_pontos_em_nota(pts):
    if pts >= 5: return "A"
    elif pts == 4: return "A"
    elif pts == 3: return "B"
    elif pts == 2: return "C"
    elif pts == 1: return "D"
    return "E"

def obter_notas_linha(row):
    notas = {}
    for m in MESES:
        pts = calcular_pontos_linha_mes(row, m)
        notas[m] = converter_pontos_em_nota(pts)
    return notas

def calcular_ranking_regras(row):
    notas_por_mes = obter_notas_linha(row)
    
    votos_reais = 0
    for m in MESES:
        if calcular_pontos_line_mes_existe(row, m):
            votos_reais += 1
            
    rank_atual = "E"
    manter_sempre_A = True
    algum_voto = False
    
    for i in range(0, 12, 2):
        m1 = MESES[i]
        m2 = MESES[i+1]
        n1 = notas_por_mes[m1]
        n2 = notas_por_mes[m2]
        
        if calcular_pontos_linha_mes(row, m1) > 0 or calcular_pontos_linha_mes(row, m2) > 0 or calcular_pontos_line_mes_existe(row, m1) or calcular_pontos_line_mes_existe(row, m2):
            algum_voto = True
            if n1 != "A" or n2 != "A":
                manter_sempre_A = False
                
            idx1 = ORDEM_RANKING.index(n1)
            idx2 = ORDEM_RANKING.index(n2)
            
            if n1 == n2:
                rank_atual = n1
            elif idx1 > idx2:
                rank_atual = n2
            elif idx1 < idx2:
                rank_atual = n2

    if not algum_voto:
        return "E"
    if manter_sempre_A and votos_reais >= 1:
        return "A" if votos_reais < 12 else "A+"
    return rank_atual

def calcular_pontos_line_mes_existe(row, mes):
    for j in ["C1", "C2", "C3", "C4", "C5", "Pontos"]:
        if f"{mes}_{j}" in row and not pd.isna(row[f"{mes}_{j}"]) and str(row[f"{mes}_{j}"]).strip() != "":
            return True
    return False

@st.cache_data(ttl=1)
def carregar_dados():
    try:
        df = pd.read_csv(URL_LEITURA)
        if df.empty:
            return pd.DataFrame()
        # Normalização forçada: Define a 1ª coluna da planilha com o nome padrão
        df.rename(columns={df.columns[0]: "Paróquia / Instituição"}, inplace=True)
        df["Paróquia / Instituição"] = df["Paróquia / Instituição"].astype(str).str.strip()
        return df
    except Exception:
        return pd.DataFrame()

df_atual = carregar_dados()

col_form, col_ranking = st.columns([1.1, 1.4])

with col_form:
    st.subheader("📝 Votação Mensal Coletiva")
    mes_selecionado = st.selectbox("Selecione o Mês da Avaliação:", MESES)
    paroquia_selecionada = st.selectbox("Selecione a Paróquia:", LISTA_PAROQUIAS)
    
    v1 = v2 = v3 = v4 = v5 = False
    if not df_atual.empty and "Paróquia / Instituição" in df_atual.columns:
        filtro = df_atual[df_atual["Paróquia / Instituição"] == paroquia_selecionada.strip()]
        if len(filtro) > 0:
            row_p = filtro.iloc[0]
            def ler_c(c_nome):
                val = str(row_p.get(f"{mes_selecionado}_{c_nome}", "False")).strip().lower()
                return val in ["true", "1", "1.0", "sim", "checked"]
            v1 = ler_c("C1")
            v2 = ler_c("C2")
            v3 = ler_c("C3")
            v4 = ler_c("C4")
            v5 = ler_c("C5")
        
    c1 = st.checkbox("1° Saldo em conformidade", value=v1, key="c1")
    c2 = st.checkbox("2° Anexos em dia", value=v2, key="c2")
    c3 = st.checkbox("3° MPM em dia", value=v3, key="c3")
    c4 = st.checkbox("4° Arquivamento físico em dia", value=v4, key="c4")
    c5 = st.checkbox("5° Tudo pronto até o quinto dia útil", value=v5, key="c5")
    
    if st.button("Salvar Avaliação Mensal", use_container_width=True):
        nova_pontuacao = sum([c1, c2, c3, c4, c5])
        payload = {
            "paroquia": paroquia_selecionada,
            "mes": mes_selecionado,
            "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5,
            "pontos": int(nova_pontuacao),
            "ranking": converter_pontos_em_nota(nova_pontuacao)
        }
        with st.spinner("Computando voto mensal..."):
            try:
                resposta = requests.post(URL_GRAVACAO, data=json.dumps(payload))
                if "Sucesso" in resposta.text:
                    st.success(f"Voto de {mes_selecionado} gravado com sucesso!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Erro no painel do Google: {resposta.text}")
            except Exception:
                st.error("Erro na conexão com o servidor da nuvem.")

with col_ranking:
    st.subheader("📊 Placar Geral Acumulado 2026")
    
    df_exibicao = pd.DataFrame({"Paróquia / Instituição": LISTA_PAROQUIAS})
    df_exibicao["Paróquia / Instituição"] = df_exibicao["Paróquia / Instituição"].str.strip()
    
    if not df_atual.empty:
        df_exibicao = df_exibicao.merge(df_atual, on="Paróquia / Instituição", how="left")
    
    df_exibicao["Ranking_Calculado"] = df_exibicao.apply(calcular_ranking_regras, axis=1)
    df_exibicao["Ranking_Calculado"] = df_exibicao["Ranking_Calculado"].fillna("E")
    
    for m in MESES:
        df_exibicao[m] = df_exibicao.apply(lambda r: obter_notas_linha(r)[m], axis=1)
        
    df_exibicao["_ordem"] = df_exibicao["Ranking_Calculado"].apply(lambda x: ORDEM_RANKING.index(x))
    df_ordenado = df_exibicao.sort_values(by=["_ordem", "Paróquia / Instituição"], ascending=[False, True])
    
    colunas_visiveis = ["Paróquia / Instituição", "Ranking_Calculado"] + MESES
    
    st.dataframe(
        df_ordenado[colunas_visiveis],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Paróquia / Instituição": st.column_config.TextColumn("Paróquia / Instituição", width="medium"),
            "Ranking_Calculado": st.column_config.TextColumn("Rank Geral 🏆", width="small"),
            "Janeiro": st.column_config.TextColumn("Jan"), "Fevereiro": st.column_config.TextColumn("Fev"),
            "Março": st.column_config.TextColumn("Mar"), "Abril": st.column_config.TextColumn("Abr"),
            "Maio": st.column_config.TextColumn("Mai"), "Junho": st.column_config.TextColumn("Jun"),
            "Julho": st.column_config.TextColumn("Jul"), "Agosto": st.column_config.TextColumn("Ago"),
            "Setembro": st.column_config.TextColumn("Set"), "Outubro": st.column_config.TextColumn("Out"),
            "Novembro": st.column_config.TextColumn("Nov"), "Dezembro": st.column_config.TextColumn("Dez"),
        }
    )
