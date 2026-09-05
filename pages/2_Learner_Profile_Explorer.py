import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_learner_features, load_cluster_profiles, 
    load_enrollment_history, load_courses, load_cluster_popularity
)
from utils.scoring import get_top_n_recommendations, check_filter_exists_in_catalog
from utils.theme import CLUSTER_COLORS, CLUSTER_ICONS
import plotly.graph_objects as go
import textwrap
from utils.theme import apply_custom_css
apply_custom_css()

st.set_page_config(page_title="Learner Profile Explorer | EduPro", page_icon="🔍", layout="wide")

learner_features = load_learner_features()
cluster_profiles = load_cluster_profiles()
enrollment_history = load_enrollment_history()
courses = load_courses()
cluster_popularity = load_cluster_popularity()

st.title("🔍 Learner Profile Explorer")
st.markdown("Select a learner to view their profile, segment, enrollment history, and personalized recommendations.")
st.divider()

all_user_ids = learner_features.index.tolist()

if 'selected_user_id' not in st.session_state:
    st.session_state['selected_user_id'] = all_user_ids[0]

col_select, col_random = st.columns([4, 1])

with col_random:
    st.write("")
    st.write("")
    if st.button("🎲 Random Learner"):
        st.session_state['selected_user_id'] = pd.Series(all_user_ids).sample(1).iloc[0]

with col_select:
    st.selectbox(
        "Select a learner",
        options=all_user_ids,
        key='selected_user_id'
    )

selected_user_id = st.session_state['selected_user_id']

st.divider()

learner = learner_features.loc[selected_user_id]
cluster_id = learner['cluster']
color = CLUSTER_COLORS[cluster_id]

col_header, col_badge, col_spacer = st.columns([1.2, 1.3, 2.5], vertical_alignment="center")

with col_header:
    st.subheader(f"{selected_user_id}")
    st.caption(f"Age {learner['Age']} · {learner['Gender']}")

with col_badge:
    st.markdown(
        f"""
        <div style="background-color:{color}22; border-left: 4px solid {color}; 
                     padding: 12px 16px; border-radius: 6px; text-align: left; display: inline-block;">
            <strong>{CLUSTER_ICONS[cluster_id]} {learner['cluster_name']}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )
    
st.divider()

segment_avg = cluster_profiles[cluster_profiles['cluster'] == cluster_id].iloc[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    delta = learner['total_enrollments'] - segment_avg['total_enrollments']
    st.metric("Total Enrollments", int(learner['total_enrollments']), 
              delta=f"{delta:+.1f} vs segment avg")

with col2:
    delta = learner['num_categories'] - segment_avg['num_categories']
    st.metric("Categories Explored", int(learner['num_categories']), 
              delta=f"{delta:+.1f} vs segment avg")

with col3:
    delta = learner['avg_spend'] - segment_avg['avg_spend']
    st.metric("Avg Spend", f"₹{learner['avg_spend']:.2f}", 
              delta=f"{delta:+.2f} vs segment avg")

with col4:
    delta = learner['recency_days'] - segment_avg['recency_days']
    st.metric("Last Active", f"{int(learner['recency_days'])}d ago", 
              delta=f"{delta:+.1f}d vs segment avg", delta_color="inverse")
    

st.divider()
st.subheader("Learning Preferences")

level_shares = {
    'Beginner': learner['beginner_share'],
    'Intermediate': learner['intermediate_share'],
    'Advanced': learner['advanced_share']
}
sorted_levels = sorted({k: v for k, v in level_shares.items() if v > 0}.items(), key=lambda x: -x[1])

cat_cols = [c for c in learner_features.columns if c.startswith('cat_share_')]
cat_values = learner[cat_cols]
cat_values = cat_values[cat_values > 0].sort_values(ascending=False).head(6)
cat_labels = [c.replace('cat_share_', '').replace('_', ' ') for c in cat_values.index]

def bar_html(label, share, color):
    html = f"""
    <div style="margin-bottom: 10px;">
        <div style="display:flex; justify-content:space-between; font-size:14px; margin-bottom:3px; max-width:380px;">
            <span>{label}</span><span>{share:.0%}</span>
        </div>
        <div style="background-color:#D9CBB0; border-radius:4px; height:8px; width:100%; max-width:380px;">
            <div style="background-color:{color}; width:{share*100}%; height:100%; border-radius:4px;"></div>
        </div>
    </div>
    """
    return textwrap.dedent(html)

level_bars = "".join(bar_html(l, s, CLUSTER_COLORS[cluster_id]) for l, s in sorted_levels)
cat_bars = "".join(bar_html(l, s, CLUSTER_COLORS[cluster_id]) for l, s in zip(cat_labels, cat_values.values))

final_html = textwrap.dedent(f"""
<div style="display:flex; gap:40px;">
<div style="flex:1;">
<strong>Level Distribution</strong><br><br>
{level_bars}
<div style="color:#7A2E2E; font-size:14px; margin-top:8px;">Preferred level: <strong>{learner['preferred_level']}</strong></div>
</div>
<div style="flex:1;">
<strong>Top Categories</strong><br><br>
{cat_bars}
<div style="color:#7A2E2E; font-size:14px; margin-top:8px;">Preferred category: <strong>{learner['preferred_category']}</strong></div>
</div>
</div>
""")

st.markdown(final_html, unsafe_allow_html=True)
    
    
st.divider()
st.subheader("Enrollment History")

user_history = enrollment_history[enrollment_history['UserID'] == selected_user_id].copy()
user_history_display = user_history[['CourseName', 'CourseCategory','CourseLevel','CourseRating', 'TransactionDate', 'Amount']].rename(
    columns={
        'CourseName': 'Course',
        'CourseCategory': 'Category',
        'CourseLevel': 'Level',
        'CourseRating': 'Rating',
        'TransactionDate': 'Enrolled On',
        'Amount': 'Amount Paid'
    }
)

user_history_display['Enrolled On'] = user_history_display['Enrolled On'].dt.strftime('%b %d, %Y')
user_history_display['Amount Paid'] = user_history_display['Amount Paid'].apply(lambda x: f"₹{x:.2f}")

st.dataframe(user_history_display, hide_index=True, use_container_width=True)



st.divider()
st.subheader("Recommended Next Courses")

if st.button("🎯 View detailed recommendations & analysis", key="goto_recs_btn", type="primary"):
    st.session_state['handoff_user_id'] = selected_user_id
    st.switch_page("pages/4_Recommendations.py")

col_level_filter, col_cat_filter = st.columns(2)

with col_level_filter:
    level_filter = st.multiselect("Filter by level", options=['Beginner', 'Intermediate', 'Advanced'])

with col_cat_filter:
    all_categories = sorted(courses['CourseCategory'].unique())
    category_filter = st.multiselect("Filter by category", options=all_categories)

already_taken = set(user_history['CourseID'])

recs = get_top_n_recommendations(
    selected_user_id, learner_features, courses, cluster_popularity,
    already_taken, n=5,
    level_filter=level_filter if level_filter else None,
    category_filter=category_filter if category_filter else None
)

if recs.empty:
    catalog_has_match = check_filter_exists_in_catalog(courses, 
                            level_filter=level_filter if level_filter else None,
                            category_filter=category_filter if category_filter else None)
    
    if not catalog_has_match:
        st.warning("No courses exist in the catalog for this combination of filters.")
    else:
        st.info("No strong matches found for this learner with the selected filters. Try broadening your selection.")
else:
    for _, course in recs.iterrows():
        with st.container():
            col_name, col_meta, col_score = st.columns([3, 2, 1])
            with col_name:
                st.markdown(f"**{course['CourseName']}**")
                
            with col_meta:
                if course['CourseType'] == 'Free':
                    price_label = "Free"
                else:
                    price_label = f"₹{course['CoursePrice']:.2f}"
                    
                st.caption(f"{course['CourseCategory']} · {course['CourseLevel']} · ⭐ {course['CourseRating']:.1f} · {price_label}")
                
            with col_score:
                st.caption(f"Match: {course['final_score']:.0%}")
            st.divider()
            
