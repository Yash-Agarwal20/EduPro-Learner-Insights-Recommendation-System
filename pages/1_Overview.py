import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_learner_features, load_cluster_profiles, 
    load_courses, load_enrollment_history
)
from utils.theme import CLUSTER_COLORS, CLUSTER_ICONS
import plotly.graph_objects as go
from utils.theme import apply_custom_css
apply_custom_css()

st.set_page_config(page_title="Overview | EduPro", page_icon="🎓", layout="wide")

learner_features = load_learner_features()
cluster_profiles = load_cluster_profiles()
courses = load_courses()
enrollment_history = load_enrollment_history()

st.title("📊 Overview")
st.markdown("A high-level look at EduPro's learner base, course catalog, and behavioral segments.")
st.divider()

st.subheader("Dataset Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Learners", f"{len(learner_features):,}")

with col2:
    st.metric("Courses", f"{len(courses)}")

with col3:
    st.metric("Total Enrollments", f"{len(enrollment_history):,}")

with col4:
    avg_rating = courses['CourseRating'].mean()
    st.metric("Avg Course Rating", f"{avg_rating:.2f} / 5")
    
    
st.divider()
st.subheader("Segment Sizes")

fig = go.Figure(data=[
    go.Bar(
        x=cluster_profiles['cluster_name'],
        y=cluster_profiles['size'],
        marker_color=[CLUSTER_COLORS[c] for c in cluster_profiles['cluster']],
        text=cluster_profiles['size'],
        textposition='outside',
    )
])

fig.update_layout(
    xaxis_title="Segment",
    yaxis_title="Number of Learners",
    height=450,
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    cluster_profiles[['cluster_name', 'size', 'pct_of_users']].rename(
        columns={'cluster_name': 'Segment', 'size': 'Learners', 'pct_of_users': '% of Users'}
    ),
    hide_index=True,
    use_container_width=True
)

if st.button("🧭 Explore clusters in more detail", key="goto_cluster_btn", type="primary"):
    st.switch_page("pages/3_Cluster_Dashboard.py")
    
st.divider()

    
import ast

st.subheader("Segment Snapshots")

cols = st.columns(5)

for idx, row in cluster_profiles.iterrows():
    cluster_id = row['cluster']
    with cols[idx]:
        st.markdown(f"### {CLUSTER_ICONS[cluster_id]}")
        st.markdown(f"**{row['cluster_name']}**")
        st.caption(f"{row['size']:,} learners · {row['pct_of_users']}%")
        
        top_cats = row['top_3_cat']
        if isinstance(top_cats, str):
            top_cats = ast.literal_eval(top_cats)  # safely parse the string back into a real list
        
        st.markdown(f"*Top category:* {top_cats[0]}")
        
        