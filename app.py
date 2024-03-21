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
        if not identificacao_emitente_match:
            # Tenta uma alternativa comum de como a identificação pode ser apresentada
            identificacao_emitente_match = re.search(r"Identificação do Emitente[\s\S]*?(\n.+)", texto)
        identificacao_emitente = identificacao_emitente_match.group(1).strip() if identificacao_emitente_match else "Não encontrado"

        # FATURA / DUPLICATA
        # Ajusta para capturar também casos onde o valor está em uma linha separada do vencimento
        faturas_matches = re.findall(r"Nº\s+\d+\s+Venc.\s+(\d{2}/\d{2}/\d{2})\s+Vl.\s+([\d.]+)", texto)
        for data, valor in faturas_matches:
            valor_formatado = valor.replace(".", "").replace(",", ".")
            dados_faturas.append({
                "IDENTIFICAÇÃO DO EMITENTE": identificacao_emitente,
                "Data da fatura": data,
                "Valor": valor_formatado
            })

        # Se não encontrar FATURA / DUPLICATA, procura DATA DE EMISSÃO e VALOR TOTAL DA NOTA
        if not dados_faturas:
            data_emissao_match = re.search(r"DATA DA EMISSÃO\s*?(\d{2}/\d{2}/\d{4})", texto)
            data_emissao = data_emissao_match.group(1) if data_emissao_match else "Não disponível"
            
            valor_total_nota_match = re.search(r"VALOR TOTAL DA NOTA\s*R\$\s*([\d.]+,\d{2})", texto)
            if valor_total_nota_match:
                valor_total = valor_total_nota_match.group(1).replace(".", "").replace(",", ".")
                dados_faturas.append({
                    "IDENTIFICAÇÃO DO EMITENTE": identificacao_emitente,
                    "Data da fatura": data_emissao,
                    "Valor": valor_total
                })

    return pd.DataFrame(dados_faturas)

# Código Streamlit para upload de arquivos e exibição de resultados
uploaded_files = st.file_uploader("Escolha os arquivos PDF", accept_multiple_files=True, type='pdf')
if uploaded_files:
    dataframe_final = pd.DataFrame()
    for uploaded_file in uploaded_files:
        df_temp = extrair_informacoes(uploaded_file)
        dataframe_final = pd.concat([dataframe_final, df_temp], ignore_index=True)

    if not dataframe_final.empty:
        st.write(dataframe_final)
    else:
        st.error("Não foi possível extrair informações dos arquivos. Verifique o formato dos PDFs.")
