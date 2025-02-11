#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 1. Documento de Elevación
prompt_elevation_identify = """Analiza el DOCUMENTO DE ELEVACIÓN siguiendo estos pasos específicos.

    Explica tus pensamientos dentro de <Thinking></Thinking> y dame tu respuesta final dentro de <Final_Conclusion></Final_Conclusion>

    <Thinking>
        1.Numeración del documento:
        - ¿Tiene número de identificación?
        - ¿Incluye el año en curso?
        - ¿El formato de numeración es correcto?
        - Observación del hallazgo

        2.Fecha de emisión:
        - ¿Está presente la fecha?
        - ¿Está claramente legible?
        - Observación del hallazgo

        3.Asunto o sumilla:
        - ¿Contiene un asunto o sumilla?
        - ¿Menciona específicamente que se trata de elevación de recurso de apelación?
        - ¿Es claro y preciso?
        - Observación del hallazgo

        4.Descripción del caso:
        - ¿Incluye una descripción del caso?
        - ¿Menciona el nombre completo del administrado?
        - ¿La descripción es clara y suficiente?
        - ¿Proporciona contexto adecuado del caso?
        - Observación del hallazgo

        5.Firma de la autoridad:
        - ¿Está firmado el documento?
        - ¿Se identifica claramente a la autoridad firmante?
        - ¿La autoridad firmante tiene la competencia para elevar el recurso?
        - ¿La firma es legible y completa?
        - Observación del hallazgo
    </Thinking>

    <Final_Conclusion>
        - Resumen de hallazgos
        - ¿El documento de elevación cumple con todos los requisitos?
        - Listado de elementos faltantes o incorrectos (si los hay)
    </Final_Conclusion>    
    """

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 2. Appeal
prompt_appeal_identify = """Analyze the images to identify if they represent an APPEAL.

            The APPEAL is a document that the administrator presents in order to question an administrative act.that causes harm and that is issued by a public entity. The deadline for thefiling of an appeal is fifteen (15) business days counted from the day following notification of the contested act.

            Explain your thoughts inside <Thinking></Thinking> and give me your final answer inside <Answer></Answer>, this one has to be just "true" or "false".
            
            <Answer>
                <Document>true/false</Document>
                <Start_Page> number of processed page by you, where the APPEAL started </Start_Page>
            </Answer>"""

prompt_appeal_end_identify  = """Analyze the images to identify the End of the APPEAL.

            The APPEAL is a document that the administrator presents in order to question an administrative act.that causes harm and that is issued by a public entity. The deadline for thefiling of an appeal is fifteen (15) business days counted from the day following notification of the contested act.
            The APPEAL document usually ends with the Signature of the administrator or the name of the administrator.

            Explain your thoughts inside <Thinking></Thinking> and give me your final answer inside <Answer></Answer>, this one has to be just "true" or "false".
            
            <Answer>
                <End_Document>true/false</End_Document>
                <End_Page> number of processed page by you, where the CHALLENGED ACT ends </End_Page>
            </Answer>"""

prompt_appeal_analyze = """Analyze the APPEAL document provided using the following questions, explain your thoughts inside <Thinking></Thinking>:

        <Thinking>
            1.Date of presentation:
            - Is the date of APPEAL receipt present? (Usually present on the first page of the APPEAL document)
            - How is it accredited? Check if it is by:
                -Seal of parties table/documentary processing unit
                -Route sheet
                -Single procedure format
                -Handwritten date
            - If it's a seal, is it completely clear, visible and sharp?
            - If the seal is not clear, visible and sharp, keep the next format where a date is present.

            2. Identification of the administrator:
            - Are full names and surnames present?
            - Identity document:
                -If it is a DNI: Does it have exactly 8 digits?
                -If it is CE: Does it have exactly 9 digits?
            - Is the data legible and clear?

            3.Request:
            - Do you clearly express your intention to appeal?
            - Does it specifically identify the administrative act that is being challenged?
            - Do you use any of the established formulas such as:
                -"I file an appeal against..."
                -"I am filing an appeal against..."
                -"I appeal..."
                -"I challenge..." or some other type of formula

            4.Basics:
            - Does it contain factual foundations?
            - Does it contain legal foundations?
            - Are they clearly identified under any of these titles?:
                -"Fundamentals.-"
                -"Factual foundations.- / Legal foundations.-"
                -"Facts.-"
                -"Legal foundations.-"
                -"Violated rules.-" or some other way that allows them to be identified
            - Are the arguments clear and related to the appeal?

            5.Signature of the administrator:
            - Is the signature present?
            - What type of signature does it contain?:
                -Physical stamp
                -Handwritten signature
                -Digital signature
            - Is the signature clear and complete?
        </Thinking>

        Give me your final answer inside <Final_Conclusion></Final_Conclusion>, which must follow the following format"

        <Final_Conclusion>
            - Does the APPEAL meet all the requirements?
            - Is the document valid for the appeal process?
        </Final_Conclusion>

        Give me your answer in Spanish or you will be penalized.
        """

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 3. Challenged Act
prompt_challenged_identify = """Analyze the images to identify if they represent a CHALLENGED ACT.

            The CHALLENGED ACT is the administrative act issued by the entity that contains a decision that produces an impact on the administrator and that is the subject of questioning through an appeal.

            For example the refusal of a request, requirement or an application.

            Explain your thoughts inside <Thinking></Thinking> and give me your final answer inside <Answer></Answer> following the next format:

            <Thinking>
                - what is the document about?:
                    - Is it about a refusal decision of a request, requirement or an application?
                    - Is it about an Administrative Resolutions?
                    - Is it contain Official communications informing about a decision?
                    - Is it about Formal communications ending contractual relationships?
                    - Is it about Documents supporting administrative decisions?
            <Thinking>
            
            <Answer>
                <Document>true/false</Document>
                <Start_Page> number of procezssed page by you, where the CHALLENGED ACT started</Start_Page>
            </Answer>"""

prompt_challenged_end_identify = """Analyze the CHALLENGED ACT to find the Signature of the authority, explain your thoughts inside <Thinking></Thinking> and use the following questions to optimize the find:

        <Thinking>
            1.Legibility of the document:
            - Is the text clearly legible?
            - Are there any blurry or illegible parts?
            - Is the quality of the printing or scanning adequate?
            
            2.Signature of the authority:
            - Is the signature present?
            - What type of signature does it contain?:
                -Physical stamp
                -Handwritten signature
                -Digital signature
        </Thinking>

        Give me your final answer inside <Final_Conclusion></Final_Conclusion>, which must follow the following format"

        <Final_Conclusion>
            - Does the CHALLENGED ACT meet all the requirements?
            - Is the document valid for the appeal process?
        </Final_Conclusion>

        Give me your answer in Spanish or you will be penalized.
        """

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 4. Notification Fee of the Challenged Act
prompt_notification_identify = """Analiza el CARGO DE NOTIFICACIÓN DEL ACTO IMPUGNADO siguiendo estos pasos específicos. Para cada elemento, indica si cumple o no cumple, explicando tu razonamiento y observaciones:

Explica tus pensamientos dentro de <Thinking></Thinking> y dame tu respuesta final dentro de <Final_Conclusion></Final_Conclusion>.

<Thinking>
    1.Tipo de documento presentado:
    - ¿Qué tipo de documento es? (identificar entre las siguientes opciones):
        -Acto Impugnado firmado y con fecha
        -Cargo de notificación
        -Constancia de notificación
        -Cédula de notificación
        -Aviso de notificación
        -Aviso o respuesta por Correo Electrónico con el documento adjunto al correo
        -Mensaje por Whatsapp
        -Oficio
        -Observación del hallazgo
        -Algún otro tipo de documento que le informe al administrado por algún medio de lo que le afecta.

    2.Datos del administrado:
    - ¿Está el nombre completo del administrado? (Si es un correo electrónico, normalmente el receptor es el Administrado)
    - ¿Se incluye la dirección del domicilio? (si es notificación personal)
    - ¿Se incluye la dirección de correo electrónico? (solo si es notificación por correo electrónico)
    - Observación del hallazgo

    3.Información del acto administrativo:
    - ¿Se identifica claramente el acto administrativo impugnado? Por Ejemplo: Comunicado de una decisión tomada
    - ¿Se describe su contenido o referencia?
    - Observación del hallazgo

    4.Datos de recepción:
    - ¿Está la fecha de recepción? La fecha puede estar junto a la firma del receptor. Si es un correo es la fecha en la que se envió el correo.
    - ¿Quién recibió el documento? Si solo hay una firma junto a la fecha de recepción, el administrado es el receptor.
    - Si no es el administrado: ¿Se especifica parentesco o relación?
    - Observación del hallazgo

    5.Datos del notificador:
    - ¿Está el nombre completo del personal notificador o de la institución notificadora?
    - ¿Incluye identificación de la entidad?
    - Observación del hallazgo

    6.En caso de notificación bajo puerta:
    - ¿Se incluye la diligencia de las visitas realizadas?
    - ¿Se documentan los intentos de notificación?
    - Observación del hallazgo

    7.En caso de notificación por correo electrónico o por whatsapp:
    - El nombre del Administrado normalmente es el nombre de la persona receptora del correo electrónico o mensaje por whatsapp.
    - No es necesaria una firma (sello/manuscrita/digital).
    - La fecha de recepción es la fecha de envío.     

    8.Firma:
    - ¿Está presente la firma del administrado o de la persona receptora del documento? Puede estar junto a la fecha de recepción en la parte inferior del documento. Si es un correo electrónico no necesita firma.
    - De existir más de una firma, la firma del administrado o del receptor será la que esté junto a la fecha.
    - ¿Qué tipo de firma es? (sello/manuscrita/digital)
    - Observación del hallazgo
</Thinking>

<Final_Conclusion>
    - Resumen de hallazgos
    - ¿El formato cumple con todos los requisitos?
    - Listado de elementos faltantes o incorrectos (si los hay)
<Final_Conclusion>
"""

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 5. Format N°1 of the Administered
prompt_format1_identify= """Analiza el Formato N° 1 DEL ADMINISTRADO siguiendo estos pasos específicos. Para cada elemento, indica si cumple o no cumple, explicando tu razonamiento y observaciones:

Explica tus pensamientos dentro de <Thinking></Thinking> y dame tu respuesta final dentro de <Final_Conclusion></Final_Conclusion>.

<Thinking>
    1.Nombres y apellidos:
    - ¿Están presentes tanto nombres como apellidos?
    - ¿Están escritos de forma completa?
    - Observación del hallazgo

    2.Documento de identidad:
    - Si es DNI: ¿Tiene exactamente 8 dígitos?
    - Si es CE: ¿Tiene exactamente 9 dígitos?
    - ¿Son todos números?
    - Observación del hallazgo

    3.Correo electrónico:
    - ¿Está presente?
    - ¿Tiene formato válido (incluye @ y dominio)?
    - Observación del hallazgo

    4.Número de celular:
    - ¿Tiene exactamente 9 dígitos?
    - ¿Son todos números?
    - Observación del hallazgo

    5.Firma del administrado:
    - ¿Está presente la firma?
    - ¿Qué tipo de firma es (sello/manuscrita/digital)?
    - Observación del hallazgo
<Thinking>

<Final_Conclusion>
    - Resumen de hallazgos
    - ¿El formato cumple con todos los requisitos?
    - Listado de elementos faltantes o incorrectos (si los hay)
<Final_Conclusion>
""" 