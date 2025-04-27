import streamlit as st
import pandas as pd
import requests
from io import StringIO
import unicodedata
from rapidfuzz import fuzz  # <-- New import for fuzzy matching

class EuroQuiz:
    def __init__(self):
        st.set_page_config(
            page_title="Squad Connections Quiz",
            page_icon="⚽️",
            layout="wide"
        )
        self.load_data()
        self.initialize_session_state()
        self.create_ui()

    def load_data(self):
        try:
            url = "https://raw.githubusercontent.com/JulianB22/Football/main/data/final_all_european_players.csv"
            response = requests.get(url)
            response.raise_for_status()

            csv_string = StringIO(response.text)
            self.df = pd.read_csv(csv_string)

            self.df['Squad'] = self.df['Squad'].astype(str).str.strip()
            self.df['Squad_normalized'] = self.df['Squad'].str.casefold()

            # Extract birth year
            self.df['YearBorn'] = pd.to_datetime(self.df['Born'], errors='coerce').dt.year

            self.team_map = dict(zip(self.df['Squad_normalized'], self.df['Squad']))
            self.all_teams = sorted(self.team_map.keys())

        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.stop()

    def initialize_session_state(self):
        if 'common_players' not in st.session_state:
            st.session_state.common_players = []
        if 'common_raw' not in st.session_state:
            st.session_state.common_raw = set()
        if 'guesses' not in st.session_state:
            st.session_state.guesses = []
        if 'show_answers' not in st.session_state:
            st.session_state.show_answers = False
        if 'correct_count' not in st.session_state:
            st.session_state.correct_count = 0

    def find_players_for_team(self, team_normalized):
        team_df = self.df[self.df['Squad_normalized'] == team_normalized]
        return set(zip(team_df['Player'], team_df['YearBorn']))

    def normalize_string(self, text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    def create_ui(self):
        st.markdown("""
            <div style="text-align: center;">
                <img src="https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg" width="160" style="margin: 10px;">
                <img src="https://i.imgur.com/KXe5dTP.png" width="100" style="margin: 10px;">
                <img src="https://i.imgur.com/L7sTT0i.png" width="100" style="margin: 10px;">
                <img src="https://i.imgur.com/Ca9NLSb.png" width="75" style="margin: 10px;"> 
                <img src="https://i.imgur.com/BYKNuEO.png" width="85" style="margin: 10px;"> 
            </div>
            <h1 style="text-align: center;">⚽️ Squad Connections Quiz</h1>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### How to Play:
        1. Select two different teams from the big 5 European leagues  
        2. Guess players who have played for both teams over the last 30 years  
        3. Get points for correct guesses!
        """)

        col1, col2 = st.columns(2)

        with col1:
            team1_display = st.selectbox("Select First Team:", [self.team_map[t] for t in self.all_teams], key='team1')
        with col2:
            team2_display = st.selectbox("Select Second Team:", [self.team_map[t] for t in self.all_teams], key='team2')

        team1_normalized = self.get_normalized_team_name(team1_display)
        team2_normalized = self.get_normalized_team_name(team2_display)

        if st.button("Find Connections", type="primary"):
            if team1_normalized == team2_normalized:
                st.error("Please select different teams")
            else:
                self.find_connections(team1_normalized, team2_normalized)

        if st.session_state.common_players:
            self.show_quiz_interface()

    def get_normalized_team_name(self, team_display_name):
        for norm, disp in self.team_map.items():
            if disp == team_display_name:
                return norm
        return team_display_name



