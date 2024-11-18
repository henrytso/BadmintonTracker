import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
from str_dt import str_to_dt, str_from_dt


class DatabaseDriver:

    def __init__(self):
        self.conn = sqlite3.connect("bdmtn.db", check_same_thread=False)
        self.conn.execute("""PRAGMA foreign_keys = 1""")
        self.create_tables()
        self.initialize_table_rows()

    def create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS player(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NULL
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS center(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                UNIQUE(name)
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS court(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER NOT NULL,
                center_id REFERENCES center(id),
                UNIQUE(number, center_id)
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS session(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start DATETIME NOT NULL,
                end DATETIME NOT NULL,
                center_id REFERENCES center(id) DEFAULT(1)
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS session_attendance(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arrival DATETIME NOT NULL,
                departure DATETIME,
                session_id REFERENCES session(id),
                player_id REFERENCES player(id)
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS interval(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start DATETIME NOT NULL,
                end DATETIME NOT NULL,
                session_id REFERENCES session(id)
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS court_signup(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interval_id REFERENCES interval(id),
                court_id REFERENCES court(id),
                player_id REFERENCES player(id)
            )
        """)

        self.conn.commit()

    def initialize_table_rows(self):
        # Create AES and Chelsea Recreation Centers
        self.conn.execute("""
            INSERT OR IGNORE INTO center (name)
            VALUES (?)
        """, ("Alfred E. Smith Recreation Center",))
        self.conn.execute("""
            INSERT OR IGNORE INTO center (name)
            VALUES (?)
        """, ("Chelsea Recreation Center",))

        # Create courts 1-4 for Alfred E. Smith Recreation Center (id: 1)
        for n in range(1, 5):
            self.conn.execute("""
                INSERT OR IGNORE INTO court (number, center_id)
                VALUES (?, ?)
            """, (n, 1))

        # Create courts 1-3 for Chelsea Recreation Center (id: 2)
        for n in range(1, 4):
            self.conn.execute("""
                INSERT OR IGNORE INTO court (number, center_id)
                VALUES (?, ?)
            """, (n, 2))

        self.conn.commit()

    def create_player(self, first_name, last_name):
        cursor = self.conn.execute("""
            INSERT INTO player (first_name, last_name)
            VALUES (?, ?)
        """, (first_name, last_name))
        
        self.conn.commit()

        return cursor.lastrowid

    def get_all_players(self):
        cursor = self.conn.execute("""
            SELECT * FROM player
        """)

        players = []

        for row in cursor:
            players.append({
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2]
            })

        return players

    def get_player_by_id(self, player_id):
        cursor = self.conn.execute("""
            SELECT * FROM player
            WHERE id = ?
        """, (player_id,))

        for row in cursor:
            return {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2]
            }

        return None

    def get_all_centers(self):
        cursor = self.conn.execute("""
            SELECT * FROM center
        """)

        centers = []

        for row in cursor:
            centers.append({
                "id": row[0],
                "name": row[1],
                "courts": self.get_courts_of_center(row[0])
            })

        return centers

    def get_courts_of_center(self, center_id):
        cursor = self.conn.execute("""
            SELECT * FROM court
            WHERE center_id = ?
        """, (center_id,))

        courts = []

        for row in cursor:
            courts.append({
                "id": row[0],
                "number": row[1]
            })

        return courts

    def get_court_by_id(self, court_id):
        cursor = self.conn.execute("""
            SELECT * FROM court
            WHERE id = ?
        """, (court_id,))

        for row in cursor:
            return {
                "id": row[0],
                "number": row[1],
                "center_id": row[2]
            }

        return None

    def get_signups_of_court(self, court_id, interval_id):
        cursor = self.conn.execute("""
            SELECT * FROM court_signup
            WHERE court_id = ? AND interval_id = ?
        """, (court_id, interval_id))

        signups = []
        
        for row in cursor:
            signups.append({
                "id": row[0],
                "interval_id": row[1],
                "court_id": row[2],
                "player_id": row[3]
            })

        return signups

    def create_session(self, start, end, center_id):
        cursor = self.conn.execute("""
            INSERT INTO session (start, end, center_id)
            VALUES (?, ?, ?)
        """, (start, end, center_id))

        session_id = cursor.lastrowid
        
        def create_intervals():
            interval_start_dt, end_dt = str_to_dt(start), str_to_dt(end)

            while interval_start_dt + timedelta(minutes=15) <= end_dt:
                interval_end_dt = interval_start_dt + timedelta(minutes=15)

                self.conn.execute("""
                    INSERT INTO interval (start, end, session_id)
                    VALUES (?, ?, ?)
                """, (str_from_dt(interval_start_dt), str_from_dt(interval_end_dt), session_id))

                interval_start_dt = interval_end_dt

        create_intervals()

        self.conn.commit()

        return session_id


    def get_all_sessions(self):
        cursor = self.conn.execute("""
            SELECT * FROM session
        """)

        sessions = []

        for row in cursor:
            sessions.append({
                "id": row[0],
                "start": row[1],
                "end": row[2],
                "center_id": row[3]
            })

        return sessions

    def get_center_by_id(self, center_id):
        cursor = self.conn.execute("""
            SELECT * FROM center
            WHERE id = ?
        """, (center_id,))

        for row in cursor:
            return {
                "id": row[0],
                "name": row[1]
            }

        return None

    def get_session_by_id(self, session_id):
        cursor = self.conn.execute("""
            SELECT * FROM session
            WHERE id = ?
        """, (session_id,))

        for row in cursor:
            return {
                "id": row[0],
                "start": row[1],
                "end": row[2],
                "center_id": row[3]
            }

        return None

    def get_intervals_of_session(self, session_id):
        cursor = self.conn.execute("""
            SELECT * FROM interval
            WHERE session_id = ?
            ORDER BY id
        """, (session_id,))

        intervals = []

        for row in cursor:
            intervals.append({
                "id": row[0],
                "start": row[1],
                "end": row[2]
                #"session_id": row[3]
            })

        return intervals

    def get_interval_by_id(self, interval_id):
        cursor = self.conn.execute("""
            SELECT * FROM interval
            WHERE id = ?
        """, (interval_id,))

        for row in cursor:
            return {
                "id": row[0],
                "start": row[1],
                "end": row[2],
                "session_id": row[3]
            }

        return None

    def get_session_attendance(self, session_id, player_id):
        cursor = self.conn.execute("""
            SELECT * FROM session_attendance
            WHERE session_id = ? AND player_id = ?
        """, (session_id, player_id))

        for row in cursor:
            return {
                "id": row[0],
                "arrival": row[1],
                "departure": row[2],
                "session_id": row[3],
                "player_id": row[4]
            }

        return None

    def get_session_attendance_by_id(self, attendance_id):
        cursor = self.conn.execute("""
            select * from session_attendance
            where id = ?
        """, (attendance_id,))

        for row in cursor:
            return {
                "id": row[0],
                "arrival": row[1],
                "departure": row[2],
                "session_id": row[3],
                "player_id": row[4],
            }

        return None

    def get_attendances_of_session(self, session_id):
        cursor = self.conn.execute("""
            SELECT * FROM session_attendance
            WHERE session_id = ?
        """, (session_id,))

        attendances = []

        for row in cursor:
            attendances.append({
                "id": row[0],
                "arrival": row[1],
                "departure": row[2],
                "session_id": row[3],
                "player_id": row[4],
            })

        return attendances

    def create_session_attendance(self, session_id, player_id, arrival):
        cursor = self.conn.execute("""
            INSERT INTO session_attendance (arrival, session_id, player_id)
            VALUES (?, ?, ?)
        """, (arrival, session_id, player_id))

        self.conn.commit()

        return cursor.lastrowid

    def set_departure_session_attendance(self, session_id, player_id, departure):
        cursor = self.conn.execute("""
            UPDATE session_attendance
            SET departure = ?
            WHERE session_id = ? AND player_id = ?
        """, (departure, session_id, player_id))

        self.conn.commit()

        return cursor.lastrowid

    def get_court_signup_by_id(self, signup_id):
        cursor = self.conn.execute("""
            SELECT * FROM court_signup
            WHERE id = ?
        """, (signup_id,))

        for row in cursor:
            return {
                "id": row[0],
                "interval_id": row[1],
                "court_id": row[2],
                "player_id": row[3],
            }
        
        return None

    def get_court_signup(self, interval_id, court_id, player_id):
        cursor = self.conn.execute("""
            SELECT * FROM court_signup
            WHERE interval_id = ? AND court_id = ? AND player_id = ?
        """, (interval_id, court_id, player_id))

        for row in cursor:
            return {
                "id": row[0],
                "interval_id": row[1],
                "court_id": row[2],
                "player_id": row[3]
            }

        return None

    def create_court_signup(self, interval_id, court_id, player_id):
        cursor = self.conn.execute("""
            INSERT INTO court_signup (interval_id, court_id, player_id)
            VALUES (?, ?, ?)
        """, (interval_id, court_id, player_id))

        self.conn.commit()

        return cursor.lastrowid

    def remove_court_signup(self, interval_id, court_id, player_id):
        cursor = self.conn.execute("""
            DELETE FROM court_signup
            WHERE interval_id = ? AND court_id = ? AND player_id = ?
        """, (interval_id, court_id, player_id))

        self.conn.commit()
        
        return cursor.lastrowid

    def get_player_signups_of_session_by_interval_court(self, session_id):
        cursor = self.conn.execute("""
            SELECT * FROM court_signup
            JOIN interval
            ON interval.id = court_signup.interval_id
            WHERE interval.session_id = ?
        """, (session_id,))

        signups = defaultdict(list)

        for row in cursor:
            interval_court_id = str(row[1]) + "-" + str(row[2])
            signups[interval_court_id].append(row[3])
        
        return signups

    def get_past_player_signups_of_session_by_interval_court(self, session_id, now):
        cursor = self.conn.execute("""
            SELECT * FROM court_signup
            JOIN interval
            ON interval.id = court_signup.interval_id
            WHERE interval.session_id = ?
            AND interval.end <= ?
        """, (session_id, now))

        signups = defaultdict(list)

        for row in cursor:
            interval_court_id = str(row[1]) + "-" + str(row[2])
            signups[interval_court_id].append(row[3])

        return signups

    def get_live_player_signups_of_session_by_interval_court(self, session_id, now):
        cursor = self.conn.execute("""
            SELECT * FROM court_signup
            JOIN interval
            ON interval.id = court_signup.interval_id
            WHERE interval.session_id = ?
            AND interval.end > ?
        """, (session_id, now))

        signups = defaultdict(list)

        for row in cursor:
            interval_court_id = str(row[1]) + "-" + str(row[2])
            signups[interval_court_id].append(row[3])

        return signups

    # Present players, not yet signed up
    def get_players_in_bank(self, session_id, now):
        cursor = self.conn.execute("""
            SELECT * FROM player
            JOIN session_attendance
            ON player.id = session_attendance.player_id
            WHERE session_attendance.departure IS NULL
            AND NOT EXISTS (
                SELECT 1 FROM court_signup
                JOIN interval
                ON interval.id = court_signup.interval_id
                WHERE session_id = ?
                AND interval.end > ?
                AND session_attendance.player_id = court_signup.player_id
            )
            ORDER BY player.first_name
        """, (session_id, now))

        bank_players = []
        
        for row in cursor:
            bank_players.append({
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2]
            })

        return bank_players

    def get_live_interval_id(self, session_id, now):
        cursor = self.conn.execute("""
            SELECT * FROM interval
            WHERE interval.session_id = ?
            AND interval.start <= ?
            AND ? < interval.end
        """, (session_id, now, now))

        for row in cursor:
            return row[0]

        return None

    # For /api/v2/sessionData/<int:session_id>/
    def get_interval_ids_of_session(self, session_id):
        cursor = self.conn.execute("""
            SELECT interval.id FROM interval
            JOIN session
            ON session.id = interval.session_id
            WHERE session.id = ?
            ORDER BY interval.id
        """, (session_id,))

        return [row[0] for row in cursor]

    def get_court_ids_of_session(self, session_id):
        cursor = self.conn.execute("""
            SELECT court.id from court
            JOIN session
            ON court.center_id = session.center_id
            WHERE session.id = ?
        """, (session_id,))

        return [row[0] for row in cursor]

def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return get_instance


DatabaseDriver = singleton(DatabaseDriver)
