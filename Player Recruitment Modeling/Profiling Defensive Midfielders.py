#Import libraries
import pandas as pd
import numpy as np

#Load data
df = pd.read_csv('USL2022playerstats.csv')


#Create functions
def minmax_norm(data):
    return (data - min(data))/(max(data)-min(data)) * 100

def minmax_norm_df(competition_df):
    new_df = competition_df.copy()
    for col_name in new_df.columns[17:]:
        if new_df[col_name].dtype in ('int64','float64'):
            new_df[col_name] = minmax_norm(new_df[col_name])
    return new_df

#Data preprocessing
df.fillna(0, inplace = True)
df = df[df['player_season_minutes'] >= 450]

#Define positions
defensive_midfield_positions = ['Right Defensive Midfielder', 'Left Defensive Midfielder', 'Centre Defensive Midfielder',  
                              'Right Centre Midfielder',  'Left Centre Midfielder']
df = df[(df['primary_position'].isin(defensive_midfield_positions)) | (df['secondary_position'].isin(defensive_midfield_positions))].reset_index(drop = True)

#Descriptor profiling
def add_descriptor_stats(df):
    df['Tackling'] = df['player_season_challenge_ratio'] * 0.5 \
                   + df['player_season_padj_tackles_90'] * 0.5
    df['Regains'] = df['player_season_defensive_action_regains_90'] *0.5 \
                    + df['player_season_pressure_regains_90'] * 0.5 
    df['Ball_recoveries'] = df['player_season_ball_recoveries_90']
    df['Heading'] = df['player_season_aerial_ratio'] * 0.5 \
                      + df['player_season_aerial_wins_90'] *0.5
    df['Durability'] = df['player_season_90s_played']
    df['Defending'] = df['player_season_obv_defensive_action_90'] * 0.6 \
                               + df['player_season_dribble_faced_ratio'] * 0.4
    df['Positioning'] = df['player_season_interceptions_90'] * 0.4 \
                          + df['player_season_blocks_per_shot'] * 0.2 \
                          + df['player_season_padj_interceptions_90'] * 0.4
    df['Passing'] = df['player_season_pressured_pass_length_ratio'] * 0.3 \
                          + df['player_season_pressured_passing_ratio'] * 0.7
    df['Progressive_passes'] = df['player_season_deep_progressions_90'] * 0.2 \
                             + df['player_season_op_f3_passes_90'] * 0.2 \
                             + df['player_season_obv_pass_90'] * 0.2 \
                             + df['player_season_through_balls_90'] * 0.2 \
                             + df['player_season_op_passes_into_box_90'] * 0.2
    df['Distribution'] = df['player_season_long_ball_ratio'] * 0.2 \
                    + df['player_season_pass_length_ratio'] * 0.2 \
                    + df['player_season_pass_length_ratio'] * 0.3 \
                    + df['player_season_pressured_pass_length_ratio'] * 0.3
    df['player_season_right_foot_ratio'] = 100 - df['player_season_left_foot_ratio'] 
    df['weak_foot_ratio'] = df[['player_season_left_foot_ratio','player_season_right_foot_ratio']].min(axis=1)
    df = minmax_norm_df(df)
    return df


df = add_descriptor_stats(df)

#Positional profiling
df['Pivot_rating'] = df['Progressive_passes'] * 0.2 \
                               + df['Passing'] * 0.15 \
                               + df['Ball_recoveries'] * 0.15 \
                               + df['Durability'] * 0.1 \
                               + df['Distribution'] * 0.2 \
                               + df['Positioning'] * 0.2  

df['Ball_winner_rating'] = df['Tackling'] * 0.15 \
                               + df['Regains'] * 0.15 \
                               + df['Ball_recoveries'] * 0.15 \
                               + df['Heading'] * 0.15 \
                               + df['Durability'] * 0.1 \
                               + df['Defending'] * 0.1 \
                               + df['Positioning'] * 0.15 \
                               + df['Passing'] * 0.1
     
df['Defensive_midfielder_general_rating'] = df['Tackling'] * 0.15 \
                               + df['Regains'] * 0.15 \
                               + df['Ball_recoveries'] * 0.2 \
                               + df['Durability'] * 0.15 \
                               + df['Defending'] * 0.1 \
                               + df['Positioning'] * 0.1 \
                               + df['Distribution'] * 0.15
                    
#Minmax normalising the ratings
df['Pivot_rating'] = np.round(minmax_norm(df['Pivot_rating']), 0)
df['Ball_winner_rating'] = np.round(minmax_norm(df['Ball_winner_rating']), 0)
df['Defensive_midfielder_general_rating'] = np.round(minmax_norm(df['Defensive_midfielder_general_rating']), 0)                                   
                       
#Profiling
df['avg_rating'] = np.round(df[['Pivot_rating', 'Ball_winner_rating', 'Defensive_midfielder_general_rating']].mean(axis = 1),2)
Profiling = df[['player_name','team_name', 'Pivot_rating', 'Ball_winner_rating', 'Defensive_midfielder_general_rating', 'avg_rating', 'primary_position','secondary_position','player_season_minutes']].sort_values('avg_rating', ascending = False)
Profiling.head(20)
Profiling.to_csv('USL_2022_Defensive_midfielders_profiling.csv')

#Descriptors
df = add_descriptor_stats(df)
Descriptors = df[['player_name','team_name','Tackling','Regains','Ball_recoveries','Heading','Durability','Defending', 'Positioning', 'Passing', 'Progressive_passes', 'Distribution', 'player_season_right_foot_ratio', 'weak_foot_ratio']]
Descriptors.head(20)
Descriptors.to_csv('USL_2022_Defensive_midfielders_descriptors.csv')
