import streamlit as st
import pandas as pd
import requests
from io import StringIO
import unicodedata

class PLTeamQuiz:
    def __init__(self):
        st.set_page_config(
            page_title="Premier League Squad Connections Quiz",
            page_icon="⚽",
            layout="wide"
        )
        self.load_data()
        self.initialize_session_state()
        self.create_ui()

    def apply_custom_style(self):
        """Apply custom font and background gradient."""
        st.markdown("""
            <style>
                html, body, [class*="css"] {
                    font-family: Rockwell, 'Serifa', Georgia, serif;
                    background: linear-gradient(135deg, #b0c4de, #ccd9e8);
                    color: #000000;
                }

                .stButton>button, .stSelectbox, .stTextInput, .stMetric, .stMarkdown, .stProgress, .stError, .stSuccess, .stInfo {
                    font-family: Rockwell, 'Serifa', Georgia, serif;
                }

                input, .stSelectbox, textarea {
                    background-color: rgba(255, 255, 255, 0.85);
                }
            </style>
        """, unsafe_allow_html=True)

    def load_data(self):
        """Load player data from CSV."""
        try:
            url = "https://raw.githubusercontent.com/JulianB22/Football/main/data/premier_league_players.csv"
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
        self.apply_custom_style()

        # 🦁 Premier League logo at the top
        st.image("https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg", width=100)

        st.title("⚽ Squad Connections Quiz")
        st.markdown("""
        ### How to Play:
        1. Select two different Premier League teams  
        2. Try to guess players who have played for both teams  
        3. Get points for correct guesses!
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

        team1_players = self.find_players_for_team(team1_normalized)
        team2_players = self.find_players_for_team(team2_normalized)

        st.session_state.common_players = sorted(list(team1_players & team2_players))
        st.session_state.guesses = []
        st.session_state.show_answers = False
        st.session_state.correct_count = 0

        st.info(f"🎯 Find players who have played for both {team1} and {team2}")
        st.info(f"🔍 Number of players to find: {len(st.session_state.common_players)}")

    def show_quiz_interface(self):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            guess = st.text_input("Enter a player name:", key="guess_input")

        with col2:
            if st.button("Submit Guess", type="primary"):
                if guess:
                    guess_normalized = self.normalize_string(guess.strip().lower())
                    if guess_normalized not in [self.normalize_string(g.lower()) for g in st.session_state.guesses]:
                        st.session_state.guesses.append(guess)
                        if guess_normalized in [self.normalize_string(p.lower()) for p in st.session_state.common_players]:
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
        correct_guesses = set([self.normalize_string(g.lower()) for g in st.session_state.guesses]) & set([self.normalize_string(p.lower()) for p in st.session_state.common_players])
        incorrect_guesses = set([self.normalize_string(g.lower()) for g in st.session_state.guesses]) - set([self.normalize_string(p.lower()) for p in st.session_state.common_players])
        remaining = set([self.normalize_string(p.lower()) for p in st.session_state.common_players]) - correct_guesses

        progress = len(correct_guesses) / len(st.session_state.common_players)
        st.progress(progress)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Correct", len(correct_guesses))
        with col2:
            st.metric("❌ Incorrect", len(incorrect_guesses))
        with col3:
            st.metric("🎯 Remaining", len(remaining))

        st.write("### Your Guesses")
        for guess in st.session_state.guesses:
            guess_normalized = self.normalize_string(guess.lower())
            if guess_normalized in correct_guesses:
                st.success(f"✅ {guess}")
            else:
                st.error(f"❌ {guess}")

if __name__ == "__main__":
    quiz = PLTeamQuiz()

