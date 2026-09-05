import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

CLUSTER_COLORS = {
    0: '#B8860B',  # Premium Explorers — brass/gold
    1: '#7A2E2E',  # Advanced Single-Shot Learners — deep maroon
    2: '#1B2A4A',  # Power Learners — deep navy
    3: '#3B7A57',  # Intermediate Value Seekers — forest green
    4: '#C97B3D',  # Beginner Explorers — warm terracotta
}

CLUSTER_ICONS = {
    0: '💎',  # Premium Explorers
    1: '🎯',  # Advanced Single-Shot Learners
    2: '🚀',  # Power Learners
    3: '🌿',  # Intermediate Value Seekers
    4: '🌱',  # Beginner Explorers
}

edupro_template = go.layout.Template()
edupro_template.layout = go.Layout(
    paper_bgcolor='#FAF6EE',
    plot_bgcolor='#FFFDF8',
    font=dict(family='Inter, sans-serif', color='#1B2A4A'),
    title_font=dict(family='Lora, serif', color='#1B2A4A'),
    colorway=[CLUSTER_COLORS[i] for i in range(5)],
)

pio.templates['edupro'] = edupro_template
pio.templates.default = 'edupro'

# in utils/theme.py, add:
def apply_custom_css():
        
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            border-right: 1px solid #D9CBB0;
        }
        </style>
    """, unsafe_allow_html=True)
    
def render_sidebar_footer():
    with st.sidebar:
        for i in range(17):
            st.write("")  # Add some spacing
        st.divider()
        st.caption("🎓 EduPro Learner Insights")
        st.caption("Segmentation & Recommendation System")
    