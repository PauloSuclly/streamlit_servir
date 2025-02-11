import json
import boto3
import base64
from typing import List, Dict, Optional
import re
import fitz

def take_screenshot_by_page(document, page):
    page = document[page]
    image = page.get_pixmap()
    image = image.tobytes()
    
    return base64.b64encode(image).decode('utf-8')

def process_images_batch(bedrock_client, case_prompt, task: str = "Identify", pdf_images: List[str] = None) -> Dict:

    system_prompt = f"You are an expert lawyer and specialist in legal document analysis, who will be in charge of analyzing, validating, classifying and comparing legal documents to find possible grounds for inadmissibility."
    
    if task == "Identify":
        prompt = case_prompt
        
    elif task == "End_Identify":
        prompt = case_prompt
        
    else:
        prompt = case_prompt
    

    # Prepare the message for Claude
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
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
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
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
def document_analyzer(bedrock_client, prompt_identify, prompt_end_identify = None, prompt_analyze = None, pdf_images: List[str] = None, batch_size: int = 10) -> str:
    """
    Process images in batches and stop when both fields are found, even across different batches
    """
    raw_result = ""
    final_result = ""
    
    for i in range(0, len(pdf_images), batch_size):
        current_batch = i // batch_size
        batch = pdf_images[i:i + batch_size]
        raw_result = process_images_batch(bedrock_client, case_prompt = prompt_identify, task = "Identify", pdf_images = batch)

        print(f"batch number: {current_batch}")
        
        print(raw_result)

        find_document = re.search(r'<Document>(.*?)</Document>', raw_result, re.DOTALL)

        if find_document:
            document = find_document.group(1)
            if document == "true":
                start_page = int(re.search(r'<Start_Page>(.*?)</Start_Page>', raw_result, re.DOTALL).group(1))
                new_batch = pdf_images[(current_batch * batch_size) + start_page - 1: ((current_batch * batch_size) + start_page - 1) + 15]
                raw_result = process_images_batch(bedrock_client, case_prompt = prompt_end_identify, task = "End_Identify", pdf_images = new_batch)
                print(raw_result)
                find_end_document = re.search(r'<End_Document>(.*?)</End_Document>', raw_result, re.DOTALL)
                if find_end_document:
                    end_document = find_end_document.group(1)
                    if end_document == "true":
                        end_page = int(re.search(r'<End_Page>(.*?)</End_Page>', raw_result, re.DOTALL).group(1))
                        new_batch = pdf_images[(current_batch * batch_size) + start_page - 1: ((current_batch * batch_size) + start_page - 1) + end_page]
                        raw_result = process_images_batch(bedrock_client, case_prompt = prompt_analyze, task = "Extract", pdf_images = new_batch)
                        print(raw_result)
                break

                            
    thinking = re.search(r'<Thinking>(.*?)</Thinking>', raw_result, re.DOTALL).group(1)
    conclusion = re.search(r'<Final_Conclusion>(.*?)</Final_Conclusion>', raw_result, re.DOTALL).group(1)

    final_result = "Análisis del Documento: \n" + thinking + "\n Conclusión Final: \n" + conclusion

    return final_result

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