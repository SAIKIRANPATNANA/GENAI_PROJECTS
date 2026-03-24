def get_mcq_prompt_template_specific(difficulty_level):
    mcq_easy_prompt_template_specific="""
   Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful multiple-choice questions and their corresponding answers. Keep the questions diverse and thought-provoking.
   Don't use phrases like from the context, based on the context, within in the context in framing questions.
   Context:
   \n {context}\n

   Difficulty Level:
   Easy

   Now generate 10 multiple-choice questions with their answers in the following format:

   1. Craft a question that assesses the reader's understanding of the main idea.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   2. Design a question focusing on a specific detail or concept mentioned in the context.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   3. Formulate a question that requires interpreting the relationship between two key elements in the context.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   4. Create a question challenging readers to make an inference or draw a conclusion.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   5. Develop a question that tests for a nuanced understanding, presenting a statement and asking which part contradicts it.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   6. Pick a term or concept from the passage and ask readers to choose the correct definition.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   7. Design a question about the implications or consequences of the information presented.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   8. Formulate a question that requires connecting the passage to a broader context or real-world application.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   9. Create a question challenging readers to identify a cause-and-effect relationship within the context.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   10. Ask a straightforward question that requires a basic inference based on information provided in the passage.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   Ensure the question is clear, concise, and relevant to the context. The correct answer should align with the information presented in the context. Don't apply any markdown, just simply give me the plain text as the output in the given format.
      """
    mcq_moderate_prompt_template_specific="""
   Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful multiple-choice questions and their corresponding answers. Keep the questions diverse and thought-provoking.
   Don't use phrases like from the context, based on the context, within in the context in framing questions.

   Context:
   \n {context}\n

   Difficulty Level:
   Moderate

   Now generate 10 multiple-choice questions with their answers in the following format:

   1. Craft a question that assesses the reader's understanding of the main idea.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   2. Design a question focusing on a specific detail or concept mentioned in the context.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   3. Formulate a question that requires interpreting the relationship between two key elements in the context.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   4. Create a question challenging readers to make an inference or draw a conclusion.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   5. Develop a question that tests for a nuanced understanding, presenting a statement and asking which part contradicts it.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   6. Pick a term or concept from the passage and ask readers to choose the correct definition.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   7. Design a question about the implications or consequences of the information presented.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   8. Formulate a question that requires connecting the passage to a broader context or real-world application.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   9. Create a question challenging readers to identify a cause-and-effect relationship within the context.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   10. Ask a straightforward question that requires a basic inference based on information provided in the passage.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   Ensure the question is clear, concise, and relevant to the context. The correct answer should align with the information presented in the context. Don't apply any markdown, just simply give me the plain text as the output in the given format.
      """
    mcq_tough_prompt_template_specific = """
   Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful multiple-choice questions and their corresponding answers. Keep the questions diverse and thought-provoking.
   Don't use phrases like from the context, based on the context, within in the context in framing questions.

   Context:
   \n {context}\n

   Difficulty Level:
   Tough

   Now generate 10 multiple-choice questions with their answers in the following format:

   1. Craft a question that assesses the reader's understanding of the main idea.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   2. Design a question focusing on a specific detail or concept mentioned in the document.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   3. Formulate a question that requires interpreting the relationship between two key elements in the .
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   4. Create a question challenging readers to make an inference or draw a conclusion.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   5. Develop a question that tests for a nuanced understanding, presenting a statement and asking which part contradicts it.
      a) Option A
      b) Option B
      c) Option C
      d) Option D
   Answer: write only right answer option here like if it a) then write a

   6. Pick a term or concept from the passage and ask readers to choose the correct definition.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   7. Design a question about the implications or consequences of the information presented.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   8. Formulate a question that requires connecting the passage to a broader context or real-world application.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   9. Create a question challenging readers to identify a cause-and-effect relationship within the context.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   10. Ask a straightforward question that requires a basic inference based on information provided in the passage.
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   Ensure the question is clear, concise, and relevant to the context. The correct answer should align with the information presented in the context. Don't apply any markdown, just simply give me the plain text as the output in the given format.
      """
    if difficulty_level == 'easy':
        return mcq_easy_prompt_template_specific
    elif difficulty_level == 'moderate':
      return mcq_moderate_prompt_template_specific
    else:
      return mcq_tough_prompt_template_specific

# def get_mcq_prompt_template_general(context,difficulty_level):
#     mcq_easy_prompt_template_general = f'''
#     Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful multiple-choice questions and their corresponding answers. Keep the questions diverse and thought-provoking.
#     Don't use phrases like from the context, based on the context, within in the context in framing questions.

#     Context: {context}
#     Difficulty Level: Easy

#     Now generate only one multiple-choice question with its answer in the following format:

#     Q) write question here
#     a) Option A
#     b) Option B
#     c) Option C
#     d) Option D
#     Answer: write answer here

#     Ensure the question is clear, concise, and relevant to the context. The correct answer should align with the information presented in the context.
#     '''
#     mcq_moderate_prompt_template_general = f'''
#     Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful multiple-choice questions and their corresponding answers. Keep the questions diverse and thought-provoking.
#     Don't use phrases like from the context, based on the context, within in the context in framing questions.

#     Context: {context}
#     Difficulty Level: Easy

#     Now generate only one multiple-choice question with its answer in the following format:

#     Q) write question here
#     a) Option A
#     b) Option B
#     c) Option C
#     d) Option D
#     Answer: write answer here

#     Ensure the question is clear, concise, and relevant to the context. The correct answer should align with the information presented in the context.
#     '''
#     mcq_tough_prompt_template_general = f'''
#     Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful multiple-choice questions and their corresponding answers. Keep the questions diverse and thought-provoking.
#     Don't use phrases like from the context, based on the context, within in the context in framing questions.

#     Context: {context}
#     Difficulty Level: Tough

#     Now generate only one multiple-choice question with its answer in the following format:

#     Q) write question here
#     a) Option A
#     b) Option B
#     c) Option C
#     d) Option D
#     Answer: write answer here

#     Ensure the question is clear, concise, and relevant to the context. The correct answer should align with the information presented in the context.
#     '''
#     if(difficulty_level=='easy'):
#       return mcq_easy_prompt_template_general
#     elif(difficulty_level=='moderate'):
#       return mcq_moderate_prompt_template_general
#     return mcq_tough_prompt_template_general
def get_mcq_prompt_template_general(context,difficulty_level):
   mcq_easy_prompt_template_general = f'''
   Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful multiple-choice questions and their corresponding answers. Keep the questions diverse and thought-provoking.
   Don't use phrases like from the context, based on the context, within in the context in framing questions.

   Context: {context}
   Difficulty Level: Easy

   Now generate only ten multiple-choice questions with their answers in the following format:

   1. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it is a) then write a

   2. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   3. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   4. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   5. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   6. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   7. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   8. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   9. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   10. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   Ensure the question is clear, concise, and relevant to the context. The correct answer should align with the information presented in the context. Don't apply any markdown, just simply give me the plain text as the output in the given format.
   '''
   mcq_moderate_prompt_template_general = f'''
   Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful multiple-choice questions and their corresponding answers. Keep the questions diverse and thought-provoking.
   Don't use phrases like from the context, based on the context, within in the context in framing questions.

   Context: {context}
   Difficulty Level: Easy

   Now generate only ten multiple-choice questions with their answers in the following format:

   1. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   2. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   3. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   4. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   5. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   6. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   7. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   8. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   9. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   10. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   Ensure the question is clear, concise, and relevant to the context. The correct answer should align with the information presented in the context. Don't apply any markdown, just simply give me the plain text as the output in the given format.
   '''
   mcq_tough_prompt_template_general = f'''
   Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful multiple-choice questions and their corresponding answers. Keep the questions diverse and thought-provoking.
   Don't use phrases like from the context, based on the context, within in the context in framing questions.

   Context: {context}
   Difficulty Level: Tough

   Now generate only ten multiple-choice questions with their answers in the following format:

   1. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   2. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   3. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   4. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a


   5. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   6. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   7. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   8. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   9. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   10. write question here
   a) Option A
   b) Option B
   c) Option C
   d) Option D
   Answer: write only right answer option here like if it a) then write a

   Ensure the question is clear, concise, and relevant to the context. The correct answer should align with the information presented in the context. Don't apply any markdown, just simply give me the plain text as the output in the given format.
   '''
   if(difficulty_level=='easy'):
      return mcq_easy_prompt_template_general
   elif(difficulty_level=='moderate'):
      return mcq_moderate_prompt_template_general
   return mcq_tough_prompt_template_general

def get_qa_prompt_template_specific(difficulty_level):
    qa__easy_prompt_template_specific="""
   Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful description answer type questions. Keep the questions diverse and thought-provoking.
   Don't use phrases like from the context, based on the context, within in the context in framing questions.

   Context:
   \n {context}\n

   Difficulty Level:
   Easy

   Now generate 5 description answer type questions with their answers in the following format:

   1. Craft a question that assesses the reader's understanding of the main idea.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   2. Design a question focusing on a specific detail or concept mentioned in the context.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   3. Formulate a question that requires interpreting the relationship between two key elements in the context.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   4. Create a question challenging readers to make an inference or draw a conclusion.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   5. Develop a question that tests for a nuanced understanding, presenting a statement and asking which part contradicts it.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   Feel free to be creative and insightful! Your questions and answers will contribute to an engaging quiz experience. Don't apply any markdown, just simply give me the plain text as the output in the given format.
      """
    qa__moderate_prompt_template_specific="""
   Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful description answer type questions. Keep the questions diverse and thought-provoking.
   Don't use phrases like from the context, based on the context, within in the context in framing questions.

   Context:
   \n {context}\n

   Difficulty Level:
   Moderate

   Now generate 5 description answer type questions with their answers in the following format:

   1. Evaluate the implications or consequences of the information presented.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   2. Connect the passage to a broader context or real-world application.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   3. Identify a cause-and-effect relationship within the context.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   4. Analyze the significance of a particular detail or concept mentioned in the context.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   5. Compare and contrast different aspects or elements presented in the passage.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   Feel free to be creative and insightful! Your questions and answers will contribute to an engaging quiz experience. Don't apply any markdown, just simply give me the plain text as the output in the given format.
      """
    qa__tough_prompt_template_specific="""
   Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful description answer type questions. Keep the questions diverse and thought-provoking.
   Don't use phrases like from the context, based on the context, within in the context in framing questions.

   Context:
   \n {context}\n

   Difficulty Level:
   Tough

   Now generate 5 description answer type questions with their answers in the following format:

   1. Critically evaluate the author's argument or viewpoint presented in the context.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   2. Assess the reliability or credibility of the information provided.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   3. Investigate the potential limitations or biases in the passage.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   4. Propose alternative interpretations or perspectives on the topic discussed.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   5. Analyze the implications of the information presented for future research or action.
      - Question: [Model-Generated Question]
      - Answer: [Model-Generated Answer]

   Feel free to be creative and insightful! Your questions and answers will contribute to an engaging quiz experience. Don't apply any markdown, just simply give me the plain text as the output in the given format.
      """
    if difficulty_level == 'easy':
        return qa__easy_prompt_template_specific
    elif difficulty_level == 'moderate':
      return qa__moderate_prompt_template_specific
    else:
      return qa__tough_prompt_template_specific

# def get_qa_prompt_template_general(context, difficulty_level):
#     qa_easy_prompt_template_general = f'''
#         Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful descriptive answer-type questions. Keep the questions diverse and thought-provoking.
#         Don't use phrases like from the context, based on the context, within in the context in framing questions.

#         Context: {context}
#         Difficulty Level: Easy

#         Now generate only one descriptive answer-type question with its answer in the following format:

#         - Question: Write your question here.

#         - Answer: Write your answer here.

#         Ensure the question is clear, concise, and relevant to the context. The answer should align with the information presented in the context.
#         '''
#     qa_moderate_prompt_template_general = f'''
#         Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful descriptive answer-type questions. Keep the questions diverse and thought-provoking.
#         Don't use phrases like from the context, based on the context, within in the context in framing questions.

#         Context: {context}
#         Difficulty Level: Moderate

#         Now generate only one descriptive answer-type question with its answer in the following format:

#         - Question: Write your question here.

#         - Answer: Write your answer here.

#         Ensure the question is clear, concise, and relevant to the context. The answer should align with the information presented in the context.
#         '''
#     qa_tough_prompt_template_general = f'''
#         Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful descriptive answer-type questions. Keep the questions diverse and thought-provoking.
#         Don't use phrases like from the context, based on the context, within in the context in framing questions.

#         Context: {context}
#         Difficulty Level: Tough

#         Now generate only one descriptive answer-type question with its answer in the following format:

#         - Question: Write your question here.

#         - Answer: Write your answer here.

#         Ensure the question is clear, concise, and relevant to the context. The answer should align with the information presented in the context.
#         '''
#     if difficulty_level == 'easy':
#         return qa_easy_prompt_template_general
#     elif difficulty_level == 'moderate':
#         return qa_moderate_prompt_template_general
#     return qa_tough_prompt_template_general
def get_qa_prompt_template_general(context, difficulty_level):
   qa_easy_prompt_template_general = f'''
      Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful descriptive answer-type questions. Keep the questions diverse and thought-provoking.
      Don't use phrases like from the context, based on the context, within in the context in framing questions.

      Context: {context}
      Difficulty Level: Easy

      Now generate only five descriptive answer-type questions with their answers in the following format:

      1. Craft a question that assesses the reader's understanding of the main idea.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      2. Design a question focusing on a specific detail or concept mentioned in the context.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      3. Formulate a question that requires interpreting the relationship between two key elements in the context.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      4. Create a question challenging readers to make an inference or draw a conclusion.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      5. Develop a question that tests for a nuanced understanding, presenting a statement and asking which part contradicts it.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]
         
      Ensure the question is clear, concise, and relevant to the context. The answer should align with the information presented in the context. Don't apply any markdown, just simply give me the plain text as the output in the given format.
               '''
   qa_moderate_prompt_template_general = f'''
      Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful descriptive answer-type questions. Keep the questions diverse and thought-provoking.
      Don't use phrases like from the context, based on the context, within in the context in framing questions.

      Context: {context}
      Difficulty Level: Moderate

      Now generate only five descriptive answer-type questions with their answers in the following format:

      1. Craft a question that assesses the reader's understanding of the main idea.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      2. Design a question focusing on a specific detail or concept mentioned in the context.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      3. Formulate a question that requires interpreting the relationship between two key elements in the context.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      4. Create a question challenging readers to make an inference or draw a conclusion.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      5. Develop a question that tests for a nuanced understanding, presenting a statement and asking which part contradicts it.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      Ensure the question is clear, concise, and relevant to the context. The answer should align with the information presented in the context. Don't apply any markdown, just simply give me the plain text as the output in the given format.
      '''
   qa_tough_prompt_template_general = f'''
      Imagine you are creating a quiz based on the following context by maintaining the below specified difficulty level. Your goal is to generate insightful descriptive answer-type questions. Keep the questions diverse and thought-provoking.
      Don't use phrases like from the context, based on the context, within in the context in framing questions.

      Context: {context}
      Difficulty Level: Tough

      Now generate only five descriptive answer-type questions with their answers in the following format:

      1. Craft a question that assesses the reader's understanding of the main idea.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      2. Design a question focusing on a specific detail or concept mentioned in the context.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      3. Formulate a question that requires interpreting the relationship between two key elements in the context.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      4. Create a question challenging readers to make an inference or draw a conclusion.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      5. Develop a question that tests for a nuanced understanding, presenting a statement and asking which part contradicts it.
         - Question: [Model-Generated Question]
         - Answer: [Model-Generated Answer]

      Ensure the question is clear, concise, and relevant to the context. The answer should align with the information presented in the context. Don't apply any markdown, just simply give me the plain text as the output in the given format.
      '''
   if difficulty_level == 'easy':
      return qa_easy_prompt_template_general
   elif difficulty_level == 'moderate':
      return qa_moderate_prompt_template_general
   return qa_tough_prompt_template_general
