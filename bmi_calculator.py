
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import math
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# -------------------- DATABASE --------------------

DB_NAME = "bmi_records.db"


def initialize_database():
    """Create the database and records table if they do not exist."""
    try:
        with sqlite3.connect(DB_NAME, timeout=5) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    record_date TEXT NOT NULL
                )
            """)
        return True

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not initialize the database:\n{error}"
        )
        return False


# -------------------- BMI CALCULATIONS --------------------

def calculate_bmi(weight, height):
    """Calculate BMI and return its category."""
    bmi = weight / (height ** 2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return bmi, category


def get_category_color(category):
    """Return a color for each BMI category."""
    colors = {
        "Underweight": "#2878B5",
        "Normal": "#16803C",
        "Overweight": "#D97706",
        "Obese": "#DC2626"
    }
    return colors.get(category, "#333333")


# -------------------- DATABASE OPERATIONS --------------------

def save_record(username, weight, height, bmi, category):
    """Save a BMI record in SQLite."""
    try:
        with sqlite3.connect(DB_NAME, timeout=5) as conn:
            conn.execute("""
                INSERT INTO bmi_records
                (username, weight, height, bmi, category, record_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                username,
                weight,
                height,
                bmi,
                category,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        return True

    except (sqlite3.Error, OSError) as error:
        messagebox.showerror(
            "Save Error",
            f"Could not save the BMI record:\n{error}"
        )
        return False


def get_user_records(username):
    """Fetch all records for one user."""
    try:
        with sqlite3.connect(DB_NAME, timeout=5) as conn:
            return conn.execute("""
                SELECT id, username, weight, height,
                       bmi, category, record_date
                FROM bmi_records
                WHERE username = ?
                ORDER BY record_date DESC, id DESC
            """, (username,)).fetchall()

    except (sqlite3.Error, OSError) as error:
        messagebox.showerror(
            "Read Error",
            f"Could not read BMI records:\n{error}"
        )
        return None


def get_all_usernames():
    """Return saved usernames for the dropdown."""
    try:
        with sqlite3.connect(DB_NAME, timeout=5) as conn:
            rows = conn.execute("""
                SELECT DISTINCT username
                FROM bmi_records
                ORDER BY username COLLATE NOCASE
            """).fetchall()
        return [row[0] for row in rows]

    except (sqlite3.Error, OSError) as error:
        messagebox.showerror(
            "Database Error",
            f"Could not load users:\n{error}"
        )
        return None


# -------------------- GUI APPLICATION --------------------

class BMICalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator - Health Tracker")
        self.root.geometry("920x720")
        self.root.minsize(760, 620)
        self.root.configure(bg="#F3F6FB")

        self.last_bmi = None
        self.last_category = None

        self.setup_styles()
        self.create_widgets()
        self.refresh_users()

    def setup_styles(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            rowheight=27,
            font=("Arial", 9)
        )
        style.configure(
            "Treeview.Heading",
            font=("Arial", 9, "bold")
        )

    def create_widgets(self):
        # Main heading
        heading = tk.Label(
            self.root,
            text="BMI CALCULATOR",
            font=("Arial", 23, "bold"),
            bg="#F3F6FB",
            fg="#183153"
        )
        heading.pack(pady=(15, 3))

        subtitle = tk.Label(
            self.root,
            text="Calculate, save and track your Body Mass Index",
            font=("Arial", 10),
            bg="#F3F6FB",
            fg="#526174"
        )
        subtitle.pack(pady=(0, 12))

        # Input section
        input_frame = tk.LabelFrame(
            self.root,
            text=" Enter Your Details ",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#183153",
            padx=15,
            pady=12
        )
        input_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(
            input_frame,
            text="User Name:",
            bg="white",
            font=("Arial", 10)
        ).grid(row=0, column=0, sticky="w", padx=6, pady=8)

        self.username_var = tk.StringVar()

        self.username_entry = ttk.Entry(
            input_frame,
            textvariable=self.username_var,
            width=25
        )
        self.username_entry.grid(
            row=0, column=1, sticky="ew", padx=6, pady=8
        )

        tk.Label(
            input_frame,
            text="Weight (kg):",
            bg="white",
            font=("Arial", 10)
        ).grid(row=0, column=2, sticky="w", padx=6, pady=8)

        self.weight_var = tk.StringVar()

        ttk.Entry(
            input_frame,
            textvariable=self.weight_var,
            width=15
        ).grid(row=0, column=3, sticky="ew", padx=6, pady=8)

        tk.Label(
            input_frame,
            text="Height (m):",
            bg="white",
            font=("Arial", 10)
        ).grid(row=1, column=0, sticky="w", padx=6, pady=8)

        self.height_var = tk.StringVar()

        ttk.Entry(
            input_frame,
            textvariable=self.height_var,
            width=15
        ).grid(row=1, column=1, sticky="ew", padx=6, pady=8)

        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)

        # Buttons
        button_frame = tk.Frame(self.root, bg="#F3F6FB")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Calculate & Save",
            command=self.calculate_and_save,
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="View History",
            command=self.show_history,
            bg="#475569",
            fg="white",
            activeforeground="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Show BMI Trend",
            command=self.show_trend,
            bg="#16803C",
            fg="white",
            activeforeground="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        # Result section
        result_frame = tk.LabelFrame(
            self.root,
            text=" BMI Result ",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#183153",
            padx=12,
            pady=12
        )
        result_frame.pack(fill="x", padx=20, pady=5)

        self.bmi_label = tk.Label(
            result_frame,
            text="BMI: --",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#183153"
        )
        self.bmi_label.pack(pady=4)

        self.category_label = tk.Label(
            result_frame,
            text="Category: Enter your details",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#526174"
        )
        self.category_label.pack(pady=4)

        self.advice_label = tk.Label(
            result_frame,
            text="BMI is a screening measure, not a diagnosis.",
            font=("Arial", 9),
            bg="white",
            fg="#526174",
            wraplength=750
        )
        self.advice_label.pack(pady=4)

        # User history section
        history_frame = tk.LabelFrame(
            self.root,
            text=" Saved BMI Records ",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#183153",
            padx=8,
            pady=8
        )
        history_frame.pack(
            fill="both", expand=True, padx=20, pady=(5, 15)
        )

        columns = (
            "date", "weight", "height", "bmi", "category"
        )

        self.history_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings",
            height=8
        )

        headings = {
            "date": "Date & Time",
            "weight": "Weight (kg)",
            "height": "Height (m)",
            "bmi": "BMI",
            "category": "Category"
        }

        widths = {
            "date": 190,
            "weight": 100,
            "height": 100,
            "bmi": 90,
            "category": 140
        }

        for col in columns:
            self.history_tree.heading(col, text=headings[col])
            self.history_tree.column(
                col,
                width=widths[col],
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            history_frame,
            orient="vertical",
            command=self.history_tree.yview
        )
        self.history_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.history_tree.pack(
            side="left", fill="both", expand=True
        )
        scrollbar.pack(side="right", fill="y")

    # -------------------- INPUT VALIDATION --------------------

    def validate_inputs(self):
        username = self.username_var.get().strip()
        weight_text = self.weight_var.get().strip()
        height_text = self.height_var.get().strip()

        if not username:
            messagebox.showwarning(
                "Missing Name",
                "Please enter a user name."
            )
            return None

        if len(username) > 100:
            messagebox.showwarning(
                "Invalid Name",
                "User name must be 100 characters or fewer."
            )
            return None

        try:
            weight = float(weight_text)
            height = float(height_text)
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Weight and height must be numeric values."
            )
            return None

        if not math.isfinite(weight) or not math.isfinite(height):
            messagebox.showerror(
                "Invalid Input",
                "Enter finite numbers for weight and height."
            )
            return None

        if weight <= 0 or height <= 0:
            messagebox.showerror(
                "Invalid Input",
                "Weight and height must be greater than zero."
            )
            return None

        # Basic plausibility checks to catch unit mistakes.
        if not 1 <= weight <= 500:
            messagebox.showerror(
                "Invalid Weight",
                "Enter weight in kilograms (1–500 kg)."
            )
            return None

        if not 0.5 <= height <= 2.8:
            messagebox.showerror(
                "Invalid Height",
                "Enter height in metres (0.5–2.8 m)."
            )
            return None

        return username, weight, height

    # -------------------- CALCULATE AND SAVE --------------------

    def calculate_and_save(self):
        values = self.validate_inputs()

        if values is None:
            return

        username, weight, height = values

        bmi, category = calculate_bmi(weight, height)

        self.last_bmi = bmi
        self.last_category = category

        color = get_category_color(category)

        self.bmi_label.config(
            text=f"BMI: {bmi:.2f}",
            fg=color
        )

        self.category_label.config(
            text=f"Category: {category}",
            fg=color
        )

        advice = {
            "Underweight":
                "Consider discussing nutrition and weight with a healthcare professional.",
            "Normal":
                "Your BMI is in the standard adult normal range. Maintain healthy habits.",
            "Overweight":
                "Consider discussing healthy lifestyle changes with a healthcare professional.",
            "Obese":
                "Consider seeking personalised guidance from a healthcare professional."
        }

        self.advice_label.config(
            text=advice[category],
            fg=color
        )

        saved = save_record(
            username, weight, height, bmi, category
        )

        if saved:
            self.refresh_users()
            self.show_history()

            messagebox.showinfo(
                "Success",
                f"BMI calculated and saved!\n\n"
                f"User: {username}\n"
                f"BMI: {bmi:.2f}\n"
                f"Category: {category}"
            )

    # -------------------- USER LIST AND HISTORY --------------------

    def refresh_users(self):
        """Refresh saved usernames while retaining the current name."""
        users = get_all_usernames()

        if users is None:
            return

        current_name = self.username_var.get().strip()

        # The user types directly into the name field.
        # Saved names can be selected using the history window.
        self.saved_users = users

        if current_name:
            self.username_var.set(current_name)

    def show_history(self):
        username = self.username_var.get().strip()

        if not username:
            messagebox.showwarning(
                "Missing Name",
                "Enter a user name to view their history."
            )
            return

        records = get_user_records(username)

        if records is None:
            return

        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        for record in records:
            _, _, weight, height, bmi, category, date = record

            self.history_tree.insert(
                "",
                "end",
                values=(
                    date,
                    f"{weight:.2f}",
                    f"{height:.2f}",
                    f"{bmi:.2f}",
                    category
                ),
                tags=(category,)
            )

        for category in (
            "Underweight", "Normal", "Overweight", "Obese"
        ):
            self.history_tree.tag_configure(
                category,
                foreground=get_category_color(category)
            )

        if not records:
            self.advice_label.config(
                text=f"No saved records found for {username}.",
                fg="#526174"
            )

    # -------------------- BMI TREND GRAPH --------------------

    def show_trend(self):
        username = self.username_var.get().strip()

        if not username:
            messagebox.showwarning(
                "Missing Name",
                "Enter a user name to view the BMI trend."
            )
            return

        records = get_user_records(username)

        if records is None:
            return

        # Records are returned newest first.
        records = list(reversed(records))

        if len(records) < 1:
            messagebox.showinfo(
                "No Data",
                "This user has no saved BMI records yet."
            )
            return

        try:
            dates = [
                datetime.strptime(record[6], "%Y-%m-%d %H:%M:%S")
                for record in records
            ]
            bmis = [record[4] for record in records]

            # A separate graph window.
            graph_window = tk.Toplevel(self.root)
            graph_window.title(f"BMI Trend - {username}")
            graph_window.geometry("800x520")

            fig, ax = plt.subplots(figsize=(8, 4.5))

            ax.plot(
                dates,
                bmis,
                marker="o",
                linewidth=2,
                label="BMI"
            )

            # Standard adult BMI reference lines.
            ax.axhline(
                18.5,
                linestyle="--",
                linewidth=1,
                label="18.5 (Underweight boundary)"
            )
            ax.axhline(
                25,
                linestyle="--",
                linewidth=1,
                label="25 (Overweight boundary)"
            )
            ax.axhline(
                30,
                linestyle="--",
                linewidth=1,
                label="30 (Obesity boundary)"
            )

            ax.set_title(f"BMI Trend for {username}")
            ax.set_xlabel("Date")
            ax.set_ylabel("BMI")
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=8)

            fig.autofmt_xdate()
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(
                fig,
                master=graph_window
            )
            canvas.draw()
            canvas.get_tk_widget().pack(
                fill="both", expand=True
            )

            def close_graph():
                plt.close(fig)
                graph_window.destroy()

            graph_window.protocol(
                "WM_DELETE_WINDOW", close_graph
            )

        except (ValueError, sqlite3.Error, OSError) as error:
            messagebox.showerror(
                "Graph Error",
                f"Could not display the BMI trend:\n{error}"
            )


# -------------------- APPLICATION ENTRY POINT --------------------

def main():
    root = tk.Tk()
    root.withdraw()

    if not initialize_database():
        root.destroy()
        return

    root.deiconify()
    app = BMICalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
