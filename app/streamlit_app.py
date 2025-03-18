import streamlit as st
import fitz  # PyMuPDF
import time
import base64
import os
import boto3
import aux_functions
import prompts
import requests
import json
from dotenv import load_dotenv


load_dotenv()

aws_access_key_id = os.getenv('AMAZON_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AMAZON_SECRET_ACCESS_KEY')

bedrock_client = boto3.client(service_name='bedrock-runtime',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name="us-east-1")
s3_client = boto3.client('s3',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name='us-east-1')
bucket_name = os.getenv('BUCKET_NAME')

st.set_page_config(layout="centered")

st.title("Validación de Documentos")

# Inicializar variables de estado en session_state
if 'resultados' not in st.session_state:
    st.session_state.resultados = {
        'doc1': None,
        'doc2': None,
        'doc3': None,
        'doc4': None,
        'doc5': None,
        'doc6': None,
        'inadmissibility': None
    }

st.markdown("""
    <style>
    .stButton > button {
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover,
    .stButton > button:active,
    .stButton > button:focus {
        color: white !important;
        background-color: #0066cc !important;
        border-color: #0066cc !important;
        transform: scale(1.02);
        box-shadow: none !important;
        outline: none !important;
    }

    /* Eliminar el outline que aparece al hacer click */
    .stButton > button:focus:not(:focus-visible) {
        box-shadow: none !important;
        outline: none !important;
    }

    /* Asegurar que no cambie a rojo */
    .stButton > button:active {
        color: white !important;
        background-color: #0066cc !important;
        border-color: #0066cc !important;
    }
    </style>
""", unsafe_allow_html=True)

# Documento 1: Documento de Elevación
st.subheader("1. Documento de Elevación")
doc1 = st.file_uploader("Subir Documento de Elevación", type=['pdf'], key="doc1")
if st.button("Validar Documento de Elevación"):
    if doc1 is not None:
        pdf_elevation_images = aux_functions.get_pages(doc1)
        with st.spinner('Procesando documento...'):
            st.session_state.resultados['doc1'] = aux_functions.document_analyzer(bedrock_client,prompt_identify = prompts.prompt_elevation_identify, prompt_end_identify=prompts.prompt_elevation_end_identify,pdf_images=pdf_elevation_images)
    else:
        st.warning("Por favor, suba un documento primero")
if st.session_state.resultados['doc1']:
    st.write(f"{st.session_state.resultados['doc1']}")

# Documento 2: Recurso de Apelación
st.subheader("2. Recurso de Apelación")
doc2 = st.file_uploader("Subir Recurso de Apelación", type=['pdf'], key="doc2")
if st.button("Validar Recurso de Apelación"):
    if doc2 is not None:
        pdf_appeal_images = aux_functions.get_pages(doc2, factor_escala=2.0)
        with st.spinner('Procesando documento...'):
            st.session_state.resultados['doc2'] = aux_functions.document_analyzer(bedrock_client,prompt_identify = prompts.prompt_appeal_identify, prompt_end_identify = prompts.prompt_appeal_end_identify, prompt_analyze = prompts.prompt_appeal_analyze, pdf_images=pdf_appeal_images, batch_size = 5)
    else:
        st.warning("Por favor, suba un documento primero")
if st.session_state.resultados['doc2']:
    st.write(f"{st.session_state.resultados['doc2']}")

# Documento 3: Acto Impugnado
st.subheader("3. Acto Impugnado")
doc3 = st.file_uploader("Subir Acto Impugnado", type=['pdf'], key="doc3")
if st.button("Validar Acto Impugnado"):
    if doc3 is not None:
        pdf_challenged_images = aux_functions.get_pages(doc3)
        with st.spinner('Procesando documento...'):
            st.session_state.resultados['doc3'] = aux_functions.document_analyzer(bedrock_client,prompt_identify = prompts.prompt_challenged_identify, prompt_end_identify=prompts.prompt_challenged_end_identify, pdf_images=pdf_challenged_images)
    else:
        st.warning("Por favor, suba un documento primero")
if st.session_state.resultados['doc3']:
    st.write(f"{st.session_state.resultados['doc3']}")

# Documento 4: Cargo de Notificación
st.subheader("4. Cargo de Notificación del Acto Impugnado")
doc4 = st.file_uploader("Subir Cargo de Notificación", type=['pdf'], key="doc4")
if st.button("Validar Cargo de Notificación"):
    if doc4 is not None:
        pdf_notification_images = aux_functions.get_pages(doc4)
        with st.spinner('Procesando documento...'):
            st.session_state.resultados['doc4'] = aux_functions.document_analyzer(bedrock_client,prompt_identify=prompts.prompt_notification_identify,pdf_images=pdf_notification_images)
    else:
        st.warning("Por favor, suba un documento primero")
if st.session_state.resultados['doc4']:
    st.write(f"{st.session_state.resultados['doc4']}")

# Documento 5: Formato N°1
st.subheader("5. Formato N°1 del Administrado")
doc5 = st.file_uploader("Subir Formato N°1", type=['pdf'], key="doc5")
if st.button("Validar Formato N°1"):
    if doc5 is not None:
        pdf_format1_images = aux_functions.get_pages(doc5)
        with st.spinner('Procesando documento...'):
            st.session_state.resultados['doc5'] = aux_functions.document_analyzer(bedrock_client,prompt_identify=prompts.prompt_format1_identify, pdf_images = pdf_format1_images)
    else:
        st.warning("Por favor, suba un documento primero")
if st.session_state.resultados['doc5']:
    st.write(f"{st.session_state.resultados['doc5']}")

# Documento 6: Documentos Emitidos
st.subheader("6. Documentos Emitidos por la Entidad")
doc6 = st.file_uploader("Subir Documentos Emitidos por la Entidad", type=['pdf'], key="doc6")
if st.button("Validar Documentos Emitidos por la Entidad"):
    if doc6 is not None:
        st.warning("Documento Emitido por la Entidad subido con éxito!")
    else:
        st.warning("Por favor, suba el Documento Emitido por la Entidad")

# Botón para analizar documentos
st.subheader("----------------------------------------------------------------------------")
st.subheader("Causales de Improcedencia")
if st.button("Analizar Posibles Causales de Improcedencia"):
    start_time = time.time()
    documentos = [doc for doc in [doc1, doc2, doc3, doc4, doc5, doc6] if doc is not None]
    st.session_state.joined_pdf = aux_functions.join_documents(documentos)
    if doc1 is not None and doc2 is not None and doc4 is not None:
        if doc6 is not None:
            with st.spinner('Analizando Posibles Causales de Improcedencia...'):
                st.session_state.resultados['inadmissibility'] = aux_functions.inadmissibility_analyzer(bedrock_client, full_doc=st.session_state.joined_pdf, elevation_doc=doc1, appeal_doc=doc2, notification_doc=doc4, entity_doc=doc6)
        else:
            with st.spinner('Analizando Posibles Causales de Improcedencia...'):
                st.session_state.resultados['inadmissibility'] = aux_functions.inadmissibility_analyzer(bedrock_client, full_doc=st.session_state.joined_pdf, elevation_doc=doc1, appeal_doc=doc2, notification_doc=doc4)
    else:
       st.warning("Por favor, suba todos los documentos primero")
    end_time = time.time()
    print(f"Tiempo de ejecución: {end_time - start_time:.4f} segundos")
if st.session_state.resultados['inadmissibility']:
    st.write(f"{st.session_state.resultados['inadmissibility']}")
