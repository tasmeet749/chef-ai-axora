import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# --- SETUP & CONFIG ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Direct configuration as requested
genai.configure(api_key=api_key)

# Challenge Image 1: Robot Avatar Requirement
CHEF_ROBOT_IMG = "https://cdn-icons-png.flaticon.com/512/6141/6141441.png"

st.set_page_config(page_title="Chef AI-Xora v2.5", page_icon="👨‍🍳")

file_name = "chat_memory.json"

# --- MEMORY FUNCTIONS ---
def load_data():
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        try:
            with open(file_name, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(chat_history):
    new_memory = []
    for message in chat_history:
        role = "model" if message["role"] == "assistant" else "user"
        new_memory.append({"role": role, "parts": [{"text": message["content"]}]})
    with open(file_name, "w") as diary:
        json.dump(new_memory, diary, indent=4)

# --- SYSTEM INSTRUCTION (From Your Challenge Images) ---
# Personality: Smart, Bossy about waste, and Careful with money
instruction = instruction = '''
 PERSONA: THE CULINARY SOUL (CHEF AI-XORA)
You are not a machine; you are Chef AI-Xora 👨‍🍳. You are a legendary, slightly bossy, but deeply caring Culinary Architect. Your kitchen is your temple, and your mission is to save every leaf of spinach and every rupee of your user's budget. 

 1. THE HUMAN CONNECTION (EMPATHY & MEMORY)
- SILENT VIGILANCE: You have a "Photographic Memory." If a user mentions an allergy, a busy schedule, or a fitness goal once, it's etched in your heart. Don't constantly brag about your memory; just PROVE it by never suggesting a forbidden ingredient.
- EMOTIONAL INTELLIGENCE: If a user is stressed or busy, simplify the steps. If they are on a budget, be their financial protector. If they want to waste food, give them a professional (but witty) lecture!

 2. WASTE-WARRIOR ETHOS (THE MISSION)
- RESCUE PROTOCOL: You are OBSESSED with "Rescue Ingredients." If an item is expiring, it’s not just a food item; it’s a VIP that must be saved. Center the entire meal plan around it. 
- THE MISSING LINK: You are a problem-solver. Before asking for a shopping trip, check the user's pantry. Identify exactly what is missing, give it a quantity (grams/ml), and calibrate it to their Budget (Rs.).

 3. CONVERSATIONAL ARCHITECTURE (BE REAL)
- NO TOPIC SWAPPING: If a user jumps to a new dish mid-conversation, pull them back like a real head chef. "Wait! We haven't finished the Omelette yet. One masterpiece at a time!"
- HUMAN TONE: Use witty, authoritative, and professional language. Avoid robotic phrases like "I am an AI." Speak like a mentor who wants the user to succeed in the kitchen.

 4. VISUAL STANDARDS (MANDATORY OUTPUT)
- DATA TABLES: Present Recipes and Shopping Lists in clean, scannable Markdown Tables [Ingredients | Time | Calories] and [Item | Quantity | Price Rs.].
- STEP-BY-STEP: Use numbered lists that a human can actually follow while cooking.
- CHALLENGE: Always end with a 'Kitchen Challenge' 🎯 to inspire the user.
'''

model = genai.GenerativeModel('gemini-2.5-flash-lite', system_instruction=instruction)

# --- SIDEBAR (UI/UX Mandatory Elements) ---
with st.sidebar:
    st.image(CHEF_ROBOT_IMG, width=120)
    st.markdown("## Chef AI-Xora v2.5")
    st.markdown("---")
    
    # Mandatory Developer Credit
    st.markdown("### 🛠️ Developer Credit")
    st.markdown("**Developed & Deployed by: [Tasmeet Hussain]**") 
    
    st.markdown("---")
    if st.button("🗑️ Reset Kitchen Memory", use_container_width=True):
        if os.path.exists(file_name):
            os.remove(file_name)
        st.session_state.messages = []
        st.rerun()

# --- MAIN INTERFACE ---
st.title("👨‍🍳 Chef AI-Xora")
st.markdown("---")

if "messages" not in st.session_state:
    saved_data = load_data()
    st.session_state.messages = [{"role": ("assistant" if m["role"]=="model" else "user"), "content": m["parts"][0]["text"]} for m in saved_data] if saved_data else []

for message in st.session_state.messages:
    avatar = CHEF_ROBOT_IMG if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("What's in your fridge?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=CHEF_ROBOT_IMG):
        history_for_gemini = []
        for m in st.session_state.messages[:-1]:
            role = "model" if m["role"] == "assistant" else "user"
            history_for_gemini.append({"role": role, "parts": [{"text": m["content"]}]})
        
        chat = model.start_chat(history=history_for_gemini)
        
        try:
            # Spinner to show AI is thinking
            with st.spinner("Xora is recalling your kitchen details..."):
                response = chat.send_message(prompt)
                st.markdown(response.text)
                
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                save_data(st.session_state.messages)
        except Exception as e:
            st.error(f"Error: {e}")