import tkinter as tk
from pynput import mouse

import pyautogui
import time
import random
import threading

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
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()


def start_capturing():
    capture_thread = threading.Thread(target=capture_clicks)
    capture_thread.start()


def update_coord_display():
    coord_display.delete(0, tk.END)
    for i, coord_set in enumerate(list_of_list_of_coords):
        coord_display.insert(tk.END, f"Set {i+1}: {coord_set}\n")


def delete_selected_set():
    selected_index = coord_display.curselection()
    if selected_index:
        list_of_list_of_coords.pop(selected_index[0])
        update_coord_display()


def click_coordinates(coordinates, sleep_time, stop_flag: StopFlag):
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
    list_of_list_of_coords, sleep_time, sleep_between_lists_time, stop_flag: StopFlag
):
    selected = random.choice(list_of_list_of_coords)
    click_result = click_coordinates(selected, sleep_time, stop_flag)
    time.sleep(sleep_between_lists_time)
    return click_result


def start_clicking(stop_flag: StopFlag):
    stop_flag.stop_requested = False
    status_label.config(text="Running click sequence...")
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

        for i in range(iteration_count):
            status_label.config(
                text=f"Running click sequence {i + 1} of {iteration_count}."
            )
            root.update_idletasks()

            if not handle_multi_list(
                list_of_list_of_coords, sleep_time, sleep_between_lists_time, stop_flag
            ):
                return

        status_label.config(text="Finished clicking.")
    except ValueError:
        print("Invalid entries.")
    except SyntaxError:
        print("Invalid coords.")


def show_help():
    help_window = tk.Toplevel(root)
    help_window.title("pySMASH Help")
    help_window.geometry("400x300")

    help_text = HELP_TEXT
    tk.Label(help_window, text=help_text, justify=tk.LEFT, wraplength=380).pack(
        padx=10, pady=10
    )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("pySMASH")
    root.attributes("-topmost", True)

    stop_flag = StopFlag()

    help_button = tk.Button(root, text="Help", command=show_help)
    help_button.grid(row=0, columnspan=2)

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

    capture_button = tk.Button(root, text="Capture Clicks", command=start_capturing)
    capture_button.grid(row=4, columnspan=2)

    start_button = tk.Button(
        root, text="Start Clicking", command=lambda: start_clicking(stop_flag)
    )
    start_button.grid(row=5, columnspan=2)

    coord_display = tk.Listbox(root, height=10, width=50)
    coord_display.grid(row=6, columnspan=2)

    delete_button = tk.Button(
        root, text="Delete Selected Set", command=delete_selected_set
    )
    delete_button.grid(row=7, columnspan=2)

    status_label = tk.Label(root, text="")
    status_label.grid(row=8, columnspan=2)

    start_keyboard_listener(root, stop_flag, status_label)

    root.mainloop()
