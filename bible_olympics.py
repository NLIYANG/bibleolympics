import streamlit as st
import pandas as pd

st.title("📖 Bible Olympics: Team Tracker")

# Session state to store team data
if "teams" not in st.session_state:
    st.session_state.teams = {}

# --- Team Registration ---
st.header("📝 Register a Team")

team_name = st.text_input("Team Name")
members = st.text_area("List of Members (one per line)")

if st.button("Add Team"):
    if team_name and team_name not in st.session_state.teams:
        st.session_state.teams[team_name] = {
            "members": members.splitlines(),
            "score": 0
        }
        st.success(f"Team '{team_name}' added!")
    elif team_name in st.session_state.teams:
        st.warning("Team already exists.")
    else:
        st.error("Please enter a team name.")

# --- Score Updater ---
st.header("🏆 Update Team Scores")

if st.session_state.teams:
    selected_team = st.selectbox("Choose a team", list(st.session_state.teams.keys()))
    score_to_add = st.number_input("Points to add", min_value=0, step=1)

    if st.button("Update Score"):
        st.session_state.teams[selected_team]["score"] += score_to_add
        st.success(f"Added {score_to_add} points to {selected_team}!")
else:
    st.info("No teams registered yet.")

# --- Leaderboard ---
st.header("📊 Leaderboard")

if st.session_state.teams:
    leaderboard_df = pd.DataFrame([
        {"Team": team, "Score": data["score"]}
        for team, data in st.session_state.teams.items()
    ])
    st.dataframe(leaderboard_df.sort_values(by="Score", ascending=False), use_container_width=True)

