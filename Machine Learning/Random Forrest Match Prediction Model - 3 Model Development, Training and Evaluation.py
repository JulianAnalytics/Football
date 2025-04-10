# Import packages
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

# Drop irrelevant variables and define target variable
features = [column for column in df.drop(columns=['Date', 'xG', 'xG.1', 'Home', 'Away', 'Referee', 'Venue', 'Score', 'result', 'home_goals', 'away_goals', 'season_start']).columns]

# Split into training and testing data
train_data = df[df['season_start'] <= 2022]
test_data = df[df['season_start'] == 2023]

X_train = train_data[features]
y_train = train_data['result']
X_test = test_data[features]
y_test = test_data['result']

# Train Random Forest model
clf = RandomForestClassifier(random_state=1)
clf.fit(X_train, y_train)

# Make predictions and evaluate model accuracy
predictions = clf.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
accuracy

# Evaluate performance in a confusion matrix
confusion_matrix(y_test, predictions)


# Tune the hyperparameters
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15, 20]
}

grid_search = GridSearchCV(estimator=clf, param_grid=param_grid, cv=5)
grid_search.fit(X_train, y_train)

grid_search.best_params_

# Using the recommendations of the best hyperparameters, train the new model
clf = RandomForestClassifier(random_state=1, n_estimators=200, max_depth=5)
clf.fit(X_train, y_train)

# Make new predictions and evaluate model accuracy
predictions = clf.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
accuracy

# Create binary variables for home, away, referee and venue
df = pd.get_dummies(df, columns=['Home', 'Away', 'Referee', 'Venue'])


# Define the features and target variable
features = [column for column in df.drop(columns=['Date', 'xG', 'xG.1', 'Score', 'result', 'home_goals', 'away_goals', 'season_start']).columns]

# Split the data into new train and test sets
train_data = df[df['season_start'] <= 2022]
test_data = df[df['season_start'] == 2023]

X_train = train_data[features]
y_train = train_data['result']
X_test = test_data[features]
y_test = test_data['result']

# Find the best hyperparameters for the new Random Forest model
grid_search = GridSearchCV(estimator=clf, param_grid=param_grid, cv=5)
grid_search.fit(X_train, y_train)

grid_search.best_params_

# Train a Random Forest model with the new features and hyperparameters 
clf = RandomForestClassifier(random_state=1, n_estimators=50, max_depth=15)
clf.fit(X_train, y_train)

# Make predictions and evaluate model
predictions = clf.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
accuracy

# Test the model by creating a row of data with has features which represent a hypothetical match.
match = {
    'Wk': [25],
    'home_rolling_avg_goals': [1.9],
    'away_rolling_avg_goals': [1.2],
    'home_rolling_avg_xG': [2.1],
    'away_rolling_avg_xG': [1.3],
    'Day_Saturday': [1],
    'Home_Chelsea': [1],
    'Away_Manchester Utd': [1],
    'Referee_Anthony Taylor': [1],
    'Venue_Stamford Bridge': [1]
}

#For all other binary variables return 0 values intead of null
match = pd.DataFrame(columns=X_train.columns, data=data)

#Predict match outcome!
match.fillna(0, inplace=True)
