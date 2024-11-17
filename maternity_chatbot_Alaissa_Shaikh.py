import streamlit as st
import google.generativeai as genai

# Configure the API key
GOOGLE_API_KEY = 'key'
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-pro')

def get_maternity_response(user_input):
    # Add context about maternity to help guide the model's responses
    context = """You are a knowledgeable and compassionate maternity care assistant. 
    Provide helpful, accurate, and supportive information about pregnancy, childbirth, 
    and early motherhood. Always recommend consulting healthcare providers for medical advice."""
    
    prompt = f"{context}\nUser: {user_input}\nAssistant:"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

# Set up Streamlit page
st.set_page_config(
    page_title="Maternity Care Assistant",
    page_icon="👶",
    layout="centered"
)

# Add custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e6f3ff;
    }
    .bot-message {
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.title("👶 Maternity Care Assistant")
st.markdown("""
Welcome to your personal Maternity Care Assistant! I'm here to provide helpful information 
about pregnancy, childbirth, and early motherhood. Remember that while I can offer general 
guidance, always consult with healthcare professionals for medical advice.
""")

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.container():
        st.markdown(f"""<div class="chat-message {'user-message' if message['role'] == 'user' else 'bot-message'}">
            <b>{'You' if message['role'] == 'user' else 'Assistant'}:</b><br>{message['content']}
            </div>""", unsafe_allow_html=True)

# Add example questions in the sidebar
st.sidebar.title("Example Questions")
example_questions = [
    "What are common early pregnancy symptoms?",
    "How can I prepare for labor?",
    "What should I pack in my hospital bag?",
    "What are some tips for managing morning sickness?",
    "How can I stay healthy during pregnancy?",
    "What are the stages of labor?",
]

# Handle example questions
selected_question = None
for question in example_questions:
    if st.sidebar.button(question):
        selected_question = question
        # Add the selected question to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        # Get bot response
        response = get_maternity_response(question)
        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# User input
user_input = st.text_input("Ask your question here:", key="user_input", placeholder="Type your question here...")

# Handle user input
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get bot response
    response = get_maternity_response(user_input)
    
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to update the chat
    st.rerun()
