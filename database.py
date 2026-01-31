import sqlite3
import os

DB_NAME = "qurupeco.db"


def get_connection():
    """Open a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)


def initialize_database():
    """Create the database and required tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table: Pathlist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pathlist (
            path TEXT PRIMARY KEY
        );
    """)

    # Table: TVEntry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TVEntry (
            filename TEXT PRIMARY KEY,
            seriesName TEXT,
            season INTEGER,
            episode INTEGER
        );
    """)

    # Table: MovieEntry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MovieEntry (
            filename TEXT PRIMARY KEY,
            movieName TEXT
        );
    """)

    conn.commit()
    conn.close()


# Optional helper: simple test insert/select (we'll use real logic later)
def test_database():
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables:", cursor.fetchall())
    conn.close()

def get_all_movies():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, movieName FROM MovieEntry ORDER BY movieName ASC;")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_tv_entries():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT filename, seriesName, season, episode
        FROM TVEntry
        ORDER BY seriesName ASC, season ASC, episode ASC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def insert_test_data():
    conn = get_connection()
    cursor = conn.cursor()

    # ----- Movies -----
    movies = [
        ("avengers.mp4", "The Avengers"),
        ("inception.mkv", "Inception"),
        ("zootopia.mp4", "Zootopia")
    ]

    for filename, movieName in movies:
        try:
            cursor.execute("INSERT INTO MovieEntry (filename, movieName) VALUES (?, ?);",
                           (filename, movieName))
        except sqlite3.IntegrityError:
            pass  # already exists

    # ----- TV Shows -----
    tv_entries = [
        ("bb_s01e01.mkv", "Breaking Bad", 1, 1),
        ("bb_s01e02.mkv", "Breaking Bad", 1, 2),
        ("bb_s02e01.mkv", "Breaking Bad", 2, 1),
        ("lost_s01e01.mp4", "Lost", 1, 1),
        ("lost_s01e02.mp4", "Lost", 1, 2),
        ("lost_s02e01.mp4", "Lost", 2, 1)
    ]

    for filename, seriesName, season, episode in tv_entries:
        try:
            cursor.execute(
                "INSERT INTO TVEntry (filename, seriesName, season, episode) VALUES (?, ?, ?, ?);",
                (filename, seriesName, season, episode)
            )
        except sqlite3.IntegrityError:
            pass  # already exists

    conn.commit()
    conn.close()

    print("Test data inserted.")

def get_paths():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM Pathlist ORDER BY path ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def add_path(path):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Pathlist (path) VALUES (?);", (path,))
    except sqlite3.IntegrityError:
        pass  # already exists
    conn.commit()
    conn.close()


def remove_path(path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Pathlist WHERE path=?;", (path,))
    conn.commit()
    conn.close()


def update_path(old_path, new_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Pathlist SET path=? WHERE path=?;", (new_path, old_path))
    conn.commit()
    conn.close()

def add_movie_entry(filename, movieName):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO MovieEntry (filename, movieName) VALUES (?, ?);",
                   (filename, movieName))
    conn.commit()
    conn.close()


def add_tv_entry(filename, seriesName, season, episode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO TVEntry (filename, seriesName, season, episode) VALUES (?, ?, ?, ?);",
        (filename, seriesName, season, episode)
    )
    conn.commit()
    conn.close()


def filename_exists(filename):
    conn = get_connection()
    cursor = conn.cursor()

    # Check MovieEntry
    cursor.execute("SELECT 1 FROM MovieEntry WHERE filename=?;", (filename,))
    if cursor.fetchone():
        conn.close()
        return True

    # Check TVEntry
    cursor.execute("SELECT 1 FROM TVEntry WHERE filename=?;", (filename,))
    if cursor.fetchone():
        conn.close()
        return True

    conn.close()
    return False

def update_movie_entry(filename, movieName):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE MovieEntry SET movieName=? WHERE filename=?;", (movieName, filename))
    conn.commit()
    conn.close()

def update_tv_entry(filename, seriesName, season, episode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE TVEntry
        SET seriesName=?, season=?, episode=?
        WHERE filename=?;
    """, (seriesName, season, episode, filename))
    conn.commit()
    conn.close()

def delete_movie_entry(filename):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM MovieEntry WHERE filename=?;", (filename,))
    conn.commit()
    conn.close()

def delete_tv_entry(filename):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TVEntry WHERE filename=?;", (filename,))
    conn.commit()
    conn.close()




if __name__ == "__main__":
    initialize_database()
    insert_test_data()

