import streamlit as st
import pandas as pd
import requests
import json
import re
import math
import time
import hashlib
import hmac
import secrets
import logging
from io import StringIO

# Configuração estrita de Logs internos
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ranking Diocesano 2026", layout="wide")

st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🏆 Ranking das Paróquias 2026")
st.markdown("Monitoramento anual contínuo com consolidação de média progressiva bimestral.")

# --- VALIDAÇÃO DE SEGURANÇA ---
REQUISITOS = ["SPREADSHEET_ID", "URL_GRAVACAO", "ADMIN_PASSWORD_HASH", "API_SECRET_KEY"]
FALTANTES = [req for req in REQUISITOS if req not in st.secrets]

if FALTANTES:
    st.error("🔒 Erro de Configuração: O ambiente não está operando em conformidade com as diretrizes de segurança.")
    logging.critical(f"Segredos ausentes no st.secrets: {FALTANTES}")
    st.stop()

SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
URL_GRAVACAO = st.secrets["URL_GRAVACAO"]
ADMIN_PASSWORD_HASH = st.secrets["ADMIN_PASSWORD_HASH"]
API_SECRET_KEY = st.secrets["API_SECRET_KEY"].encode('utf-8')

URL_LEITURA = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"

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
    "A+": "👑 A+", "A": "🟢 A", "B": "🔵 B", "C": "🟡 C", "D": "🟠 D", "E": "🔴 E", "-": "⚪ -"
}

# --- FUNÇÕES DE SEGURANÇA E TRATAMENTO ---
def verificar_senha(senha_candidata):
    senha_limpa = str(senha_candidata).strip()
    senha_hash = hashlib.sha256(senha_limpa.encode('utf-8')).hexdigest()
    hash_esperado = str(ADMIN_PASSWORD_HASH).strip()
    return hmac.compare_digest(senha_hash, hash_esperado)

def gerar_token_assinatura(payload_dict):
    mensagem = json.dumps(payload_dict, sort_keys=True).encode('utf-8')
    return hmac.new(API_SECRET_KEY, mensagem, hashlib.sha256).hexdigest()

def limpar_texto(txt):
    if pd.isna(txt): return ""
    txt = str(txt).strip().lower()
    txt = re.sub(r'^\d+[\s\.\-\–\_]+', '', txt)
    txt = re.sub(r'[^a-z0-9áéíóúâêôçãõ]', '', txt)
    return txt

def converter_pontos_em_nota(val_str):
    """Mapeia pontuações de 0 a 5 para as respectivas notas de E a A+."""
    try:
        p = int(float(str(val_str).strip()))
        if p >= 5: return "A+"
        elif p == 4: return "A"
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
        
        # Se nenhum mês do bimestre foi avaliado, pula o bimestre
        if nota1 == "" and nota2 == "":
            continue
        
        # Se apenas 1 mês foi avaliado, considera a nota desse único mês
        if nota1 != "" and nota2 == "":
            nota_do_bimestre = nota1
        elif nota1 == "" and nota2 != "":
            nota_do_bimestre = nota2
        else:
            idx1 = ORDEM_RANKING.index(nota1)
            idx2 = ORDEM_RANKING.index(nota2)
            nota_do_bimestre = nota1 if idx1 <= idx2 else nota2

        pesos_bimestres.append(ORDEM_RANKING.index(nota_do_bimestre))
        
    if not pesos_bimestres: return "E"
        
    media_pesos = sum(pesos_bimestres) / len(pesos_bimestres)
    idx_final = math.floor(media_pesos + 0.5)
    idx_final = max(0, min(idx_final, len(ORDEM_RANKING) - 1))
    return ORDEM_RANKING[idx_final]

@st.cache_data(ttl=60)
def carregar_dados_da_nuvem(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return pd.DataFrame()
            
        df = pd.read_csv(StringIO(res.text), dtype=str)
        if df.empty: return pd.DataFrame()
        
        orig_col = df.columns[0]
        df.rename(columns={orig_col: "Paróquia_Original"}, inplace=True)
        df["Chave_Limpa"] = df["Paróquia_Original"].apply(limpar_texto)
        
        # Remove duplicatas para evitar multiplicações de linhas no merge
        df = df.drop_duplicates(subset=["Chave_Limpa"], keep="last")
        return df
    except Exception as e:
        logging.error(f"Falha ao carregar dados externos: {str(e)}")
        return pd.DataFrame()

# Inicialização de Session State
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "limpar_voto" not in st.session_state:
    st.session_state["limpar_voto"] = False

df_atual = carregar_dados_da_nuvem(URL_LEITURA)

# --- LAYOUT DO APP ---
col_form, col_ranking = st.columns([1.1, 1.4])

with col_form:
    st.subheader("📝 Votação Mensal")
    
    if not st.session_state["autenticado"]:
        with st.form("form_login"):
            senha_input = st.text_input("Insira a senha de administrador para votar:", type="password")
            botao_liberar = st.form_submit_button("Liberar Painel", use_container_width=True)
            
            if botao_liberar:
                if verificar_senha(senha_input):
                    st.session_state["autenticado"] = True
                    st.success("Acesso liberado!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Verifique a senha inserida.")
                    logging.warning("Tentativa falha de login administrativo interceptada.")
    else:
        st.info("🔓 Modo Administrador Ativo")
        if st.button("Sair/Bloquear"):
            st.session_state["autenticado"] = False
            st.rerun()
            
        st.divider()
        
        mes_selecionado = st.selectbox("Selecione o Mês da Avaliação:", MESES)
        paroquia_selecionada = st.selectbox("Selecione a Paróquia:", LISTA_PAROQUIAS)
        
        if st.session_state["limpar_voto"]:
            for key in ["c1", "c2", "c3", "c4", "c5"]:
                st.session_state[key] = False
            st.session_state["limpar_voto"] = False

        c1 = st.checkbox("1° Saldo em conformidade", key="c1")
        c2 = st.checkbox("2° Anexos em dia", key="c2")
        c3 = st.checkbox("3° MPM em dia", key="c3")
        c4 = st.checkbox("4° Arquivamento físico em dia", key="c4")
        c5 = st.checkbox("5° Tudo pronto até o quinto dia útil", key="c5")
        
        if st.button("Salvar Avaliação Mensal", use_container_width=True):
            nova_pontuacao = sum([c1, c2, c3, c4, c5])
            nota_mes = converter_pontos_em_nota(nova_pontuacao)
            
            dados_base = {
                "mes": str(mes_selecionado),
                "nonce": secrets.token_hex(16),
                "paroquia": str(paroquia_selecionada), 
                "pontos": int(nova_pontuacao), 
                "ranking": str(nota_mes),
                "timestamp": int(time.time())
            }
            
            assinatura = gerar_token_assinatura(dados_base)
            
            payload = {
                "dados": dados_base,
                "assinatura_digital": assinatura
            }
            
            with st.spinner("Enviando dados sob canal criptografado..."):
                try:
                    headers = {'Content-Type': 'application/json', 'X-Requested-With': 'Streamlit App'}
                    resposta = requests.post(URL_GRAVACAO, data=json.dumps(payload), headers=headers, timeout=10)
                    
                    if resposta.status_code == 200 and ("sucesso" in resposta.text.lower() or "success" in resposta.text.lower()):
                        st.success("Avaliação enviada com sucesso!")
                        st.session_state["limpar_voto"] = True
                        st.cache_data.clear()
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error("A requisição foi recusada pelo servidor remoto devido a uma falha de integridade ou validação.")
                        logging.error(f"Erro na API Remota. Status: {resposta.status_code}. Resposta: {resposta.text}")
                except Exception as e:
                    st.error("Falha temporária de rede. Tente novamente mais tarde.")
                    logging.error(f"Exceção capturada no tráfego de saída: {str(e)}")

with col_ranking:
    st.subheader(f"🏆 Placar Geral Anual - {len(LISTA_PAROQUIAS)} Paróquias")
    
    df_exibicao = pd.DataFrame({"Paróquia / Instituição": LISTA_PAROQUIAS})
    df_exibicao["Chave_Limpa"] = df_exibicao["Paróquia / Instituição"].apply(limpar_texto)
    
    if not df_atual.empty and "Chave_Limpa" in df_atual.columns:
        df_exibicao = df_exibicao.merge(df_atual, on="Chave_Limpa", how="left")
    
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
