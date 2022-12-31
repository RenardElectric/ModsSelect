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


def read_minecraft_versions():
    with open("config/minecraft_versions.json", "r", encoding="UTF-8") as file:
        minecraft_versions = json.loads(file.read())
        for version in minecraft_versions:
            tools.minecraft_versions.append(version[0])
            tools.minecraft_versions_compatible.append(version)


def read_mods():
    mod_names = []
    for file in os.listdir("config/mods"):
        with open(f"config/mods/{file}", "r") as mods:
            mods = json.loads(mods.read())
            for mod in mods:
                if mod["name"] not in mod_names:
                    tools.mods_list.append(mod)
                    mod_names.append(mod["name"])
                else:
                    for mod_info in tools.mods_list:
                        if mod["name"] == mod_info["name"] and mod["categories"] is not None:
                            for category in mod["categories"]:
                                if category not in mod_info["categories"]:
                                    mod_info["categories"].append(category)

    tools.mods_list_length = len(tools.mods_list)

    categories = []
    for mod in tools.mods_list:
        if mod["categories"] is not None:
            for category in mod["categories"]:
                if category not in categories and category is not None:
                    categories.append(category)
    categories.append("Other")
    tools.categories = categories
    tools.categories_length = len(categories)


def read_config():
    try:
        with open(f"config/config.json", "r") as config:
            config = json.loads(config.read())
            if config["mods_directory"] is not None:
                tools.mods_directory = config["mods_directory"]
                tools.minecraft_version = config["minecraft_version"]
                for version_compatible in tools.minecraft_versions_compatible:
                    if version_compatible[0] == tools.minecraft_version:
                        tools.minecraft_version_compatible = version_compatible[1]
                tools.mod_loader = config["mod_loader"]
                tools.allow_compatible_versions = config["allow_compatible_versions"]
                tools.lists_directory = config["lists_directory"]
    except FileNotFoundError:
        with open(f"config/config.json", "w") as file:
            data = {
                "mods_directory": None,
                "minecraft_version": None,
                "mod_loader": None,
                "allow_compatible_versions": None,
                "lists_directory": None
            }
            file.write(json.dumps(data, indent=4))


def main_gui():
    root.title(" ModsSelect ")
    root.geometry("900x850")
    # root.resizable(False, False)
    # root.attributes('-topmost', True)

    gui_elements.Menu(root).pack(fill="x")
    gui_elements.App(root).pack(expand=True, fill="both", padx=15, pady=15)

    root.update()

    ntkutils.placeappincenter(root)


root = tk.Tk()

if __name__ == "__main__":

    read_minecraft_versions()
    read_mods()
    read_config()

    main_gui()

    root.protocol("WM_DELETE_WINDOW", lambda: gui_elements.on_closing(root))
    root.mainloop()
