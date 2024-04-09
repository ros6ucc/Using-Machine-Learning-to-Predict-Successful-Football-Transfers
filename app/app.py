from flask import Flask, request, render_template_string, render_template, jsonify
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)

# Load your models and scaler
minModel = joblib.load('minModel.pkl')
valueModel = joblib.load('valueModel.pkl')
scaler = joblib.load('scaler.save')

# Load your data
stat = pd.read_csv('19-22_data.csv')
club_data = pd.read_csv('club_data.csv')

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        player = request.form['player']
        club = request.form['club']
        
        prediction_results , metrics, image_url, success_score, formatted_minutes_percentage, predicted_minutes_color, formatted_transfer_value, formatted_previous_value, value_at_transfer, player_predicted_value_rounded, player_age, current_club, league_weight = prediction_function(player, club)
    
        if metrics is None:
            # This means the player is already at the club, so display the message
            return render_template_string("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Prediction Results Error</title>
                    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}"> 
                    <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
                    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
                    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>                     
                </head>
                <div class="main-container">
                        <p>{{ prediction_results }}</p>
                    <a href="/" class="back-link">Try Again?</a>
                </div>
                </html>
            """, prediction_results=prediction_results,)
        
        metrics_html = metrics.replace('\n', '<br>')
        
        return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Prediction Results</title>
                <link rel="icon" href="static/icon.png" type="image/x-icon">
                <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}"> 
                <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
                <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>                     
            </head>
            <body>
                <div class="result-container">
                    <a class="home-button" href="/">
                        <img src="{{ url_for('static', filename='home.png') }}" alt="Home" />
                    </a>
                    <h2>Prediction Results</h2>
                    <div class="content-container">
                        <div class="player-image-container">
                            <img src="{{ image_url }}" alt="Player Image" class="player-image">
                        </div>
                        <div class="info-container">
                            <div class="results">
                                <p>{{ prediction_results }}</p>
                                <div class="success-score-container">
                                <div id="scoreContainer" data-score="{{ success_score }}"></div>
                                </div>
                            </div>
                            <div class="player-details-container">
                                <h3> Details:</h3>
                                <div class="stat-item">
                                    <span class="stat-title" title="This represents the percentage of total available playing minutes the player is predicted to play for the new club.">Predicted Minutes Percentage:</span>
                                    <span class="stat-value" style="border: 2px solid {{ predicted_minutes_color }}; padding: 2px; border-radius: 5px; display: inline-block;">
                                        {{ formatted_minutes_percentage }}
                                    </span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-title" title="This is an estimate of the player's future value in the transfer market based on their performance statistics, age and peak value.">Predicted Transfer Value:</span>
                                    <span id="transferValue" class="stat-value">{{ formatted_transfer_value }}  →  Current Transfer Value: {{ formatted_previous_value }}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-title" title="A player's age has a massive influence on their transfer appeal">Player Age:</span>
                                    <span id="age" class="stat-value">{{ player_age }}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-title" title="Transfers between clubs in the same league have historically been more successful">Current Club:</span>
                                    <span id="club" class="stat-value">{{ current_club }}</span>
                                </div>
                                <a href
                            </div>
                        </div>
                    </div>
                </div>
            <script>
            $(document).ready(function() {
                $("#player").autocomplete({
                    source: "{{ url_for('suggest', partial_name='') }}" + $("#player").val(),
                    minLength: 2
                });

                // Club suggestions
                $("#club").autocomplete({
                    source: "{{ url_for('suggest_club', partial_name='') }}" + $("#club").val(),
                    minLength: 2
                });

                // Function to display the success score in a circular gradient
                function displaySuccessScore(score) {
                    const scoreContainer = document.getElementById('scoreContainer');
                    if (!scoreContainer) return;

                    const radius = 90; 
                    const strokeWidth = 30;
                    const circumference = 2 * Math.PI * radius;
                    let offset = circumference - (score / 100) * circumference;

                    // Set properties for the animation
                    // scoreContainer.style.setProperty('--initial-offset', circumference);
                    scoreContainer.style.setProperty('--final-offset', offset);

                    const redValue = Math.round((1 - (score / 100)) * 255);
                    const greenValue = Math.round((score / 100) * 255);
                    const color = `rgb(${redValue}, ${greenValue}, 0)`;

                    scoreContainer.innerHTML = `
                        <svg height="300" width="300">
                            <circle cx="150" cy="150" r="${radius}" fill="transparent" stroke="lightgrey" stroke-width="${strokeWidth}"></circle>
                            <circle class="score-circle" cx="150" cy="150" r="${radius}" fill="transparent" stroke="${color}" stroke-width="${strokeWidth}"
                                stroke-dasharray="${circumference}" stroke-dashoffset="${circumference}"
                                transform="rotate(-90 150 150)"></circle>
                            <text x="50%" y="50%" text-anchor="middle" stroke="${color}" stroke-width="1px" dy=".3em" font-size="30">${score}%</text>
                        </svg>
                    `;
                }

                // Invoke the function to display the success score with the correct score value.
                var successScore = {{ success_score | tojson }};
                displaySuccessScore(successScore);
            });

            var playerPredictedValueRounded = {{ player_predicted_value_rounded | tojson }};
            var valueAtTransfer = {{ value_at_transfer | tojson }};
            var player_age = {{ player_age }};
            var league_weight = {{ league_weight }};

            window.onload = function() {
                var valueChangeClass = "";
                if (playerPredictedValueRounded > valueAtTransfer) {
                    valueChangeClass = "value-risen";
                } else if (playerPredictedValueRounded < valueAtTransfer) {
                    valueChangeClass = "value-fallen";
                } else {
                    valueChangeClass = "value-maintained";
                }

                document.getElementById('transferValue').classList.add(valueChangeClass);
                                      
                var ageChangeClass = "";
                if (player_age > 32) {
                    ageChangeClass = "value-fallen";
                } else if (player_age <= 20) {
                    ageChangeClass = "value-maintained";
                } else {
                    ageChangeClass = "value-risen";
                }

                document.getElementById('age').classList.add(ageChangeClass);
                                      
                var clubChangeClass = "";
                if (league_weight == 5) {
                    clubChangeClass = "value-risen";
                } else {
                    clubChangeClass = "value-fallen";
                }
                                      
                document.getElementById('club').classList.add(clubChangeClass);
            };                      
            </script>
            </body>
            </html>
            """, prediction_results=prediction_results, metrics_html=metrics_html, image_url=image_url, success_score=success_score, formatted_minutes_percentage=formatted_minutes_percentage, predicted_minutes_color=predicted_minutes_color, formatted_transfer_value=formatted_transfer_value, formatted_previous_value=formatted_previous_value, value_at_transfer=value_at_transfer, player_predicted_value_rounded=player_predicted_value_rounded, player_age=player_age, current_club=current_club, league_weight=league_weight)
    
    # Initial form for input
    return render_template_string("""
        <!DOCTYPE html>
            <html>
        <head>
            <title>Prediction Input Form</title>
            <link rel="icon" href="static/icon.png" type="image/x-icon">
            <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
            <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
            <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
        </head>
        <body><div class="main-container">
            <a class="search-button" href="{{ url_for('suggest_players') }}">
                <img src="{{ url_for('static', filename='search.png') }}" alt="Home" />
            </a>
            <h2>European Transfer Prediction System</h2>
            <form method="post" class="prediction-form">
                <div class="form-group">
                    <label for="player">Player:</label>
                    <input type="text" id="player" name="player" required>
                </div>
                <div class="form-group">
                    <label for="club">Club:</label>
                    <input type="text" id="club" name="club" required>
                </div>
                <button type="submit" class="submit-btn1">Get Prediction</button>
            </form>
            <a href="{{ url_for('about') }}" class="learn-more-link">Learn more about the model</a>
            <script type="text/javascript">
                var suggestPlayerURL = "{{ url_for('suggest', partial_name='') }}";
            </script>
            <script src="{{ url_for('static', filename='js/app.js') }}"></script>
        </div>
        </body>
        </html>
    """)


@app.route('/suggest/<string:partial_name>')
def suggest(partial_name):
    current_players = stat[stat['season'] == 2022]
    suggestions = current_players[current_players['name'].str.contains(partial_name, case=False, na=False)]
    suggestions = suggestions[['name', 'image_url']].drop_duplicates().to_dict(orient='records')
    return jsonify(suggestions)

@app.route('/suggest_club/<string:partial_name>')
def suggest_club(partial_name):
    club_suggestions = club_data[club_data['club_name'].str.contains(partial_name, case=False, na=False)]['club_name'].drop_duplicates().tolist()
    return jsonify({'suggestions' :club_suggestions})

def calculate_color(score):
    # Red to Green gradient
    red = 255 * (1 - score / 100)
    green = 255 * (score / 100)
    blue = 0  # keep blue at 0 for red to green gradient
    return f"rgb({int(red)}, {int(green)}, {int(blue)})"

def prediction_function(player, club):
    # Filter stat for the selected player and club
    player_data = stat[(stat['name'] == player) & (stat['season'] == 2022)]
    club_df = club_data[club_data['club_name'] == club]
    
    if player not in stat['name'].values:
        return f"Player does not exist.", None, None, None, None, None, None, None, None, None, None, None, None
    
    if club not in club_data['club_name'].values:
        return f"Club does not exist.", None, None, None, None, None, None, None, None, None, None, None, None
    
    # Assuming 'features' list is defined somewhere with the correct feature names
    features = ['age', 'avg_minutes_percentage', 'minutes_played', 'MP', 'games', 'goals_against', 'goals', 'goals_for','assists','clean_sheet','highest_market_value_in_eur','previous_value']  # Replace with actual feature names
    
    # Find details for new club
    average_MP_for_club = club_df['club_average_matches'].iloc[0]
    club_league = club_df['domestic_competition_id'].iloc[0]

    # League weight calculation
    current_league = player_data['domestic_competition_id'].iloc[0]
    league_weight = 0
    if club_league == current_league:
        league_weight = 5
    
    # Update 'MP' for the player
    player_data['MP'] = average_MP_for_club

    # Find the player's age
    player_age = player_data['age'].iloc[0] 

    # Find the image URL for the player
    image_url = player_data['image_url'].iloc[0] if not player_data['image_url'].empty else None

    current_club = player_data['club_name'].iloc[0]

    if club == current_club:
        return f"{player} is already at {current_club}.", None, None, None, None, None, None, None, None, None, None, None, None
    
    # Prepare data for prediction
    X_player = player_data[features]
    X_player_scaled = scaler.transform(X_player)
    
    # Predict minutes percentage and transfer value
    player_predicted_minutes_percentage = minModel.predict(X_player_scaled)[0]
    player_predicted_value = valueModel.predict(X_player_scaled)[0]
    player_predicted_value_rounded = np.round(player_predicted_value / 1_000_000) * 1_000_000
    
    # Calculate success score
    value_at_transfer = player_data['previous_value'].iloc[0]
    success_score = calculate_success_score(player_predicted_value_rounded, value_at_transfer, player_predicted_minutes_percentage, player_age, league_weight)
    
    # Formatting changes here
    # Convert minutes percentage to a percentage format for display
    player_predicted_minutes_percentage = min(player_predicted_minutes_percentage, 1.0)
    formatted_minutes_percentage = "{:.0f}%".format(player_predicted_minutes_percentage * 100)
    predicted_minutes_color = calculate_color(player_predicted_minutes_percentage * 100)
    
    # Format transfer value in millions and add the Euro symbol for display
    formatted_transfer_value = "€{:.0f} Million".format(player_predicted_value_rounded / 1_000_000)
    formatted_previous_value = "€{:.0f} Million".format(value_at_transfer / 1_000_000)
    
    # Prepare results string using the formatted values
    prediction_results = f"{player} → {club} = Success Score:"
    metrics = f"Predicted Minutes Percentage: {formatted_minutes_percentage}\nPredicted Transfer Value: {formatted_transfer_value}\nCurrent Transfer Value: {formatted_previous_value}"
    return prediction_results, metrics, image_url, success_score, formatted_minutes_percentage, predicted_minutes_color, formatted_transfer_value, formatted_previous_value, value_at_transfer, player_predicted_value_rounded, player_age, current_club, league_weight

def calculate_success_score(predicted_value, value_at_transfer, predicted_minutes_percentage, player_age, league_weight):
    # Assuming 'weight_minutes' and 'weight_value' are defined
    weight_minutes = 0.475
    weight_value = 0.475

    # Adjust weight_minutes based on player's age
    if player_age > 32 or player_age <= 20:
        weight_minutes = 0.3

    if player_age > 32:
        weight_value = 0.3

    if value_at_transfer > 0:
        value_ratio = predicted_value / value_at_transfer if predicted_value < value_at_transfer else 1
    else:
        value_ratio = 0
    valueX = value_ratio * weight_value * 100
    valueY = min(predicted_minutes_percentage, 1) * weight_minutes * 100
    valueY = min(valueY, 50)

    success_score = valueX + valueY + league_weight
    success_score = round(success_score)
    success_score = min(success_score, 100)
    return success_score

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/suggest_players', methods=['GET', 'POST'])
def suggest_players():
    if request.method == 'POST':
        club = request.form['club']
        sub_position = request.form['sub_position']
        budget = request.form['budget']

        # Convert "No Limit" to a very high number to simplify logic
        if budget == "No Limit":
            budget = float('inf')
        else:
            budget = float(budget) 

        # Check if the club exists
        if club not in club_data['club_name'].values:
            return render_template_string("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Club Not Found</title>
                    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">
                    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
                </head>
                <body>
                    <div class="main-container">
                        <p>Club '{{ club }}' not found. Please try another club.</p>
                        <a href="/suggest_players" class="back-link">Back</a>
                    </div>
                </body>
                </html>
            """, club=club)

        # Call a function to get top player suggestions
        suggestions = get_player_suggestions(club, sub_position, budget)

        # Display suggestions
        return render_template('suggestions.html', suggestions=suggestions)
    else:
        # Display the form
        return render_template('suggest_players_form.html')

def get_player_suggestions(club, sub_position, budget):
    # Filter players by position and other criteria
    filtered_players = stat[(stat['sub_position'] == sub_position) & (stat['season'] == 2022)]
    club_df = club_data[club_data['club_name'] == club]
    
    suggestions = []
    for index, player_row in filtered_players.iterrows():
        # Assuming features list is defined somewhere with the correct feature names
        features = ['age', 'avg_minutes_percentage', 'minutes_played', 'MP', 'games', 'goals_against', 'goals', 'goals_for', 'assists', 'clean_sheet', 'highest_market_value_in_eur', 'previous_value']
        average_MP_for_club = club_df['club_average_matches'].iloc[0]
        player_row['MP'] = average_MP_for_club
        player_age = player_row['age']
        current_club = player_row['club_name']


        # Prepare data for prediction
        X_player = player_row[features].values.reshape(1, -1)
        X_player_scaled = scaler.transform(X_player)

        club_league = club_df['domestic_competition_id'].iloc[0]
        current_league = player_row['domestic_competition_id']
        league_weight = 0
        if club_league == current_league:
            league_weight = 10

        # Predict minutes percentage and transfer value
        player_predicted_minutes_percentage = minModel.predict(X_player_scaled)[0]
        player_predicted_value = valueModel.predict(X_player_scaled)[0]
        player_predicted_value = valueModel.predict(X_player_scaled)[0]
        if np.isinf(player_predicted_value):
            print("Infinity detected in predictions")
        player_predicted_value_rounded = np.round(player_predicted_value / 1_000_000) * 1_000_000
        value_at_transfer = player_row['previous_value']
        success_score = calculate_success_score(player_predicted_value_rounded, value_at_transfer, player_predicted_minutes_percentage, player_age, league_weight)

        player_predicted_minutes_percentage = min(player_predicted_minutes_percentage, 1.0)
        formatted_minutes_percentage = "{:.0f}%".format(player_predicted_minutes_percentage * 100)
        formatted_transfer_value = "€{:.0f} Million".format(player_predicted_value_rounded / 1_000_000)

        if player_predicted_value_rounded <= budget and current_club != club:
            suggestions.append({
                'player': player_row['name'],
                'games' : player_row['games'],
                'age' : player_age,
                'success_score': success_score,
                'metrics': f"Predicted Minutes Percentage: {formatted_minutes_percentage}.   /    Predicted Transfer Value: {formatted_transfer_value}",
                'details': f"{player_age} years old.    /   Current Club: {current_club}.",
                'image_url': player_row.get('image_url', '')
            })
    
    # Sort suggestions by success score, descending
    sorted_suggestions = sorted(suggestions, key=lambda k: (k['success_score'], k['games'], -k['age']), reverse=True)
    
    return sorted_suggestions[:15]



if __name__ == '__main__':
    app.run(debug=True)