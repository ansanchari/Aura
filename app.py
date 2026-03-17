import streamlit as st
from datetime import date
from aura_retriever import AuraHealthRouter
from cycle_scheduler import CycleScheduler, UserProfile

st.set_page_config(page_title="Aura | Offline Health & Productivity", page_icon="🌸", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText, p {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #1A202C;
    }

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(135deg, #FFF5F7 0%, #FFFFFF 100%);
        color: #2D3748;
    }
    
    [data-testid="stSidebar"] {
        background-color: #FAFAFC !important;
        border-right: 1px solid #F1F5F9;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #FF758C 0%, #FF7EB3 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 117, 140, 0.2);
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 117, 140, 0.4);
        border: none;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
    }
    
    .stChatMessage {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #F1F5F9;
        margin-bottom: 12px;
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        background-color: #FFFFFF;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #FF7EB3;
        box-shadow: 0 0 0 2px rgba(255, 126, 179, 0.2);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_ai_brain():
    return AuraHealthRouter()

@st.cache_resource
def load_scheduler():
    return CycleScheduler(), UserProfile()

aura_agent = load_ai_brain()
scheduler, profile = load_scheduler()

st.sidebar.markdown("""
<div style="text-align: center; padding-bottom: 20px;">
    <h2 style="font-size: 2.2rem; margin:0; background: linear-gradient(90deg, #FF758C 0%, #FF7EB3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🌸 Aura</h2>
</div>
""", unsafe_allow_html=True)

current_day = profile.get_current_cycle_day()

if current_day:
    st.sidebar.success(f"**Status:** Engine Active\n\n**Current Cycle Day:** {current_day}")
    st.sidebar.caption("Aura is autonomously calculating your biological phase.")
else:
    st.sidebar.warning("Cycle not logged yet.")

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("### ⚙️ Update Cycle")
new_start_date = st.sidebar.date_input("When did your last cycle start?", value=date.today())
if st.sidebar.button("Lock In Date"):
    profile.lock_in_start_date(new_start_date)
    st.rerun()

st.markdown("""
<div style="text-align: center; padding: 2rem 0 3rem 0;">
    <h1 style="font-size: 3.5rem; margin-bottom: 0;">
        Welcome to <span style="background: linear-gradient(90deg, #FF758C 0%, #FF7EB3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Aura</span>
    </h1>
    <p style="font-size: 1.2rem; color: #64748B; font-weight: 300; margin-top: 0.5rem;">
        Your secure, offline-first women's health and productivity companion.
    </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💬 Medical AI Chat", "⚡ Autonomous Lifestyle"])

with tab1:
    st.markdown("### Clinical Knowledge Base")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello. I am Aura. How can I support your health today?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about PCOS, Endometriosis, cycle health..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Reviewing medical literature..."):
                response = aura_agent.ask_aura(prompt)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

with tab2:
    if not current_day:
        st.info("👈 Please set your cycle start date in the sidebar to unlock lifestyle features.")
    else:
        phase_name, phase_data = scheduler.get_current_phase(current_day)
        
        with st.container(border=True):
            st.markdown(f"### 🧬 Phase: <span style='color: #FF758C;'>{phase_name}</span> (Day {current_day})", unsafe_allow_html=True)
            st.markdown(f"<span style='color: #4A5568;'>**Bio-Context:** {phase_data['advice']}</span>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### 🛒 Predictive Nutrition Planner")
        st.caption("Generate a future-tense grocery list and meal plan based on your upcoming hormonal needs.")
        
        if "diet_plan" not in st.session_state:
            st.session_state.diet_plan = None
        if "diet_chat" not in st.session_state:
            st.session_state.diet_chat = []

        if st.button("✨ Auto-Generate Upcoming Meal Plan"):
            with st.spinner("Designing your hormone-optimized menu..."):
                prompt = f"""
                You are Aura, an expert dietitian. The user is in their {phase_name} phase. 
                Clinical dietary advice for this phase: {phase_data['diet']}
                
                Write a concise, future-tense 2-day meal plan and a short grocery list for them. 
                Keep it practical, highly empathetic, and format it beautifully using markdown. 
                Strict rule: Keep your response under 600 words to ensure it does not cut off.
                """
                response = aura_agent.llm.invoke(prompt)
                st.session_state.diet_plan = response.content
                st.session_state.diet_chat = [{"role": "assistant", "content": "Here is your 2-day plan! Let me know if you need to swap out any ingredients."}]

        if st.session_state.diet_plan:
            with st.container(border=True):
                st.markdown(st.session_state.diet_plan)
            
            st.markdown("<br>#### 🔄 Ingredient Swaps", unsafe_allow_html=True)
            for msg in st.session_state.diet_chat:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                
            if swap_query := st.chat_input("Can't find an ingredient? Ask for an alternative..."):
                st.session_state.diet_chat.append({"role": "user", "content": swap_query})
                with st.chat_message("user"):
                    st.markdown(swap_query)
                
                with st.chat_message("assistant"):
                    with st.spinner("Finding alternatives..."):
                        swap_prompt = f"""
                        You are a helpful dietitian. The user is on a diet for their {phase_name} menstrual phase. 
                        They asked: '{swap_query}'. Provide a 1-paragraph, direct alternative that still fits their hormonal needs.
                        """
                        swap_response = aura_agent.llm.invoke(swap_prompt)
                        st.markdown(swap_response.content)
                st.session_state.diet_chat.append({"role": "assistant", "content": swap_response.content})

        st.markdown("<br><hr>", unsafe_allow_html=True)
        st.markdown("#### ⚡ Intelligent Task Routing")
        st.caption("Aura sorts your week to prevent biological burnout. Drop your tasks below.")
        
        user_tasks = st.text_area("Your To-Do List:", value="Code the backend logic\nPitch project to the judges\nDesign the presentation slides\nRest and read a book", height=120, label_visibility="collapsed")
        
        if st.button("🚀 Optimize My Schedule"):
            task_list = user_tasks.split("\n")
            result = scheduler.optimize_tasks(current_day, task_list)
            
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### ✅ Optimal for Today")
                for t in result["highly_recommended"]:
                    with st.container(border=True):
                        st.markdown(f"**{t}**")
                    
            with col2:
                st.markdown("##### ⏳ Defer to Next Phase")
                for t in result["do_if_necessary"]:
                    with st.container(border=True):
                        st.markdown(f"<span style='color: #A0AEC0;'>_{t}_</span>", unsafe_allow_html=True)