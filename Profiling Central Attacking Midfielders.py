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
centre_attacking_midfield_positions = ['Centre Attacking Midfielder',  
                              'Right Centre Midfielder',  'Left Centre Midfielder']
df = df[(df['primary_position'].isin(centre_attacking_midfield_positions)) | (df['secondary_position'].isin(centre_attacking_midfield_positions))].reset_index(drop = True)

#Descriptor profiling
def add_descriptor_stats(df):
    df['Durability'] = df['player_season_90s_played']
    df['Progressive_passes'] = df['player_season_deep_progressions_90'] * 0.2 \
                             + df['player_season_op_f3_passes_90'] * 0.2 \
                             + df['player_season_obv_pass_90'] * 0.2 \
                             + df['player_season_through_balls_90'] * 0.2 \
                             + df['player_season_op_passes_into_box_90'] * 0.2
    df['Distribution'] = df['player_season_long_ball_ratio'] * 0.2 \
                    + df['player_season_pass_length_ratio'] * 0.2 \
                    + df['player_season_pass_length_ratio'] * 0.3 \
                    + df['player_season_pressured_pass_length_ratio'] * 0.3
    df['Chance_creation'] = df['player_season_key_passes_90'] * 0.33 \
                          + df['player_season_obv_90'] * 0.33 \
                          + df['player_season_positive_outcome_90'] * 0.33
    df['Assists'] = df['player_season_assists_90'] * 0.5 \
                          + df['player_season_xa_90'] * 0.5
    df['Set_pieces'] = df['player_season_sp_key_passes_90'] * 0.5 \
                          + df['player_season_sp_xa_90'] * 0.5
    df['Progressive_runs'] = df['player_season_carry_ratio'] * 0.3 \
                             + df['player_season_obv_dribble_carry_90'] * 0.2 \
                             + df['player_season_carry_length'] * 0.2 \
                             + df['player_season_carries_90'] * 0.3  
    df['Dribbling'] = df['player_season_dribble_ratio'] * 0.5 \
                          + df['player_season_dribbles_90'] * 0.5
    df['Goal_contributions'] = df['player_season_shots_key_passes_90'] * 0.5 \
                          + df['player_season_npxgxa_90'] * 0.5
    df['player_season_right_foot_ratio'] = 100 - df['player_season_left_foot_ratio'] 
    df['weak_foot_ratio'] = df[['player_season_left_foot_ratio','player_season_right_foot_ratio']].min(axis=1)
    df = minmax_norm_df(df)
    return df


df = add_descriptor_stats(df)

#Positional profiling
df['Number_10_rating'] = df['Dribbling'] * 0.15 \
                               + df['Chance_creation'] * 0.2 \
                               + df['Progressive_runs'] * 0.2 \
                               + df['Goal_contributions'] * 0.2 \
                               + df['Set_pieces'] * 0.15\
                               + df['Durability'] * 0.1  

df['Creator_rating'] = df['Progressive_passes'] * 0.2 \
                               + df['Dribbling'] * 0.1 \
                               + df['Chance_creation'] * 0.2 \
                               + df['Progressive_runs'] * 0.2 \
                               + df['Assists'] * 0.1 \
                               + df['Distribution'] * 0.1 \
                               + df['Durability'] * 0.1


df['Central_attacking_midfielder_general_rating'] = df['Dribbling'] * 0.15 \
                               + df['Chance_creation'] * 0.15 \
                               + df['Progressive_runs'] * 0.2 \
                               + df['Goal_contributions'] * 0.15 \
                               + df['Set_pieces'] * 0.1 \
                               + df['Durability'] * 0.1 \
                               + df['Progressive_passes'] * 0.15
                    
#Minmax normalising the ratings
df['Number_10_rating'] = np.round(minmax_norm(df['Number_10_rating']), 0)
df['Creator_rating'] = np.round(minmax_norm(df['Creator_rating']), 0)
df['Central_attacking_midfielder_general_rating'] = np.round(minmax_norm(df['Central_attacking_midfielder_general_rating']), 0)                             
                       
#Profiling
df['avg_rating'] = np.round(df[['Number_10_rating', 'Creator_rating', 'Central_attacking_midfielder_general_rating']].mean(axis = 1),2)
Profiling = df[['player_name','team_name','Number_10_rating', 'Creator_rating', 'Central_attacking_midfielder_general_rating', 'avg_rating', 'primary_position','secondary_position','player_season_minutes']].sort_values('avg_rating', ascending = False)
Profiling.head(20)
Profiling.to_csv('USL_2022_Central_attacking_midfielders_profiling.csv')

#Descriptors
df = add_descriptor_stats(df)
Descriptors = df[['player_name','team_name','Durability','Progressive_passes','Distribution','Chance_creation','Assists','Set_pieces', 'Progressive_runs', 'Dribbling', 'Goal_contributions', 'player_season_right_foot_ratio', 'weak_foot_ratio']]
Descriptors.head(20)
Descriptors.to_csv('USL_2022_Central_attacking_midfielders_descriptors.csv')
