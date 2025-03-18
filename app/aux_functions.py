import json
import boto3
import base64
from typing import List
import re
import fitz
import prompts
import uuid
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
from io import BytesIO

def take_screenshot_by_page(document, page, factor_escala):
    page = document[page]
    matriz_escala = fitz.Matrix(factor_escala, factor_escala)
    image = page.get_pixmap(matrix=matriz_escala)
    image = image.tobytes()
    
    return base64.b64encode(image).decode('utf-8')

def get_pages(doc, factor_escala = 1.0) -> list:
    pdf_images = []
    pdf = fitz.open(stream=doc.read(), filetype="pdf")
    for j in range(len(pdf)):
        pdf_images.append(take_screenshot_by_page(pdf,j, factor_escala))

    return pdf_images

def upload_to_s3(s3_client, file, bucket, folder):
    # Crear un nombre único para el archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    file_name = f"{folder}/{timestamp}_{unique_id}_{file.name}"
    
    # Subir archivo a S3
    s3_client.upload_fileobj(file, bucket, file_name)
    
    # Devolver el path del archivo en S3
    return f"s3://{bucket}/{file_name}"

def join_documents(documents_list):
    """
    Unir múltiples documentos PDF en uno solo.
    
    Args:
        documents_list: Lista de archivos UploadedFile de Streamlit
        
    Returns:
        BytesIO: Un objeto BytesIO con el PDF combinado
    """
    # Crear un nuevo documento PDF
    joined_doc = fitz.open()
    
    # Procesar cada documento de la lista
    for doc in documents_list:
        if doc is not None:
            try:
                # Reiniciar la posición del archivo
                doc.seek(0)
                
                # Crear un PDF temporal con los bytes del archivo
                pdf_temp = fitz.open(stream=doc.read(), filetype="pdf")
                
                # Insertar las páginas en el documento unido
                joined_doc.insert_pdf(pdf_temp)
                
                # Cerrar el PDF temporal
                pdf_temp.close()
            except Exception as e:
                print(f"Error al procesar documento: {e}")
    
    # Crear un objeto BytesIO para almacenar el PDF combinado
    joined_pdf = BytesIO()
    joined_doc.save(joined_pdf)
    joined_pdf.seek(0)
    
    # Close the joined document
    joined_doc.close()
    
    return joined_pdf

def process_images_batch(bedrock_client, case_prompt, pdf_images: List[str] = None) -> str:

    system_prompt = f"You are an expert lawyer and specialist in legal document analysis, who will be in charge of analyzing, validating, classifying and comparing legal documents to find possible grounds for inadmissibility."
    

    # Prepare the message for Claude
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": case_prompt
                }
            ]
        }
    ]

    # Add images to the message
    if pdf_images is not None:
        for iter in range(len(pdf_images)):

            messages[0]["content"].append({"type" : "text", 
                                        "text" : f"Page Number {iter+1}"})

            messages[0]["content"].append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": pdf_images[iter]
                }
            })

    try:
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0", #us.anthropic.claude-3-7-sonnet-20250219-v1:0 anthropic.claude-3-5-sonnet-20240620-v1:0
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "system": system_prompt,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0
            })
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    except Exception as e:
        print(f"Error processing batch: {e}")
        return None
#bedrock_client, case_prompt, task: str = "Identify", pdf_images: List[str] = None

def document_analyzer(bedrock_client, prompt_identify: str, task: str = "analyze", prompt_end_identify: str = None, prompt_analyze: str = None, pdf_images: list[str] = None, batch_size: int = 10) -> str:
    """
    Process images in batches and stop when both fields are found, even across different batches
    """
    raw_result = ""
    final_result = ""
    if pdf_images is not None:
        for i in range(0, len(pdf_images), batch_size):
            current_batch = i // batch_size
            batch = pdf_images[i:i + batch_size]
            raw_result = process_images_batch(bedrock_client, case_prompt = prompt_identify, pdf_images = batch)

            print(f"batch number: {current_batch}")
            
            #print(raw_result)

            find_document = re.search(r'<Document>(.*?)</Document>', raw_result, re.DOTALL)
            find_inadmissibility = re.search(r'<Find_Inadmissibility_Ground>(.*?)</Find_Inadmissibility_Ground>', raw_result, re.DOTALL)

            if find_document:
                document = find_document.group(1)
                if document == "true":
                    start_page = int(re.search(r'<Start_Page>(.*?)</Start_Page>', raw_result, re.DOTALL).group(1))
                    new_batch = pdf_images[(current_batch * batch_size) + start_page - 1: ((current_batch * batch_size) + start_page - 1) + 15]
                    raw_result = process_images_batch(bedrock_client, case_prompt = prompt_end_identify, pdf_images = new_batch)
                    #print(raw_result)
                    find_end_document = re.search(r'<End_Document>(.*?)</End_Document>', raw_result, re.DOTALL)
                    if find_end_document:
                        end_document = find_end_document.group(1)
                        if end_document == "true":
                            end_page = int(re.search(r'<End_Page>(.*?)</End_Page>', raw_result, re.DOTALL).group(1))
                            new_batch = pdf_images[(current_batch * batch_size) + start_page - 1: ((current_batch * batch_size) + start_page - 1) + end_page]
                            raw_result = process_images_batch(bedrock_client, case_prompt = prompt_analyze, pdf_images = new_batch)
                            #print(raw_result)
                    break

            if find_inadmissibility:
                innadmissibility = find_inadmissibility.group(1)
                if innadmissibility == "true":
                    break
            
    else:
        raw_result = process_images_batch(bedrock_client, case_prompt = prompt_identify)

    if task == "analyze":
        thinking = re.search(r'<Thinking>(.*?)</Thinking>', raw_result, re.DOTALL).group(1)
        conclusion = re.search(r'<Final_Conclusion>(.*?)</Final_Conclusion>', raw_result, re.DOTALL).group(1)
        final_result = "Análisis del Documento: \n" + thinking + "\n Conclusión Final: \n" + conclusion
    if task == "inadmissibility":
        final_result = re.search(r'<Final_Conclusion>(.*?)</Final_Conclusion>', raw_result, re.DOTALL).group(1)

    return final_result

def mootness_analyzer(bedrock_client, elevation_doc, entity_doc):
    elevation_doc.seek(0)
    if entity_doc:
        try:
            entity_doc.seek(0)
            pdf_elevation_images = get_pages(elevation_doc)
            pdf_entity_images = get_pages(entity_doc)#

            elevation_summary = document_analyzer(bedrock_client, task = "inadmissibility", prompt_identify = prompts.prompt_elevation_identify, prompt_end_identify=prompts.prompt_elevation_inadmissibility,pdf_images=pdf_elevation_images, batch_size = 5)
            print(elevation_summary)

            entity_summary = document_analyzer(bedrock_client, task = "inadmissibility", prompt_identify = prompts.prompt_entity_inadmissibility_identify, pdf_images=pdf_entity_images, batch_size = 10)
            print(entity_summary)

            prompt_mootness = f"""Analiza la acción del Documento de Elevación {elevation_summary} y el resumen del Documento Enviado por la Entidad {entity_summary} para encontrar una posible causal de improcedencia por Sustracción de la Materia.

            Explica tus pensamientos dentro de <Thinking></Thinking> y dame tu respuesta final dentro de <Final_Conclusion></Final_Conclusion>.

            <Thinking>
                - La pretensión se llega a producir? 
                - Existe una circunstancia que hace innecesario el cumplimiento de la pretensión? Por ejemplo: El Administrado reclamando algo sobre su trabajo, pero en medio de la disputa legal renuncia a su trabajo.
                - Cualquier circunstancia que hace innecesario el cumplimiento de la pretensión, que no sea un caso de avocamiento indebido.
            </Thinking>

            <Final_Conclusion>
                <Summary>resumen de hallazgos</Summary>
                <Find_Inadmissibility_Ground>true or false</Find_Inadmissibility_Ground>
                <Inadmissibility_Ground>si se encontró una causal de improcedencia por Sustracción de la Materia, responda solo con el nombre: Sustracción de la Materia</Inadmissibility_Ground>
            </Final_Conclusion>
            """
            raw_answer = document_analyzer(bedrock_client, task = "inadmissibility", prompt_identify = prompt_mootness)

            find_inadmissibility = re.search(r'<Find_Inadmissibility_Ground>(.*?)</Find_Inadmissibility_Ground>', raw_answer, re.DOTALL).group(1)
            if find_inadmissibility == "true":
                inadmissibility_ground = re.search(r'<Inadmissibility_Ground>(.*?)</Inadmissibility_Ground>', raw_answer, re.DOTALL).group(1)
                conclusion = re.search(r'<Summary>(.*?)</Summary>', raw_answer, re.DOTALL).group(1)
                final_result = "\n● " + inadmissibility_ground + "\n- Motivo: " + conclusion.strip() + "\n"
                #print(final_result)
            
            else:
                final_result = None
        
        except Exception as e:
            print(f"Error in mootness_analyzer: {e}")
            return f"Error in mootness_analyzer: {e}"
    
    else:
        final_result = None

    print(final_result)
    return final_result

def improper_assumption_analyzer(bedrock_client, entity_doc):
    if entity_doc:
        try:
            entity_doc.seek(0)
            pdf_entity_images = get_pages(entity_doc)

            prompt_improper_assumption = """Analyze the images to get relevant insights about the legal document provided using the following directions:

                All the legal actions are being conducted by the Tribunal of SERVIR, that is a tribunal of first instance, any legal action presented to a Superior Court of Justice or Judiciary is out of SERVIR control, because those entitys are superior than SERVIR.

                Explain your thoughts inside <Thinking></Thinking> and give me your final answer inside <Answer></Answer>.

                <Thinking>
                    - Does it mention the intention that SERVIR court refrain from ruling?
                    - Does it mention about elevating or presenting a legal action to any Superior Court of Justice or Judiciary instead of continuing the process with the Tribunal of SERVIR?
                </Thinking>
                
                <Final_Conclusion>
                    <Summary> summary of findings </Summary>
                    <Find_Inadmissibility_Ground> true or false </Find_Inadmissibility_Ground>
                    <Inadmissibility_Ground> if a Improper assumption of jurisdiction was found, answer just with the name: Avocamiento Indebido </Inadmissibility_Ground>
                </Final_Conclusion>
                
                Give me all your answer in Spanish or you will be penalized."""
            
            raw_answer = document_analyzer(bedrock_client, task = "inadmissibility", prompt_identify = prompt_improper_assumption, pdf_images=pdf_entity_images, batch_size = 10)

            find_inadmissibility = re.search(r'<Find_Inadmissibility_Ground>(.*?)</Find_Inadmissibility_Ground>', raw_answer, re.DOTALL).group(1)
            if find_inadmissibility == "true":
                inadmissibility_ground = re.search(r'<Inadmissibility_Ground>(.*?)</Inadmissibility_Ground>', raw_answer, re.DOTALL).group(1)
                conclusion = re.search(r'<Summary>(.*?)</Summary>', raw_answer, re.DOTALL).group(1)
                final_result = "\n● " + inadmissibility_ground + "\n- Motivo: " + conclusion.strip() + "\n"
                #print(final_result)
            
            else:
                final_result = None

        except Exception as e:
            print(f"Error in improper_assumption_analyzer: {e}")
            return f"Error in improper_assumption_analyzer: {e}"
    
    else:
        final_result = None

    print(final_result)
    return final_result

def withdrawal_analyzer(bedrock_client, full_doc):

    try:
        full_doc.seek(0)
        pdf_full_doc_images = get_pages(full_doc)

        prompt_withdrawal = """Analyze the images to get relevant insights about the legal document provided using the following directions:

        Explain your thoughts inside <Thinking></Thinking> and give me your final answer inside <Answer></Answer>.

        <Thinking>
            - Does it explicitly and clearly mention the withdrawal of the appeal? It can be a document where in the Subject or Sumilla explicitly mention to withdraw the appeal
        </Thinking>
        
        <Final_Conclusion>
            <Summary> Summary of findings </Summary>
            <Find_Inadmissibility_Ground> true or false </Find_Inadmissibility_Ground>
            <Inadmissibility_Ground> If a Ground of Inadmissibility was found, answer just with the name: Desistimiento </Inadmissibility_Ground>
        </Final_Conclusion>
            
        Give me all your answer in Spanish or you will be penalized."""
        
        raw_answer = document_analyzer(bedrock_client, task = "inadmissibility", prompt_identify = prompt_withdrawal, pdf_images=pdf_full_doc_images, batch_size = 19)

        find_inadmissibility = re.search(r'<Find_Inadmissibility_Ground>(.*?)</Find_Inadmissibility_Ground>', raw_answer, re.DOTALL).group(1)
        if find_inadmissibility == "true":
            inadmissibility_ground = re.search(r'<Inadmissibility_Ground>(.*?)</Inadmissibility_Ground>', raw_answer, re.DOTALL).group(1)
            conclusion = re.search(r'<Summary>(.*?)</Summary>', raw_answer, re.DOTALL).group(1)
            final_result = "\n● " + inadmissibility_ground + "\n- Motivo: " + conclusion.strip() + "\n"
            #print(final_result)
        
        else:
            final_result = None

    except Exception as e:
        print(f"Error in withdrawal_analyzer: {e}")
        return f"Error in withdrawal_analyzer: {e}"

    print(final_result)
    return final_result

def extemporaneous_analyzer(bedrock_client, appeal_doc, notification_doc):
    try:
        appeal_doc.seek(0)
        notification_doc.seek(0)
        pdf_appeal_images = get_pages(appeal_doc)
        pdf_notification_images = get_pages(notification_doc)

        apeal_date_str = document_analyzer(bedrock_client, task = "inadmissibility", prompt_identify = prompts.prompt_appeal_identify, prompt_end_identify = prompts.prompt_appeal_end_identify, prompt_analyze = prompts.prompt_appeal_extemporaneous_identify, pdf_images=pdf_appeal_images, batch_size = 5)
        notification_date_str = document_analyzer(bedrock_client, task = "inadmissibility", prompt_identify=prompts.prompt_notification_inadmissibility_identify, pdf_images = pdf_notification_images)

        print(apeal_date_str)
        print(notification_date_str)

        prompt_extemporaneous = f"""Analiza la fecha del Recurso de Apelación {apeal_date_str} y la fecha del Cargo de Notificación del Acto Impugnado {notification_date_str} para encontrar una posible causal de improcedencia por Extemporaneidad.
        Explica tus pensamientos dentro de <Thinking></Thinking> y dame tu respuesta final dentro de <Final_Conclusion></Final_Conclusion>.

        <Thinking>
            - Cuantos días hábiles hay entre estas fechas? No consideres el inicio del rango como día hábil
            - La cantidad de días hábiles es mayor a 15 días?
        </Thinking>

        <Final_Conclusion>
            <Summary>resumen de hallazgos</Summary>
            <Find_Inadmissibility_Ground>true or false</Find_Inadmissibility_Ground>
            <Inadmissibility_Ground>si se encontró una causal de improcedencia por Extemporáneo, responda solo con el nombre: Extemporáneo</Inadmissibility_Ground>
        </Final_Conclusion>
        """
        raw_answer = document_analyzer(bedrock_client, task = "inadmissibility", prompt_identify = prompt_extemporaneous)

        find_inadmissibility = re.search(r'<Find_Inadmissibility_Ground>(.*?)</Find_Inadmissibility_Ground>', raw_answer, re.DOTALL).group(1)
        if find_inadmissibility == "true":
            inadmissibility_ground = re.search(r'<Inadmissibility_Ground>(.*?)</Inadmissibility_Ground>', raw_answer, re.DOTALL).group(1)
            conclusion = re.search(r'<Summary>(.*?)</Summary>', raw_answer, re.DOTALL).group(1)
            final_result = "\n● " + inadmissibility_ground + "\n- Motivo: " + conclusion.strip() + "\n"
            #print(final_result)
        
        else:
            final_result = None

        print(final_result)
        return final_result

    except Exception as e:
            print(f"Error in extemporaneous_analyzer: {e}")
            return None

def inadmissibility_analyzer(bedrock_client, full_doc, elevation_doc, appeal_doc, notification_doc, entity_doc = None):
    final_answer = f"Causal(es) de Improcedencia: \n"
    full_doc.seek(0)
    elevation_doc.seek(0)
    appeal_doc.seek(0)
    notification_doc.seek(0)
    if entity_doc:
        entity_doc.seek(0)
    with ThreadPoolExecutor(max_workers=4) as executor:
        analyze_funcs = [
            executor.submit(mootness_analyzer, bedrock_client, elevation_doc, entity_doc),
            executor.submit(extemporaneous_analyzer, bedrock_client, appeal_doc, notification_doc),
            executor.submit(improper_assumption_analyzer, bedrock_client, entity_doc),
            executor.submit(withdrawal_analyzer, bedrock_client, full_doc)
        ]

        [mootness, extemporaneous, improper_assumption, withdrawal] = [a.result() for a in analyze_funcs]

    if all(inadmissibility is None for inadmissibility in [mootness, extemporaneous, improper_assumption, withdrawal]):
        final_answer += "\n- No se encontraron Causales de Improcedencia"
    
    else:
        if mootness:
            final_answer += mootness

        if extemporaneous:
            final_answer += extemporaneous

        if improper_assumption:
            final_answer += improper_assumption

        if withdrawal:
            final_answer += withdrawal

    print(final_answer)
    return final_answer

"""
def main():
    pdf_path = ["Expedientes divididos por requisitos/00068-2024/2. RECURSO DE APELACIÓN.pdf",
                "Expedientes divididos por requisitos/00169-2024/2. Recurso de Apelación-Exp.00169-2024.pdf",
                "Expedientes divididos por requisitos/02428-2024/2. Recurso de Apelación - Exp.2428-2024.pdf",
                "Expedientes divididos por requisitos/08754-2024/2. RECURSO DE APELACIÓN.pdf"]

    pdf_images = []

    pdf = fitz.open(pdf_path[3])
    for j in range(len(pdf)):
        pdf_images.append(take_screenshot_by_page(pdf,j))

    document_analyzer(pdf_images)

if __name__ == "__main__":
    main()"""