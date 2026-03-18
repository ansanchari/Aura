import streamlit as st
import math
from datetime import date
import time
import io
import plotly.graph_objects as go
import speech_recognition as sr
from fpdf import FPDF
from audio_recorder_streamlit import audio_recorder
from aura_retriever import AuraHealthRouter
from cycle_scheduler import CycleScheduler, UserProfile

st.set_page_config(page_title="Aura | Health & Productivity", page_icon="🌸", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"], .stMarkdown, .stText, p { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #1A202C; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background: linear-gradient(135deg, #FFF5F7 0%, #FFFFFF 100%); color: #2D3748; }
    [data-testid="stSidebar"] { background-color: #FAFAFC !important; border-right: 1px solid #F1F5F9; }
    
    .stButton>button { background: linear-gradient(90deg, #FF758C 0%, #FF7EB3 100%); color: #FFFFFF !important; border: none; border-radius: 12px; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(255, 117, 140, 0.2); }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 117, 140, 0.4); }
    
    [data-testid="stVerticalBlockBorderWrapper"] { background: rgba(255, 255, 255, 0.6) !important; backdrop-filter: blur(10px) !important; border-radius: 16px !important; border: 1px solid rgba(255, 255, 255, 0.8) !important; box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important; }
    .stChatMessage { background-color: #FFFFFF; border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #F1F5F9; margin-bottom: 12px; }

    .stTextInput>div>div>input {
        border-radius: 12px; border: 1px solid #E2E8F0; background-color: #FFFFFF; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }
    .stTextInput>div>div>input:focus {
        border-color: #FF7EB3; box-shadow: 0 0 0 2px rgba(255, 126, 179, 0.2);
    }

    .stTextArea textarea {
        background-color: #FFFFFF !important;
        background-image: repeating-linear-gradient(transparent, transparent 31px, #F1F5F9 31px, #F1F5F9 32px) !important;
        line-height: 32px !important; padding: 8px 15px !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 16px !important; border: 1px solid #E2E8F0 !important; border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important; resize: vertical;
    }
    .stTextArea textarea:focus { border-color: #FF7EB3 !important; box-shadow: 0 0 0 3px rgba(255, 126, 179, 0.15) !important; outline: none !important; }
</style>
""", unsafe_allow_html=True)

def generate_pdf(phase_name, diet_plan, highly_recommended):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=16, style="B")
    pdf.cell(0, 10, f"Aura Weekly Blueprint: {phase_name} Phase", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("helvetica", size=14, style="B")
    pdf.cell(0, 10, "Diet & Nutrition:", ln=True)
    pdf.set_font("helvetica", size=11)
    clean_diet = diet_plan.replace('*', '') if diet_plan else "No plan generated."
    clean_diet = str(diet_plan)
    replacements = {
        '“': '"', '”': '"', 
        '‘': "'", '’': "'", 
        '—': '-', '–': '-', 
        '•': '-', '*': '-'
    }
    for old, new in replacements.items():
        clean_diet = clean_diet.replace(old, new)
    
    clean_diet = clean_diet.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 8, clean_diet)
    pdf.ln(5)
    
    pdf.set_font("helvetica", size=14, style="B")
    pdf.cell(0, 10, "Priority Tasks for Today:", ln=True)
    pdf.set_font("helvetica", size=11)
    for task in highly_recommended:
        pdf.cell(0, 8, f"- {task}", ln=True)
        
    return bytes(pdf.output())

@st.cache_resource
def load_ai_brain():
    return AuraHealthRouter()

@st.cache_resource
def load_scheduler():
    return CycleScheduler(), UserProfile()

aura_agent = load_ai_brain()
scheduler, profile = load_scheduler()

st.sidebar.markdown("""<div style="text-align: center; padding-bottom: 20px;"><h2 style="font-size: 2.2rem; margin:0; background: linear-gradient(90deg, #FF758C 0%, #FF7EB3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🌸 Aura</h2></div>""", unsafe_allow_html=True)

current_day = profile.get_current_cycle_day()

if current_day:
    st.sidebar.success(f"**Status:** Engine Active\n\n**Current Cycle Day:** {current_day}")
else:
    st.sidebar.warning("Cycle not logged yet.")

st.sidebar.markdown("### ⚙️ Update Cycle")
new_start_date = st.sidebar.date_input("When did your last cycle start?", value=date.today())
if st.sidebar.button("Lock In Date"):
    profile.lock_in_start_date(new_start_date)
    st.rerun()

st.markdown("""<div style="text-align: center; padding: 2rem 0 2rem 0;"><h1 style="font-size: 3.5rem; margin-bottom: 0;">Welcome to <span style="background: linear-gradient(90deg, #FF758C 0%, #FF7EB3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Aura</span></h1><p style="font-size: 1.2rem; color: #64748B; font-weight: 300;">Your secure, offline-first women's health and productivity companion.</p></div>""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💬 Medical AI Chat", "⚡ Autonomous Lifestyle"])

with tab1:
    st.markdown("### Clinical Knowledge Base")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello. I am Aura. How can I support your health today?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("<br>", unsafe_allow_html=True)
    col_mic, col_space = st.columns([1, 5])
    with col_mic:
        audio_bytes = audio_recorder(text="🎙️ Click to Speak", recording_color="#FF4D6D", neutral_color="#64748B")

    prompt = st.chat_input("Or type your symptoms here...")
    final_prompt = None

    if audio_bytes and ("last_audio" not in st.session_state or st.session_state.last_audio != audio_bytes):
        st.session_state.last_audio = audio_bytes
        with st.spinner("Transcribing..."):
            try:
                r = sr.Recognizer()
                audio_file = io.BytesIO(audio_bytes)
                with sr.AudioFile(audio_file) as source:
                    audio_data = r.record(source)
                    final_prompt = r.recognize_google(audio_data)
            except Exception:
                st.error("I couldn't quite catch that. Please try again or use the text box.")

    if prompt:
        final_prompt = prompt

    if final_prompt:
        st.session_state.messages.append({"role": "user", "content": final_prompt})
        with st.chat_message("user"):
            st.markdown(final_prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Reviewing medical literature..."):
                response = aura_agent.ask_aura(final_prompt)
                st.markdown(response)
                
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with tab2:
    if not current_day:
        st.info("👈 Please set your cycle start date in the sidebar to unlock lifestyle features.")
    else:
        phase_name, phase_data = scheduler.get_current_phase(current_day)
        
        with st.container(border=True):
            col_chart, col_text = st.columns([1, 2], gap="large")
            with col_chart:
                phases = ['Menstrual', 'Follicular', 'Ovulatory', 'Luteal']
                days_in_phase = [5, 8, 4, 11] 
                
                colors = ['#BD1A47', '#FAD1DA', '#F68EAD', '#F24D79'] 
                
                angle_deg = ((current_day - 0.5) / 28) * 360
                angle_rad = math.radians(angle_deg)
                
                glider_radius = 0.43 
                glider_x = 0.5 + glider_radius * math.sin(angle_rad)
                glider_y = 0.5 + glider_radius * math.cos(angle_rad)

                fig = go.Figure(data=[go.Pie(
                    labels=phases, values=days_in_phase, hole=0.76, sort=False,
                    direction='clockwise', rotation=90, textinfo='none', hoverinfo='label',
                    marker=dict(colors=colors, line=dict(color='#FFFFFF', width=6)) # Thicker white gaps
                )])
                
                fig.update_layout(
                    showlegend=False, margin=dict(t=0, b=0, l=0, r=0), 
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280, 
                    annotations=[
                        dict(text="DAY", x=0.5, y=0.58, font_size=16, font_color='#8FA0B5', showarrow=False),
                        dict(text=str(current_day), x=0.5, y=0.38, font_size=64, font_color='#1E293B', showarrow=False),
                        
                        dict(
                            text="●", x=glider_x, y=glider_y - 0.015, font_size=62, 
                            font_color='rgba(0,0,0,0.15)', showarrow=False, xanchor='center', yanchor='middle'
                        ),
                        dict(
                            text="●", x=glider_x, y=glider_y, font_size=62, 
                            font_color='#FFFFFF', showarrow=False, xanchor='center', yanchor='middle'
                        ),
                        dict(
                            text="●", x=glider_x, y=glider_y, font_size=46, 
                            font_color='#BD1A47', showarrow=False, xanchor='center', yanchor='middle'
                        )
                    ]
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': False})
                
            with col_text:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"### 🧬 Phase: <span style='color: #A4133C;'>{phase_name}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color: #4A5568;'>**Bio-Context:** {phase_data['advice']}</span>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### 🛒 Predictive Nutrition Planner")
        
        if "diet_plan" not in st.session_state:
            st.session_state.diet_plan = None
            
        if st.button("✨ Auto-Generate Upcoming Meal Plan"):
            with st.status("🔮 Generating your biological blueprint...", expanded=True) as status:
                st.write("✨ Analyzing phase biomarkers...")
                time.sleep(1) 
                st.write("✨ Cross-referencing clinical nutritional requirements...")
                time.sleep(1)
                st.write("✨ Plating your menu using Mistral AI...")
                
                prompt = f"You are Aura, an expert dietitian. The user is in their {phase_name} phase. Clinical dietary advice: {phase_data['diet']}. Write a concise, future-tense 2-day meal plan and grocery list. Keep under 400 words."
                response = aura_agent.llm.invoke(prompt)
                st.session_state.diet_plan = response.content
                status.update(label="Blueprint Complete!", state="complete", expanded=False)

        if st.session_state.diet_plan:
            with st.container(border=True):
                st.markdown(st.session_state.diet_plan)

        st.markdown("<br><hr>", unsafe_allow_html=True)
        st.markdown("#### ⚡ Intelligent Task Routing")
        
        user_tasks = st.text_area("Your To-Do List:", value="Code the backend logic\nPitch project to the judges\nDesign the presentation slides\nRest and read a book", height=120)
        
        if st.button("🚀 Optimize My Schedule"):
            task_list = user_tasks.split("\n")
            result = scheduler.optimize_tasks(current_day, task_list)
            st.session_state.current_tasks = result
            
        if "current_tasks" in st.session_state:
            result = st.session_state.current_tasks
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### ✅ Optimal for Today")
                with st.container(border=True):
                    for i, t in enumerate(result["highly_recommended"]):
                        st.checkbox(t, key=f"do_{i}")
                        
            with col2:
                st.markdown("##### ⏳ Defer to Next Phase")
                with st.container(border=True):
                    for i, t in enumerate(result["do_if_necessary"]):
                        st.checkbox(t, key=f"defer_{i}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            pdf_bytes = generate_pdf(phase_name, st.session_state.diet_plan, result["highly_recommended"])
            
            st.download_button(
                label="📥 Download My Week (PDF)",
                data=pdf_bytes,
                file_name=f"Aura_{phase_name}_Blueprint.pdf",
                mime="application/pdf",
                use_container_width=True
            )
