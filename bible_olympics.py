import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="📖 Bible Olympics", layout="centered")
st.title("📖 Bible Olympics: Score Tracker & Team Manager")

# --- Constants ---
EVENTS = ["Bible Trivia", "Bible Memorization", "Bible Relay", "Sword Drill"]
PLACEMENT_POINTS = {"1st": 10, "2nd": 7, "3rd": 5, "Participation": 2}
EXTRA_POINTS = {"✨ Memory Bonus": 3, "💥 Teamwork": 2, "🧠 Creativity": 1}

# --- Data Store ---
if "teams" not in st.session_state:
    st.session_state.teams = {}

# --- Helper to calculate total score ---
def calculate_total(team):
    return sum(team["score"].values()) + team.get("bonus", 0)

# --- Team Registration ---
st.header("📝 Register a Team")
with st.form("register_team"):
    team_name = st.text_input("Team Name")
    members = st.text_area("Team Members (one per line)")
    submitted = st.form_submit_button("Add Team")

    if submitted:
        if team_name in st.session_state.teams:
            st.warning("Team already exists!")
        elif team_name.strip() and members.strip():
            st.session_state.teams[team_name] = {
                "members": members.splitlines(),
                "score": {event: 0 for event in EVENTS},
                "bonus": 0
            }
            st.success(f"Team '{team_name}' registered!")
        else:
            st.error("Please provide both team name and members.")

# --- Scoring Section ---
st.header("🏆 Event Scoring")
if st.session_state.teams:
    selected_event = st.selectbox("Select Event", EVENTS)
    placement_teams = {}

    cols = st.columns(len(PLACEMENT_POINTS))
    for i, (place, pts) in enumerate(PLACEMENT_POINTS.items()):
        with cols[i]:
            placement_teams[place] = st.selectbox(f"{place} ({pts} pts)", ["None"] + list(st.session_state.teams.keys()), key=f"{selected_event}_{place}")

    if st.button("Assign Scores"):
        for place, team_name in placement_teams.items():
            if team_name and team_name != "None":
                st.session_state.teams[team_name]["score"][selected_event] = PLACEMENT_POINTS[place]
        st.success("Scores updated!")
else:
    st.info("Register teams first to enable scoring.")

# --- Bonus Points ---
st.header("✨ Bonus Points")
if st.session_state.teams:
    col1, col2 = st.columns(2)
    with col1:
        bonus_team = st.selectbox("Choose Team", list(st.session_state.teams.keys()), key="bonus_team")
    with col2:
        bonus_type = st.selectbox("Bonus Type", list(EXTRA_POINTS.keys()), key="bonus_type")

    if st.button("Add Bonus"):
        st.session_state.teams[bonus_team]["bonus"] += EXTRA_POINTS[bonus_type]
        st.success(f"Added {EXTRA_POINTS[bonus_type]} bonus points to {bonus_team}")

# --- Leaderboard ---
st.header("📊 Leaderboard")
if st.session_state.teams:
    leaderboard = []
    for team, data in st.session_state.teams.items():
        total = calculate_total(data)
        leaderboard.append({
            "Team": team,
            "Total Score": total,
            **data["score"],
            "Bonus": data.get("bonus", 0)
        })
    df = pd.DataFrame(leaderboard).sort_values(by="Total Score", ascending=False)
    st.dataframe(df, use_container_width=True)
