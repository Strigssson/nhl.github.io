import requests
import pandas as pd
from datetime import datetime
import pytz

# NHL Teams API URL
api_url = "https://api-web.nhle.com/v1/standings/now"


# Fetch data
response = requests.get(api_url)

#print(response.json())

df = pd.json_normalize(response.json()['standings'])

df['ties'] = df['gamesPlayed'] - df['regulationWins'] - df['losses']

# Step 1: Group by ties and aggregate team names
grouped = df.groupby('ties')['teamAbbrev.default'].apply(list).reindex(range(30)).fillna('').reset_index()

# Step 2: Create an empty DataFrame to hold the results
max_teams = max(grouped['teamAbbrev.default'].apply(len))  # Find the maximum number of teams in any list
teams_df = pd.DataFrame(columns=range(11))  # Initialize an empty DataFrame with 11 columns

# Step 3: Populate the DataFrame with teams, filling with NaN if necessary
for index, team_list in enumerate(grouped['teamAbbrev.default']):
    # Add the teams to the DataFrame
    for i in range(len(team_list)):
        teams_df.loc[i, index] = team_list[i]

# Display the final DataFrame
teams_df = teams_df.fillna('')

html_table = teams_df.to_html(index=True)
# Save the HTML table to a file
with open('table.html', 'w') as f:
    f.write(html_table)

print("HTML table created successfully.")

# Get the current timestamp
# Set the timezone for Bratislava
bratislava_tz = pytz.timezone('Europe/Bratislava')

# Get the current time in Bratislava timezone
timestamp = datetime.now(bratislava_tz).strftime('%Y-%m-%d %H:%M:%S')


with open('table.html', 'r') as f:
    table_content = f.read()

# Replace the placeholder in index.html with the actual table content
with open('index.html', 'w') as f:
    f.write(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NHL Teams Table</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
        </style>
    </head>
    <body>
        <h1>NHL X</h1>
        <div>
            {table_content}
        </div>
   <div style="margin-top: 20px; font-size: 0.9em; color: #666;">
            <p>Last updated: {timestamp}</p>
        </div>
    </body>
    </html>
    """)

print("index.html created successfully with the table.")
