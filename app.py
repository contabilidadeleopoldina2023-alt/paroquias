import math
import time

# Configuração da página
# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ranking Diocesano 2026", layout="wide")

st.title(" Ranking das Paróquias 2026 ")
st.title("🏆 Ranking das Paróquias 2026")
st.markdown("Monitoramento anual contínuo com consolidação de média progressiva bimestral.")

# --- SEGURANÇA E CONEXÕES (URLs Escondidas em st.secrets) ---
# Caso as chaves não existam no st.secrets, o app exibirá um aviso de segurança amigável e interromperá a execução.
if "SPREADSHEET_ID" not in st.secrets or "URL_GRAVACAO" not in st.secrets:
    st.error("🔒 Erro de Configuração: As credenciais de produção não foram detectadas no ambiente.")
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
@@ -86,7 +92,7 @@
        elif p == 3: return "B"
        elif p == 2: return "C"
        elif p == 1: return "D"
    except:
    except (ValueError, TypeError):
        pass
    return "E"

@@ -120,6 +126,7 @@
        idx1 = ORDEM_RANKING.index(n1_valid)
        idx2 = ORDEM_RANKING.index(n2_valid)

        # Mantém a regra conservadora (menor nota do bimestre prevalece)
        nota_do_bimestre = n1_valid if idx1 <= idx2 else n2_valid
        pesos_bimestres.append(ORDEM_RANKING.index(nota_do_bimestre))

@@ -142,6 +149,9 @@
    except Exception:
        return pd.DataFrame()

# Inicializações do Session State de segurança e controle
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "limpar_voto" not in st.session_state:
    st.session_state["limpar_voto"] = False

@@ -152,47 +162,73 @@

with col_form:
    st.subheader("📝 Votação Mensal")
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

        payload = {
            "paroquia": paroquia_selecionada, 
            "mes": mes_selecionado,
            "pontos": int(nova_pontuacao), 
            "ranking": nota_mes
        }
        mes_selecionado = st.selectbox("Selecione o Mês da Avaliação:", MESES)
        paroquia_selecionada = st.selectbox("Selecione a Paróquia:", LISTA_PAROQUIAS)

        with st.spinner("Conectando com o Google Sheets..."):
            try:
                resposta = requests.post(URL_GRAVACAO, data=json.dumps(payload), timeout=10)
                if "Sucesso" in resposta.text or "sucesso" in resposta.text.lower():
                    st.success(f"Avaliação de {mes_selecionado} enviada com sucesso!")
                    st.session_state["limpar_voto"] = True
                    st.cache_data.clear()
                    time.sleep(1.2)
                    st.rerun()
                else:
                    st.error(f"Erro de resposta da API do Google: {resposta.text}")
            except Exception as e:
                st.error("Erro técnico de rede na comunicação em nuvem.")
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
@@ -204,30 +240,30 @@
        df_exibicao = df_exibicao.merge(df_atual, on="Chave_Limpa", how="left")

        nao_encontradas = df_exibicao["Paróquia_Original"].isna().sum()
        if nao_encontradas > 0 and nao_encontradas < len(LISTA_PAROQUIAS):
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
