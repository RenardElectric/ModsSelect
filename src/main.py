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
import json

import gui_elements
import tools


def main_gui():
    root.title(" ModsSelect ")
    root.geometry("875x825")
    # root.resizable(False, False)
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
    f = open("config/minecraft_versions.json", "r")
    tools.minecraft_versions = json.loads(f.read())
    f.close()

    f = open("config/mods.json", "r")
    tools.mods_list = json.loads(f.read())
    f.close()
    tools.mods_list_length = len(tools.mods_list)

    categories = []
    for mod in tools.mods_list:
        if mod["category"] not in categories and mod["category"] is not None:
            categories.append(mod["category"])
    categories.append("Other")
    tools.categories = categories
    tools.categories_length = len(categories)

    main_gui()

    def on_closing():
        json_object = json.dumps(tools.mods_list, indent=4)
        with open("config/mods.json", "w") as outfile:
            outfile.write(json_object)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
