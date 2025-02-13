import streamlit as st
import fitz  # PyMuPDF
import time
import os
import boto3
import aux_functions
import prompts
from dotenv import load_dotenv


load_dotenv()

aws_access_key_id = os.getenv('AMAZON_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AMAZON_SECRET_ACCESS_KEY')

bedrock_client = boto3.client(service_name='bedrock-runtime',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name="us-east-1")

st.set_page_config(layout="centered")

def contar_paginas(pdf_file):
    if pdf_file is not None:
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            return doc.page_count
        except Exception as e:
            return f"Error al procesar el PDF: {str(e)}"
    return None

st.title("Validación de Documentos")

# Inicializar variables de estado en session_state
if 'resultados' not in st.session_state:
    st.session_state.resultados = {
        'doc1': None,
        'doc2': None,
        'doc3': None,
        'doc4': None,
        'doc5': None,
        'doc6': None
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
        pdf_elevation_images = []
        pdf_elevation = fitz.open(stream=doc1.read(), filetype="pdf")
        for j in range(len(pdf_elevation)):
            pdf_elevation_images.append(aux_functions.take_screenshot_by_page(pdf_elevation,j))
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
        pdf_appeal_images = []
        pdf_appeal = fitz.open(stream=doc2.read(), filetype="pdf")
        for j in range(len(pdf_appeal)):
            pdf_appeal_images.append(aux_functions.take_screenshot_by_page(pdf_appeal,j))
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
        pdf_challenged_images = []
        pdf_challenged = fitz.open(stream=doc3.read(), filetype="pdf")
        for j in range(len(pdf_challenged)):
            pdf_challenged_images.append(aux_functions.take_screenshot_by_page(pdf_challenged,j))
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
        pdf_notification_images = []
        pdf_notification = fitz.open(stream=doc4.read(), filetype="pdf")
        for j in range(len(pdf_notification)):
            pdf_notification_images.append(aux_functions.take_screenshot_by_page(pdf_notification,j))
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
        pdf_format1_images = []
        pdf_format1 = fitz.open(stream=doc5.read(), filetype="pdf")
        for j in range(len(pdf_format1)):
            pdf_format1_images.append(aux_functions.take_screenshot_by_page(pdf_format1,j))
        with st.spinner('Procesando documento...'):
            st.session_state.resultados['doc5'] = aux_functions.document_analyzer(bedrock_client,prompt_identify=prompts.prompt_format1_identify, pdf_images = pdf_format1_images)
    else:
        st.warning("Por favor, suba un documento primero")
if st.session_state.resultados['doc5']:
    st.write(f"{st.session_state.resultados['doc5']}")

# Documento 6: Documentos Emitidos
st.subheader("6. Documentos Emitidos por la Entidad")
doc6 = st.file_uploader("Subir Documentos Emitidos", type=['pdf'], key="doc6")
if st.button("Validar Documentos Emitidos"):
    if doc6 is not None:
        st.warning("Función no implementada...")
    else:
        st.warning("Función no implementada...")

# Botón para analizar documentos
st.markdown("---")
if st.button("Analizar Documentos"):
    if doc2 is not None and doc6 is not None:
        with st.spinner('Analizando documentos...'):
           st.warning("Función no implementada...")
    else:
       st.warning("Función no implementada...")
