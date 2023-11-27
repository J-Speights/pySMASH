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


list_of_list_of_coords = []
current_list_of_coords = []


def on_click(x, y, button, pressed):
    """
    Handles saving clicks to the list_of_coords during capture_clicks.
    Each left click appends to current_list_of_coords,
    A right click will append that current_list_of_coords
        to list_of_list_of_coords and exit after cleanup.
    """
    global list_of_list_of_coords, current_list_of_coords
    if button == mouse.Button.left and pressed:
        current_list_of_coords.append((x, y))
    elif button == mouse.Button.right and not pressed:
        if current_list_of_coords:
            list_of_list_of_coords.append(current_list_of_coords.copy())
            current_list_of_coords.clear()
            update_coord_display()
        return False


def capture_clicks():
    """Creates a mouseclick listener."""
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()


def start_capturing():
    "Creates a new thread for capturing click events."
    capture_thread = threading.Thread(target=capture_clicks)
    capture_thread.start()


def update_coord_display():
    """
    Handles updating the coordinate display.
    Throws the whole "display set" away and rebuilds it when called.
    """
    coord_display.delete(0, tk.END)
    for i, coord_set in enumerate(list_of_list_of_coords):
        coord_display.insert(tk.END, f"Set {i+1}: {coord_set}\n")


def delete_selected_set():
    """Removes a given list from the list of list of coordinates."""
    selected_index = coord_display.curselection()
    if selected_index:
        list_of_list_of_coords.pop(selected_index[0])
        update_coord_display()


def click_coordinates(coordinates, sleep_time, stop_flag: StopFlag):
    """
    Given a list of (x,y) coord pair, clicks the locations on the screen.
    Waits for the determined sleep_time betwen clicks.
    """
    try:
        for x, y in coordinates:
            if stop_flag.stop_requested:
                return False
            pyautogui.click(x, y)
            time.sleep(sleep_time)
    except pyautogui.FailSafeException:
        status_label.config(text="pyAutoGui Failsafe triggered. Stopping.")
        return False
    return True


def handle_multi_list(
    list_of_list_of_coords: list[list[int]],
    sleep_time: float,
    sleep_between_lists_time: float,
    stop_flag: StopFlag,
    use_random_order: bool,
    current_index: int = 0,
):
    """
    Manages the "click order" for a given list_of_coords.
    If use_random_order, randomly picks a list_of_coords from the list of lists.
    If not, runs through the entries sequentially.
    """
    if use_random_order:
        selected = random.choice(list_of_list_of_coords)
    else:
        selected = list_of_list_of_coords[current_index]
    click_result = click_coordinates(selected, sleep_time, stop_flag)
    time.sleep(sleep_between_lists_time)
    return click_result


def click_sequence_handler(
    stop_flag: StopFlag,
):
    """
    Main function for click sequence.
    Reads in user options and iterates over the coord list(s).
    """
    stop_flag.stop_requested = False
    status_label.config(text="Running click sequence...")
    root.update()
    root.update_idletasks()

    if not list_of_list_of_coords:
        status_label.config(
            text="No Coord sets available. \nPlease capture coords or finish current set."
        )
        return
    try:
        sleep_time = float(sleep_time_entry.get())
        sleep_between_lists_time = float(sleep_between_lists_entry.get())
        iteration_count = int(iteration_count_entry.get())
        use_random_order = use_random_order_var.get() == 1

        for i in range(iteration_count):
            status_label.config(
                text=f"Running click sequence {i + 1} of {iteration_count}."
            )
            root.update()
            root.update_idletasks()

            if use_random_order:
                for _ in list_of_list_of_coords:
                    if not handle_multi_list(
                        list_of_list_of_coords,
                        sleep_time,
                        sleep_between_lists_time,
                        stop_flag,
                        use_random_order,
                    ):
                        return
            else:
                for j in range(len(list_of_list_of_coords)):
                    if not handle_multi_list(
                        list_of_list_of_coords,
                        sleep_time,
                        sleep_between_lists_time,
                        stop_flag,
                        use_random_order,
                        j,
                    ):
                        return

        status_label.config(text="Finished clicking.")
        root.update()
        root.update_idletasks()
    except ValueError:
        status_label.config(text="Invalid entries. Please check and try again.")
        root.update()
        root.update_idletasks()
    except SyntaxError:
        status_label.config(text="Invalid coords. Please check and try again.")
        root.update()
        root.update_idletasks()


def save_configuration() -> None:
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
            "list_of_list_of_coords": list_of_list_of_coords,
            "sleep_time": sleep_time_entry.get(),
            "sleep_between_lists_time": sleep_between_lists_entry.get(),
            "iteration_count": iteration_count_entry.get(),
        }
        with open(filename, "w") as config_file:
            json.dump(config, config_file, indent=4)


def load_configuration(filename="config.json"):
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
                global list_of_list_of_coords

                list_of_list_of_coords = config["list_of_list_of_coords"]
                sleep_time_entry.delete(0, tk.END)
                sleep_time_entry.insert(0, config["sleep_time"])
                sleep_between_lists_entry.delete(0, tk.END)
                sleep_between_lists_entry.insert(0, config["sleep_between_lists_time"])
                iteration_count_entry.delete(0, tk.END)
                iteration_count_entry.insert(0, config["iteration_count"])
                update_coord_display()
        except (FileNotFoundError, json.JSONDecodeError):
            status_label.config(
                text="Config File not found or invalid. Loading default values."
            )


def show_help():
    """Creates a top level help window. Shows help text (found in config.py)"""
    help_window = tk.Toplevel(root)
    help_window.title("pySMASH Help")
    help_window.geometry("400x750")

    help_text = HELP_TEXT
    tk.Label(help_window, text=help_text, justify=tk.LEFT, wraplength=380).pack(
        padx=10, pady=10
    )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("pySMASH")
    root.attributes("-topmost", True)

    stop_flag = StopFlag()

    help_button = tk.Button(
        root, text="? Help ?", command=show_help, width=20, height=1, bg="light yellow"
    )
    help_button.grid(row=0, columnspan=2, pady=(5, 5))

    tk.Label(root, text="Sleep Time between clicks (sec):").grid(row=1)
    sleep_time_entry = tk.Entry(root)
    sleep_time_entry.grid(row=1, column=1)
    sleep_time_entry.insert(0, default_sleep_time)

    tk.Label(root, text="Sleep Time between lists (sec): ").grid(row=2)
    sleep_between_lists_entry = tk.Entry(root)
    sleep_between_lists_entry.grid(row=2, column=1)
    sleep_between_lists_entry.insert(0, default_sleep_between_lists_time)

    tk.Label(root, text="Iteration Count: ").grid(row=3)
    iteration_count_entry = tk.Entry(root)
    iteration_count_entry.grid(row=3, column=1)
    iteration_count_entry.insert(0, default_iteration_count)

    use_random_order_var = tk.IntVar()
    use_random_order_checkbox = tk.Checkbutton(
        root, text="Use Random Order", variable=use_random_order_var
    )
    use_random_order_checkbox.grid(row=4, columnspan=2)

    capture_button = tk.Button(
        root,
        text="Capture Clicks",
        command=start_capturing,
        width=20,
        height=2,
        bg="light blue",
    )
    capture_button.grid(row=5, columnspan=2, pady=(10, 5))

    coord_display = tk.Listbox(root, height=10, width=50)
    coord_display.grid(row=6, columnspan=2)

    start_button = tk.Button(
        root,
        text="Start Clicking",
        command=lambda: click_sequence_handler(stop_flag),
        width=20,
        height=2,
        bg="light green",
    )
    start_button.grid(row=7, columnspan=2, pady=(10, 0))

    delete_button = tk.Button(
        root,
        text="Delete Selected Set",
        command=delete_selected_set,
        width=20,
        height=1,
        bg="light pink",
    )
    delete_button.grid(row=10, columnspan=2, pady=(10, 5))

    save_config = tk.Button(
        root,
        text="Save Config",
        width=20,
        height=1,
        bg="light yellow",
        command=save_configuration,
    )
    save_config.grid(row=11, column=0, pady=(10, 5), padx=(5, 5))

    load_config = tk.Button(
        root,
        text="Load Config",
        width=20,
        height=1,
        bg="light yellow",
        command=load_configuration,
    )
    load_config.grid(row=11, column=1, pady=(10, 5), padx=(5, 5))

    status_label = tk.Label(root, text="")
    status_label.grid(row=12, columnspan=2)

    start_keyboard_listener(root, stop_flag, status_label)

    root.mainloop()
