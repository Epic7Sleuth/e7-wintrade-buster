import csv
import os

import requests
from collections import defaultdict

# Function to fetch JSON data for a user via a REST API call
def get_json_data_for_user(user):
    user_id = user['id']
    api_url = f"https://epic7.gg.onstove.com/gameApi/getBattleList?nick_no={user_id}&world_code=world_global&lang=en&season_code=pvp_rta_ss11"  # Replace with the actual API endpoint
    response = requests.post(api_url)
    return response.json()

# Your CSV data containing the list of users
csv_file = r''  # Replace with the path to your CSV file csv files is made with code,id,name I filltered out anyone bellow rank 70
output_file = r''  # Replace with the desired output file path# Initialize an object database to store the results
result_database = defaultdict(lambda: defaultdict(lambda: {'enemy_id': 0, 'Loss Turn 0': 0, 'Loss Turn 1': 0, 'Win Turn 0': 0, 'Win Turn 1': 0, 'Rank':"blank"}))

# Counter to keep track of processed users
processed_user_count = 0
non_rta_player = 0
# Loop through the list of users from the CSV
with open(csv_file, mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file, delimiter=',')
    for user in csv_reader:
        
        user_id = user['id']
        user_name = user['name']
        # Fetch JSON data for the user
        json_data = get_json_data_for_user(user)

        try:
            # Extract user's name and nick_no from the fetched JSON data
            battle_list = json_data['result_body']['battle_list']
            for battle in battle_list:
                if battle['season_code'] != "pvp_rta_ss11f":  # Exclude cases with season_code "pvp_rta_ss11f"
                    turn = battle['turn']
                    is_win = battle['iswin']
                    enemy_nick = battle['enemy_nick_no']  # Get the "enemy_nick_no"

                    if is_win == 2 and (turn == 0 or turn == 1):
                        result_database[user_name][enemy_nick]['Loss Turn 0' if turn == 0 else 'Loss Turn 1'] += 1
                        if result_database[user_name][enemy_nick]['Rank'] == "blank":
                            result_database[user_name][enemy_nick]['Rank'] = battle['grade_code']
                            result_database[user_name][enemy_nick]['Enemy id'] = battle['matchPlayerNicknameno']
                        
                    elif is_win == 1 and (turn == 0 or turn == 1):
                        result_database[user_name][enemy_nick]['Win Turn 0' if turn == 0 else 'Win Turn 1'] += 1
                        if result_database[user_name][enemy_nick]['Rank'] == "blank":
                            result_database[user_name][enemy_nick]['Rank'] = battle['grade_code']
                            result_database[user_name][enemy_nick]['Enemy id'] = battle['matchPlayerNicknameno']
        except Exception as e:
            #print(f"{user_name} has no battle history: {non_rta_player}")
            non_rta_player += 1
        # Increment the processed user count
        processed_user_count += 1

        # Check if 100 users have been processed, and save the changes to the CSV file
        if processed_user_count == 100:
                # Write the result database to the CSV file
            with open(output_file, mode='a', encoding='utf-8', newline='') as output_csv:
                fieldnames = ['Name', 'id', 'Enemy Nick', 'Enemy id','Rank', 'Loss Turn 0', 'Loss Turn 1', 'Win Turn 0', 'Win Turn 1', 'Total Loss', 'Total Win']
                csv_writer = csv.DictWriter(output_csv, fieldnames=fieldnames)

                # Write the header row only if the file is empty
                if os.stat(output_file).st_size == 0:
                    csv_writer.writeheader()

                for name, enemies in result_database.items():
                    for enemy_nick, stats in enemies.items():
                        row = {
                            'Name': name,
                            'id': user_id,
                            'Enemy Nick': enemy_nick,
                            'Enemy id': stats['Enemy id'],
                            'Rank': stats['Rank'],
                            'Loss Turn 0': stats['Loss Turn 0'],
                            'Loss Turn 1': stats['Loss Turn 1'],
                            'Win Turn 0': stats['Win Turn 0'],
                            'Win Turn 1': stats['Win Turn 1'],
                            'Total Loss': stats['Loss Turn 0'] + stats['Loss Turn 1'],
                            'Total Win': stats['Win Turn 0'] + stats['Win Turn 1']
                        }
                        csv_writer.writerow(row)


            # Reset the processed user count and clear the result database
            processed_user_count = 0
            result_database.clear()

# Save any remaining changes to the CSV file (for users < 100)
if processed_user_count > 0:
    # Write the result database to the CSV file
    with open(output_file, mode='a', encoding='utf-8', newline='') as output_csv:
        fieldnames = ['Name', 'id', 'Enemy Nick', 'Enemy id','Rank', 'Loss Turn 0', 'Loss Turn 1', 'Win Turn 0', 'Win Turn 1', 'Total Loss', 'Total Win']
        csv_writer = csv.DictWriter(output_csv, fieldnames=fieldnames)

        # Write the header row only if the file is empty
        if os.stat(output_file).st_size == 0:
            csv_writer.writeheader()

        for name, enemies in result_database.items():
            for enemy_nick, stats in enemies.items():
                row = {
                    'Name': name,
                    'id': user_id,
                    'Enemy Nick': enemy_nick,
                    'Enemy id': stats['Enemy id'],
                    'Rank': stats['Rank'],
                    'Loss Turn 0': stats['Loss Turn 0'],
                    'Loss Turn 1': stats['Loss Turn 1'],
                    'Win Turn 0': stats['Win Turn 0'],
                    'Win Turn 1': stats['Win Turn 1'],
                    'Total Loss': stats['Loss Turn 0'] + stats['Loss Turn 1'],
                    'Total Win': stats['Win Turn 0'] + stats['Win Turn 1']
                }
                csv_writer.writerow(row)

print("Results saved to output.csv")
print(f"number of non rta players: {non_rta_player}")