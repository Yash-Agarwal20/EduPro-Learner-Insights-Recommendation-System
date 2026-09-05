import streamlit as st
from utils.data_loader import load_learner_features, load_cluster_profiles
from utils.theme import apply_custom_css, render_sidebar_footer

st.set_page_config(
    page_title="EduPro Learner Insights",
    page_icon="🎓",
    layout="wide"
)

apply_custom_css()
render_sidebar_footer()


def home_page():
    learner_features = load_learner_features()
    cluster_profiles = load_cluster_profiles()

    st.title("🎓 EduPro Learner Insights")
    st.markdown(
        "A learner segmentation and personalized course recommendation system for EduPro, "
        "built on behavioral clustering and content-aware scoring. "
        "Use the sidebar to explore learner profiles, cluster segments, and personalized recommendations."
    )

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        st.metric("Total Learners", f"{len(learner_features):,}")

    with col2:
        st.metric("Segments Identified", f"{len(cluster_profiles)}")

    with col3:
        largest_segment = cluster_profiles.loc[cluster_profiles['size'].idxmax()]
        st.metric("Largest Segment", largest_segment['cluster_name'], f"{largest_segment['pct_of_users']}% of users")

    st.divider()
    st.info("👈 Select a page from the sidebar to get started.")

pages = [
    st.Page(
        home_page,
        title="Home",
        icon="🏠"
    ),

    st.Page(
        "pages/1_Overview.py",
        title="Overview",
        icon="📊"
    ),

    st.Page(
        "pages/2_Learner_Profile_Explorer.py",
        title="Learner Profile",
        icon="🔍"
    ),

    st.Page(
        "pages/3_Cluster_Dashboard.py",
        title="Cluster Dashboard",
        icon="🧭"
    ),

    st.Page(
        "pages/4_Recommendations.py",
        title="Recommendations",
        icon="🎯"
    ),

    st.Page(
        "pages/5_Segment_Comparison.py",
        title="Segment Comparison",
        icon="📈"
    ),
]


pg = st.navigation(pages)

pg.run()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=Inter:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Lora', serif !important;
    }
    </style>
""", unsafe_allow_html=True)
