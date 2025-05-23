import streamlit as st
import pandas as pd
import requests
import random
from io import StringIO
import unicodedata
from rapidfuzz import fuzz

class EuroQuiz:
    def __init__(self):
        st.set_page_config(
            page_title="Players in Common Challenge",
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
            self.df['YearBorn'] = pd.to_numeric(self.df['Born'], errors='coerce', downcast='integer')

            self.leagues = sorted(self.df['League'].unique())
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
        if 'team1' not in st.session_state:
            st.session_state.team1 = "Arsenal"
        if 'team2' not in st.session_state:
            st.session_state.team2 = "Barcelona"
        if 'selected_league' not in st.session_state:
            st.session_state.selected_league = "All"
        if 'previous_team1' not in st.session_state:
            st.session_state.previous_team1 = ""
        if 'previous_team2' not in st.session_state:
            st.session_state.previous_team2 = ""

    def find_players_for_team(self, team_normalized):
        team_df = self.df[self.df['Squad_normalized'] == team_normalized]
        return set(zip(team_df['Player'], team_df['YearBorn']))

    def normalize_string(self, text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    def get_normalized_team_name(self, team_display_name):
        for norm, disp in self.team_map.items():
            if disp == team_display_name:
                return norm
        return team_display_name.casefold()

    def create_ui(self):
        st.markdown("""
            <div style="text-align: center;">
                <img src="https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg" width="160" style="margin: 10px;">
                <img src="https://i.imgur.com/KXe5dTP.png" width="100" style="margin: 10px;">
                <img src="https://i.imgur.com/L7sTT0i.png" width="100" style="margin: 10px;">
                <img src="https://i.imgur.com/Ca9NLSb.png" width="75" style="margin: 10px;"> 
                <img src="https://i.imgur.com/BYKNuEO.png" width="85" style="margin: 10px;"> 
            </div>
            <h1 style="text-align: center;">Players in Common Challenge</h1>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### How to Play:
        1. Select or randomise two different teams from the top 5 European leagues
        2. Guess players who have played for both teams over the last 30 years  
        3. Get points for correct guesses!
        """)

        random_team_list = [
            "Arsenal", "Chelsea", "Real Madrid", "Bayern Munich", "Atlético Madrid",
            "Dortmund", "Milan", "Inter", "Liverpool", "Manchester City", "Manchester Utd",
            "Roma", "Tottenham", "Valencia", "Paris S-G", "Marseille", "Juventus",
            "Aston Villa", "Newcastle Utd", "Lazio"
        ]

        all_available_teams = sorted(self.df['Squad'].unique())

        league_flags = {
            "All": "🌍", "Premier League": "🇬🇧", "La Liga": "🇪🇸",
            "Bundesliga": "🇩🇪", "Serie A": "🇮🇹", "Ligue 1": "🇫🇷"
        }

        leagues = ["All"] + list(self.leagues)
        league_options = [f"{league_flags.get(league, '')} {league}" for league in leagues]
        selected_league_with_flag = st.selectbox("Filter by League:", league_options, key="league_filter")
        selected_league = selected_league_with_flag.split(' ', 1)[1] if ' ' in selected_league_with_flag else selected_league_with_flag
        st.session_state.selected_league = selected_league

        if selected_league != "All":
            league_teams = self.df[self.df['League'] == selected_league]['Squad'].unique()
            selection_teams = sorted(league_teams)
        else:
            selection_teams = all_available_teams

        random_teams = selection_teams if selected_league != "All" else random_team_list

        if len(random_teams) < 2:
            st.error(f"Not enough teams in {selected_league} to randomize. Please select a different league.")
            return

        if st.button("🎲 Randomise Teams"):
            team1, team2 = random.sample(random_teams, 2)
            st.session_state.team1 = team1
            st.session_state.team2 = team2

        col1, col2 = st.columns(2)
        with col1:
            team1_display = st.selectbox("Select First Team:", selection_teams, key='team1')
        with col2:
            team2_display = st.selectbox("Select Second Team:", selection_teams, key='team2')

        team1_norm = self.get_normalized_team_name(team1_display)
        team2_norm = self.get_normalized_team_name(team2_display)

        # If team selection changed, reset session state
        if (team1_norm != st.session_state.previous_team1) or (team2_norm != st.session_state.previous_team2):
            st.session_state.guesses = []
            st.session_state.correct_count = 0
            st.session_state.show_answers = False
            st.session_state.common_players = []
            st.session_state.common_raw = set()
            st.session_state.previous_team1 = team1_norm
            st.session_state.previous_team2 = team2_norm

        if team1_norm != team2_norm:
            self.find_connections(team1_norm, team2_norm)

        if st.session_state.common_players:
            self.show_quiz_interface()

    def find_connections(self, team1_norm, team2_norm):
        team1_players = self.find_players_for_team(team1_norm)
        team2_players = self.find_players_for_team(team2_norm)

        common = set()
        for player1, year1 in team1_players:
            for player2, year2 in team2_players:
                if self.normalize_string(player1.lower()) == self.normalize_string(player2.lower()) and year1 == year2:
                    common.add((player1, year1))

        st.session_state.common_raw = common
        st.session_state.common_players = sorted([p for p, y in common if pd.notna(y)])

        team1_display = self.team_map.get(team1_norm, team1_norm.title())
        team2_display = self.team_map.get(team2_norm, team2_norm.title())
        st.info(f"🎯 Find {len(st.session_state.common_players)} players who have played for both {team1_display} and {team2_display}")

    def show_quiz_interface(self):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            with st.form(key="guess_form", clear_on_submit=True):
                guess = st.text_input("Enter a player name:", key="guess_input")
                submitted = st.form_submit_button("Submit Guess")

                if submitted and guess:
                    guess_normalized = self.normalize_string(guess.strip().lower())
                    already_guessed = [self.normalize_string(g.lower()) for g in st.session_state.guesses]

                    if guess_normalized not in already_guessed:
                        st.session_state.guesses.append(guess)
                        matched = False
                        for player, _ in st.session_state.common_raw:
                            player_norm = self.normalize_string(player.lower())
                            surname = self.normalize_string(player.split()[-1].lower())
                            if (fuzz.token_set_ratio(guess_normalized, player_norm) >= 90 or
                                fuzz.token_set_ratio(guess_normalized, surname) >= 90):
                                matched = True
                                break
                        if matched:
                            st.session_state.correct_count += 1

        with col3:
            if st.button("Show/Hide Answers", type="secondary"):
                st.session_state.show_answers = not st.session_state.show_answers

        if st.session_state.guesses:
            self.show_results()

        if st.session_state.show_answers:
            st.write("### 📝 All Players")
            for player in st.session_state.common_players:
                st.write(f"• {player}")

    def show_results(self):
        correct_names = {self.normalize_string(name.lower()) for name, _ in st.session_state.common_raw}
        guessed = {self.normalize_string(g.lower()): g for g in st.session_state.guesses}

        correct_guesses = []
        incorrect_guesses = []

        for guess_norm, original_guess in guessed.items():
            match_found = False
            for name in correct_names:
                if fuzz.token_set_ratio(guess_norm, name) >= 90:
                    match_found = True
                    break
            if match_found:
                correct_guesses.append(original_guess)
            else:
                incorrect_guesses.append(original_guess)

        st.progress(len(correct_guesses) / len(st.session_state.common_players))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Correct", len(correct_guesses))
        with col2:
            st.metric("❌ Incorrect", len(incorrect_guesses))
        with col3:
            st.metric("🎯 Remaining", len(st.session_state.common_players) - len(correct_guesses))

        st.write("### Your Guesses")
        for guess in st.session_state.guesses:
            if guess in correct_guesses:
                st.success(f"✅ {guess}")
            else:
                st.error(f"❌ {guess}")

if __name__ == "__main__":
    quiz = EuroQuiz()

