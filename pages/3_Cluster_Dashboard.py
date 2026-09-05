import streamlit as st
import plotly.graph_objects as go
from utils.data_loader import load_learner_features, load_cluster_profiles
from utils.theme import CLUSTER_COLORS, CLUSTER_ICONS
from utils.theme import apply_custom_css
apply_custom_css()

st.set_page_config(page_title="Cluster Dashboard | EduPro", page_icon="🧭", layout="wide")

learner_features = load_learner_features()
cluster_profiles = load_cluster_profiles()

st.title("🧭 Cluster Dashboard")
st.markdown("A visual map of EduPro's 5 learner segments, projected into two dimensions.")
st.divider()

fig = go.Figure()

for cluster_id in sorted(learner_features['cluster'].unique()):
    subset = learner_features[learner_features['cluster'] == cluster_id]
    fig.add_trace(go.Scatter(
        x=subset['viz_x'],
        y=subset['viz_y'],
        mode='markers',
        name=subset['cluster_name'].iloc[0],
        marker=dict(color=CLUSTER_COLORS[cluster_id], size=5, opacity=0.6),
        hovertext=subset.index,
        hoverinfo='text+name'
    ))

fig.update_layout(
    xaxis_title="Component 1",
    yaxis_title="Component 2",
    height=600,
    legend_title="Segment"
)

st.plotly_chart(fig, use_container_width=True)
st.caption("This 2D view captures ~22% of the full feature space and is a simplified visual guide — actual segment assignment uses all 23 engineered features.")

st.divider()
st.subheader("Segment Guide")

descriptions = {
    0: "Small but high-value: fewer enrollments, but the highest spend and paid-course rate of any segment.",
    1: "The largest segment — learners who jump straight into Advanced content, often in a single enrollment.",
    2: "The most engaged segment by far: highest enrollment volume, most recently active, spread across levels.",
    3: "Budget-conscious and Intermediate-focused, but the most satisfied — highest average course ratings.",
    4: "Just starting out — almost exclusively Beginner-level courses, moderate spend.",
}

cols = st.columns(5)
for idx, row in cluster_profiles.iterrows():
    cluster_id = row['cluster']
    with cols[idx]:
        st.markdown(f"### {CLUSTER_ICONS[cluster_id]}")
        st.markdown(f"**{row['cluster_name']}**")
        st.caption(f"{row['size']:,} learners · {row['pct_of_users']}%")
        st.write(descriptions[cluster_id])
        
        
st.divider()
st.subheader("Explore by Feature")

color_option = st.selectbox(
    "Color points by",
    options=['Cluster', 'Total Enrollments', 'Avg Spend', 'Recency (days)', 'Pct Paid']
)

feature_map = {
    'Total Enrollments': 'total_enrollments',
    'Avg Spend': 'avg_spend',
    'Recency (days)': 'recency_days',
    'Pct Paid': 'pct_paid',
}

if color_option == 'Cluster':
    st.info("Scroll up — the main scatter plot above already shows cluster coloring.")
else:
    feature_col = feature_map[color_option]
    
    custom_scale = [
    [0.0, '#D9CBB0'],   # low — matches our muted tan border color, not the cream background
    [0.5, '#C97B3D'],   # mid — our terracotta cluster color
    [1.0, '#7A2E2E'],   # high — our deep maroon cluster color
    ]
    
    fig2 = go.Figure(data=go.Scatter(
        x=learner_features['viz_x'],
        y=learner_features['viz_y'],
        mode='markers',
        marker=dict(
            color=learner_features[feature_col],
            colorscale=custom_scale,
            colorbar=dict(title=color_option),
            size=5,
            opacity=0.6
        ),
        hovertext=learner_features.index,
        hoverinfo='text'
    ))
    fig2.update_layout(xaxis_title="Component 1", yaxis_title="Component 2", height=600)
    st.plotly_chart(fig2, use_container_width=True)