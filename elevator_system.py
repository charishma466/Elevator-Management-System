import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Database functions
def connect_to_database(database_name):
    try:
        conn = sqlite3.connect(database_name)
        print("Connected to database successfully.")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_table(conn, create_table_sql):
    try:
        with conn:
            conn.execute(create_table_sql)
            print("Table created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def insert_data(conn, insert_data_sql, data):
    try:
        with conn:
            conn.execute(insert_data_sql, data)
            print("Data inserted successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")

def fetch_data(conn, fetch_data_sql):
    try:
        c = conn.cursor()
        c.execute(fetch_data_sql)
        rows = c.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")
        return None

# Elevator functions
def move_elevator_up(elevator, target_floor):
    print(f"Elevator {elevator.id} moving up from floor {elevator.current_floor} to floor {target_floor}")
    elevator.current_floor = target_floor

def move_elevator_down(elevator, target_floor):
    print(f"Elevator {elevator.id} moving down from floor {elevator.current_floor} to floor {target_floor}")
    elevator.current_floor = target_floor

def open_elevator_door(elevator):
    print(f"Opening elevator {elevator.id} door")
    elevator.door_open = True

def close_elevator_door(elevator):
    print(f"Closing elevator {elevator.id} door")
    elevator.door_open = False

# Elevator class
class Elevator:
    def __init__(self, elevator_id, num_floors=10, conn=None):
        self.id = elevator_id
        self.num_floors = num_floors
        self.current_floor = 0
        self.door_open = False
        self.conn = conn

    def move_to_floor(self, target_floor):
        if target_floor > self.num_floors or target_floor < 0:
            print("Invalid floor number.")
            return
        initial_floor = self.current_floor
        if target_floor > self.current_floor:
            move_elevator_up(self, target_floor)
        elif target_floor < self.current_floor:
            move_elevator_down(self, target_floor)
        else:
            print("Elevator is already at the target floor.")
        self.log_to_database(initial_floor, target_floor, "moved")

    def open_doors(self):
        open_elevator_door(self)
        self.log_to_database(self.current_floor, self.current_floor, "doors_open")

    def close_doors(self):
        close_elevator_door(self)
        self.log_to_database(self.current_floor, self.current_floor, "doors_closed")

    def log_to_database(self, initial_floor, target_floor, status):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_data(self.conn, "INSERT INTO elevator_data (elevator_id, initial_floor, target_floor, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (self.id, initial_floor, target_floor, status, timestamp))

# Elevator Controller class
class ElevatorController:
    def __init__(self, num_elevators=1, num_floors=10):
        self.conn = connect_to_database("elevator.db")
        self.elevators = [Elevator(i, num_floors, self.conn) for i in range(num_elevators)]
        self.setup_database()

    def setup_database(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS elevator_data (
        id INTEGER PRIMARY KEY,elevator_id INTEGER,
        initial_floor INTEGER,target_floor INTEGER,
        status TEXT,timestamp TEXT );"""
        create_table(self.conn, create_table_sql)

    def request_elevator(self, elevator_id, target_floor):
        if 0 <= elevator_id < len(self.elevators):
            self.elevators[elevator_id].move_to_floor(target_floor)
        else:
            print(f"Invalid elevator ID: {elevator_id}. Valid range is 0 to {len(self.elevators) - 1}.")

    def open_elevator_doors(self, elevator_id):
        if 0 <= elevator_id < len(self.elevators):
            self.elevators[elevator_id].open_doors()
        else:
            print(f"Invalid elevator ID: {elevator_id}. Valid range is 0 to {len(self.elevators) - 1}.")

    def close_elevator_doors(self, elevator_id):
        if 0 <= elevator_id < len(self.elevators):
            self.elevators[elevator_id].close_doors()
        else:
            print(f"Invalid elevator ID: {elevator_id}. Valid range is 0 to {len(self.elevators) - 1}.")

    def print_elevator_status(self):
        for i, elevator in enumerate(self.elevators):
            print(f"Elevator {i} is on floor {elevator.current_floor} with door {'open' if elevator.door_open else 'closed'}.")

# GUI Class
class ElevatorGUI:
    def __init__(self, master, controller):
        self.master = master
        self.controller = controller
        master.title("Elevator Control System")
        self.label = tk.Label(master, text="Elevator Control System")
        self.label.pack()

        self.elevator_id_label = tk.Label(master, text="Elevator ID")
        self.elevator_id_label.pack()
        self.elevator_id_entry = tk.Entry(master)
        self.elevator_id_entry.pack()

        self.floor_label = tk.Label(master, text="Target Floor")
        self.floor_label.pack()
        self.floor_entry = tk.Entry(master)
        self.floor_entry.pack()

        self.move_button = tk.Button(master, text="Move Elevator", command=self.move_elevator)
        self.move_button.pack()

        self.open_door_button = tk.Button(master, text="Open Doors", command=self.open_doors)
        self.open_door_button.pack()

        self.close_door_button = tk.Button(master, text="Close Doors", command=self.close_doors)
        self.close_door_button.pack()

        self.status_button = tk.Button(master, text="Show Status", command=self.show_status)
        self.status_button.pack()

    def move_elevator(self):
        try:
            elevator_id = int(self.elevator_id_entry.get())
            target_floor = int(self.floor_entry.get())
            print(f"Moving elevator {elevator_id} to floor {target_floor}")
            self.controller.request_elevator(elevator_id, target_floor)
        except ValueError:
            messagebox.showerror("Input error", "Please enter valid numbers for elevator ID and target floor.")

    def open_doors(self):
        try:
            elevator_id = int(self.elevator_id_entry.get())
            print(f"Opening doors for elevator {elevator_id}")
            self.controller.open_elevator_doors(elevator_id)
        except ValueError:
            messagebox.showerror("Input error", "Please enter a valid elevator ID.")

    def close_doors(self):
        try:
            elevator_id = int(self.elevator_id_entry.get())
            print(f"Closing doors for elevator {elevator_id}")
            self.controller.close_elevator_doors(elevator_id)
        except ValueError:
            messagebox.showerror("Input error", "Please enter a valid elevator ID.")

    def show_status(self):
        self.controller.print_elevator_status()

# Main program
root = tk.Tk()
controller = ElevatorController(num_elevators=3, num_floors=10)  # Ensure you have at least 1 elevator
gui = ElevatorGUI(root, controller)
root.mainloop()

#cd C:\Users\Hi\Desktop\ELEVATOR
#python elevator_system.py

