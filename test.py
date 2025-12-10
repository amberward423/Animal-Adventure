
from db_setting import *
from flask import Flask, request
from flask_cors import CORS
import json
from geopy import distance

from func import check_animal

app = Flask(__name__)

CORS(app)
@app.route("/animal_adventure/start_game")
def start_game():
    game_id = add_player()
    stats = get_stats(game_id)
    airports = final_airport_list(game_id,stats[0]["location"])
    data = {'game_id':game_id, 'stats': stats, 'airports': airports}
    return json.dumps(data)


@app.route("/animal_adventure/check_balance/<game_id>")
def check_stats(game_id):
    stats = get_stats(game_id)
    return stats


@app.route("/animal_adventure/buy_fuel/<game_id>")
def buy_fuel(game_id):
    stats = update_fuel(game_id)
    return stats


@app.route("/animal_adventure/choose_airport/<game_id>/<icao>")
def choose_airport(game_id,icao):
    stats = update_location(game_id,icao)
    return stats

@app.route("/animal_adventure/check_animal/<game_id>/<icao>/")
def check_animal(game_id,location):
    stats = c_a(game_id,location)
    if not stats:
        return json.dumps(stats)
    if stats['rescued'] == 0:
        return json.dumps(stats)


def add_player():
    cursor = get_db()
    cursor.execute(
        """INSERT INTO game (screen_name, money, player_range, location, turn_time)  
           VALUES (%s, %s, %s, %s, %s)""",
           ('Amber',1000,5000,'efhk','5'))
    game_id = cursor.lastrowid

    return game_id

def get_stats(game_id):
    cursor = get_db()
    cursor.execute(
        """SELECT money,player_range,turn_time,location FROM game WHERE id = %s""",
        (game_id,))

    result = cursor.fetchall()
    return result



def update_fuel(game_id):
    cursor = get_db()
    # UPDATE the fuel amount for the player
    cursor.execute(
        """UPDATE game
        SET money = money - 100,
            player_range = player_range + 1000
        WHERE id = %s;
        """,
        (game_id,))
    return get_stats(game_id)


def update_location(game_id,icao):
    cursor = get_db()
    cursor.execute(
        """UPDATE game
            SET location = %s,
            player_range = player_range - 100,
            money = money - 0,
            turn_time = turn_time - 1
           WHERE id = %s
        """,
        (icao,game_id,))

    return get_stats(game_id)


def final_airport_list(game_id, icao):
    airports = get_airports()
    s_airports = sorted_airports(airports,icao)
    return s_airports




def get_airports():
    """ Retrieve a random selection of large airports located in Europe. """
    db = get_db()
    db.execute("""
        SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
        FROM airport
        WHERE continent = 'EU'
        AND type = 'large_airport'
        ORDER BY RAND()
        LIMIT 20
    """)
    result = db.fetchall()
    return result

def get_airport_info(icao):
    """ Retrieve information about a specific airport by its ICAO code. """
    db = get_db()
    db.execute("""
    SELECT iso_country, ident, name, latitude_deg, longitude_deg 
    FROM airport
    WHERE ident = %s
    """, (icao,))
    result = db.fetchone()
    return result


def calculate_distance(current, target):
    """ Calculate the distance (in kilometers) between two airports. """
    start = get_airport_info(current)
    end = get_airport_info(target)
    return distance.distance((start['latitude_deg'], start['longitude_deg']),
                             (end['latitude_deg'], end['longitude_deg'])).km


def airports_in_range(icao, a_ports, p_range):
    """ Find all airports that are within a range from the player's current location. """
    in_range = []
    for a_port in a_ports:
        dist = calculate_distance(icao, a_port['ident'])
        if dist <= p_range and not dist == 0:
            in_range.append(a_port)
    return in_range


def sorted_airports(airports, current_airport):
    """ Sort a list of airports by their distance from the current location. """
    airport_distances = []
    for airport in airports:
        ap_distance = calculate_distance(current_airport, airport["ident"])
        airport_distances.append({
            "icao": airport["ident"],
            "name": airport["name"],
            "distance_km": round(ap_distance)
        })
        airport_distances.sort(key=lambda x: x["distance_km"])
    return airport_distances




def c_a(game_id, current_airport):
    """ Check if there is an unrescued animal located at the current airport. """
    db = get_db()
    db.execute("""
    select id from located_animals 
    WHERE game_id = %s 
    AND location = %s
    """, (game_id, current_airport), )
    result = db.fetchone()
    if not result:
        return None
    if result['rescued'] == 0:
        return result
    return None


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=3000)