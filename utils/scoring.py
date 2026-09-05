def score_courses_for_learner(user_id, learner_features, courses_df, cluster_popularity, already_taken, w_pop=0.5, w_rating=0.15, w_content=0.35):
    learner = learner_features.loc[user_id]
    cluster = learner['cluster']

    candidates = courses_df[~courses_df['CourseID'].isin(already_taken)].copy()

    candidates['popularity_score'] = candidates['CourseID'].map(
        cluster_popularity.get(cluster, {})).fillna(0)

    candidates['rating_score'] = (candidates['CourseRating'] - 1) / 4

    def content_score(row):
        cat_col = 'cat_share_' + row['CourseCategory'].replace(' ', '_')
        level_col = row['CourseLevel'].lower() + '_share'
        return (learner.get(cat_col, 0) + learner.get(level_col, 0)) / 2

    candidates['content_score'] = candidates.apply(content_score, axis=1)

    candidates['final_score'] = (w_pop * candidates['popularity_score'] +
                                   w_rating * candidates['rating_score'] +
                                   w_content * candidates['content_score'])

    return candidates.sort_values('final_score', ascending=False)


def get_top_n_recommendations(user_id, learner_features, courses_df, cluster_popularity, already_taken, n=5, w_pop=0.5, w_rating=0.15, w_content=0.35, level_filter=None, category_filter=None):

    recs = score_courses_for_learner(user_id, learner_features, courses_df, cluster_popularity, already_taken, w_pop=w_pop, w_rating=w_rating, w_content=w_content)

    if level_filter:
        recs = recs[recs['CourseLevel'].isin(level_filter)]
    if category_filter:
        recs = recs[recs['CourseCategory'].isin(category_filter)]

    return recs.head(n)


def check_filter_exists_in_catalog(courses_df, level_filter=None, category_filter=None):
    subset = courses_df.copy()
    if level_filter:
        subset = subset[subset['CourseLevel'].isin(level_filter)]
    if category_filter:
        subset = subset[subset['CourseCategory'].isin(category_filter)]
    return len(subset) > 0