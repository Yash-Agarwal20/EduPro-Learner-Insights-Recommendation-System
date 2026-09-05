import streamlit as st
import plotly.graph_objects as go
from utils.data_loader import load_cluster_profiles
from utils.theme import CLUSTER_COLORS, CLUSTER_ICONS
from utils.theme import apply_custom_css
apply_custom_css()

st.set_page_config(page_title="Segment Comparison | EduPro", page_icon="📈", layout="wide")

cluster_profiles = load_cluster_profiles()

st.title("📈 Segment Comparison")
st.markdown("Compare EduPro's learner segments side by side across key behavioral dimensions.")
st.divider()

segment_options = cluster_profiles['cluster_name'].tolist()

selected_segments = st.multiselect(
    "Select segments to compare",
    options=segment_options,
    default=segment_options
)

if len(selected_segments) < 2:
    st.warning("Select at least 2 segments to compare.")
    st.stop()

comparison_df = cluster_profiles[cluster_profiles['cluster_name'].isin(selected_segments)]

st.divider()
st.subheader("Behavioral Comparison")

radar_metrics = {
    'total_enrollments': 'Enrollment Volume',
    'avg_spend': 'Avg Spend',
    'pct_paid': '% Paid',
    'avg_course_rating_enrolled': 'Avg Rating',
    'recency_days': 'Recency',
}

# Normalize each metric 0-1 across ALL 5 clusters (not just selected ones, so scale stays consistent 
# regardless of which segments are toggled on/off)
normalized = cluster_profiles.copy()
for col in radar_metrics:
    col_min, col_max = cluster_profiles[col].min(), cluster_profiles[col].max()
    if col == 'recency_days':
        # invert recency: LOWER days = MORE recently active = should read as "higher" on the chart
        normalized[col] = 1 - (cluster_profiles[col] - col_min) / (col_max - col_min)
    else:
        normalized[col] = (cluster_profiles[col] - col_min) / (col_max - col_min)

fig = go.Figure()

for _, row in normalized[normalized['cluster_name'].isin(selected_segments)].iterrows():
    cluster_id = row['cluster']
    values = [row[col] for col in radar_metrics]
    values.append(values[0])  # close the loop
    labels = list(radar_metrics.values())
    labels.append(labels[0])
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        name=row['cluster_name'],
        line=dict(color=CLUSTER_COLORS[cluster_id])
    ))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    height=550
)

st.plotly_chart(fig, use_container_width=True)
st.caption("All metrics normalized 0-1 across all 5 segments. Recency is inverted so higher = more recently active.")

st.divider()
st.subheader("Detailed Comparison")

table_cols = ['cluster_name', 'size', 'pct_of_users', 'total_enrollments', 'avg_spend', 'pct_paid', 'avg_course_rating_enrolled', 'recency_days', 'Age']

display_table = comparison_df[table_cols].rename(columns={
    'cluster_name': 'Segment', 'size': 'Learners', 'pct_of_users': '% of Users',
    'total_enrollments': 'Avg Enrollments', 'avg_spend': 'Avg Spend (₹)',
    'pct_paid': '% Paid', 'avg_course_rating_enrolled': 'Avg Rating',
    'recency_days': 'Recency (days)', 'Age': 'Avg Age'
})

st.dataframe(display_table, hide_index=True, use_container_width=True)


st.divider()
st.subheader("Level Distribution by Segment")

level_cols = ['beginner_share', 'intermediate_share', 'advanced_share']
level_labels = ['Beginner', 'Intermediate', 'Advanced']

fig2 = go.Figure()

for _, row in comparison_df.iterrows():
    cluster_id = row['cluster']
    fig2.add_trace(go.Bar(
        name=row['cluster_name'],
        x=level_labels,
        y=[row[c] for c in level_cols],
        marker_color=CLUSTER_COLORS[cluster_id]
    ))

fig2.update_layout(
    barmode='group',
    yaxis_title="Share of Enrollments",
    yaxis_range=[0, 1],
    height=450
)

st.plotly_chart(fig2, use_container_width=True)