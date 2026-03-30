import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
def getResponse():
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        file_id = genai.upload_file(path='h.pdf')
        user_input = """
        **1. Synopsis (3 Pages):**
        Create a detailed, clear, and coherent synopsis of the content in the file. The synopsis should:
        - Provide an organized summary of the key concepts, themes, and insights.
        - Maintain logical flow and cover all major topics comprehensively.
        - Be at least two pages long, written in an engaging and professional tone.

        **2. Keywords and Definitions (2 Page):**
        Generate a list of relevant keywords from the file, along with their definitions. The list should:
        - Highlight the most important terms and concepts discussed in the file.
        - Include concise definitions for each keyword, providing a clear understanding of their meanings and context.

        **Output Requirements:**
        - Structure the responses in the given order (Synopsis, Keywords and Definitions).
        - Ensure the content is logical, comprehensive, and written in a professional tone.
        """
        response = model.generate_content([file_id, user_input])
        return response.text
    except Exception as e:
        print(e)
