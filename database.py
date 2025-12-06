import sqlite3

def get_connection():
    conn = sqlite3.connect("meal_planner.db")
    conn.row_factory = sqlite3.Row  # Pour retourner les résultats sous forme de dictionnaire
    return conn
