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
    # root.configure(bg='blue')


mods_tree = None
old_checked_and_children = []


def tick():
    for i, checked_and_children in enumerate(old_checked_and_children):
        checked = len(mods_tree.get_checked(str(i)))
        children = len(mods_tree.get_children(str(i)))
        if checked_and_children[0] != checked or checked_and_children[1] != children:
            mods_tree.item(str(i), text=f"category{i+1} ({checked}/{children})")
            checked_and_children[0] = checked
            checked_and_children[1] = children
    root.after(100, tick)


root = tk.Tk()

if __name__ == "__main__":
    main_gui()
    mods_tree = gui_elements.get_mods_tree()
    old_checked_and_children = [[len(mods_tree.get_checked('0')), len(mods_tree.get_children('0'))]]
    tick()
    root.mainloop()
