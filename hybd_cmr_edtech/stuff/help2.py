
import google.generativeai as genai
genai.configure(api_key='AIzaSyCJW8en5jWYmvnsiGwICUkfvccVuXFVcm4')
def getResponse():
    try: 
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        file_id = genai.upload_file(path='h.pdf')
        user_input = """
    **3. Short-Answer Questions (10):**
        Formulate ten short-answer questions focusing on key points or concepts from the file. Each question should:
        - Be precise and test comprehension of specific ideas.
        - Have direct, concise answers (1-2 sentences) that capture the essence of the concept.

        **4. Long-Answer Questions (6):**
        Create six long-answer questions based on the major themes, topics, or insights in the file. Each question should:
        - Require detailed and in-depth answers.
        - Include answers with thorough explanations, relevant examples, and illustrations where applicable.
        - Be structured into at least 2-3 paragraphs per answer for comprehensive coverage.

        **5. Multiple-Choice Questions (20):**
        Develop a set of twenty multiple-choice questions (MCQs) covering the file’s content. Each question should:
        - Test various aspects of the material, including definitions, concepts, applications, and examples.
        - Provide four answer choices, with the correct answer clearly marked.
        - Include questions ranging from basic recall to advanced analytical understanding.

        **Output Requirements:**
        - Structure the responses in the given order (Short-Answer Questions, Long-Answer Questions, and MCQs).
        - Ensure the content is logical, comprehensive, and written in a professional tone.
            """
        response = model.generate_content([file_id, user_input])
        return response.text
    except Exception as e:
        print(e)