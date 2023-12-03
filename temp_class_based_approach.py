import tkinter as tk
from pynput import mouse
from tkinter import filedialog

import pyautogui
import time
import random
import threading
import json

from keyboard_listener import StopFlag, start_keyboard_listener
from config import (
    HELP_TEXT,
    default_iteration_count,
    default_sleep_between_lists_time,
    default_sleep_time,
)


class PySmashApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("pySMASH")
        self.root.attributes("-topmost", True)

        self.list_of_list_of_coords = []
        self.current_list_of_coords = []

        self.stop_flag = StopFlag()

        self.setup_ui()
        start_keyboard_listener(self.root, self.stop_flag, self.status_label)

    def setup_ui(self):
        self.help_button = tk.Button(
            self.root,
            text="? Help ?",
            command=self.show_help,
            width=20,
            height=1,
            bg="light yellow",
        )
        self.help_button.grid(row=0, columnspan=2, pady=(5, 5))

        tk.Label(self.root, text="Sleep Time between clicks (sec):").grid(row=1)
        self.sleep_time_entry = tk.Entry(self.root)
        self.sleep_time_entry.grid(row=1, column=1)
        self.sleep_time_entry.insert(0, default_sleep_time)

        tk.Label(self.root, text="Sleep Time between lists (sec): ").grid(row=2)
        self.sleep_between_lists_entry = tk.Entry(self.root)
        self.sleep_between_lists_entry.grid(row=2, column=1)
        self.sleep_between_lists_entry.insert(0, default_sleep_between_lists_time)

        tk.Label(self.root, text="Iteration Count: ").grid(row=3)
        self.iteration_count_entry = tk.Entry(self.root)
        self.iteration_count_entry.grid(row=3, column=1)
        self.iteration_count_entry.insert(0, default_iteration_count)

        self.use_random_order_var = tk.IntVar()
        self.use_random_order_checkbox = tk.Checkbutton(
            self.root, text="Use Random Order", variable=self.use_random_order_var
        )
        self.use_random_order_checkbox.grid(row=4, columnspan=2)

        self.capture_button = tk.Button(
            self.root,
            text="Capture Clicks",
            command=self.start_capturing,
            width=20,
            height=2,
            bg="light blue",
        )
        self.capture_button.grid(row=5, columnspan=2, pady=(10, 5))

        self.coord_display = tk.Listbox(self.root, height=10, width=50)
        self.coord_display.grid(row=6, columnspan=2)

        if not self.list_of_list_of_coords:
            self.start_button_state = "disabled"
        else:
            self.start_button_state = "normal"

        self.start_button = tk.Button(
            self.root,
            text="Start Clicking",
            command=lambda: self.click_sequence_handler(),
            width=20,
            height=2,
            state=self.start_button_state,
            bg="light green",
        )
        self.start_button.grid(row=7, columnspan=2, pady=(10, 0))

        self.delete_button = tk.Button(
            self.root,
            text="Delete Selected Set",
            command=self.delete_selected_set,
            width=20,
            height=1,
            bg="light pink",
        )
        self.delete_button.grid(row=10, columnspan=2, pady=(10, 5))

        self.save_config = tk.Button(
            self.root,
            text="Save Config",
            width=20,
            height=1,
            bg="light yellow",
            command=self.save_configuration,
        )
        self.save_config.grid(row=11, column=0, pady=(10, 5), padx=(5, 5))

        self.load_config = tk.Button(
            self.root,
            text="Load Config",
            width=20,
            height=1,
            bg="light yellow",
            command=self.load_configuration,
        )
        self.load_config.grid(row=11, column=1, pady=(10, 5), padx=(5, 5))

        self.status_label = tk.Label(self.root, text="")
        self.status_label.grid(row=12, columnspan=2)

    def on_click(self, x, y, button, pressed):
        """
        Handles saving clicks to the list_of_coords during capture_clicks.
        Each left click appends to current_list_of_coords,
        A right click will append that current_list_of_coords
            to list_of_list_of_coords and exit after cleanup.
        """
        if button == mouse.Button.left and pressed:
            self.current_list_of_coords.append((x, y))
        elif button == mouse.Button.right and not pressed:
            if self.current_list_of_coords:
                self.list_of_list_of_coords.append(self.current_list_of_coords.copy())
                self.current_list_of_coords.clear()
                self.update_coord_display()
            return False

    def capture_clicks(self):
        """Creates a mouseclick listener."""
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    def start_capturing(self):
        "Creates a new thread for capturing click events."
        capture_thread = threading.Thread(target=self.capture_clicks)
        capture_thread.start()

    def update_coord_display(self):
        """
        Handles updating the coordinate display.
        Throws the whole "display set" away and rebuilds it when called.
        Also handles updating the start_button's state.
        """
        self.coord_display.delete(0, tk.END)
        for i, coord_set in enumerate(self.list_of_list_of_coords):
            self.coord_display.insert(tk.END, f"Set {i+1}: {coord_set}\n")
        self.start_button["state"] = (
            "normal" if self.list_of_list_of_coords else "disabled"
        )

    def delete_selected_set(self):
        """Removes a given list from the list of list of coordinates."""
        selected_index = self.coord_display.curselection()
        if selected_index:
            self.list_of_list_of_coords.pop(selected_index[0])
            self.update_coord_display()

    def click_coordinates(self, coordinates, sleep_time):
        """
        Given a list of (x,y) coord pair, clicks the locations on the screen.
        Waits for the determined sleep_time betwen clicks.
        """
        try:
            for x, y in coordinates:
                if self.stop_flag.stop_requested:
                    return False
                pyautogui.click(x, y)
                time.sleep(sleep_time)
        except pyautogui.FailSafeException:
            self.status_label.config(text="pyAutoGui Failsafe triggered. Stopping.")
            return False
        return True

    def handle_multi_list(
        self,
        sleep_time: float,
        sleep_between_lists_time: float,
        current_index: int = 0,
    ):
        """
        Manages the "click order" for a given list_of_coords.
        If use_random_order, randomly picks a list_of_coords from the list of lists.
        If not, runs through the entries sequentially.
        """
        if self.use_random_order:
            selected = random.choice(self.list_of_list_of_coords)
        else:
            selected = self.list_of_list_of_coords[current_index]
        click_result = self.click_coordinates(selected, sleep_time)
        time.sleep(sleep_between_lists_time)
        return click_result

    def click_sequence_handler(self):
        """
        Main function for click sequence.
        Reads in user options and iterates over the coord list(s).
        """
        self.stop_flag.stop_requested = False
        self.status_label.config(text="Running click sequence...")
        self.root.update()
        self.root.update_idletasks()

        if not self.list_of_list_of_coords:
            self.status_label.config(
                text="No Coord sets available. \nPlease capture coords or finish current set."
            )
            return
        try:
            sleep_time = float(self.sleep_time_entry.get())
            sleep_between_lists_time = float(self.sleep_between_lists_entry.get())
            iteration_count = int(self.iteration_count_entry.get())
            use_random_order = self.use_random_order_var.get() == 1

            for i in range(iteration_count):
                self.status_label.config(
                    text=f"Running click sequence {i + 1} of {iteration_count}."
                )
                self.root.update()
                self.root.update_idletasks()

                if use_random_order:
                    for _ in self.list_of_list_of_coords:
                        if not self.handle_multi_list(
                            sleep_time,
                            sleep_between_lists_time,
                            use_random_order,
                        ):
                            return
                else:
                    for j in range(len(self.list_of_list_of_coords)):
                        if not self.handle_multi_list(
                            sleep_time,
                            sleep_between_lists_time,
                            use_random_order,
                            j,
                        ):
                            return

            self.status_label.config(text="Finished clicking.")
            self.root.update()
            self.root.update_idletasks()
        except ValueError:
            self.status_label.config(
                text="Invalid entries. Please check and try again."
            )
            self.root.update()
            self.root.update_idletasks()
        except SyntaxError:
            self.status_label.config(text="Invalid coords. Please check and try again.")
            self.root.update()
            self.root.update_idletasks()

    def save_configuration(self) -> None:
        """
        Save configuration in json format.
        Prompts a dialogue to create a new file.
        """
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if filename:
            config = {
                "list_of_list_of_coords": self.list_of_list_of_coords,
                "sleep_time": self.sleep_time_entry.get(),
                "sleep_between_lists_time": self.sleep_between_lists_entry.get(),
                "iteration_count": self.iteration_count_entry.get(),
            }
            with open(filename, "w") as config_file:
                json.dump(config, config_file, indent=4)

    def load_configuration(self, filename="config.json"):
        """
        Prompt dialogue to load user configuration.
        Loads json file as dict.
        """
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, "r") as config_file:
                    config = json.load(config_file)

                    self.list_of_list_of_coords = config["list_of_list_of_coords"]
                    self.sleep_time_entry.delete(0, tk.END)
                    self.sleep_time_entry.insert(0, config["sleep_time"])
                    self.sleep_between_lists_entry.delete(0, tk.END)
                    self.sleep_between_lists_entry.insert(
                        0, config["sleep_between_lists_time"]
                    )
                    self.iteration_count_entry.delete(0, tk.END)
                    self.iteration_count_entry.insert(0, config["iteration_count"])
                    self.update_coord_display()
                    self.start_button["state"] = (
                        "normal" if self.list_of_list_of_coords else "disabled"
                    )
            except (FileNotFoundError, json.JSONDecodeError):
                self.status_label.config(
                    text="Config File not found or invalid. Loading default values."
                )

    def show_help(self):
        """Creates a top level help window. Shows help text (found in config.py)"""
        self.help_window = tk.Toplevel(self.root)
        self.help_window.title("pySMASH Help")
        self.help_window.geometry("400x750")

        help_text = HELP_TEXT
        tk.Label(
            self.help_window, text=help_text, justify=tk.LEFT, wraplength=380
        ).pack(padx=10, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = PySmashApp(root)
    root.mainloop()
