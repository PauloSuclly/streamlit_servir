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
            st.session_state.resultados['doc1'] = aux_functions.document_analyzer(bedrock_client,prompt_identify = prompts.prompt_elevation_identify,pdf_images=pdf_elevation_images)
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
        with st.spinner('Procesando documento...'):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            st.session_state.resultados['doc6'] = contar_paginas(doc6)
    else:
        st.warning("Por favor, suba un documento primero")
if st.session_state.resultados['doc6']:
    st.write(f"Número de páginas: {st.session_state.resultados['doc6']}")

# Botón para analizar documentos
st.markdown("---")
if st.button("Analizar Documentos"):
    if doc2 is not None and doc6 is not None:
        with st.spinner('Analizando documentos...'):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            paginas_doc2 = contar_paginas(doc2)
            paginas_doc6 = contar_paginas(doc6)
            st.write("Resultado del análisis:")
            st.write(f"Recurso de Apelación: {paginas_doc2} páginas")
            st.write(f"Documentos Emitidos por la Entidad: {paginas_doc6} páginas")
    else:
        st.warning("Por favor, asegúrese de haber subido el Recurso de Apelación y los Documentos Emitidos por la Entidad")



# Opción con 2 columnas
"""# Inicializar variables en session_state si no existen
if 'resultados' not in st.session_state:
    st.session_state.resultados = {}

def contar_paginas(pdf_file, key):
    if pdf_file is not None:
        try:
            # Crear barra de progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simular proceso de carga
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
                status_text.text(f"Procesando... {i+1}%")
            
            # Leer el PDF y contar páginas
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            num_paginas = len(doc)
            doc.close()
            
            # Guardar resultado en session_state
            st.session_state.resultados[key] = num_paginas
            
            # Limpiar barra de progreso y mostrar resultado
            progress_bar.empty()
            status_text.empty()
            return num_paginas
            
        except Exception as e:
            st.error(f"Error al procesar el documento: {str(e)}")
            return None
    return None

# Crear columnas para organizar la interfaz
col1, col2 = st.columns(2)

with col1:
    # Documento de Elevación
    st.subheader("1. Documento de Elevación")
    doc_elevacion = st.file_uploader("Subir Documento de Elevación", type="pdf", key="elevacion")
    if st.button("Validar Documento de Elevación"):
        resultado = contar_paginas(doc_elevacion, "elevacion")
    if "elevacion" in st.session_state.resultados:
        st.write(f"Número de páginas: {st.session_state.resultados['elevacion']}")

    # Recurso de Apelación
    st.subheader("2. Recurso de Apelación")
    recurso_apelacion = st.file_uploader("Subir Recurso de Apelación", type="pdf", key="apelacion")
    if st.button("Validar Recurso de Apelación"):
        resultado = contar_paginas(recurso_apelacion, "apelacion")
    if "apelacion" in st.session_state.resultados:
        st.write(f"Número de páginas: {st.session_state.resultados['apelacion']}")

    # Acto Impugnado
    st.subheader("3. Acto Impugnado")
    acto_impugnado = st.file_uploader("Subir Acto Impugnado", type="pdf", key="impugnado")
    if st.button("Validar Acto Impugnado"):
        resultado = contar_paginas(acto_impugnado, "impugnado")
    if "impugnado" in st.session_state.resultados:
        st.write(f"Número de páginas: {st.session_state.resultados['impugnado']}")

with col2:
    # Cargo de Notificación
    st.subheader("4. Cargo de Notificación")
    cargo_notificacion = st.file_uploader("Subir Cargo de Notificación", type="pdf", key="notificacion")
    if st.button("Validar Cargo de Notificación"):
        resultado = contar_paginas(cargo_notificacion, "notificacion")
    if "notificacion" in st.session_state.resultados:
        st.write(f"Número de páginas: {st.session_state.resultados['notificacion']}")

    # Formato N°1
    st.subheader("5. Formato N°1 del Administrado")
    formato_1 = st.file_uploader("Subir Formato N°1", type="pdf", key="formato")
    if st.button("Validar Formato N°1"):
        resultado = contar_paginas(formato_1, "formato")
    if "formato" in st.session_state.resultados:
        st.write(f"Número de páginas: {st.session_state.resultados['formato']}")

    # Documentos Emitidos
    st.subheader("6. Documentos Emitidos por la Entidad")
    docs_entidad = st.file_uploader("Subir Documentos Emitidos", type="pdf", key="entidad")
    if st.button("Validar Documentos Emitidos"):
        resultado = contar_paginas(docs_entidad, "entidad")
    if "entidad" in st.session_state.resultados:
        st.write(f"Número de páginas: {st.session_state.resultados['entidad']}")

# Botón para analizar documentos al final de la página
st.markdown("---")
if st.button("Analizar Documentos"):
    st.subheader("Resultado del Análisis")
    
    # Verificar si los documentos necesarios están cargados
    if "apelacion" in st.session_state.resultados and "entidad" in st.session_state.resultados:
        st.write(f"Recurso de Apelación: {st.session_state.resultados['apelacion']} páginas")
        st.write(f"Documentos Emitidos por la Entidad: {st.session_state.resultados['entidad']} páginas")
    else:
        st.warning("Por favor, valide primero el Recurso de Apelación y los Documentos Emitidos por la Entidad")"""