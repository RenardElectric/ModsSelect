# -*- coding: utf-8 -*-
"""
Author: RenardElectric
License: GNU GPLv3
Source: ModsSelect
"""

import tkinter as tk

import darkdetect
import ntkutils
import sv_ttk

import gui_elements


def main_gui():
    root.title(" Pythonista Planet Desktop App ")
    # root.resizable(False, False)
    # root.geometry("500x500")
    # root.attributes('-topmost', True)

    if darkdetect.theme() == "Dark":
        sv_ttk.set_theme("dark")
        ntkutils.dark_title_bar(root)
        # bg_color = ttk.Style().lookup(".", "background")
        # root.wm_attributes("-transparent", "blue")
        # HWND = int(root.frame(), base=16)
        # mc.ApplyMica(HWND, mc.MICAMODE.DARK)
    else:
        gui_elements.light_title_bar(root)
        sv_ttk.set_theme("light")
        # bg_color = ttk.Style().lookup(".", "background")
        # root.wm_attributes("-transparent", bg_color)
        # HWND = int(root.frame(), base=16)
        # mc.ApplyMica(HWND, mc.MICAMODE.LIGHT)

    root.update()

    gui_elements.App(root).pack(expand=True, fill="both", padx=15, pady=15)

    root.update()

    ntkutils.placeappincenter(root)

root = tk.Tk()

if __name__ == "__main__":
    main_gui()
    root.mainloop()
