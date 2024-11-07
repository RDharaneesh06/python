Simport tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3
import hashlib

class Room:
    def __init__(self, room_number):
        self.room_number = room_number
        self.is_available = True
        self.occupant_name = None

    def book(self, name):
        if self.is_available:
            self.is_available = False
            self.occupant_name = name
            return f"Room {self.room_number} successfully booked by {name}."
        else:
            return f"Room {self.room_number} is already booked."

    def cancel(self):
        if not self.is_available:
            occupant = self.occupant_name
            self.is_available = True
            self.occupant_name = None
            return f"Booking for room {self.room_number} by {occupant} has been cancelled."
        else:
            return f"Room {self.room_number} is already available."

    def status(self):
        return f"Room {self.room_number} is {'available' if self.is_available else f'booked by {self.occupant_name}'}."

class Hostel:
    def __init__(self, total_rooms):
        self.rooms = [Room(i + 1) for i in range(total_rooms)]
        self.create_databases()

    def create_databases(self):
        self.conn = sqlite3.connect('hostel_booking.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                role TEXT
            )
        ''')
        self.conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, role):
        try:
            if not username or not password or role not in ['admin', 'user']:
                return "All fields are required and role must be 'admin' or 'user'."
            
            hashed_password = self.hash_password(password)
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                                (username, hashed_password, role))
            self.conn.commit()
            return "User registered successfully!"
        except sqlite3.IntegrityError:
            return "Username already exists."

    def authenticate_user(self, username, password):
        hashed_password = self.hash_password(password)
        self.cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close_database(self):
        self.conn.close()

class HostelApp:
    def __init__(self, root, total_rooms):
        self.root = root
        self.hostel = Hostel(total_rooms)
        self.show_initial_screen()

    def show_initial_screen(self):
        self.clear_interface()
        tk.Label(self.root, text="Hostel Room Booking System", font=("Helvetica", 16, "bold"), fg="blue").pack(pady=10)
        tk.Button(self.root, text="User Login", command=self.show_user_login_screen, bg="lightblue").pack(pady=5)
        tk.Button(self.root, text="Admin Login", command=self.show_admin_login_screen, bg="lightgreen").pack(pady=5)
        tk.Button(self.root, text="Register", command=self.show_register_screen, bg="orange").pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.close_app, bg="red", fg="white").pack(pady=5)

    def show_user_login_screen(self):
        self.clear_interface()
        tk.Label(self.root, text="User Login", font=("Helvetica", 14, "bold"), fg="darkblue").pack()
        self.create_login_fields(self.handle_user_login)

    def show_admin_login_screen(self):
        self.clear_interface()
        tk.Label(self.root, text="Admin Login", font=("Helvetica", 14, "bold"), fg="darkred").pack()
        self.create_login_fields(self.handle_admin_login)

    def create_login_fields(self, login_command):
        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        tk.Button(self.root, text="Login", command=login_command, bg="lightblue").pack(pady=5)
        tk.Button(self.root, text="Back", command=self.show_initial_screen, bg="gray").pack(pady=5)

    def show_register_screen(self):
        self.clear_interface()
        tk.Label(self.root, text="Register", font=("Helvetica", 14, "bold"), fg="darkgreen").pack()
        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        tk.Label(self.root, text="Role (admin/user):").pack()
        self.role_entry = tk.Entry(self.root)
        self.role_entry.pack()
        tk.Button(self.root, text="Register", command=self.handle_register, bg="lightgreen").pack(pady=5)
        tk.Button(self.root, text="Back", command=self.show_initial_screen, bg="gray").pack(pady=5)

    def handle_user_login(self):
        self.authenticate('user')

    def handle_admin_login(self):
        self.authenticate('admin')

    def authenticate(self, required_role):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.hostel.authenticate_user(username, password)
        if role == required_role:
            if role == 'admin':
                self.setup_admin_interface()
            else:
                self.setup_user_interface()
        else:
            messagebox.showerror("Login Failed", f"Invalid {required_role} credentials.")

    def handle_register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_entry.get().lower()
        message = self.hostel.register_user(username, password, role)
        messagebox.showinfo("Registration", message)

    def setup_admin_interface(self):
        self.clear_interface()
        tk.Label(self.root, text="Admin Interface", font=("Helvetica", 14, "bold"), fg="darkred").pack()
        tk.Button(self.root, text="Show All Room Statuses", command=self.show_all_statuses, bg="lightblue").pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.close_app, bg="red", fg="white").pack(pady=5)

    def setup_user_interface(self):
        self.clear_interface()
        tk.Label(self.root, text="User Interface", font=("Helvetica", 14, "bold"), fg="darkblue").pack()
        tk.Label(self.root, text="Room Number:").pack()
        self.room_entry = tk.Entry(self.root)
        self.room_entry.pack()
        tk.Label(self.root, text="Occupant's Name:").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()
        tk.Button(self.root, text="Submit Booking", command=self.book_room, bg="lightgreen").pack(pady=5)
        tk.Button(self.root, text="Cancel Booking", command=self.cancel_booking, bg="orange").pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.close_app, bg="red", fg="white").pack(pady=5)

    def show_all_statuses(self):
        status_window = tk.Toplevel(self.root)
        status_window.title("Room Statuses")
        status_display = scrolledtext.ScrolledText(status_window, width=40, height=15)
        status_display.pack()
        statuses = [room.status() for room in self.hostel.rooms]
        status_display.insert(tk.END, "\n".join(statuses))
        status_display.configure(state='disabled')

    def book_room(self):
        room_number = self.room_entry.get()
        occupant_name = self.name_entry.get()
        if room_number.isdigit() and 1 <= int(room_number) <= len(self.hostel.rooms):
            message = self.hostel.rooms[int(room_number) - 1].book(occupant_name)
            messagebox.showinfo("Booking Status", message)
        else:
            messagebox.showerror("Error", "Invalid room number or name.")

    def cancel_booking(self):
        room_number = self.room_entry.get()
        if room_number.isdigit() and 1 <= int(room_number) <= len(self.hostel.rooms):
            message = self.hostel.rooms[int(room_number) - 1].cancel()
            messagebox.showinfo("Cancellation Status", message)
        else:
            messagebox.showerror("Error", "Invalid room number.")

    def clear_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def close_app(self):
        self.hostel.close_database()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hostel Room Booking System")
    app = HostelApp(root, total_rooms=10)
    root.mainloop()
    