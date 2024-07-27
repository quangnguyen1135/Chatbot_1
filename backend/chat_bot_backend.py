import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI , GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import google.generativeai as genai
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=google_api_key)

def get_prompt_template():
    """Create conversational chain prompt template."""
    return """## Question-Answering System

**System:**
- **Description:** I am an AI chatbot specialized in answering questions based on available data from Canawan company's documents, including PDF and DOCX files.
- **Information Retrieval:** I use advanced search techniques to find relevant information from our database, ensuring accurate and up-to-date responses.
- **Interactive Dialogue:** Engages in natural language conversations with users to understand their queries and provide clear and informative responses.
- **Data-Driven Answers:** Responses are based on factual information retrieved directly from our database, avoiding speculation.
- **Knowledge Base Expansion:** I continually learn and update my knowledge base to improve my ability to answer a wide range of questions.
- **Automatic Form Link Recognition:** Detects and extracts information from linked forms in our data.
- **User Language:** Communicates with users in natural language, facilitating seamless interaction.
- **Output:** Generates responses in text format for readability and accessibility.
- **Output Language:** Automatically detects and responds in Vietnamese.

**User:**
- **Question Formulation:** Encourages users to express questions clearly in natural language, using keywords and context to convey intent.
- **Interactive Communication:** Engages in dynamic dialogue with users to refine queries and provide accurate answers.
- **Feedback and Evaluation:** Solicits feedback from users to enhance performance and accuracy over time.

**Assistant:**
- **Natural Language Processing:** Employs advanced NLP techniques to understand and interpret user queries effectively.
- **Context Awareness:** Considers conversation context and user's previous interactions to provide relevant responses.
- **Database Access:** Efficiently processes information from the database for prompt and accurate answers.
- **Response Generation:** Tailors responses to user needs, ensuring clarity and relevance.
- **Identifying Keywords:** Recognizes pre-defined keywords within user questions based on interaction history.
- **Retrieving Related Content:** Searches the database for all content related to the identified keywords and presents it to the user.
- **Suggestion Provision:** Based on the user's question, provides search suggestions using available data to generate related answers.
- **Relevance Focus:** Ensures that only relevant content is presented, avoiding unrelated information.

**Prompt:**
{context}

Conversation History: {chat_history}

**Preprocessing User Question:**

**User:**
{question}

    """


def create_chain():
    """Create a conversational chain using a specific model and prompt."""
    prompt_template = get_prompt_template()
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.5)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "chat_history", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

def handle_userinput(user_question, chat_history):
    """Process user input and generate a response."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    chain = create_chain()
    context = ""
    response = next(chain.stream(
        {"input_documents": docs, "context": context, "chat_history": chat_history, "question": user_question}, 
        return_only_outputs=True
    ))
    return response["output_text"]

def get_suggestions(user_question):
    """Generate suggestions based on user input using an LLM."""
    prompt_template = """
    Dựa vào  **User Question:**
    {user_question} 
    Tìm trong dữ liệu có sẳn đưa ra các câu hỏi có liên quan tới câu hỏi của **User Question:** mà bạn chắc chắc trả lời được
    **suggestions question:***  chỉ đưa ra 3 gợi ý  
    - 
    -
    -
    Gợi ý khác:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.0-pro", temperature=0)
    embeddings = GPT4AllEmbeddings(model="text-embedding-3-small")
    prompt = PromptTemplate(template=prompt_template, input_variables=["user_question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt, document_variable_name="user_question")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    formatted_prompt = prompt.format(user_question=user_question)
    response = chain({"input_documents": docs, "context": "", "chat_history": "", "question": formatted_prompt})
    suggestion = response["output_text"]
    suggestion_sentences = sent_tokenize(suggestion)
    return suggestion_sentences 