import streamlit as st
import pandas as pd
import requests
from io import StringIO
import unicodedata

class EuroQuiz:
    def __init__(self):
        st.set_page_config(
            page_title="Squad Connections Quiz",
            page_icon="https://upload.wikimedia.org/wikipedia/commons/a/a2/Premier_League_logo_2016.svg",
            layout="wide"
        )
        self.load_data()
        self.initialize_session_state()
        self.create_ui()

    def load_data(self):
        try:
            url = "https://raw.githubusercontent.com/JulianB22/Football/main/data/european_leagues_players.csv"
            response = requests.get(url)
            response.raise_for_status()
            csv_string = StringIO(response.text)
            self.df = pd.read_csv(csv_string)
            self.df['Squad'] = self.df['Squad'].str.lower()
            self.all_teams = sorted(self.df['Squad'].unique())
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.stop()

    def initialize_session_state(self):
        if 'common_players' not in st.session_state:
            st.session_state.common_players = []
        if 'guesses' not in st.session_state:
            st.session_state.guesses = []
        if 'show_answers' not in st.session_state:
            st.session_state.show_answers = False
        if 'correct_count' not in st.session_state:
            st.session_state.correct_count = 0

    def find_players_for_team(self, team):
        team = team.lower()
        return set(self.df[self.df['Squad'] == team]['Player'].unique())

    def normalize_string(self, text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    def create_ui(self):
        # Display league logos using st.image
        st.image("https://upload.wikimedia.org/wikipedia/commons/a/a2/Premier_League_logo_2016.svg", width=90)
        st.image("https://upload.wikimedia.org/wikipedia/commons/4/47/La_Liga_logo_2023.svg", width=90)
        st.image("https://upload.wikimedia.org/wikipedia/commons/0/0e/Serie_A_logo_2019.svg", width=90)
        st.image("https://upload.wikimedia.org/wikipedia/commons/1/1b/Bundesliga_Logo_2010.svg", width=90)
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/7f/Ligue_1_logo_2018.svg", width=90)

        st.markdown("<h1 style='text-align: center;'>Squad Connections Quiz</h1>", unsafe_allow_html=True)

        st.markdown("""
        ### How to Play:
        1. Select two different teams
        2. Guess players who have played for both teams
        3. Earn points for correct answers!
        """)

        col1, col2 = st.columns(2)
        with col1:
            team1 = st.selectbox("Select First Team:", [team.title() for team in self.all_teams], key='team1')
        with col2:
            team2 = st.selectbox("Select Second Team:", [team.title() for team in self.all_teams], key='team2')

        if st.button("Find Connections", type="primary"):
            if team1 == team2:
                st.error("Please select different teams")
            else:
                self.find_connections(team1, team2)

        if st.session_state.common_players:
            self.show_quiz_interface()

    def find_connections(self, team1, team2):
        team1_normalized = self.normalize_string(team1.lower())
        team2_normalized = self.normalize_string(team2.lower())

        players1 = self.find_players_for_team(team1_normalized)
        players2 = self.find_players_for_team(team2_normalized)

        st.session_state.common_players = sorted(list(players1 & players2))
        st.session_state.guesses = []
        st.session_state.show_answers = False
        st.session_state.correct_count = 0

        st.info(f"🎯 Find players who played for both **{team1}** and **{team2}**")
        st.info(f"🔍 Total players: {len(st.session_state.common_players)}")

    def show_quiz_interface(self):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            guess = st.text_input("Enter a player name:", key="guess_input")

        with col2:
            if st.button("Submit Guess", type="primary"):
                if guess:
                    guess_normalized = self.normalize_string(guess.strip().lower())
                    already_guessed = [self.normalize_string(g.lower()) for g in st.session_state.guesses]
                    valid_players = [self.normalize_string(p.lower()) for p in st.session_state.common_players]
                    if guess_normalized not in already_guessed:
                        st.session_state.guesses.append(guess)
                        if guess_normalized in valid_players:
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
        normalized_guesses = {self.normalize_string(g.lower()) for g in st.session_state.guesses}
        correct = {self.normalize_string(p.lower()) for p in st.session_state.common_players}
        correct_guesses = normalized_guesses & correct
        incorrect_guesses = normalized_guesses - correct
        remaining = correct - correct_guesses

        st.progress(len(correct_guesses) / max(len(correct), 1))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Correct", len(correct_guesses))
        with col2:
            st.metric("❌ Incorrect", len(incorrect_guesses))
        with col3:
            st.metric("🎯 Remaining", len(remaining))

        st.write("### Your Guesses")
        for g in st.session_state.guesses:
            if self.normalize_string(g.lower()) in correct_guesses:
                st.success(f"✅ {g}")
            else:
                st.error(f"❌ {g}")

if __name__ == "__main__":
    EuroQuiz()
