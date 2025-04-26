import streamlit as st
import pandas as pd
from pathlib import Path

class PLTeamQuiz:
    def __init__(self):
        st.set_page_config(page_title="Premier League Team Connection Quiz", layout="wide")
        self.load_data()
        self.initialize_session_state()
        self.create_ui()
    
    def load_data(self):
        """Load player data from CSV."""
        try:
            self.df = pd.read_csv('premier_league_players_all_seasons.csv')
            self.all_teams = sorted(self.df['Squad'].unique())
        except FileNotFoundError:
            st.error("Data file not found. Please ensure the data file exists.")
            st.stop()
    
    def initialize_session_state(self):
        """Initialize session state variables."""
        if 'common_players' not in st.session_state:
            st.session_state.common_players = []
        if 'guesses' not in st.session_state:
            st.session_state.guesses = []
        if 'show_answers' not in st.session_state:
            st.session_state.show_answers = False
    
    def find_players_for_team(self, team):
        """Find all players who have played for a team."""
        return set(self.df[self.df['Squad'] == team]['Player'].unique())
    
    def create_ui(self):
        """Create the Streamlit user interface."""
        st.title("Premier League Team Connection Quiz")
        st.write("Find players who have played for both selected teams!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            team1 = st.selectbox("Select First Team:", self.all_teams, key='team1')
        
        with col2:
            team2 = st.selectbox("Select Second Team:", self.all_teams, key='team2')
        
        if st.button("Find Connections"):
            if team1 == team2:
                st.error("Please select different teams")
            else:
                self.find_connections(team1, team2)
        
        if st.session_state.common_players:
            self.show_quiz_interface()
    
    def find_connections(self, team1, team2):
        """Find players who played for both teams."""
        team1_players = self.find_players_for_team(team1)
        team2_players = self.find_players_for_team(team2)
        st.session_state.common_players = sorted(list(team1_players & team2_players))
        st.session_state.guesses = []
        st.session_state.show_answers = False
        
        st.info(f"Find players who have played for both {team1} and {team2}")
        st.info(f"Number of players to find: {len(st.session_state.common_players)}")
    
    def show_quiz_interface(self):
        """Show the quiz interface with guessing and scoring."""
        guess = st.text_input("Enter a player name:")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Submit Guess"):
                if guess:
                    if guess not in st.session_state.guesses:
                        st.session_state.guesses.append(guess)
        
        with col2:
            if st.button("Toggle Answers"):
                st.session_state.show_answers = not st.session_state.show_answers
        
        if st.session_state.guesses:
            self.show_results()
        
        if st.session_state.show_answers:
            st.write("### All Players")
            for player in st.session_state.common_players:
                st.write(player)
    
    def show_results(self):
        """Show the results of the user's guesses."""
        correct_guesses = set(st.session_state.guesses) & set(st.session_state.common_players)
        incorrect_guesses = set(st.session_state.guesses) - set(st.session_state.common_players)
        remaining = set(st.session_state.common_players) - correct_guesses
        
        st.write("### Your Guesses")
        for guess in st.session_state.guesses:
            if guess in correct_guesses:
                st.success(guess)
            else:
                st.error(guess)
        
        st.write(f"Correct: {len(correct_guesses)} | "
                f"Incorrect: {len(incorrect_guesses)} | "
                f"Remaining: {len(remaining)}")

if __name__ == "__main__":
    quiz = PLTeamQuiz()
