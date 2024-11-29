import streamlit as st


# Configure page - this must be the first Streamlit command
st.set_page_config(
    page_title="Promise Care - Emotional Maternity Support",
    page_icon="💌",
    layout="wide",
    initial_sidebar_state="expanded"
)


import google.generativeai as genai
from datetime import datetime
import json
import random
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from PIL import Image
import io


# Configure Google Gemini API
GOOGLE_API_KEY = "AIzaSyCK52fieOP6EfzKM4uiULmrDdfs5A8KWoI"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')


def get_ai_response(prompt, chat_history):
    # Prepare context from chat history
    context = "\n".join([f"User: {msg['user']}\nAssistant: {msg['assistant']}"
                        for msg in chat_history[-3:]])
   
    # Construct the full prompt with specialized focus
    full_prompt = f"""You are a compassionate AI assistant specializing in supporting second-time pregnant women who have experienced previous miscarriage(s).
Your role is to provide emotional support, evidence-based information, and gentle guidance while being extremely sensitive to their past experiences and current anxieties.


Previous conversation:
{context}


Current question: {prompt}


Remember to:
1. Be extremely empathetic and acknowledge the emotional complexity of pregnancy after loss
2. Provide evidence-based information with extra sensitivity
3. Always encourage regular consultation with healthcare providers
4. Use gentle, supportive language
5. Focus on both emotional and physical well-being
6. Validate feelings of anxiety while offering coping strategies
7. Emphasize that each pregnancy is different
8. Include positive affirmations when appropriate
9. Mention the importance of support networks
10. Be mindful of potentially triggering language


Important: Never start your response with any prefix like 'AI Assistant:' or 'Empathetic AI Assistant:'. Just provide your response directly, with a small greet"""


    try:
        response = model.generate_content(full_prompt)
        # Remove any potential AI Assistant prefix if it still appears
        response_text = response.text
        if "AI Assistant:" in response_text:
            response_text = response_text.split("AI Assistant:", 1)[1].strip()
        if "Empathetic AI Assistant:" in response_text:
            response_text = response_text.split("Empathetic AI Assistant:", 1)[1].strip()
        return response_text
    except Exception as e:
        return f"I apologize, but I encountered an error. Please try again or rephrase your question. Error: {str(e)}"




# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'journal_entries' not in st.session_state:
    st.session_state.journal_entries = []
if 'mood_history' not in st.session_state:
    st.session_state.mood_history = []
if 'recent_activities' not in st.session_state:
    st.session_state.recent_activities = []
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'last_check_in' not in st.session_state:
    st.session_state.last_check_in = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'profile_pic' not in st.session_state:
    st.session_state.profile_pic = None
if 'due_date' not in st.session_state:
    st.session_state.due_date = datetime.now()
if 'email' not in st.session_state:
    st.session_state.email = ""
if 'custom_affirmations' not in st.session_state:
    st.session_state.custom_affirmations = []
if 'mood_logs' not in st.session_state:
    st.session_state.mood_logs = []
if 'goals' not in st.session_state:
    st.session_state.goals = []
if 'feedback_history' not in st.session_state:
    st.session_state.feedback_history = []
if 'selected_mood' not in st.session_state:
    st.session_state.selected_mood = None

# Daily affirmations
DAILY_AFFIRMATIONS = [
    "You are strong and capable of handling this journey.",
    "Each day brings new hope and strength.",
    "Your body knows how to grow this precious life.",
    "You are creating a miracle.",
    "You are glowing with maternal energy.",
    "Trust your instincts and your body.",
    "You are prepared for this beautiful journey.",
    "Every day you grow stronger as a mother.",
    "Your baby feels your love and strength.",
    "You are surrounded by support and love."
]


def get_daily_affirmation():
    # Get today's date as a seed for consistent daily affirmation
    today = datetime.now().date()
    # Combine default and custom affirmations
    all_affirmations = DAILY_AFFIRMATIONS + list(st.session_state.custom_affirmations)
    # Use the date to select an affirmation
    seed = int(today.strftime("%Y%m%d"))
    random.seed(seed)
    affirmation = random.choice(all_affirmations)
    random.seed()  # Reset the seed
    return affirmation


# Daily quotes and tips
DAILY_QUOTES = [
    "Your strength is greater than any challenge ahead. 💪",
    "Every day is a new beginning. 🌅",
    "Trust your journey. 🌸",
    "You are doing amazing! 🌟",
    "Take it one day at a time. 🍃",
    "Your baby feels your love. 💝",
    "Breathe in peace, breathe out stress. 🧘‍♀️",
    "You've got this, mama! 👑"
]


DAILY_TIPS = [
    "Stay hydrated throughout the day! 💧",
    "Take short walks when you feel up to it. 🚶‍♀️",
    "Practice gentle stretching. 🧘‍♀️",
    "Get plenty of rest. 😴",
    "Eat small, frequent meals. 🥗",
    "Connect with other moms. 👯‍♀️",
    "Keep track of your baby's movements. 👶",
    "Don't forget your prenatal vitamins! 💊"
]


# Extended moods with emojis and activities
MOODS = {
    "😊 Happy": {
        "description": "joyful and excited",
        "activities": [
            "Take bump photos with creative weekly pregnancy signs",
            "Work on your baby's scrapbook or memory book",
            "Shop online for cute maternity outfits",
            "Plan and organize your baby's nursery",
            "Listen to your baby's heartbeat recording",
            "Browse and save baby names you love",
            "Watch pregnancy vlogs or join mom groups",
            "Create a fun pregnancy announcement if you haven't yet"
        ]
    },
    "🥰 Loved": {
        "description": "supported and cherished",
        "activities": [
            "Have your partner read to the baby",
            "Create a playlist for the baby together",
            "Plan a babymoon with your partner",
            "Take maternity photos with loved ones",
            "Have a date night with pregnancy-safe foods",
            "Start a family traditions wishlist",
            "Record video messages for the baby",
            "Create a family tree for your little one"
        ]
    },
    "😌 Peaceful": {
        "description": "calm and content",
        "activities": [
            "Try pregnancy-safe yoga poses",
            "Listen to guided pregnancy meditations",
            "Sit in your nursery and imagine life with baby",
            "Gently massage your bump with oil",
            "Practice deep breathing exercises",
            "Write in your pregnancy journal",
            "Take a warm (not hot) bath",
            "Go for a gentle walk in nature"
        ]
    },
    "😔 Anxious": {
        "description": "worried or uncertain",
        "activities": [
            "Practice mindful breathing exercises",
            "Talk to your healthcare provider",
            "Join a pregnancy after loss support group",
            "Write down your feelings and fears",
            "Do gentle stretching or prenatal yoga",
            "Listen to calming pregnancy affirmations",
            "Connect with other moms who understand",
            "Create a list of positive pregnancy milestones"
        ]
    },
    "😢 Sad": {
        "description": "feeling down or blue",
        "activities": [
            "Talk to a trusted friend or family member",
            "Schedule a counseling session",
            "Practice gentle self-care activities",
            "Write down your feelings",
            "Listen to uplifting music",
            "Take a warm bath",
            "Watch your favorite comfort movie",
            "Join a pregnancy support group"
        ]
    },
    "✨ Hopeful": {
        "description": "feeling optimistic and positive",
        "activities": [
            "Start a pregnancy milestone journal",
            "Create a vision board for your nursery",
            "Make a playlist for your baby",
            "Browse through positive birth stories",
            "Plan a small celebration for each trimester",
            "Take weekly progression photos",
            "Write letters to your future baby",
            "Join positive pregnancy support communities"
        ]
    },
    "⚡ Energetic": {
        "description": "feeling active and motivated",
        "activities": [
            "Try pregnancy-safe workout routines",
            "Organize the baby's room or clothes",
            "Start a pregnancy-friendly hobby",
            "Plan and prep healthy meals",
            "Take a prenatal exercise class",
            "Go for a nature walk",
            "Dance to your favorite music",
            "Work on a baby-related DIY project"
        ]
    },
    "🤢 Nauseous": {
        "description": "feeling queasy or sick",
        "activities": [
            "Try eating crackers or dry toast before getting out of bed",
            "Sip on warm ginger tea with honey",
            "Keep a stash of pregnancy-friendly candies (like sour drops) in your bag",
            "Try the BRAT diet (Bananas, Rice, Applesauce, Toast)",
            "Use a pregnancy pillow for comfortable rest",
            "Keep ice chips or pregnancy pops handy",
            "Have small meals every 2-3 hours",
            "Try lemon-infused water or sprite for quick relief"
        ]
    },
    "😤 Frustrated": {
        "description": "feeling irritated or annoyed",
        "activities": [
            "Try pregnancy-safe stretches for back pain",
            "Use a maternity belt for support",
            "Get a prenatal massage from a certified therapist",
            "Do gentle pregnancy exercises on YouTube",
            "Use ice packs or heat pads for comfort",
            "Take a break with your favorite snacks",
            "Chat with other moms about their experiences",
            "Look at your baby's ultrasound pictures"
        ]
    },
    "🥺 Overwhelmed": {
        "description": "feeling too much to handle",
        "activities": [
            "Put your feet up and watch your favorite comfort show",
            "Order grocery delivery instead of shopping",
            "Ask partner/family to help with household chores",
            "Take a warm (not hot) bubble bath",
            "Use a pregnancy app to track one thing at a time",
            "Join online pregnancy support groups",
            "Take a power nap - even 15 minutes helps",
            "Make a list of questions for your next doctor visit"
        ]
    },
    "🤩 Excited": {
        "description": "feeling enthusiastic and eager",
        "activities": [
            "Take bump photos with creative weekly pregnancy signs",
            "Work on your baby's scrapbook or memory book",
            "Shop online for cute maternity outfits",
            "Plan and organize your baby's nursery",
            "Listen to your baby's heartbeat recording",
            "Browse and save baby names you love",
            "Watch pregnancy vlogs or join mom groups",
            "Create a fun pregnancy announcement if you haven't yet"
        ]
    },
    "😇 Blessed": {
        "description": "feeling grateful and thankful",
        "activities": [
            "Write a gratitude list",
            "Share your joy with loved ones",
            "Take milestone photos",
            "Create pregnancy memories",
            "Plan a celebration",
            "Write letters to your baby",
            "Start a family tradition",
            "Make a pregnancy scrapbook"
        ]
    }
}


def get_daily_quote():
    day_of_year = datetime.now().timetuple().tm_yday
    return DAILY_QUOTES[day_of_year % len(DAILY_QUOTES)]


def get_daily_tip():
    day_of_year = datetime.now().timetuple().tm_yday
    return DAILY_TIPS[day_of_year % len(DAILY_TIPS)]


def add_activity(activity_type, description):
    st.session_state.recent_activities.insert(0, {
        "type": activity_type,
        "description": description,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # Keep only last 20 activities
    st.session_state.recent_activities = st.session_state.recent_activities[:20]


# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #FFF0F5;  /* Light pink color */
    }
    .main {
        padding: 20px;
        border-radius: 10px;
        background-color: #FFF0F5;
    }
   
    .profile-pic {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        margin: 10px auto;
        display: block;
        border: 3px solid #FFB6C1;
    }
   
    .sidebar {
        padding: 20px;
        background-color: #FFE4E1;
        border-radius: 10px;
    }
   
    .chat-message {
        padding: 10px;
        margin: 5px;
        border-radius: 10px;
    }
   
    .user-message {
        background-color: #FFE4E1;
    }
   
    .bot-message {
        background-color: #FFF0F5;
    }
   
    .mood-tracker {
        margin: 20px 0;
    }
   
    .stButton>button {
        background-color: #FFB6C1 !important;
        color: black !important;
        border: none !important;
        padding: 10px !important;
        border-radius: 5px !important;
        margin: 5px !important;
        font-weight: 500 !important;
    }
   
    .stButton>button:hover {
        background-color: #FF69B4 !important;
        color: black !important;
    }
   
    div[data-testid="stFileUploadDropzone"] {
        background-color: #FFE4E1 !important;
        border: 2px dashed #FFB6C1 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
   
    div[data-testid="stImage"] img {
        border-radius: 50% !important;
        border: 3px solid #FFB6C1 !important;
    }
    /* Mood button container */
    .mood-buttons-container {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 12px !important;
        justify-content: center !important;
        margin: 25px 0 !important;
        padding: 15px !important;
        background-color: rgba(255, 255, 255, 0.5) !important;
        border-radius: 15px !important;
        box-shadow: 0 2px 10px rgba(255, 182, 193, 0.2) !important;
    }

    /* Individual mood button */
    .mood-button {
        background-color: #FFE6EA !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 24px !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        flex: 0 1 calc(20% - 12px) !important;
        text-align: center !important;
        min-width: 130px !important;
        box-shadow: 0 2px 5px rgba(255, 182, 193, 0.3) !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        color: #333 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
    }

    .mood-button:hover {
        background-color: #FFB6C1 !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 4px 12px rgba(255, 182, 193, 0.4) !important;
    }

    .mood-button:active {
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(255, 182, 193, 0.3) !important;
    }

    .mood-button.selected {
        background-color: #FFB6C1 !important;
        color: #000 !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(255, 182, 193, 0.5) !important;
        border: 2px solid #FF69B4 !important;
    }

    /* Emoji in mood button */
    .mood-button span {
        font-size: 20px !important;
        line-height: 1 !important;
    }

    /* Make buttons responsive */
    @media (max-width: 992px) {
        .mood-button {
            flex: 0 1 calc(25% - 12px) !important;
        }
    }

    @media (max-width: 768px) {
        .mood-button {
            flex: 0 1 calc(33.33% - 12px) !important;
            min-width: 110px !important;
            font-size: 14px !important;
        }
        .mood-buttons-container {
            gap: 10px !important;
            padding: 12px !important;
        }
    }

    @media (max-width: 480px) {
        .mood-button {
            flex: 0 1 calc(50% - 10px) !important;
            padding: 10px 20px !important;
        }
        .mood-buttons-container {
            gap: 8px !important;
            padding: 10px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for chat interface
st.markdown("""
<style>
    /* Remove white box behind chat input */
    .stChatInput, 
    .stChatInput > div,
    .stChatInput > div > div,
    .stChatInput iframe,
    .stChatInput [data-testid="stChatInput"] {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #FFE6EA !important; /* Light pink for user messages */
    }
    .bot-message {
        background-color: #FFD1DC !important; /* Slightly darker pink for assistant messages */
        margin-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for success stories
st.markdown("""
<style>
    /* Success Stories styling */
    .success-story {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        border-left: 5px solid #FFB6C1;
        background-color: #FFF0F5;
    }
    .story-title {
        color: #FF69B4;
        font-size: 1.3rem;
        margin-bottom: 1rem;
    }
    .story-quote {
        font-style: italic;
        padding: 1rem;
        background-color: #FFE4E1;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #696969;
    }
    .story-message {
        color: #4A4A4A;
        line-height: 1.6;
    }
    .story-divider {
        border: none;
        height: 2px;
        background: linear-gradient(to right, #FFB6C1, transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for pink buttons
st.markdown("""
<style>
    button[kind="secondary"] {
        background-color: #FFB6C1 !important;
    }
    div.stButton > button:first-child {
        background-color: #FFB6C1 !important;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for info boxes
st.markdown("""
<style>
    /* Override Streamlit's info box color */
    div[data-baseweb="notification"] {
        background-color: #FFE4E1 !important;
        border: 2px solid #FFB6C1 !important;
    }
    
    div[data-baseweb="notification"] div {
        color: #333333 !important;
    }
    
    .element-container div[data-stale="false"] .stAlert {
        background-color: #FFE4E1 !important;
        border-color: #FFB6C1 !important;
    }
    
    .element-container div[data-stale="false"] .stAlert > div {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)


# Get time-based greeting
def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"


# Update check-in streak
def update_streak():
    today = datetime.now().date()
    if st.session_state.last_check_in:
        last_date = datetime.strptime(st.session_state.last_check_in, "%Y-%m-%d").date()
        if today - last_date == timedelta(days=1):
            st.session_state.streak += 1
        elif today - last_date > timedelta(days=1):
            st.session_state.streak = 1
    else:
        st.session_state.streak = 1
    st.session_state.last_check_in = today.strftime("%Y-%m-%d")


# Get mood-based suggestions
def get_mood_suggestions(mood):
    suggestions = {
        "😊 Happy": [
            "Take bump photos with creative weekly pregnancy signs",
            "Work on your baby's scrapbook or memory book",
            "Shop online for cute maternity outfits",
            "Plan and organize your baby's nursery",
            "Listen to your baby's heartbeat recording",
            "Browse and save baby names you love",
            "Watch pregnancy vlogs or join mom groups",
            "Create a fun pregnancy announcement if you haven't yet"
        ],
        "🥰 Loved": [
            "Have your partner read to the baby",
            "Create a playlist for the baby together",
            "Plan a babymoon with your partner",
            "Take maternity photos with loved ones",
            "Have a date night with pregnancy-safe foods",
            "Start a family traditions wishlist",
            "Record video messages for the baby",
            "Create a family tree for your little one"
        ],
        "😌 Peaceful": [
            "Try pregnancy-safe yoga poses",
            "Listen to guided pregnancy meditations",
            "Sit in your nursery and imagine life with baby",
            "Gently massage your bump with oil",
            "Play calming music for the baby",
            "Take a gentle walk in nature",
            "Practice hypnobirthing techniques",
            "Write in your pregnancy journal"
        ],
        "🤗 Grateful": [
            "Take weekly bump progression photos",
            "Write thank-you notes to your medical team",
            "Make a list of pregnancy milestones achieved",
            "Create a baby registry with joy",
            "Share ultrasound photos with close family",
            "Plan a small celebration for each trimester",
            "Make a pregnancy timeline scrapbook",
            "Start a 'Letters to My Baby' journal"
        ],
        "😢 Sad": [
            "Talk to a trusted friend or family member",
            "Schedule a counseling session",
            "Practice gentle self-care activities",
            "Write down your feelings",
            "Listen to uplifting music",
            "Take a warm bath",
            "Watch your favorite comfort movie",
            "Join a pregnancy support group"
        ],
        "😰 Anxious": [
            "Count baby's kicks with a tracking app",
            "Call your doctor if you need reassurance",
            "Watch positive birth stories",
            "Prepare your hospital bag early for peace of mind",
            "Read pregnancy books from trusted sources",
            "Join birthing classes online or in-person",
            "Practice pregnancy-safe breathing exercises",
            "Write letters to your baby about your feelings"
        ],
        "🤢 Nauseous": [
            "Try eating crackers or dry toast before getting out of bed",
            "Sip on warm ginger tea with honey",
            "Keep a stash of pregnancy-friendly candies (like sour drops) in your bag",
            "Try the BRAT diet (Bananas, Rice, Applesauce, Toast)",
            "Use a pregnancy pillow for comfortable rest",
            "Keep ice chips or pregnancy pops handy",
            "Have small meals every 2-3 hours",
            "Try lemon-infused water or sprite for quick relief"
        ],
        "😤 Frustrated": [
            "Try pregnancy-safe stretches for back pain",
            "Use a maternity belt for support",
            "Get a prenatal massage from a certified therapist",
            "Do gentle pregnancy exercises on YouTube",
            "Use ice packs or heat pads for comfort",
            "Take a break with your favorite snacks",
            "Chat with other moms about their experiences",
            "Look at your baby's ultrasound pictures"
        ],
        "🥺 Overwhelmed": [
            "Put your feet up and watch your favorite comfort show",
            "Order grocery delivery instead of shopping",
            "Ask partner/family to help with household chores",
            "Take a warm (not hot) bubble bath",
            "Use a pregnancy app to track one thing at a time",
            "Join online pregnancy support groups",
            "Take a power nap - even 15 minutes helps",
            "Make a list of questions for your next doctor visit"
        ],
        "🤩 Excited": [
            "Take bump photos with creative weekly pregnancy signs",
            "Work on your baby's scrapbook or memory book",
            "Shop online for cute maternity outfits",
            "Plan and organize your baby's nursery",
            "Listen to your baby's heartbeat recording",
            "Browse and save baby names you love",
            "Watch pregnancy vlogs or join mom groups",
            "Create a fun pregnancy announcement if you haven't yet"
        ],
        "😇 Blessed": [
            "Write a gratitude list",
            "Share your joy with loved ones",
            "Take milestone photos",
            "Create pregnancy memories",
            "Plan a celebration",
            "Write letters to your baby",
            "Start a family tradition",
            "Make a pregnancy scrapbook"
        ],
        "✨ Hopeful": [
            "Start a pregnancy milestone journal",
            "Create a vision board for your nursery",
            "Make a playlist for your baby",
            "Browse through positive birth stories",
            "Plan a small celebration for each trimester",
            "Take weekly progression photos",
            "Write letters to your future baby",
            "Join positive pregnancy support communities"
        ],
        "⚡ Energetic": [
            "Try pregnancy-safe workout routines",
            "Organize the baby's room or clothes",
            "Start a pregnancy-friendly hobby",
            "Plan and prep healthy meals",
            "Take a prenatal exercise class",
            "Go for a nature walk",
            "Dance to your favorite music",
            "Work on a baby-related DIY project"
        ]
    }
    return suggestions.get(mood, [
        "Take things one moment at a time",
        "Remember every pregnancy journey is unique",
        "Connect with your healthcare provider",
        "Join pregnancy support groups",
        "Focus on self-care activities you enjoy",
        "Stay hydrated and rest when needed",
        "Track your symptoms and moods",
        "Reach out to loved ones for support"
    ])


# Sidebar Navigation
with st.sidebar:
    st.markdown("## 📱 Menu")
   
    # Profile Section with circular picture
    st.markdown("### 👤 Profile")
    uploaded_file = st.file_uploader("Choose a profile picture", type=['png', 'jpg', 'jpeg'])
   
    if uploaded_file is not None:
        # Read the file and convert to bytes
        bytes_data = uploaded_file.getvalue()
        st.session_state.profile_pic = bytes_data
        st.image(bytes_data, width=100, use_container_width=False)
    elif st.session_state.profile_pic is not None:
        st.image(st.session_state.profile_pic, width=100, use_container_width=False)
    else:
        st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=100)
   
    # Name Input
    user_name = st.text_input("Enter your name:", value=st.session_state.user_name)
    if user_name != st.session_state.user_name:
        st.session_state.user_name = user_name


    # Navigation
    st.markdown("### 📍 Navigation")
    tabs = st.tabs(["💭 Chat", "📚 Resources", "📝 Journal", "🔔 Recent Activities"])


    with tabs[0]:  # Chat Tab
        st.markdown("#### 🫂 Emotional Support")
        emotional_questions = [
            "How can I balance my emotions during this journey?",
            "How do I cope with unexpected triggers of grief or anxiety?",
            "What are effective ways to manage intrusive thoughts?",
            "What are the signs of burnout or emotional exhaustion?",
            "How can I involve my partner in my emotional journey?",
            "How can I support my partner if they are struggling too?",
            "What are ways to build emotional resilience?",
            "How can I incorporate mindfulness into my daily routine?",
            "Are there any specific meditation or breathing exercises for calming emotions?"
        ]
        for q in emotional_questions:
            if st.button(q, key=f"eq_{q}"):
                response = get_ai_response(q, st.session_state.chat_history)
                st.session_state.chat_history.append({
                    "user": q,
                    "assistant": response,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                add_activity("Chat", f"Asked about: {q}")
                st.rerun()


    with tabs[1]:  # Resources Tab
        #st.markdown("#### 📚 Support Resources")
        
        # Support Resources Section
        st.markdown("### 🤝 Support Resources")
        st.markdown("#### 📞 24/7 Support Hotline: +91 8999 851 757")
        
        # Resource Categories
        resource_categories = [
            "📘 Emotional and Mental Health Resources",
            "💪 Physical Health and Wellness",
            "👶 Preparing for Baby",
            "📖 Educational Guides",
            "🥗 Nutrition and Diet",
            "🏥 Labor and Delivery Preparation",
            "👨‍👩‍👦 Partner and Family Support",
            "📋 Specialized Pregnancy Topics",
            "🎮 Fun and Interactive Resources"
        ]
        
        for category in resource_categories:
            if st.button(category):
                query = f"Please provide comprehensive information and resources about {category.split(' ', 1)[1]}. Include practical tips, recommended reading, and helpful tools."
                response = get_ai_response(query, st.session_state.chat_history)
                st.markdown(f"### {category}")
                st.write(response)
                add_activity("Resource", f"Accessed {category} information")


    with tabs[2]:  # Journal Tab
        st.markdown("#### 📝 Journal")
        
        # Create a form for the journal entry
        with st.form(key="journal_form"):
            journal_prompt = st.selectbox(
                "Choose a prompt:",
                [
                    "How are you feeling today?",
                    "What are you grateful for?",
                    "What's on your mind?",
                    "Write your own entry..."
                ],
                key="journal_prompt"
            )
            journal_entry = st.text_area("Your thoughts:", height=150, key="journal_text")
            submit_button = st.form_submit_button(label="Save Entry")
            
            if submit_button and journal_entry:
                new_entry = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "prompt": journal_prompt,
                    "entry": journal_entry
                }
                if 'journal_entries' not in st.session_state:
                    st.session_state.journal_entries = []
                st.session_state.journal_entries.append(new_entry)
                add_activity("Journal", "Wrote new journal entry")
                st.success("Journal entry saved!")
                st.rerun()

        # Display past entries
        st.markdown("### 📚 Past Journal Entries")
        if not st.session_state.journal_entries:
            st.info("No journal entries yet. Start writing to see your entries here!")
        else:
            for entry in reversed(st.session_state.journal_entries):
                with st.expander(f"Entry from {entry['date']}"):
                    st.write(f"**Prompt:** {entry['prompt']}")
                    st.write(entry['entry'])


    with tabs[3]:  # Recent Activities Tab
        st.markdown("#### 🔔 Recent Activities")
        for activity in st.session_state.recent_activities:
            icon = "💭" if activity["type"] == "Chat" else "📚" if activity["type"] == "Resource" else "📝" if activity["type"] == "Journal" else "⭐"
            st.markdown(f"{icon} **{activity['type']}**: {activity['description']}  \n*{activity['timestamp']}*")


# Main Content Area
st.markdown(f"# 💌 Promise Care - Emotional Maternity Support")

# Welcome Section with Time-based Greeting
greeting_name = f", {st.session_state.user_name}" if st.session_state.user_name else ""
st.markdown(f"### {get_greeting()}{greeting_name} 💝")
st.markdown(f"*Today's Affirmation:* _{get_daily_affirmation()}_")

# Progress Tracking
col1, col2 = st.columns([2,1])
with col1:
    
    st.markdown("### 📈 Your Progress")
    st.markdown(f"**Check-in Streak:** 🔥 {st.session_state.streak} days")
   
    # Mood Distribution Chart
    if st.session_state.mood_logs:
        mood_counts = {}
        for entry in st.session_state.mood_logs:
            mood = entry['mood']
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
       
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(mood_counts.keys()),
            values=list(mood_counts.values()),
            hole=.4,
            marker=dict(
                colors=['#FFB6C1', '#FFC0CB', '#FFE4E1', '#FFF0F5', '#DB7093', '#FF69B4', '#FFB6C1', '#DDA0DD', '#FF1493', '#C71585'],
                line=dict(color='#FFFFFF', width=2)
            ),
            textposition='inside',
            textinfo='label+percent',
            insidetextorientation='radial',
            textfont=dict(size=12, color='#4A4A4A'),
            hovertemplate="<b>%{label}</b><br>" +
                         "Count: %{value}<br>" +
                         "Percentage: %{percent}<br>" +
                         "<extra></extra>"
        )])
        fig.update_layout(
            showlegend=False,
            width=400,
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig)
    else:
        st.info("Start tracking your moods to see your emotional journey! 📊")


with col2:
    st.markdown("### 🎯 Goals")
    new_goal = st.text_input("Add a new goal:", key="main_new_goal")
    if st.button("Add Goal", key="main_add_goal"):
        if new_goal:
            st.session_state.goals.append({
                "goal": new_goal,
                "completed": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            add_activity("Goal", "Added new goal")
            st.success("Goal added successfully!")
            st.rerun()
   
    # Display existing goals with checkboxes
    for idx, goal in enumerate(st.session_state.goals):
        col1, col2 = st.columns([4,1])
        with col1:
            if goal.get('completed', False):
                st.markdown(f"~~{goal['goal']}~~")
            else:
                st.write(goal['goal'])
        with col2:
            if st.button("✓" if not goal.get('completed', False) else "↻", key=f"complete_{idx}"):
                goal['completed'] = not goal.get('completed', False)
                st.rerun()


# Chat Interface
st.markdown("### 💭 Chat with Assistant")

# Initialize the chat input key in session state if it doesn't exist
if 'chat_input_key' not in st.session_state:
    st.session_state.chat_input_key = 0

user_input = st.text_input("Looking for support? Let's chat!", 
                          key=f"chat_input_{st.session_state.chat_input_key}",
                          on_change=lambda: setattr(st.session_state, 'enter_pressed', True) if not st.session_state.get('enter_pressed', False) else None)

if user_input and st.session_state.get('enter_pressed', False):
    response = get_ai_response(user_input, st.session_state.chat_history)
    st.session_state.chat_history.append({
        "user": user_input,
        "assistant": response,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    add_activity("Chat", f"Asked: {user_input}")
    st.session_state.enter_pressed = False
    # Increment the key to create a new input box
    st.session_state.chat_input_key += 1
    st.rerun()


# Display chat history
for message in st.session_state.chat_history:
    st.markdown(f'<div class="chat-message user-message">👤 You: {message["user"]}</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="chat-message bot-message">{message["assistant"]}</div>',
                unsafe_allow_html=True)

# Success Stories Section
stories = [
    {
        "title": "Ellie's Journey: Finding Hope After Loss",
        "quote": "My son arrived in July 2023 following a problem-free pregnancy. He was happy and healthy. It was both the hardest and most amazing thing I've experienced. I feel so lucky.",
        "message": "After experiencing a miscarriage, Ellie found strength through counseling and support. Her journey led to the birth of her healthy son, showing that there is hope after loss. She shares her story to inspire others and remind them that healing is possible.",
        "emoji": "🌅"
    },
    {
        "title": "Vicki's Story: The Power of Perseverance",
        "quote": "I gave birth to my daughter, Clara, in April of this year (2023). I also chose to turn my pain into power.",
        "message": "After two miscarriages, including one with twins, Vicki's journey led to the birth of her daughter Clara. She transformed her experience into positive change by creating a workplace miscarriage policy. Her story shows how personal challenges can lead to meaningful impact.",
        "emoji": "💪"
    },
    {
        "title": "Angie's Message of Hope",
        "quote": "You will laugh again. You will find joy in something. It's not the old normal, but it's pretty close.",
        "message": "Ten years after her miscarriages, Angie is now a mother of two children. Her story shows that while grief remains a part of you, joy and happiness return. She emphasizes the importance of giving yourself time to heal and being gentle with your emotions.",
        "emoji": "🌈"
    }
]

st.markdown("### ✨ Stories of Hope and Healing")
st.write("""
Here you'll find inspiring stories from other mothers who have navigated their pregnancy journey. 
These stories showcase resilience, hope, and the beautiful moments of motherhood.
""")

for story in stories:
    with st.expander(f"{story['emoji']} {story['title']}"):
        st.markdown(f"""
        <div class="success-story">
            <div class="story-quote">"{story['quote']}"</div>
            <div class="story-message">{story['message']}</div>
        </div>
        """, unsafe_allow_html=True)

# Daily Check-in Section
st.markdown("### 📝 Daily Check-in")
st.write("How are you feeling today? Select your mood below:")

# Initialize selected_mood in session state if not present
if 'selected_mood' not in st.session_state:
    st.session_state.selected_mood = None

# Mood Selection Buttons - Create a grid layout
cols = st.columns(4)  # 4 buttons per row
mood_list = list(MOODS.keys())

# Create rows of buttons, 4 per row
for i in range(0, len(mood_list), 4):
    row_moods = mood_list[i:i+4]
    for j, mood in enumerate(row_moods):
        with cols[j]:
            button_style = "background-color: #FFB6C1;" if st.session_state.selected_mood == mood else ""
            if st.button(
                mood, 
                key=f"mood_btn_{mood}", 
                help=f"Select if you're feeling {MOODS[mood]['description']}", 
                use_container_width=True
            ):
                st.session_state.selected_mood = mood
                # Add mood to logs with timestamp
                st.session_state.mood_logs.append({
                    "mood": mood,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "description": MOODS[mood]["description"]
                })
                add_activity("Mood", f"Logged mood: {mood}")
                st.rerun()

# Display suggestions based on selected mood
if st.session_state.selected_mood:
    st.markdown("---")
    
    # Calculate mood percentages
    mood_counts = {}
    total_moods = len(st.session_state.mood_logs)
    for entry in st.session_state.mood_logs:
        mood = entry['mood']
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    # Create a title showing the current mood percentage
    current_mood = st.session_state.selected_mood
    current_mood_count = mood_counts.get(current_mood, 0)
    mood_percentage = (current_mood_count / total_moods * 100) if total_moods > 0 else 100
    
    # Display the mood percentage with custom styling
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 10px;
        margin-bottom: 20px;
        font-size: 24px;
        color: #FF69B4;
        font-weight: bold;
    ">
        Your Current Mood: {mood_percentage:.0f}% {current_mood.split()[1]}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### 💝 Suggested Activities for {st.session_state.selected_mood}")
    st.markdown(f"*When you're feeling {MOODS[st.session_state.selected_mood]['description']}, try these activities:*")
    
    # Create columns for activities
    activity_cols = st.columns(2)
    suggestions = MOODS[st.session_state.selected_mood]['activities']
    
    # Split suggestions between columns
    mid_point = len(suggestions) // 2
    
    # First column of activities
    with activity_cols[0]:
        for suggestion in suggestions[:mid_point]:
            # Create a container for each suggestion with a soft pink background
            with st.container():
                st.markdown(f"""
                <div style="
                    background-color: #FFE4E1;
                    padding: 10px;
                    border-radius: 10px;
                    margin: 5px 0;
                    border: 1px solid #FFB6C1;
                ">
                    ✨ {suggestion}
                </div>
                """, unsafe_allow_html=True)
    
    # Second column of activities
    with activity_cols[1]:
        for suggestion in suggestions[mid_point:]:
            with st.container():
                st.markdown(f"""
                <div style="
                    background-color: #FFE4E1;
                    padding: 10px;
                    border-radius: 10px;
                    margin: 5px 0;
                    border: 1px solid #FFB6C1;
                ">
                    ✨ {suggestion}
                </div>
                """, unsafe_allow_html=True)

    # Add a clear mood button
    st.markdown("---")
    if st.button("Clear Selection", key="clear_mood"):
        st.session_state.selected_mood = None
        st.rerun()

else:
    st.markdown("---")
    st.info("Select a mood above to see personalized activity suggestions! 🌟")

st.markdown("---")

# Feedback Section with History
st.markdown("### 📝 Share Your Feedback")
feedback = st.text_area("Your feedback helps us improve:", key="feedback_input")
if st.button("Submit Feedback"):
    if feedback:
        st.session_state.feedback_history.append({
            "feedback": feedback,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        add_activity("Feedback", "Submitted new feedback")
        st.success("Thank you for your feedback!")
        st.session_state.feedback = ""

if st.button("View Past Feedback"):
    st.markdown("### 📋 Feedback History")
    for entry in reversed(st.session_state.feedback_history):
        with st.expander(f"Feedback from {entry['timestamp']}"):
            st.write(entry['feedback'])

# Add supportive message at the end
st.markdown("---")
st.markdown("""
<div style="
    background-color: #FFE4E1;
    padding: 15px;
    border-radius: 10px;
    margin: 20px 0;
    border: 2px solid #FFB6C1;
    text-align: center;
">
    <p style="
        color: #333;
        margin-bottom: 10px;
        font-size: 16px;
    ">
        ⚠️ This AI assistant provides support and guidance, but always consult your healthcare team for medical advice.
    </p>
    <p style="
        color: #333;
        margin-bottom: 0;
        font-size: 16px;
    ">
        Remember: You are not alone in this journey. 🌈
    </p>
    <p style="
        color: #333;
        margin-bottom: 0;
        font-size: 16px;
    ">
       ✨ This project is primarily done by Alaissa Shaikh, with significant contributions and support from Omm Tharkude showcasing the power of teamwork and collaboration. ✨
    </p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")

# Help Button
if st.button("❓ Need Help?"):
    st.markdown("""
    ### How to Use This App
    1. Use the sidebar to navigate different sections
    2. Track your daily mood with the emoji buttons
    3. Ask questions in the chat
    4. Save helpful resources to your favorites
    5. Journal your thoughts and feelings
    """)