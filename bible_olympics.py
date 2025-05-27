import streamlit as st
import pandas as pd
import os
from PIL import Image
import copy

st.set_page_config(page_title="📖 Bible Olympics", layout="centered")

# --- Load logo ---
logo = Image.open(r"C:\Users\0236106\Downloads\YG LOGOS (2).png")  # Update this path if needed
st.image(logo, width=150)

st.title("📖 Bible Olympics: Score Tracker & Team Manager")

# --- Constants ---
EVENTS = ["Bible Trivia", "Bible Memorization", "Bible Relay", "Sword Drill"]
PLACEMENT_POINTS = {"1st": 10, "2nd": 7, "3rd": 5, "Participation": 2}
EXTRA_POINTS = {
    "Best ✨ Team Spirit": 3,
    "Fastest 🏃 Bible Finder(s)": 2,
    "Most 🧠 Knowledgeable": 2,
    "Best 💥 Team Name": 1
}

# --- Data Store ---
if "undo_stack" not in st.session_state:
    st.session_state.undo_stack = []

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
            placement_teams[place] = st.selectbox(
                f"{place} ({pts} pts)",
                ["None"] + list(st.session_state.teams.keys()),
                key=f"{selected_event}_{place}"
            )

    if st.button("Assign Scores"):
        # Save current state for undo
        st.session_state.undo_stack.append(copy.deepcopy(st.session_state.teams))

        placed_teams = set()
        for place, team_name in placement_teams.items():
            if team_name and team_name != "None":
                st.session_state.teams[team_name]["score"][selected_event] = PLACEMENT_POINTS[place]
                placed_teams.add(team_name)

        # Assign participation points to others
        for team_name in st.session_state.teams:
            if team_name not in placed_teams:
                st.session_state.teams[team_name]["score"][selected_event] = PLACEMENT_POINTS["Participation"]

        st.success("Scores updated with placements and participation!")
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
        # Save current state for undo
        st.session_state.undo_stack.append(copy.deepcopy(st.session_state.teams))

        st.session_state.teams[bonus_team]["bonus"] += EXTRA_POINTS[bonus_type]
        st.success(f"Added {EXTRA_POINTS[bonus_type]} bonus points to {bonus_team}")

# --- Leaderboard ---
st.header("📊 Live Leaderboard")
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

    df = pd.DataFrame(leaderboard).sort_values(by="Total Score", ascending=False).reset_index(drop=True)

    # Add Rank and Emoji
    medals = ["🥇", "🥈", "🥉"]
    df.insert(0, "🏅 Rank", [medals[i] if i < 3 else f"{i+1}" for i in range(len(df))])

    # Render leaderboard as styled HTML
    def render_html_table(df):
        table_html = """
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
                font-family: 'Segoe UI', sans-serif;
            }
            th, td {
                padding: 8px;
                text-align: center;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f0f0f0;
                font-weight: bold;
            }
            tr:nth-child(even) {
                background-color: #fafafa;
            }
            td.highlight {
                background-color: #d1e7dd;
                font-weight: bold;
                color: #155724;
            }
        </style>
        <table>
            <thead><tr>""" + ''.join([f"<th>{col}</th>" for col in df.columns]) + "</tr></thead><tbody>"

        for _, row in df.iterrows():
            table_html += "<tr>"
            for col in df.columns:
                value = row[col]
                if col == "Total Score":
                    table_html += f'<td class="highlight">{value}</td>'
                else:
                    table_html += f'<td>{value}</td>'
            table_html += "</tr>"

        table_html += "</tbody></table>"
        return table_html

    # Undo Button
    if st.button("↩️ Undo Last Change") and st.session_state.undo_stack:
        st.session_state.teams = st.session_state.undo_stack.pop()
        st.success("Undo successful!")

    st.markdown(render_html_table(df), unsafe_allow_html=True)
