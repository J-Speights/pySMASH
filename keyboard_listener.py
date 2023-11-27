from pynput import keyboard
import tkinter as tk
from typing import Union


class StopFlag:
    def __init__(self):
        self.stop_requested = False


def on_press(
    key: Union[keyboard.Key, keyboard.KeyCode],
    stop_flag: StopFlag,
    status_label: tk.Label,
    root: tk.Tk,
) -> Union[None, bool]:
    if key == keyboard.Key.esc:
        stop_flag.stop_requested = True
        status_label.config(text="User pressed Esc, Stopping...")
        root.update()
        root.update_idletasks()
        return False


def start_keyboard_listener(
    root: tk.Tk, stop_requested: StopFlag, status_label: tk.Label
) -> None:
    listener = keyboard.Listener(
        on_press=lambda key: on_press(key, stop_requested, status_label, root)
    )
    listener.start()
