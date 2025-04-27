import streamlit as st
import pandas as pd
import requests
from io import StringIO
import unicodedata

class EuropeanLeaguesQuiz:
    def __init__(self):
        st.set_page_config(
            page_title="European Leagues Squad Connections Quiz",
            page_icon="https://upload.wikimedia.org/wikipedia/commons/3/33/European_Leagues_logo.svg",  # Example image URL
            layout="wide"
        )
        self.load_data()
        self.initialize_session_state()
        self.create_ui()

    def load_data(self):
        """Load player data from GitHub raw URL."""
        try:
            # Replace this URL with the raw URL of your CSV file in GitHub
            url = "https://raw.githubusercontent.com/username/repository-name/main/european_leagues_players.csv"
            self.df = pd.read_csv(url)

            # Convert columns to strings before using .str accessor
            self.df['Squad'] = self.df['Squad'].astype(str).str.lower()  # Ensure Squad column is a string
            self.df['Player'] = self.df['Player'].astype(str).str.lower()  # Ensure Player column is a string
            self.df['Born'] = self.df['Born'].astype(str).str.lower()  # Ensure Born column is a string
            
            self.all_teams = sorted(self.df['Squad'].unique())
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.stop()

    def initialize_session_state(self):
        """Initialize session state variables."""
        if 'common_players' not in st.session_state:
            st.session_state.common_players = []
        if 'guesses' not in st.session_state:
            st.session_state.guesses = []
        if 'show_answers' not in st.session_state:
            st.session_state.show_answers = False
        if 'correct_count' not in st.session_state:
            st.session_state.correct_count = 0

    def find_players_for_team(self, team):
        """Find all players who have played for a team."""
        # Convert team name to lowercase for case-insensitive comparison
        team = team.lower()
        return set(self.df[self.df['Squad'] == team]['Player'].unique())

    def normalize_string(self, text):
        """Normalize a string by removing accents."""
        # Normalize the string and remove accents (NFD: Normalization Form Decomposed)
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    def create_ui(self):
        """Create the Streamlit user interface."""
        # Display the European Leagues logo above the title
        st.markdown("""
            <div style="text-align: center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/3/33/European_Leagues_logo.svg" width="200">
            </div>
            <h1 style="text-align: center;">European Leagues Squad Connections Quiz</h1>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### How to Play:
        1. Select two different European leagues
        2. Guess players who have played for both leagues
        3. Get points for correct guesses!
        """)

        col1, col2 = st.columns(2)

        with col1:
            # Display teams with the first letter of each word capitalized
            team1 = st.selectbox("Select First League Team:", [team.title() for team in self.all_teams], key='team1')

        with col2:
            # Display teams with the first letter of each word capitalized
            team2 = st.selectbox("Select Second League Team:", [team.title() for team in self.all_teams], key='team2')

        if st.button("Find Connections", type="primary"):
            if team1 == team2:
                st.error("Please select different teams")
            else:
                self.find_connections(team1, team2)

        if st.session_state.common_players:
            self.show_quiz_interface()

    def find_connections(self, team1, team2):
        """Find players who played for both teams."""
        # Normalize team names to handle case-insensitive and accent-insensitive comparison
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
        """Show the quiz interface with guessing and scoring."""
        # Create three columns
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            guess = st.text_input("Enter a player name:", key="guess_input")

        with col2:
            if st.button("Submit Guess", type="primary"):
                if guess:
                    # Normalize guess to lowercase and remove accents
                    guess_normalized = self.normalize_string(guess.strip().lower())
                    if guess_normalized not in [self.normalize_string(g.lower()) for g in st.session_state.guesses]:  # Compare case-insensitively
                        st.session_state.guesses.append(guess)
                        if guess_normalized in [self.normalize_string(p.lower()) for p in st.session_state.common_players]:  # Compare case-insensitively
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
        """Show the results of the user's guesses."""
        correct_guesses = set([self.normalize_string(g.lower()) for g in st.session_state.guesses]) & set([self.normalize_string(p.lower()) for p in st.session_state.common_players])
        incorrect_guesses = set([self.normalize_string(g.lower()) for g in st.session_state.guesses]) - set([self.normalize_string(p.lower()) for p in st.session_state.common_players])
        remaining = set([self.normalize_string(p.lower()) for p in st.session_state.common_players]) - correct_guesses

        # Create a progress bar
        progress = len(correct_guesses) / len(st.session_state.common_players)
        st.progress(progress)

        # Show stats in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Correct", len(correct_guesses))
        with col2:
            st.metric("❌ Incorrect", len(incorrect_guesses))
        with col3:
            st.metric("🎯 Remaining", len(remaining))

        # Show guesses with emojis
        st.write("### Your Guesses")
        for guess in st.session_state.guesses:
            guess_normalized = self.normalize_string(guess.lower())
            if guess_normalized in correct_guesses:
                st.success(f"✅ {guess}")
            else:
                st.error(f"❌ {guess}")

if __name__ == "__main__":
    quiz = EuropeanLeaguesQuiz()

