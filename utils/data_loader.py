import streamlit as st
import pandas as pd
import json

@st.cache_data
def load_learner_features(path='data/learner_features.csv'):
    df = pd.read_csv(path)
    df = df.set_index('UserID')
    return df

@st.cache_data
def load_cluster_profiles(path='data/cluster_profiles.csv'):
    df = pd.read_csv(path)
    return df

@st.cache_data
def load_cluster_popularity(path='data/cluster_popularity.json'):
    with open(path) as f:
        raw = json.load(f)
    # convert cluster keys back to int, keep course keys as strings (matches CourseID dtype)
    cluster_popularity = {int(cluster_id): scores for cluster_id, scores in raw.items()}
    return cluster_popularity

@st.cache_data
def load_courses(path='data/courses.csv'):
    df = pd.read_csv(path)
    return df

@st.cache_data
def load_enrollment_history(path='data/enrollment_history.csv'):
    df = pd.read_csv(path, parse_dates=['TransactionDate'])
    return df