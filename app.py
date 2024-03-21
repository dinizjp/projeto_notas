import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import base64
from io import BytesIO
import openpyxl

def extrair_informacoes(arquivo):
    doc = fitz.open(stream=arquivo.read(), filetype="pdf")
    dados_faturas = []

    for pagina in doc:
        texto = pagina.get_text()

        # IDENTIFICAÇÃO DO EMITENTE
        identificacao_emitente_match = re.search(r"IDENTIFICAÇÃO DO EMITENTE[\s\S]*?(\n.+)", texto)
        identificacao_emitente = identificacao_emitente_match.group(1).strip() if identificacao_emitente_match else "Não encontrado"

        # Tentar extrair FATURA / DUPLICATA
        faturas_matches = re.findall(r"Vencimento:\s(\d{2}/\d{2}/\d{4})[\s\S]*?Valor:\sR\$\s([\d.]*\,\d{2})", texto)

        if faturas_matches:
            for data, valor in faturas_matches:
                valor_formatado = valor.replace(".", "").replace(",", ".")
                dados_faturas.append({
                    "IDENTIFICAÇÃO DO EMITENTE": identificacao_emitente,
                    "Data da fatura": data,
                    "Valor": valor_formatado
                })
        else:
            # Se não encontrar FATURA / DUPLICATA, procura DATA DE EMISSÃO e VALOR TOTAL DA NOTA
            data_emissao_match = re.search(r"DATA DE EMISSÃO[\s\S]*?(\d{2}/\d{2}/\d{4})", texto)
            data_emissao = data_emissao_match.group(1) if data_emissao_match else "Não disponível"
            
            valor_total_nota_match = re.search(r"VALOR TOTAL DA NOTA[\s\S]*?([\d.]+,\d{2})", texto)
            if valor_total_nota_match:
                valor_total = valor_total_nota_match.group(1).replace(".", "").replace(",", ".")
                dados_faturas.append({
                    "IDENTIFICAÇÃO DO EMITENTE": identificacao_emitente,
                    "Data da fatura": data_emissao,
                    "Valor": valor_total
                })

    return pd.DataFrame(dados_faturas)

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    val = to_excel(df)
    b64 = base64.b64encode(val).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="extracao.xlsx">Download Excel</a>'
    return href

st.title('Extrator de Notas Fiscais')

uploaded_files = st.file_uploader("Escolha os arquivos PDF", accept_multiple_files=True, type='pdf')
if uploaded_files:
    dataframe_final = pd.DataFrame()
    for uploaded_file in uploaded_files:
        df_temp = extrair_informacoes(uploaded_file)
        dataframe_final = pd.concat([dataframe_final, df_temp], ignore_index=True)

    st.write(dataframe_final)

    st.markdown(get_table_download_link(dataframe_final), unsafe_allow_html=True)
