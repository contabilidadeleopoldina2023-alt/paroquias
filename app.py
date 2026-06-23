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
    "48. Paróquia de Santana - PIRAPETINGA",
