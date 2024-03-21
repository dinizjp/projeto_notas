import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import base64
from io import BytesIO
import openpyxl

def processar_pdf(arquivo):
    dados_faturas = []
    doc = fitz.open(stream=arquivo.read(), filetype="pdf")
    
    for pagina in doc:
        texto = pagina.get_text()
        # Inclua aqui sua lógica de processamento de texto extraído
        
        # Exemplo simplificado de adição de dados ao DataFrame
        dados_faturas.append({"IDENTIFICAÇÃO DO EMITENTE": "Exemplo Emitente", "Valor": "100.00"})
    
    return pd.DataFrame(dados_faturas)

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Gera um link para download do DataFrame como um arquivo Excel."""
    val = to_excel(df)
    b64 = base64.b64encode(val).decode()  # Transforma bytes em base64 (string)
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="extracao.xlsx">Download Excel</a>'
    return href

st.title('Extrator de Notas Fiscais')

uploaded_files = st.file_uploader("Escolha os arquivos PDF", accept_multiple_files=True, type='pdf')
if uploaded_files:
    dataframe_final = pd.DataFrame()
    for uploaded_file in uploaded_files:
        df_temp = processar_pdf(uploaded_file)
        dataframe_final = pd.concat([dataframe_final, df_temp], ignore_index=True)

    st.write(dataframe_final)

    st.markdown(get_table_download_link(dataframe_final), unsafe_allow_html=True)
