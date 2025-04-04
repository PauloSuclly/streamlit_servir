# Analizador de Causales de Improcedencia Legal

## Descripción General
Sistema automatizado que utiliza IA para analizar documentos legales y detectar posibles causales de improcedencia en procedimientos administrativos, especialmente orientado a procesos del Tribunal de SERVIR.

Esta herramienta procesa documentos PDF relacionados con apelaciones y recursos legales, utilizando modelos de IA Claude a través de AWS Bedrock para identificar automáticamente posibles motivos de improcedencia. El sistema analiza en paralelo múltiples causales como:

- Sustracción de la materia
- Avocamiento indebido
- Desistimiento
- Extemporaneidad

Además, antes de realizar la identificación de causales de improcedencia, analiza y valida los 5 documentos que generan un caso (Expediente), estos documentos son:
- Documento de Elevación
- Recurso de Apelación
- Acto Impugnado
- Cargo de Notificación
- Formato N°1

## Características
- Procesamiento de documentos PDF convirtiéndolos en imágenes para análisis con IA
- Análisis de múltiples páginas mediante procesamiento por lotes
- Ejecución paralela de análisis para mayor eficiencia
- Detección de causales específicas de improcedencia legal
- Respuestas estructuradas con justificación de hallazgos

## Requisitos
- Python 3.6+
- Cuenta de AWS con acceso a Bedrock
- Paquetes Python requeridos:
  - boto3
  - PyMuPDF (fitz)
  - json
  - base64
  - re
  ```sh
  pip install boto3 pymupdf
  ```

## Uso
```python
import boto3
from aux_functions import document_analyzer

# Inicializar el cliente de AWS Bedrock
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name='tu-region'  # ej., 'us-east-1'
) # boto3.client(service_name='bedrock-runtime',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name="us-east-1")

# Ejecutar el análisis del documento
resultado = document_analyzer(
    bedrock_client,
    prompt_identify = prompts.prompt_appeal_identify,
    prompt_end_identify = prompts.prompt_appeal_end_identify,
    prompt_analyze = prompts.prompt_appeal_analyze,
    pdf_images=pdf_appeal_images,
    batch_size = 5  # Opcional
)

# Mostrar los resultados
print(resultado)
```

## Principales Funciones
### `document_analyzer(bedrock_client, prompt_identify: str, task: str = "analyze", prompt_end_identify: str = None, prompt_analyze: str = None, pdf_images: list[str] = None, batch_size: int = 10)`
Función principal que realiza el análisis de documentos legales del expediente.

**Parámetros:**
- `bedrock_client`: Cliente AWS Bedrock
- `prompt_identify`: Prompt de análisis e identificación inicial
- `task`: Documento de elevación (Opcional, las 2 opciones son "analyze" y "inadmissibility")
- `prompt_end_identify`: Prompt de identificación del final del documento buscado (Opcional, solo para ciertos documentos)
- `prompt_analyze`: Prompt de análisis completo (Opcional, solo para ciertos documentos)
- `pdf_images`: Lista de imágenes codificadas en base64 (Opcional)
- `batch_size`: Número de imágenes a procesar en cada lote (Opcional)

**Retorna:** Resumen estructurado de los analizado en el documento

### `inadmissibility_analyzer(bedrock_client, full_doc, elevation_doc, appeal_doc, notification_doc, entity_doc=None)`
Función principal que coordina todos los análisis de causales de improcedencia.

**Parámetros:**
- `bedrock_client`: Cliente AWS Bedrock
- `full_doc`: Expediente completo en formato PDF
- `elevation_doc`: Documento de elevación
- `appeal_doc`: Recurso de apelación
- `notification_doc`: Cargo de notificación
- `entity_doc`: Documento de la entidad (opcional)

**Retorna:** Resumen estructurado de las causales de improcedencia encontradas

## Análisis Específicos
- `mootness_analyzer`: Detecta sustracción de la materia
- `improper_assumption_analyzer`: Detecta avocamiento indebido
- `withdrawal_analyzer`: Detecta desistimiento
- `extemporaneous_analyzer`: Detecta extemporaneidad

## Procesamiento de Documentos
- `get_pages`: Convierte PDF a imágenes codificadas en base64
- `join_documents`: Une múltiples PDFs en uno solo
- `document_analyzer`: Analiza documentos mediante el modelo de IA

### `get_pages(doc, factor_escala=3)`

Convierte un documento PDF a una lista de imágenes codificadas en base64.

**Parámetros:**

- `doc`: Documento obtenido por stream = doc.read() (File Uploader de Streamlit)
- `factor_escala`: Factor de escalado para la calidad de imagen (Predeterminado: 1.0)

**Retorna:**
Lista de imágenes codificadas en base64.

## Notas de Implementación
- El sistema utiliza Claude 3.5 Sonnet a través de AWS Bedrock para análisis de documentos
- Las respuestas están estructuradas mediante etiquetas XML para facilitar su procesamiento
- Se utiliza procesamiento paralelo para mejorar la eficiencia del análisis

## Limitaciones
- El análisis está optimizado para documentos legales de SERVIR
- La precisión depende de la calidad de los PDFs proporcionados
- Requiere correcta configuración de permisos en AWS Bedrock (Cuando pasen a CDK o SAM, por el tema de los permisos del S3, Lambda, etc)

