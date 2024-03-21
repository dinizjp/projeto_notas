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
        # Aqui você insere a lógica de processamento do PDF, como feito anteriormente
        # Exemplo básico:
        identificacao_emitente_match = re.search(r"IDENTIFICAÇÃO DO EMITENTE[\s\S]*?(\n.+)", texto)
        identificacao_emitente = identificacao_emitente_match.group(1).strip() if identificacao_emitente_match else "Não encontrado"
        
        valor_total_nota_match = re.search(r"VALOR TOTAL DA NOTA[\s\S]*?R\$ ([\d.]*\,?\d*)", texto)
        valor_total = valor_total_nota_match.group(1).replace(".", "").replace(",", ".") if valor_total_nota_match else "0.00"
        
        # Apenas um exemplo de dado adicionado
        dados_faturas.append({"IDENTIFICAÇÃO DO EMITENTE": identificacao_emitente, "Valor": valor_total})
    
    return pd.DataFrame(dados_faturas)

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    val = to_excel(df)
    b64 = base64.b64encode(val).decode()  # Valores codificados em base64
    return f'<a href="data:application/octet-stream;base64,{b64}" download="extracao.xlsx">Download do arquivo Excel</a>'

st.title('Extrator de Notas Fiscais')

uploaded_files = st.file_uploader("Escolha os arquivos PDF", accept_multiple_files=True, type='pdf')
if uploaded_files:
    dataframe_final = pd.DataFrame()
    for uploaded_file in uploaded_files:
        df_temp = processar_pdf(uploaded_file)
        dataframe_final = pd.concat([dataframe_final, df_temp], ignore_index=True)

    st.write(dataframe_final)

    st.markdown(get_table_download_link(dataframe_final), unsafe_allow_html=True)
