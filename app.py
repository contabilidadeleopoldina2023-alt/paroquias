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

def converter_pontos_em_nota(pontos):
    try:
        pts = int(float(pontos))
    except:
        pts = 0
    if pts >= 5: return "A"
    elif pts == 4: return "A"
    elif pts == 3: return "B"
    elif pts == 2: return "C"
    elif pts == 1: return "D"
    return "E"

def calcular_ranking_regras(row):
    notas_por_mes = []
    votos_computados = 0
    
    for m in MESES:
        col = f"{m}_Pontos"
        if col in row and not pd.isna(row[col]) and str(row[col]).strip() != "":
            nota = converter_pontos_em_nota(row[col])
            notas_por_mes.append(nota)
            votos_computados += 1
        else:
            notas_por_mes.append("E")
            
    if votos_computados == 0:
        return "E"
        
    rank_atual = "E"
    manter_sempre_A = True
    
    for i in range(0, 12, 2):
        n1 = notas_por_mes[i]
        n2 = notas_por_mes[i+1]
        
        # Só interfere na nota se pelo menos um dos meses do bimestre tiver sido preenchido
        if i < votos_computados or (i+1) < votos_computados:
            if n1 != "A" or n2 != "A":
                manter_sempre_A = False
                
            idx1 = ORDEM_RANKING.index(n1)
            idx2 = ORDEM_RANKING.index(n2)
            
            if n1 == n2:
                rank_atual = n1
            elif idx1 > idx2:
                rank_atual = n2 # Caiu no segundo mês
            elif idx1 < idx2:
                rank_atual = n2 # Subiu no segundo mês
                
    if manter_sempre_A and votos_computados >= 1:
        # Se os meses avaliados até aqui forem todos A, já exibe como A provisório/definitivo
        return "A" if votos_computados < 12 else "A+"
        
    return rank_atual

def criar_fallback_df():
    df = pd.DataFrame({"Paróquia / Instituição": LISTA_PAROQUIAS})
    for m in MESES:
        df[f"{m}_Pontos"] = 0
    return df

@st.cache_data(ttl=1)
def carregar_dados():
    try:
        df = pd.read_csv(URL_LEITURA)
        if df.empty or "Paróquia / Instituição" not in df.columns:
            return criar_fallback_df()
        
        # Se a paróquia existir mas faltarem colunas de meses no CSV, cria elas vazias
        for m in MESES:
            if f"{m}_Pontos" not in df.columns:
                df[f"{m}_Pontos"] = 0
        return df
    except Exception:
        return criar_fallback_df()

df
