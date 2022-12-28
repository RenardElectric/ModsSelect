# -*- coding: utf-8 -*-
"""
Author: RenardElectric
License: GNU GPLv3
Source: ModsSelect
"""

import json
import os
import tkinter as tk

import ntkutils

import gui_elements
import tools


def main_gui():
    root.title(" ModsSelect ")
    root.geometry("890x825")
    # root.resizable(False, False)
    # root.attributes('-topmost', True)

    gui_elements.App(root).pack(expand=True, fill="both", padx=15, pady=15)

    root.update()

    ntkutils.placeappincenter(root)


root = tk.Tk()

if __name__ == "__main__":
    with open("config/minecraft_versions.json", "r", encoding="UTF-8") as file:
        tools.minecraft_versions = json.loads(file.read())

    mod_names = []

    for file in os.listdir("config/mods"):
        with open(f"config/mods/{file}", "r") as mods:
            mods = json.loads(mods.read())
            for mod in mods:
                if mod["name"] not in mod_names:
                    tools.mods_list.append(mod)
                    mod_names.append(mod["name"])

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
        # json_object = json.dumps(tools.mods_list, indent=4)
        for file in os.listdir("config/mods"):
            mods_list = []
            with open(f"config/mods/{file}", "r") as mods:
                mods = json.loads(mods.read())
                for mod in mods:
                    for mod_info in tools.mods_list:
                        if mod["name"] == mod_info["name"]:
                            mods_list.append(mod_info)
            with open(f"config/mods/{file}", "w") as outfile:
                outfile.write(json.dumps(mods_list, indent=4))
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
