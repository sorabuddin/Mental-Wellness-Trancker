import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import json
import datetime

# 1. Page Config
st.set_page_config(
    page_title="MindSync | Student Mental Wellness Tracker",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Premium styling (CSS)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Global Font and Background */
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
    background-color: #0A0F1D !important;
    color: #E2E8F0 !important;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #0F162A !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Glassmorphic Container Card */
.glass-card {
    background: rgba(30, 41, 59, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

/* Color Coding for Stress Level Cards */
.stress-1 { border-left: 6px solid #10B981; } /* Calm Green */
.stress-2 { border-left: 6px solid #10B981; }
.stress-3 { border-left: 6px solid #10B981; }
.stress-4 { border-left: 6px solid #F59E0B; } /* Moderate Yellow */
.stress-5 { border-left: 6px solid #F59E0B; }
.stress-6 { border-left: 6px solid #F59E0B; }
.stress-7 { border-left: 6px solid #F59E0B; }
.stress-8 { border-left: 6px solid #EF4444; } /* High Red */
.stress-9 { border-left: 6px solid #EF4444; }
.stress-10 { border-left: 6px solid #EF4444; }

/* Custom badges/tags */
.custom-badge {
    background: rgba(139, 92, 246, 0.15);
    color: #C084FC;
    padding: 6px 14px;
    border-radius: 30px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-right: 8px;
    margin-bottom: 8px;
    display: inline-block;
    border: 1px solid rgba(139, 92, 246, 0.3);
    transition: all 0.3s ease;
}
.custom-badge:hover {
    background: rgba(139, 92, 246, 0.25);
    transform: translateY(-2px);
}

.trigger-badge {
    background: rgba(244, 63, 94, 0.15);
    color: #FDA4AF;
    border: 1px solid rgba(244, 63, 94, 0.3);
}
.trigger-badge:hover {
    background: rgba(244, 63, 94, 0.25);
}

/* Custom Chat Bubbles */
.chat-bubble-user {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
    color: #FFFFFF;
    border-radius: 20px 20px 0px 20px;
    padding: 14px 20px;
    margin: 10px 0 10px auto;
    max-width: 80%;
    text-align: right;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    word-wrap: break-word;
}

.chat-bubble-companion {
    background: rgba(30, 41, 59, 0.85);
    color: #E2E8F0;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px 20px 20px 0px;
    padding: 14px 20px;
    margin: 10px auto 10px 0;
    max-width: 80%;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    word-wrap: break-word;
}

/* Pulsating Breathing Circle animation */
@keyframes breathe {
    0%, 100% { transform: scale(0.85); opacity: 0.6; box-shadow: 0 0 20px rgba(99, 102, 241, 0.4); }
    50% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 40px rgba(139, 92, 246, 0.8); }
}
.breathing-circle {
    width: 120px;
    height: 120px;
    background: radial-gradient(circle, #A78BFA 0%, #6366F1 100%);
    border-radius: 50%;
    margin: 30px auto;
    animation: breathe 8s infinite ease-in-out;
}

/* Custom Text inputs & buttons styling */
.stButton>button {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
    color: white !important;
    border: none !important;
    padding: 10px 24px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
}
.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5) !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Sidebar setup: Mock Login, Profiles, and Plotly line chart
st.sidebar.markdown("<h2 style='text-align: center; color: #A78BFA; font-weight: 800;'>🧘 MindSync</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #94A3B8; font-size: 0.9em; margin-bottom: 20px;'>A Safe Space for Competitive Exam Students</p>", unsafe_allow_html=True)

st.sidebar.subheader("👤 Student Profile")
student_name = st.sidebar.text_input("Student Name", "Aarav Sharma")
target_exam = st.sidebar.selectbox("Target Exam", ["JEE", "NEET", "UPSC", "GATE"])

# API Key handling
st.sidebar.subheader("🔑 Gemini Authentication")
secrets_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        secrets_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

api_key_placeholder = "Configured in secrets" if secrets_key else ""
api_key_input = st.sidebar.text_input("Enter GEMINI_API_KEY", value=secrets_key, type="password", help="If not set in secrets, enter manually here.")

# Decide the active API key
api_key = api_key_input if api_key_input else secrets_key

# Mock historical mood data based on Target Exam to make it custom
today = datetime.date.today()
dates = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]

if "mood_history" not in st.session_state or st.session_state.get("prev_exam") != target_exam:
    st.session_state.prev_exam = target_exam
    # Create customized mock datasets per exam to add realism
    mock_moods = {
        "JEE": [6, 7, 5, 8, 4, 7, 8],
        "NEET": [7, 6, 8, 5, 7, 6, 7],
        "UPSC": [5, 6, 6, 4, 5, 7, 6],
        "GATE": [8, 7, 8, 6, 7, 8, 8]
    }
    st.session_state.mood_history = pd.DataFrame({
        "Date": [d.strftime("%b %d") for d in dates],
        "Mood Level": mock_moods[target_exam]
    })

# Add Plotly mood history chart to sidebar
st.sidebar.subheader("📈 7-Day Mood Trend")
st.sidebar.markdown("<p style='font-size: 0.85em; color: #94A3B8;'>Calculated from journaling logs. 10 = Calm/Optimistic, 1 = Extremely Stressed.</p>", unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=st.session_state.mood_history["Date"],
    y=st.session_state.mood_history["Mood Level"],
    mode='lines+markers',
    line=dict(color='#A78BFA', width=3, shape='spline'),
    marker=dict(size=8, color='#6366F1', symbol='circle'),
    hovertemplate="<b>%{x}:</b> Mood %{y}/10<extra></extra>"
))
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=10, r=10, t=10, b=10),
    height=180,
    yaxis=dict(
        range=[1, 10.5],
        gridcolor='rgba(255, 255, 255, 0.05)',
        tickfont=dict(color='#64748B'),
        dtick=2
    ),
    xaxis=dict(
        gridcolor='rgba(0,0,0,0)',
        tickfont=dict(color='#64748B')
    ),
    showlegend=False
)
st.sidebar.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Main window header
st.markdown(f"<h1 style='color: #FFFFFF; font-weight: 800; margin-bottom: 5px;'>MindSync Companion</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #94A3B8; font-size: 1.15em; margin-bottom: 30px;'>Welcome, <b>{student_name}</b>. Track your stress triggers, discover coping techniques, and talk to our empathetic wellness companion. Preparing for <b>{target_exam}</b> is a journey—you are not alone.</p>", unsafe_allow_html=True)

# Main Window Tabs
tab1, tab2 = st.tabs(["📝 Daily Journaling & Analysis", "💬 Talk to Companion"])

# 4. TAB 1: JOURNAL ANALYSIS ENGINE
with tab1:
    st.markdown("<h3 style='color: #A78BFA; font-weight: 700; margin-top: 10px;'>How was your day?</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Write freely about your prep status, feelings, test outcomes, peer pressure, or sleep quality. Let AI analyze hidden patterns and provide coping mechanisms.</p>", unsafe_allow_html=True)
    
    journal_text = st.text_area(
        label="Journal Entry",
        placeholder="Today was overwhelming. I spent all day on organic chemistry but failed the mock test in the evening. I feel like my competition is miles ahead and I'm letting my parents down...",
        height=180,
        label_visibility="collapsed"
    )
    
    analyze_btn = st.button("Submit Journal & Analyze")
    
    if analyze_btn:
        if not api_key:
            st.warning("⚠️ Please provide a Gemini API Key in the sidebar to run the analysis.")
        elif not journal_text.strip():
            st.info("💡 Please write a journal entry before submitting.")
        else:
            with st.spinner("Analyzing your entry with MindSync AI..."):
                try:
                    # Configure genai SDK
                    genai.configure(api_key=api_key)
                    
                    # Prompt structure
                    prompt = f"""
                    You are a compassionate, expert mental health counselor specialized in helping students preparing for high-stakes competitive exams (like JEE, NEET, UPSC, GATE).
                    Your task is to analyze the student's journal entry and output a structured JSON response.
                    
                    Output MUST be a single, valid JSON object matching the JSON structure below. Do not wrap the JSON object in markdown blocks (e.g. do not use ```json) or add any extra text or headers. Just output the raw JSON text.
                    
                    JSON Structure:
                    {{
                        "stress_level": <integer from 1 to 10 where 10 is maximum stress>,
                        "triggers": [<array of string triggers detected, e.g., "Mock Test Burnout", "Peer Pressure", "Parental Expectations", "Sleep Deprivation", "Fear of Failure">],
                        "emotional_patterns": [<array of strings describing hidden emotional patterns and self-doubt levels, e.g., "Imposter Syndrome", "Fear of not finishing syllabus", "Catastrophizing">],
                        "coping_strategy": "<markdown formatted string with a warm, personalized coping strategy, deep breathing exercise, or mindset reframing exercise tailored specifically to their journal log>"
                    }}
                    
                    Student target exam: {target_exam}
                    Student Journal Entry:
                    "{journal_text}"
                    """
                    
                    # Instantiate model
                    model = genai.GenerativeModel("gemini-3.5-flash")
                    response = model.generate_content(
                        prompt,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    
                    # Parse response
                    analysis = json.loads(response.text.strip())
                    
                    stress_level = int(analysis.get("stress_level", 5))
                    triggers = list(analysis.get("triggers", []))
                    emotional_patterns = list(analysis.get("emotional_patterns", []))
                    coping_strategy = str(analysis.get("coping_strategy", ""))
                    
                    # Dynamically update the 7-day mood trend chart
                    # Mood score is 11 - stress_level
                    new_mood = 11 - stress_level
                    today_str = today.strftime("%b %d")
                    
                    # Update mood history dataframe
                    mood_history_df = st.session_state.mood_history.copy()
                    if mood_history_df.iloc[-1]["Date"] == today_str:
                        mood_history_df.loc[mood_history_df.index[-1], "Mood Level"] = new_mood
                    else:
                        new_row = pd.DataFrame({"Date": [today_str], "Mood Level": [new_mood]})
                        mood_history_df = pd.concat([mood_history_df.iloc[1:], new_row], ignore_index=True)
                    st.session_state.mood_history = mood_history_df
                    
                    # Rerender results beautifully
                    st.success("Analysis Complete! Your mood history has been updated.")
                    
                    col1, col2 = st.columns([1, 1.5], gap="large")
                    
                    with col1:
                        # Stress Index Card
                        card_class = f"stress-{stress_level}"
                        stress_desc = "Low/Calm" if stress_level <= 3 else "Moderate" if stress_level <= 7 else "Severe Stress"
                        
                        st.markdown(f"""
                        <div class="glass-card {card_class}">
                            <h4 style='color: #FFFFFF; margin-top: 0;'>Stress Level Index</h4>
                            <div style='display: flex; align-items: baseline;'>
                                <span style='font-size: 3rem; font-weight: 800; color: #FFFFFF;'>{stress_level}</span>
                                <span style='font-size: 1.25rem; color: #94A3B8; margin-left: 5px;'>/ 10</span>
                            </div>
                            <p style='color: #E2E8F0; font-weight: 600; margin-top: 10px;'>Status: {stress_desc}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Stress Triggers Card
                        triggers_html = "".join([f"<span class='custom-badge trigger-badge'>{t}</span>" for t in triggers]) if triggers else "<span style='color: #64748B;'>No stress triggers detected.</span>"
                        st.markdown(f"""
                        <div class="glass-card">
                            <h4 style='color: #FFFFFF; margin-top: 0;'>🔍 Detected Stress Triggers</h4>
                            <div style='margin-top: 15px;'>{triggers_html}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Emotional Patterns
                        patterns_html = "".join([f"<span class='custom-badge'>{p}</span>" for p in emotional_patterns]) if emotional_patterns else "<span style='color: #64748B;'>No clear emotional patterns.</span>"
                        st.markdown(f"""
                        <div class="glass-card">
                            <h4 style='color: #FFFFFF; margin-top: 0;'>🧠 Emotional Patterns & Self-Doubt</h4>
                            <div style='margin-top: 15px;'>{patterns_html}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col2:
                        # Personalized Coping Strategy
                        st.markdown(f"""
                        <div class="glass-card" style="height: 100%;">
                            <h4 style='color: #A78BFA; margin-top: 0;'>🧘 Personalized Coping Plan</h4>
                            <div style='color: #E2E8F0; margin-top: 15px; font-size: 1rem; line-height: 1.6;'>
                                {coping_strategy}
                            </div>
                            <hr style="border-color: rgba(255,255,255,0.08); margin: 25px 0 15px 0;" />
                            <h5 style="color: #A78BFA; margin-top: 0; text-align: center;">Mindful Breathing Guide</h5>
                            <div class="breathing-circle"></div>
                            <p style="text-align: center; color: #94A3B8; font-size: 0.9em; margin-bottom: 0;">Follow the pulsating circle. Inhale (expand) and Exhale (contract).</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Failed to analyze. Please check your API key or connection. Details: {e}")

# 5. TAB 2: EMPATHETIC CHAT COMPANION
with tab2:
    st.markdown("<h3 style='color: #A78BFA; font-weight: 700; margin-top: 10px;'>Talk to MindSync Companion</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>An AI companion ready to listen, validate your feelings, and help you wind down. No academic tutoring, no judgment.</p>", unsafe_allow_html=True)
    
    # Initialize message list
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi there! I know study sessions can get intense, and mock tests can be tough. I'm here if you want to vent or need a quick breathing break. What's on your mind today?"}
        ]
        
    # Render Chat messages
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end;">
                <div class="chat-bubble-user">
                    {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start;">
                <div class="chat-bubble-companion">
                    <span style="font-weight: 600; color: #A78BFA;">🧘 MindSync Companion:</span><br/>
                    {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    # Chat Input
    user_input = st.chat_input("Vibe-check or share how you're feeling...")
    
    if user_input:
        # Append user message
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        
        # Display immediately
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end;">
            <div class="chat-bubble-user">
                {user_input}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Retrieve companion response
        if not api_key:
            reply = "I'd love to chat and support you, but I need a valid Gemini API Key to connect. Please provide your key in the sidebar!"
            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start;">
                <div class="chat-bubble-companion">
                    <span style="font-weight: 600; color: #A78BFA;">🧘 MindSync Companion:</span><br/>
                    {reply}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Writing..."):
                try:
                    # Configure SDK
                    genai.configure(api_key=api_key)
                    
                    # Continuous Chat initialization or recovery
                    if "gemini_chat" not in st.session_state or st.session_state.gemini_chat is None:
                        model = genai.GenerativeModel(
                            model_name="gemini-3.5-flash",
                            system_instruction="You are an exceptionally warm, empathetic, and grounded digital companion for students going through intense academic pressure. Focus entirely on emotional validation, stress reduction, and motivational encouragement. Keep responses short and conversational. Never provide academic tutoring. If the user expresses extreme crisis, safely point them to standard professional medical resources."
                        )
                        st.session_state.gemini_chat = model.start_chat(history=[])
                    
                    # Send message
                    response = st.session_state.gemini_chat.send_message(user_input)
                    reply = response.text
                    
                    # Save assistant message
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    
                    # Refresh the UI page to show new chat history properly
                    st.rerun()
                    
                except Exception as e:
                    # Backup generation if chat object fails
                    try:
                        model = genai.GenerativeModel("gemini-3.5-flash")
                        history_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_messages[:-1]])
                        prompt = f"""
                        System Instruction: You are an exceptionally warm, empathetic, and grounded digital companion for students going through intense academic pressure. Focus entirely on emotional validation, stress reduction, and motivational encouragement. Keep responses short and conversational. Never provide academic tutoring. If the user expresses extreme crisis, safely point them to standard professional medical resources.
                        
                        Conversation History:
                        {history_context}
                        
                        User message: {user_input}
                        """
                        response = model.generate_content(prompt)
                        reply = response.text
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error connecting to AI: {ex}")
                        
    # Standard medical support card
    st.markdown("""
    <div style="margin-top: 40px;" class="glass-card">
        <h4 style="color: #EF4444; margin-top: 0;">🚨 Urgent Crisis Support Helpline</h4>
        <p style="color: #E2E8F0; margin-bottom: 10px;">If you are experiencing extreme emotional distress, hopelessness, or thoughts of self-harm, please reach out to one of the following free, confidential, and professional 24/7 helplines:</p>
        <ul style="color: #94A3B8; padding-left: 20px;">
            <li><b>AASRA Helpline:</b> +91-9820466726 (Call 24/7 for support across India)</li>
            <li><b>KIRAN Mental Health Helpline:</b> 1800-599-0019 (Government helpline)</li>
            <li><b>Vandrevala Foundation Helpline:</b> +91-9999666555</li>
            <li><b>Tele-MANAS:</b> 14416 or 1800 891 4416</li>
        </ul>
        <p style="color: #E2E8F0; font-size: 0.85em; margin-top: 10px;">Please remember: seeking professional help is a sign of strength. You do not have to carry this alone.</p>
    </div>
    """, unsafe_allow_html=True)
