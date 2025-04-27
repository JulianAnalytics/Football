import streamlit as st
import pandas as pd
import requests
from io import StringIO
import unicodedata

class EuroQuiz:
    def __init__(self):
        st.set_page_config(
            page_title="Squad Connections Quiz",
            page_icon="⚽️",  # Soccer emoji as the page icon
            layout="wide"
        )
        self.load_data()
        self.initialize_session_state()
        self.create_ui()

    def load_data(self):
        """Load player data from CSV."""
        try:
            url = "https://raw.githubusercontent.com/JulianB22/Football/main/data/final_all_european_players.csv"
            response = requests.get(url)
            response.raise_for_status()

            csv_string = StringIO(response.text)
            self.df = pd.read_csv(csv_string)

            # Clean and normalize squad names
            self.df['Squad'] = self.df['Squad'].astype(str).str.strip()
            self.df['Squad_normalized'] = self.df['Squad'].str.casefold()

            # Map normalized name to original name for display
            self.team_map = dict(zip(self.df['Squad_normalized'], self.df['Squad']))
            self.all_teams = sorted(self.team_map.keys())

            # Add a column for country flags (e.g., for Germany, Spain, France)
            # For now, we will manually map some of the teams to their respective countries.
            self.team_countries = {
                "Germany": "https://flagcdn.com/w320/de.png",  # Germany flag URL
                "Spain": "https://flagcdn.com/w320/es.png",  # Spain flag URL
                "France": "https://flagcdn.com/w320/fr.png",  # France flag URL
                "Italy": "https://flagcdn.com/w320/it.png",  # Italy flag URL
                "England": "https://flagcdn.com/w320/gb.png",  # England flag URL
            }

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

    def find_players_for_team(self, team_normalized):
        return set(self.df[self.df['Squad_normalized'] == team_normalized]['Player'].unique())

    def normalize_string(self, text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    def create_ui(self):
        st.markdown("""
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
            team1_display = st.selectbox("Select First Team:", [self.get_team_with_flag(t) for t in self.all_teams], key='team1')
        with col2:
            team2_display = st.selectbox("Select Second Team:", [self.get_team_with_flag(t) for t in self.all_teams], key='team2')

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
        return team_display_name.casefold()

    def get_team_with_flag(self, team_normalized):
        """Get team name with flag icon."""
        team_name = self.team_map.get(team_normalized, team_normalized.title())
        country = self.get_country_from_team(team_name)
        flag_url = self.team_countries.get(country, None)
        flag_html = f'<img src="{flag_url}" width="30" style="vertical-align: middle;">' if flag_url else ''
        return f"{flag_html} {team_name}"

    def get_country_from_team(self, team_name):
        """Map team to its country (this is a simple example, adjust as needed)."""
        if "Bayern" in team_name or "Borussia" in team_name:  # For teams in Germany
            return "Germany"
        elif "Barcelona" in team_name or "Real Madrid" in team_name:  # For teams in Spain
            return "Spain"
        elif "Paris" in team_name or "Marseille" in team_name:  # For teams in France
            return "France"
        elif "Juventus" in team_name or "AC Milan" in team_name:  # For teams in Italy
            return "Italy"
        elif "Manchester" in team_name or "Liverpool" in team_name:  # For teams in England
            return "England"
        else:
            return "Unknown"

    def find_connections(self, team1_norm, team2_norm):
        team1_players = self.find_players_for_team(team1_norm)
        team2_players = self.find_players_for_team(team2_norm)

        st.session_state.common_players = sorted(list(team1_players & team2_players))
        st.session_state.guesses = []
        st.session_state.show_answers = False
        st.session_state.correct_count = 0

        team1_display = self.team_map.get(team1_norm, team1_norm.title())
        team2_display = self.team_map.get(team2_norm, team2_norm.title())

        st.info(f"🎯 Find players who have played for both {team1_display} and {team2_display}")
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
        correct_guesses = set([self.normalize_string(g.lower()) for g in st.session_state.guesses]) & \
                          set([self.normalize_string(p.lower()) for p in st.session_state.common_players])
        incorrect_guesses = set([self.normalize_string(g.lower()) for g in st.session_state.guesses]) - \
                            set([self.normalize_string(p.lower()) for p in st.session_state.common_players])
        remaining = set([self.normalize_string(p.lower()) for p in st.session_state.common_players]) - correct_guesses

        st.progress(len(correct_guesses) / len(st.session_state.common_players))

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
    quiz = EuroQuiz()

