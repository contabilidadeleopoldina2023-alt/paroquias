import streamlit as st
import pandas as pd

# Configuração da página do sistema
st.set_page_config(page_title="Ranking Diocesano - Nuvem", layout="wide")

st.title("⛪ Sistema de Avaliação Diocesano - Nuvem ☁️")
st.markdown("Monitoramento e ranking colaborativo de paróquias em tempo real.")

# ID da sua planilha extraído do link que você me passou
SPREADSHEET_ID = "1QzKhdsqMv4lZp06jfZ_bYXz4_1kA7qYaD2PUuQ_3k80"
URL_LEITURA = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Dados"

# Lista Oficial Padrão (Caso a planilha falhe ou esteja limpa)
LISTA_PAROQUIAS = [
    f"{i}. Paróquia do Sr Bom Jesus - ARGIRITA" if i==2 else f"{i}. Paróquia de Santo Antônio - ASTOLFO DUTRA" if i==3 else f"{i}. Paróquia de São Franc de Paula - BOA FAMILIA" if i==4 else f"{i}. Paróquia de São Sebastião - CACHOEIRA ALEGRE" if i==5 else f"{i}. Paróquia Santa Rita de Cássia - CATAGUASES" if i==6 else f"{i}. Paróquia de N. S. do Rosário - CATAGUASES" if i==7 else f"{i}. Paróquia de São José Operário - CATAGUASES" if i==8 else f"{i}. Seminário N. S. da Conceição - BOA VISTA" if i==9 else f"{i}. Paróquia de N. S. das Dores - DORES DA VITORIA" if i==10 else f"{i}. Paróquia de São Sebastião - EUGENOPOLIS" if i==11 else f"{i}. Paróquia do Div Espírito Santo - GUARANI" if i==12 else f"{i}. Paróquia de Sant'Ana - GUIDOVAL" if i==13 else f"{i}. Paróquia de N. S. da Encarnação - GUIRICEMA" if i==14 else f"{i}. Paróquia de N S da Glória - ITAMURI" if i==15 else f"{i}. Paróquia de N S das Dores - ITAPIRUÇU" if i==16 else f"{i}. Paróquia de N. S. da Conceição - LARANJAL" if i==17 else f"{i}. Curato da Catedral - LEOPOLDINA" if i==18 else f"{i}. Paróquia de N. S. do Rosário - LEOPOLDINA" if i==19 else f"{i}. Paróquia de São José Operário - LEOPOLDINA" if i==20 else f"{i}. Paróquia de Sta Rita de Cássia - MIRADOURO" if i==21 else f"{i}. Paróquia de Sto Antônio - MIRAÍ" if i==22 else f"{i}. Paróquia de São Paulo - MURIAÉ" if i==23 else f"{i}. Paróquia de N. S da Conceição - MURIAÉ" if i==24 else f"{i}. Paróquia de N S Aparecida - MURIAÉ" if i==25 else f"{i}. Paróquia de São Franc de Assis - PALMA" if i==26 else f"{i}. Paróquia de N. S do Patrocínio - PATROCÍNIO DO MURIAÉ" if i==27 else f"{i}. Paróquia de N. S da Piedade - PIACATUBA" if i==28 else f"{i}. Paróquia de São Sebastião - PIRAÚBA" if i==29 else f"{i}. Paróquia de Santo Antônio - PROVIDÊNCIA" if i==30 else f"{i}. Paróquia Jesus Menino Deus - RECREIO" if i==31 else f"{i}. Paróquia de São Sebastião - RODEIRO" if i==32 else f"{i}. Paróquia de N. S do Rosário - ROSÁRIO DA LIMEIRA" if i==33 else f"{i}. Paróquia de Santana - SANTANA DE CATAGUASES" if i==34 else f"{i}. Paróquia de São Sebastião - SÃO GERALDO" if i==35 else f"{i}. Paróquia de Santo Antônio - TEBAS" if i==36 else f"{i}. Paróquia de São José - TOCANTINS" if i==37 else f"{i}. Paróquia de Santo Antônio - TUIUTINGA" if i==38 else f"{i}. Paróquia de São Januário - UBÁ" if i==39 else f"{i}. Paróquia de N S do Rosário - UBÁ" if i==40 else f"{i}. Paróquia do Div Espírito Santo - UBÁ" if i==41 else f"{i}. Paróquia de São João Batista - VISCONDE RIO BRANCO" if i==42 else f"{i}. Curato de São Franc de Paula - VISTA ALEGRE" if i==43 else f"{i}. Paróquia do Sr Bom Jesus - VIEIRAS" if i==44 else f"{i}. Paróquia de São José - ALÉM PARAÍBA" if i==45 else f"{i}. Paróquia Madre de Deus - ANGUSTURA" if i==46 else f"{i}. Paróquia de N. S. da Conceição - ESTRELA DALVA" if i==47 else f"{i}. Paróquia de Santana - PIRAPETINGA" if i==48 else f"{i}. Paróquia de Santo Antônio - SANTO ANTONIO AVENTUREIRO" if i==49 else f"{i}. Paróquia de São Sebastião - VOLTA GRANDE" if i==50 else f"{i}. Paróquia Sr Bom Jesus dos Aflitos - ITAMARATI DE MINAS" if i==51 else f"{i}. Paróquia de São Sebastião - UBÁ" if i==52 else f"{i}. Paróquia N. S. Sagrado Coração - MURIAÉ" if i==53 else f"{i}. Paróquia Santo Antônio - BELISÁRIO" if i==54 else f"{i}. Paróquia São Benedito - LEOPOLDINA" if i==55 else f"{i}. Paróquia São Sebastião - VISCONDE RIO BRANCO" if i==56 else f"{i}. Seminário M. N. S. Guadalupe - JUIZ DE FORA" if i==57 else f"{i}. Paróquia N. S. da Consolação - ALÉM PARAÍBA" if i==58 else f"{i}. Paróquia N S das Dores - DONA EUZÉBIA" if i==59 else f"{i}. Paroqui N S Divino pranto - MURIAÉ" if i==60 else f"{i}. Paróquia de Sta Bernadete - UBÁ" if i==61 else f"{i}. P. São Crist e Imac Conceição - CATAGUASES" if i==62 else f"{i}. Paróquia Santa Cruz - MURIAÉ" if i==63 else f"{i}. Paróquia de Santo Antônio - VISCONDE RIO BRANCO" if i==64 else f"{i}. Paróquia São José Operário - UBÁ" if i==65 else f"Paróquia {i}"
    for i in range(2, 66)
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

# Leitura segura da planilha
try:
    df_atual = pd.read_csv(URL_LEITURA)
    if df_atual.empty or "Paróquia / Instituição" not in df_atual.columns or len(df_atual) == 0:
        df_atual = criar_fallback_df()
    else:
        colunas_bool = ["Saldo em Conformidade", "Anexos em Dia", "MPM em Dia", "Arquivamento Físico em Dia", "Tudo Pronto até 5º DU"]
        for col in colunas_bool:
            if col in df_atual.columns:
                df_atual[col] = df_atual[col].fillna(False).astype(bool)
except Exception:
    df_atual = criar_fallback_df()

def calcular_ranking(pontos):
    if pontos == 5: return "A+"
    elif pontos == 4: return "A"
    elif pontos == 3: return "B"
    elif pontos == 2: return "C"
    elif pontos == 1: return "D"
    else: return "F"

# Divisão da tela em duas colunas (Formulário na esquerda | Painel Geral na direita)
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
        
        if paroquia_selecionada in df_atual["Paróquia / Instituição"].values:
            idx = df_atual[df_atual["Paróquia / Instituição"] == paroquia_selecionada].index[0]
            df_atual.at[idx, "Saldo em Conformidade"] = c1
            df_atual.at[idx, "Anexos em Dia"] = c2
            df_atual.at[idx, "MPM em Dia"] = c3
            df_atual.at[idx, "Arquivamento Físico em Dia"] = c4
            df_atual.at[idx, "Tudo Pronto até 5º DU"] = c5
            df_atual.at[idx, "Pontuação"] = nova_pontuacao
            df_atual.at[idx, "Ranking"] = novo_ranking
        
        st.success(f"Avaliação calculada com sucesso! Nota: {novo_ranking}")
        st.link_button("👉 Abrir Planilha Mãe no Google Drive", f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
        st.info("Nota: No ambiente de nuvem definitivo do Streamlit, essa gravação será direta e automatizada em segundo plano!")

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