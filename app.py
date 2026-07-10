import streamlit as st
import pandas as pd
import requests
import json
import re
import math
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ranking Diocesano 2026", layout="wide")

st.title("🏆 Ranking das Paróquias 2026")
st.markdown("Monitoramento anual contínuo com consolidação de média progressiva bimestral.")

# --- VALIDAÇÃO DE SEGURANÇA (Vindos do st.secrets) ---
REQUISITOS = ["SPREADSHEET_ID", "URL_GRAVACAO", "ADMIN_PASSWORD", "API_TOKEN"]
FALTANTES = [req for req in REQUISITOS if req not in st.secrets]

if FALTANTES:
    st.error(f"🔒 Erro de Configuração: As credenciais de produção não foram detectadas ({', '.join(FALTANTES)}).")
    st.stop()

SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
URL_GRAVACAO = st.secrets["URL_GRAVACAO"]
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
API_TOKEN = st.secrets["API_TOKEN"]

# URL de Leitura com timestamp para evitar cache do Google Sheets
URL_LEITURA = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&v={int(time.time())}"

# --- LISTA OFICIAL DE PARÓQUIAS (64 itens) ---
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

MAPA_EMOJIS = {
    "A+": "👑 A+",
    "A": "🟢 A",
    "B": "🔵 B",
    "C": "🟡 C",
    "D": "🟠 D",
    "E": "🔴 E",
    "-": "⚪ -"
}

# --- FUNÇÕES DE TRATAMENTO ---
def limpar_texto(txt):
    if pd.isna(txt): return ""
    txt = str(txt).strip().lower()
    txt = re.sub(r'^\d+[\s\.\-\–\_]+', '', txt)
    txt = re.sub(r'[^a-z0-9áéíóúâêôçãõ]', '', txt)
    return txt

def converter_pontos_em_nota(val_str):
    try:
        p = int(float(str(val_str).strip()))
        if p >= 4: return "A"
        elif p == 3: return "B"
        elif p == 2: return "C"
        elif p == 1: return "D"
    except (ValueError, TypeError):
        pass
    return "E"

def obter_nota_mes_planilha(row, mes):
    col_rank = f"{mes}_Ranking"
    if col_rank in row.index and not pd.isna(row[col_rank]):
        val = str(row[col_rank]).strip().upper()
        if val in ORDEM_RANKING: return val
        if val.isdigit(): return converter_pontos_em_nota(val)

    col_pontos = f"{mes}_Pontos"
    if col_pontos in row.index and not pd.isna(row[col_pontos]):
        val_pts = str(row[col_pontos]).strip()
        if val_pts.upper() not in ["TRUE", "FALSE", ""]:
            return converter_pontos_em_nota(val_pts)
            
    return ""

def calcular_ranking_justo_bimestral(row):
    pesos_bimestres = []
    for i in range(0, 12, 2):
        m1, m2 = MESES[i], MESES[i+1]
        nota1 = obter_nota_mes_planilha(row, m1)
        nota2 = obter_nota_mes_planilha(row, m2)
        
        if nota1 == "" and nota2 == "": continue
            
        n1_valid = nota1 if nota1 != "" else "E"
        n2_valid = nota2 if nota2 != "" else "E"
        
        idx1 = ORDEM_RANKING.index(n1_valid)
        idx2 = ORDEM_RANKING.index(n2_valid)
        
        # Mantém a regra conservadora (menor nota do bimestre prevalece)
        nota_do_bimestre = n1_valid if idx1 <= idx2 else n2_valid
        pesos_bimestres.append(ORDEM_RANKING.index(nota_do_bimestre))
        
    if not pesos_bimestres: return "E"
        
    media_pesos = sum(pesos_bimestres) / len(pesos_bimestres)
    idx_final = math.floor(media_pesos + 0.5)
    idx_final = max(0, min(idx_final, len(ORDEM_RANKING) - 1))
    return ORDEM_RANKING[idx_final]

@st.cache_data(ttl=60)
def carregar_dados_da_nuvem(url):
    try:
        df = pd.read_csv(url, dtype=str)
        if df.empty: return pd.DataFrame()
        orig_col = df.columns[0]
        df.rename(columns={orig_col: "Paróquia_Original"}, inplace=True)
        df["Chave_Limpa"] = df["Paróquia_Original"].apply(limpar_texto)
        return df
    except Exception:
        return pd.DataFrame()

# Inicializações do Session State de segurança e controle
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "limpar_voto" not in st.session_state:
    st.session_state["limpar_voto"] = False

df_atual = carregar_dados_da_nuvem(URL_LEITURA)

# --- LAYOUT DO APP ---
col_form, col_ranking = st.columns([1.1, 1.4])

with col_form:
    st.subheader("📝 Votação Mensal")
    
    # Sistema Simples de Trava por Senha administrativa
    if not st.session_state["autenticado"]:
        senha_input = st.text_input("Insira a senha de administrador para votar:", type="password")
        if st.button("Liberar Painel"):
            if senha_input == ADMIN_PASSWORD:
                st.session_state["autenticado"] = True
                st.success("Acesso liberado!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Senha incorreta.")
    else:
        st.info("🔓 Modo Administrador Ativo")
        if st.button("Sair/Bloquear"):
            st.session_state["autenticado"] = False
            st.rerun()
            
        st.divider()
        
        mes_selecionado = st.selectbox("Selecione o Mês da Avaliação:", MESES)
        paroquia_selecionada = st.selectbox("Selecione a Paróquia:", LISTA_PAROQUIAS)
        
        if st.session_state["limpar_voto"]:
            st.session_state["c1"] = False
            st.session_state["c2"] = False
            st.session_state["c3"] = False
            st.session_state["c4"] = False
            st.session_state["c5"] = False
            st.session_state["limpar_voto"] = False

        c1 = st.checkbox("1° Saldo em conformidade", key="c1")
        c2 = st.checkbox("2° Anexos em dia", key="c2")
        c3 = st.checkbox("3° MPM em dia", key="c3")
        c4 = st.checkbox("4° Arquivamento físico em dia", key="c4")
        c5 = st.checkbox("5° Tudo pronto até o quinto dia útil", key="c5")
        
        if st.button("Salvar Avaliação Mensal", use_container_width=True):
            nova_pontuacao = sum([c1, c2, c3, c4, c5])
            nota_mes = converter_pontos_em_nota(nova_pontuacao)
            
            # Payload agora envia um TOKEN de autenticação que sua API externa deve validar
            payload = {
                "api_token": API_TOKEN, 
                "paroquia": paroquia_selecionada, 
                "mes": mes_selecionado,
                "pontos": int(nova_pontuacao), 
                "ranking": nota_mes
            }
            
            with st.spinner("Conectando com o Google Sheets de forma segura..."):
                try:
                    headers = {'Content-Type': 'application/json'}
                    resposta = requests.post(URL_GRAVACAO, data=json.dumps(payload), headers=headers, timeout=15)
                    
                    if resposta.status_code == 200 and ("Sucesso" in resposta.text or "sucesso" in resposta.text.lower()):
                        st.success(f"Avaliação de {mes_selecionado} enviada com sucesso!")
                        st.session_state["limpar_voto"] = True
                        st.cache_data.clear()
                        time.sleep(1.2)
                        st.rerun()
                    else:
                        st.error(f"Erro de validação ou processamento da API: {resposta.text}")
                except requests.exceptions.Timeout:
                    st.error("Erro: Tempo limite de conexão esgotado. A planilha demorou muito para responder.")
                except Exception as e:
                    st.error("Erro técnico crítico na comunicação de rede com o servidor.")

with col_ranking:
    st.subheader(f"🏆 Placar Geral Anual - {len(LISTA_PAROQUIAS)} Paróquias")
    
    df_exibicao = pd.DataFrame({"Paróquia / Instituição": LISTA_PAROQUIAS})
    df_exibicao["Chave_Limpa"] = df_exibicao["Paróquia / Instituição"].apply(limpar_texto)
    
    if not df_atual.empty and "Chave_Limpa" in df_atual.columns:
        df_exibicao = df_exibicao.merge(df_atual, on="Chave_Limpa", how="left")
        
        nao_encontradas = df_exibicao["Paróquia_Original"].isna().sum()
        if 0 < nao_encontradas < len(LISTA_PAROQUIAS):
            st.caption(f"ℹ️ {nao_encontradas} paróquia(s) ainda não possuem histórico computado na planilha.")
    
    for m in MESES:
        df_exibicao[m] = df_exibicao.apply(lambda r: obter_nota_mes_planilha(r, m), axis=1)
        
    df_exibicao["Ranking_Calculado"] = df_exibicao.apply(calcular_ranking_justo_bimestral, axis=1)
    
    df_visual = df_exibicao.copy()
    df_visual["_ordem"] = df_visual["Ranking_Calculado"].apply(lambda x: ORDEM_RANKING.index(x) if x in ORDEM_RANKING else 0)
    
    df_visual["Ranking_Calculado"] = df_visual["Ranking_Calculado"].map(MAPA_EMOJIS).fillna(MAPA_EMOJIS["E"])
    for m in MESES:
        df_visual[m] = df_visual[m].apply(lambda x: MAPA_EMOJIS[x] if x in MAPA_EMOJIS and x != "" else MAPA_EMOJIS["-"])
    
    df_ordenado = df_visual.sort_values(by=["_ordem", "Paróquia / Instituição"], ascending=[False, True])
    colunas_visiveis = ["Paróquia / Instituição", "Ranking_Calculado"] + MESES
    
    st.dataframe(
        df_ordenado[colunas_visiveis],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Paróquia / Instituição": st.column_config.TextColumn("Paróquia / Instituição", width="large"),
            "Ranking_Calculado": st.column_config.TextColumn("Rank Geral 🏆", width="small")
        }
    )
