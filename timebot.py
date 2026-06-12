import streamlit as st
import requests
import json
import google.generativeai as genai
from gtts import gTTS
from PIL import Image
import io
import os
from datetime import datetime
import base64
#from stability_sdk import client
#from stability_sdk.interfaces.gooseai.generation.generation_pb2 import *

# Configure the page with new theme
st.set_page_config(
    page_title="Chronicles AI - Historical Journey",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS with new theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #2E86AB;
        --secondary: #A23B72;
        --accent: #F18F01;
        --dark: #2B2D42;
        --light: #F8F9FA;
        --success: #28A745;
    }
    
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: var(--dark);
        text-align: center;
        margin-bottom: 2rem;
        opacity: 0.8;
    }
    
    .card {
        background: peachpuff;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border-left: 5px solid var(--accent);
    }
    
    .timeline-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }
    
    .perspective-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }
    
    .story-container {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        padding: 0.7rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, var(--dark) 0%, #1a1b2d 100%);
    }
    
    /* Custom input styling */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.7rem;
    }
    
    .stSelectbox>div>div>div {
        border-radius: 10px;
    }
    
    /* Achievement badges */
    .badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        background: var(--accent);
        color: white;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'events_data' not in st.session_state:
    st.session_state.events_data = None
if 'selected_year' not in st.session_state:
    st.session_state.selected_year = None
if 'journey_count' not in st.session_state:
    st.session_state.journey_count = 0
if 'image_settings' not in st.session_state:
    st.session_state.image_settings = {
        "style": "Cinematic realism",
        "mood": "Dramatic",
        "aspect_ratio": "16:9"
    }

# New header section
st.markdown('<div class="main-header">🌍 Nostalgic Ai</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle" style="color: green;">Step into the past through immersive AI-generated historical experiences</div>',
    unsafe_allow_html=True
)

# Sidebar for navigation and info
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    st.markdown("---")
    
    if st.session_state.generated_content:
        st.success(f"🎯 Currently exploring: {st.session_state.generated_content['year']}")
        if st.button("🔄 Start New Journey"):
            # Cleanup audio file
            if (st.session_state.generated_content.get('audio_file') and 
                os.path.exists(st.session_state.generated_content['audio_file'])):
                os.remove(st.session_state.generated_content['audio_file'])
            
            # Reset session state
            st.session_state.generated_content = None
            st.session_state.events_data = None
            st.session_state.selected_year = None
            st.rerun()
    else:
        st.info("✨ Enter a year to begin your historical journey")
    
    st.markdown("---")
    st.markdown("### 📊 Your Progress")
    st.markdown(f"**Journeys Completed:** {st.session_state.journey_count}")
    
    # Achievement badges
    if st.session_state.journey_count >= 1:
        st.markdown('<span class="badge">🎖️ First Journey</span>', unsafe_allow_html=True)
    if st.session_state.journey_count >= 3:
        st.markdown('<span class="badge">🏆 History Buff</span>', unsafe_allow_html=True)
    if st.session_state.journey_count >= 5:
        st.markdown('<span class="badge">👑 Time Master</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("• Try different years and perspectives")
    st.markdown("• Explore both well-known and obscure historical periods")
    st.markdown("• Use headphones for the best audio experience")
    
    st.markdown("---")
    st.markdown("### 🎨 Image Studio")
    image_style = st.selectbox(
        "Visual style",
        ["Cinematic realism", "Vintage painting", "Documentary photo", "Illustrated concept art"],
        index=["Cinematic realism", "Vintage painting", "Documentary photo", "Illustrated concept art"].index(
            st.session_state.image_settings["style"]
        )
    )
    image_mood = st.selectbox(
        "Mood",
        ["Dramatic", "Hopeful", "Somber", "Triumphant"],
        index=["Dramatic", "Hopeful", "Somber", "Triumphant"].index(
            st.session_state.image_settings["mood"]
        )
    )
    image_aspect = st.selectbox(
        "Aspect ratio",
        ["16:9", "1:1", "3:2", "9:16"],
        index=["16:9", "1:1", "3:2", "9:16"].index(
            st.session_state.image_settings["aspect_ratio"]
        )
    )
    st.session_state.image_settings = {
        "style": image_style,
        "mood": image_mood,
        "aspect_ratio": image_aspect
    }

# Hardcoded API Keys
perplexity_api_key = "ppl"
gemini_api_key = "A1zs"
stability_api_key = "REVAAENR"

# API functions (same as before, but keeping them for completeness)
def get_historical_events(year, api_key):
    """Fetch historical events using Perplexity AI"""
    url = "https://api.perplexity.ai/chat/completions"
    
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": """You are a expert historian. Extract 3-5 major historical events for the given year. 
                For each event, suggest 4 interesting perspectives from which to experience the event.
                Return ONLY valid JSON in this exact format:
                {
                    "events": [
                        {
                            "event": "Event name",
                            "date": "Specific date if known", 
                            "significance": "Brief significance",
                            "perspectives": ["Perspective 1", "Perspective 2", "Perspective 3", "Perspective 4"]
                        }
                    ]
                }"""
            },
            {
                "role": "user",
                "content": f"What were the major globally significant historical events in {year}? Focus on events that had wide impact."
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
        "search_mode": "web",
        "return_related_questions": False
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Clean the response and parse JSON
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        
        data = json.loads(content)
        return data.get('events', [])
        
    except Exception as e:
        st.error(f"❌ Error fetching historical events: {str(e)}")
        return get_fallback_events(year)

def get_fallback_events(year):
    """Fallback events if API fails"""
    fallback_events = {
        "1947": [
            {
                "event": "India's Independence",
                "date": "August 15, 1947",
                "significance": "India gained independence from British rule",
                "perspectives": ["Freedom Fighter", "British Soldier", "Local Merchant", "Journalist"]
            },
            {
                "event": "Partition of India", 
                "date": "August 14, 1947",
                "significance": "Division of British India into India and Pakistan",
                "perspectives": ["Refugee", "Government Official", "Relief Worker", "Historian"]
            }
        ],
        "1969": [
            {
                "event": "Apollo 11 Moon Landing",
                "date": "July 20, 1969",
                "significance": "First humans walked on the moon",
                "perspectives": ["Astronaut", "Mission Control Engineer", "TV Viewer", "Scientist"]
            }
        ]
    }
    
    return fallback_events.get(year, [
        {
            "event": f"Major Historical Events of {year}",
            "date": year,
            "significance": "Significant events that shaped history during this period",
            "perspectives": ["Witness", "Participant", "Historian", "Journalist"]
        }
    ])

def generate_story(event, perspective, year, gemini_api_key):
    """Generate historical story using Gemini"""
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Write an immersive, first-person historical narrative from the perspective of a {perspective} 
        experiencing the event: "{event['event']}" in the year {year}.
        
        Requirements:
        - Write in first-person perspective as if the reader IS the {perspective}
        - Make it emotionally engaging and historically plausible
        - Include sensory details (sights, sounds, smells)
        - Length: 300-400 words
        - Focus on the human experience and emotions
        - Historical accuracy is important
        
        Event context: {event.get('significance', '')}
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        st.error(f"❌ Story generation failed: {str(e)}")
        return f"""**Story from {perspective} perspective:**

As a {perspective}, I found myself at the heart of {event['event']} in {year}. The air was thick with anticipation and the weight of history unfolding before my eyes.

{event.get('significance', 'This moment would echo through time, shaping the world in ways we could scarcely imagine.')}

I could feel the collective energy of the crowd, hear the distant sounds that marked this pivotal moment, and sense the profound shift happening around me. As someone experiencing this firsthand, the emotions ranged from awe to trepidation, from hope to solemn responsibility.

This was not just an event in a history book—it was a living, breathing moment that would define generations to come."""

def generate_image(event, perspective, year, api_key, style="Cinematic realism", mood="Dramatic", aspect_ratio="16:9"):
    """Generate historical image using Stability AI"""
    try:
        url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        
        prompt = (
            f"Historical scene: {event['event']} in {year} from {perspective} perspective. "
            f"Style: {style}. Mood: {mood}. Highly detailed, visually immersive, authentic period clothing and environment."
        )
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'image/*'
        }
        
        data = {
            'prompt': prompt,
            'output_format': 'webp',
            'aspect_ratio': aspect_ratio,
            'negative_prompt': 'text overlays, modern objects, watermark, logo, blurry, distorted faces'
        }
        
        response = requests.post(url, headers=headers, files={'none': ''}, data=data, timeout=30)
        response.raise_for_status()
        
        return response.content, prompt
        
    except Exception as e:
        st.error(f"❌ Image generation failed: {str(e)}")
        return None, None

def generate_audio(story_text):
    """Generate audio from story text using gTTS"""
    try:
        if len(story_text) > 4000:
            story_text = story_text[:4000] + "... [story continues]"
        
        tts = gTTS(text=story_text, lang='en', slow=False)
        audio_file = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        tts.save(audio_file)
        return audio_file
        
    except Exception as e:
        st.error(f"❌ Audio generation failed: {str(e)}")
        return None

def display_events_interface(events, year, perplexity_api_key, gemini_api_key, stability_api_key):
    """Display events and perspectives for user selection with new design"""
    st.markdown(
    f'<div class="card"><h3 style="color: black;">📜 Historical Events in {year}</h3></div>',
    unsafe_allow_html=True
)

    # Create event selection with cards
    event_options = [f"{i+1}. {event['event']} ({event.get('date', 'Date unknown')})" 
                    for i, event in enumerate(events)]
    
    selected_event_str = st.selectbox("**Select an historical event:**", event_options, key="event_selector")
    event_index = int(selected_event_str.split('.')[0]) - 1
    selected_event = events[event_index]
    
    # Display event significance in a card
    st.markdown(f'<div class="timeline-card"><strong>📖 Significance:</strong> {selected_event["significance"]}</div>', unsafe_allow_html=True)
    
    # Perspective selection with cards
    st.markdown("### 👥 Choose Your Perspective")
    col1, col2, col3, col4 = st.columns(4)
    
    perspectives = selected_event['perspectives']
    for i, perspective in enumerate(perspectives):
        with [col1, col2, col3, col4][i]:
            st.markdown(f'<div class="perspective-card" style="text-align: center; cursor: pointer;" onclick="alert(\'Selected: {perspective}\')">{perspective}</div>', unsafe_allow_html=True)
    
    perspective = st.selectbox("**Experience through the eyes of:**", 
                              perspectives, key="perspective_selector")
    
    # Generate button with new styling
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 Generate Immersive Experience", use_container_width=True, key="generate_btn"):
            with st.spinner("🌌 Crafting your journey through time..."):
                # Generate story
                story = generate_story(selected_event, perspective, year, gemini_api_key)
                if not story:
                    st.error("❌ Failed to generate story")
                    return
                
                # Generate image
                image_bytes, image_prompt = generate_image(
                    selected_event,
                    perspective,
                    year,
                    stability_api_key,
                    st.session_state.image_settings["style"],
                    st.session_state.image_settings["mood"],
                    st.session_state.image_settings["aspect_ratio"]
                )
                
                # Generate audio
                audio_file = generate_audio(story)
                
                # Store in session state
                st.session_state.generated_content = {
                    'event': selected_event,
                    'perspective': perspective,
                    'year': year,
                    'story': story,
                    'image_bytes': image_bytes,
                    'audio_file': audio_file,
                    'image_prompt': image_prompt,
                    'image_settings': dict(st.session_state.image_settings)
                }
                
                st.session_state.journey_count += 1
                st.rerun()

def display_generated_content():
    """Display the generated story, image, and audio with new design"""
    content = st.session_state.generated_content
    
    st.markdown("---")
    st.markdown('<div class="main-header">🎭 Your Historical Journey</div>', unsafe_allow_html=True)
    
    # Display event info in a modern card layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### 🌟 {content['year']}: {content['event']['event']}")
        st.markdown(f"**🧑‍💼 Perspective:** {content['perspective']}")
        st.markdown(f"**📅 Date:** {content['event'].get('date', 'Historical period')}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("### 📊 Journey Stats")
        st.markdown(f"**Year Explored:** {content['year']}")
        st.markdown(f"**Total Journeys:** {st.session_state.journey_count}")
        st.markdown(f"**Perspective:** {content['perspective']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display image with enhanced styling
    if content['image_bytes']:
        st.markdown("### 🖼️ Historical Reconstruction")
        try:
            image = Image.open(io.BytesIO(content['image_bytes']))
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.image(image, use_container_width=True, 
                        caption=f"✨ {content['event']['event']} - Through the eyes of a {content['perspective']}")
                if content.get('image_settings'):
                    settings = content['image_settings']
                    st.caption(
                        f"Style: {settings.get('style', 'N/A')} | Mood: {settings.get('mood', 'N/A')} | Aspect: {settings.get('aspect_ratio', 'N/A')}"
                    )
                with st.expander("🧠 Image prompt details"):
                    st.code(content.get('image_prompt', 'Prompt not available'))
        except Exception as e:
            st.error(f"❌ Error displaying image: {str(e)}")
    
    # Display story with new container
    st.markdown("### 📖 Immersive Narrative")
    with st.expander("✨ Explore Your Story", expanded=True):
       st.markdown(
    f'<div class="story-container" style="color: black;">{content["story"]}</div>',
    unsafe_allow_html=True
)

    # Audio player with better styling
    if content['audio_file'] and os.path.exists(content['audio_file']):
        st.markdown("### 🔊 Audio Narration")
        with open(content['audio_file'], "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.audio(audio_bytes, format='audio/mp3')
    
    # Action buttons at the bottom
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🖼️ Regenerate Image Only", use_container_width=True):
            with st.spinner("🎨 Re-rendering visual scene..."):
                new_image_bytes, new_prompt = generate_image(
                    content['event'],
                    content['perspective'],
                    content['year'],
                    stability_api_key,
                    st.session_state.image_settings["style"],
                    st.session_state.image_settings["mood"],
                    st.session_state.image_settings["aspect_ratio"]
                )
                if new_image_bytes:
                    st.session_state.generated_content['image_bytes'] = new_image_bytes
                    st.session_state.generated_content['image_prompt'] = new_prompt
                    st.session_state.generated_content['image_settings'] = dict(st.session_state.image_settings)
                    st.rerun()
                else:
                    st.warning("Could not regenerate image. Please try again.")
    with col2:
        if st.button("🌍 Start New Historical Journey", use_container_width=True):
            # Cleanup audio file
            if (st.session_state.generated_content.get('audio_file') and 
                os.path.exists(st.session_state.generated_content['audio_file'])):
                os.remove(st.session_state.generated_content['audio_file'])
            
            # Reset session state
            st.session_state.generated_content = None
            st.session_state.events_data = None
            st.session_state.selected_year = None
            st.rerun()

# Main app functionality with new layout
def main():
    # API key validation
    if not all([perplexity_api_key, gemini_api_key, stability_api_key]):
        st.error("❌ Please update the API keys in the code with your actual API keys")
        st.info("🔑 Replace 'your_perplexity_api_key_here', 'your_gemini_api_key_here', and 'your_stability_api_key_here' with your actual API keys")
        return
    
    # Check if API keys are still placeholder values
    if ("your_perplexity_api_key_here" in perplexity_api_key or 
        "your_gemini_api_key_here" in gemini_api_key or 
        "your_stability_api_key_here" in stability_api_key):
        st.error("❌ Please update the API keys in the code with your actual API keys")
        st.info("🔑 Replace the placeholder API keys with your actual API keys in the code")
        return
    
    # Main content area
    if not st.session_state.generated_content:
        st.markdown("---")
        
        # Year input section with new design
        st.markdown('<div class="card"><h3 ">🔮 Begin Your Journey</h3></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            year_input = st.text_input("**Enter a historical year to explore:**", 
                                      placeholder="e.g., 1969, 1776, 1945, 1066...",
                                      key="year_input")
            
            search_clicked = st.button("🔍 Discover Historical Events", use_container_width=True, key="search_btn")
        
        # Popular years quick selection
        st.markdown("### ⚡ Quick Select Popular Years")
        quick_cols = st.columns(5)
        quick_years = ["1776", "1865", "1912", "1945", "1969"]
        for i, year in enumerate(quick_years):
            with quick_cols[i]:
                if st.button(f"🗓️ {year}", use_container_width=True):
                    st.session_state.quick_year = year
                    st.rerun()
        
        # Store events in session state to prevent re-fetching
        if search_clicked and year_input:
            if not year_input.isdigit():
                st.error("❌ Please enter a valid year (numbers only)")
                return
            
            with st.spinner("🔍 Exploring historical archives..."):
                events = get_historical_events(year_input, perplexity_api_key)
            
            if events:
                st.session_state.events_data = events
                st.session_state.selected_year = year_input
                st.rerun()
            else:
                st.error("❌ No historical events found for this year. Try another year!")
    
    # Display events interface if we have data
    if st.session_state.events_data and st.session_state.selected_year:
        display_events_interface(
            st.session_state.events_data, 
            st.session_state.selected_year,
            perplexity_api_key,
            gemini_api_key, 
            stability_api_key
        )
    
    # Display generated content if available
    if st.session_state.generated_content:
        display_generated_content()

# Run the app
if __name__ == "__main__":
    main()
