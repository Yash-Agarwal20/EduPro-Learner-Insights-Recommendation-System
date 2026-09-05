import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_learner_features, load_courses, load_cluster_popularity, load_enrollment_history
)
from utils.scoring import get_top_n_recommendations, check_filter_exists_in_catalog
from utils.theme import CLUSTER_COLORS, CLUSTER_ICONS
from utils.theme import apply_custom_css
apply_custom_css()

st.set_page_config(page_title="Recommendations | EduPro", page_icon="🎯", layout="wide")

learner_features = load_learner_features()
courses = load_courses()
cluster_popularity = load_cluster_popularity()
enrollment_history = load_enrollment_history()

st.title("🎯 Recommendations")
st.markdown("Deep-dive into personalized course recommendations — adjust scoring weights and see the full breakdown.")
st.divider()

all_user_ids = learner_features.index.tolist()

# One-time handoff: if we arrived via the button, seed our own state from it, then clear it
if 'handoff_user_id' in st.session_state:
    st.session_state['rec_selected_user_id'] = st.session_state['handoff_user_id']
    del st.session_state['handoff_user_id']

if 'rec_selected_user_id' not in st.session_state:
    st.session_state['rec_selected_user_id'] = all_user_ids[0]

col_select, col_random = st.columns([4, 1])

with col_random:
    st.write("")
    st.write("")
    if st.button("🎲 Random Learner", key="rec_random_btn"):
        st.session_state['rec_selected_user_id'] = pd.Series(all_user_ids).sample(1).iloc[0]

with col_select:
    st.selectbox("Select a learner", options=all_user_ids, key='rec_selected_user_id')

selected_user_id = st.session_state['rec_selected_user_id']

st.divider()
st.subheader("Scoring Weights")
st.caption("Adjust how much each factor contributes to the recommendation score. Defaults reflect our empirically-tuned weights (Precision@5 evaluation).")

col_w1, col_w2, col_w3 = st.columns(3)

with col_w1:
    w_pop = st.slider("Popularity in Cluster", 0.0, 1.0, 0.5, 0.05)
with col_w2:
    w_rating = st.slider("Course Rating", 0.0, 1.0, 0.15, 0.05)
with col_w3:
    w_content = st.slider("Content Match", 0.0, 1.0, 0.35, 0.05)

weight_sum = w_pop + w_rating + w_content
if abs(weight_sum - 1.0) > 0.01:
    st.warning(f"Weights sum to {weight_sum:.2f}, not 1.0 — scores will still rank correctly, but the 'Match %' display assumes weights sum to 1.")
    
col_level_filter, col_cat_filter = st.columns(2)

with col_level_filter:
    level_filter = st.multiselect("Filter by level", options=['Beginner', 'Intermediate', 'Advanced'], key='rec_level_filter')

with col_cat_filter:
    all_categories = sorted(courses['CourseCategory'].unique())
    category_filter = st.multiselect("Filter by category", options=all_categories, key='rec_category_filter')
    

st.divider()
st.subheader("Recommended Courses — Full Breakdown")

user_history = enrollment_history[enrollment_history['UserID'] == selected_user_id]
already_taken = set(user_history['CourseID'])

recs = get_top_n_recommendations(
    selected_user_id, learner_features, courses, cluster_popularity,
    already_taken, n=10,
    w_pop=w_pop, w_rating=w_rating, w_content=w_content,
    level_filter=level_filter if level_filter else None,
    category_filter=category_filter if category_filter else None
)

if recs.empty:
    catalog_has_match = check_filter_exists_in_catalog(
        courses,
        level_filter=level_filter if level_filter else None,
        category_filter=category_filter if category_filter else None
    )
    if not catalog_has_match:
        st.warning("No courses exist in the catalog for this combination of filters.")
    else:
        st.info("No strong matches found for this learner with the selected filters. Try broadening your selection.")
else:
    display_df = recs[['CourseName', 'CourseCategory', 'CourseLevel', 'CourseType', 'CoursePrice', 'CourseRating', 'popularity_score', 'rating_score', 'content_score', 'final_score']].copy()
    
    display_df['Price'] = display_df.apply(
        lambda r: "Free" if r['CourseType'] == 'Free' else f"₹{r['CoursePrice']:.2f}", axis=1
    )
    
    display_df = display_df.rename(columns={
        'CourseName': 'Course', 'CourseCategory': 'Category', 'CourseLevel': 'Level',
        'CourseRating': 'Rating', 'popularity_score': 'Popularity', 
        'rating_score': 'Rating Score', 'content_score': 'Content Match', 'final_score': 'Total Score'
    })
    
    display_df = display_df[['Course', 'Category', 'Level', 'Price', 'Rating',
                               'Popularity', 'Rating Score', 'Content Match', 'Total Score']]
    
    st.dataframe(
        display_df.style.format({
            'Rating': '{:.2f}', 'Popularity': '{:.3f}', 'Rating Score': '{:.3f}',
            'Content Match': '{:.3f}', 'Total Score': '{:.3f}'
        }).background_gradient(subset=['Total Score'], cmap='YlOrBr'),
        hide_index=True,
        use_container_width=True
    )