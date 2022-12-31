# -*- coding: utf-8 -*-
"""
Author: RenardElectric
License: GNU GPLv3
Source: ModsSelect
"""

import ctypes
import json
import os
import threading
import tkinter as tk
from multiprocessing.pool import ThreadPool
from tkinter import ttk

import darkdetect
import ntkutils
import sv_ttk
from tqdm.auto import tqdm
from ttkwidgets.autohidescrollbar import AutoHideScrollbar

import parallel_API
import sun_valley_titlebar
import tools
from AutocompleteEntry import AutocompleteEntry
from CheckboxTreeview import CheckboxTreeview
from Tooltip import Tooltip

mods_list_tree = None
mods_tree = None
mods_menu = None
commands = None
progressbar = None

lock = threading.Lock()


class Commands(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=15, text="Tools")

        global commands
        commands = self

        self.columnconfigure(0, weight=1)

        self.add_widgets()

    def validation_mods_directory_on_return(self, event):
        self.directory_entry.validate()

    def change_minecraft_version(self, event):
        if not tools.minecraft_version == commands.minecraft_version_combo.get():
            tools.minecraft_version = commands.minecraft_version_combo.get()
            for version_compatible in tools.minecraft_versions_compatible:
                if version_compatible[0] == tools.minecraft_version:
                    tools.minecraft_version_compatible = version_compatible[1]
            self.update_tree()

    def change_minecraft_loader(self, event):
        if not tools.mod_loader == commands.minecraft_loader_combo.get():
            tools.mod_loader = commands.minecraft_loader_combo.get()
            self.update_tree()

    def update_tree(self):
        mods_class = self.master.children.get('!mods')
        if mods_class is not None:
            threading.Thread(target=mods_class.update_tree, daemon=True).start()

    def change_environment(self):
        mods_class = self.master.children.get('!mods')
        if mods_class is not None:
            threading.Thread(target=mods_class.update_tree, daemon=True).start()

    def add_widgets(self):
        self.directory_entry = ttk.Entry(self, validatecommand=lambda: tools.validation_directory(self, "mods_directory"))
        self.directory_entry.grid(row=0, column=0, padx=(0, 10), pady=(10, 0), sticky="ew")
        self.directory_entry.bind('<Return>', self.validation_mods_directory_on_return)
        Tooltip(self.directory_entry, text="Write the directory where you want to manage your mods")
        self.directory_entry.insert(0, tools.mods_directory)
        tools.validation_directory(self, "mods_directory")

        self.directory_button = ttk.Button(self, text="...", command=lambda: tools.find_directory(self))
        self.directory_button.grid(row=0, column=1, pady=(10, 0))
        Tooltip(self.directory_button, text="Choose the directory where you want to manage your mods")

        self.mods_version_and_env_label = ttk.Label(self)
        self.mods_version_and_env_label.grid(row=0, column=3, padx=10)

        self.mods_version_label = ttk.Label(self.mods_version_and_env_label)
        self.mods_version_label.grid(row=0)

        self.minecraft_version_combo = ttk.Combobox(self.mods_version_label, state="readonly", values=tools.minecraft_versions, width=5)
        self.minecraft_version_combo.pack()
        self.minecraft_version_combo.set(tools.minecraft_version)
        self.minecraft_version_combo.bind('<<ComboboxSelected>>', self.change_minecraft_version)
        Tooltip(self.minecraft_version_combo, text="Choose the minecraft version in which you want your mods to be on")

        self.minecraft_loader_combo = ttk.Combobox(self.mods_version_label, state="readonly", values=["fabric", "forge", "quilt"], width=5)
        self.minecraft_loader_combo.pack(pady=(10, 0))
        self.minecraft_loader_combo.set(tools.mod_loader)
        self.minecraft_loader_combo.bind('<<ComboboxSelected>>', self.change_minecraft_loader)
        Tooltip(self.minecraft_loader_combo, text="Choose the minecraft mod loader in which you want your mods to be on")

        self.mods_management_label = ttk.Label(self)
        self.mods_management_label.grid(row=0, column=4)

        self.download_button = ttk.Button(self.mods_management_label, text="Download Mods", command=lambda: threading.Thread(target=tools.download_mods, args=(self,), daemon=True).start())
        self.download_button.pack()
        Tooltip(self.download_button, text="Download the mods you selected")

        self.delete_button = ttk.Button(self.mods_management_label, text="Delete Mods", command=tools.delete_mods)
        self.delete_button.pack(pady=(10, 0), fill="x")
        Tooltip(self.delete_button, text="Delete the mods you selected")

        self.update_button = ttk.Button(self, text="Update Mods", command=lambda: threading.Thread(target=tools.update_mods, args=(self,), daemon=True).start())
        self.update_button.grid(row=0, column=5, padx=10, pady=(10, 0))
        Tooltip(self.update_button, text="Update the mods in the selected directory to the minecraft version you chose")

        self.change_minecraft_version("")
        self.change_minecraft_loader("")


class Mods(ttk.LabelFrame):

    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=15, text="Mods")

        self.add_widgets()

    def update_tree(self):
        try:
            commands.minecraft_version_combo["state"] = "disabled"
            commands.minecraft_loader_combo["state"] = "disabled"
        except RuntimeError:
            print("error in Mods.update_tree")

        mods_menu.state("disabled")

        self.autocomplete_entry["state"] = "disabled"

        categories = tools.categories
        args = []
        mods = []
        for i, category in enumerate(categories):
            args.append((category, str(i)))
            if mods_tree.get_children(str(i)) is not None:
                for item in mods_tree.get_children(str(i)):
                    mods_tree.delete(item)
                    mods.append(item)

        print()
        print("\nUpdating mods infos:")
        progressbar.config(maximum=len(tools.mods_list))
        mod_list_sorted = []
        for result in ThreadPool(len(args)).imap_unordered(parallel_API.update_tree_parallel, args):
            if result is not None:
                mod_list_sorted += result
        progressbar.config(value=0)

        print(" "*300)
        print(" "*300)
        print(" "*300)

        progressbar.config(maximum=len(mod_list_sorted))
        for mod in tqdm(mod_list_sorted, desc="Mod tree", unit="mods"):
            mods_tree.insert(parent=mod[2], index="end", iid=len(mods_tree.get_tree_items()),
                             text=mod[0], values=mod[1])
            if mods_tree.tag_has("checked_focus", mod[2]) or mods_tree.tag_has("checked", mod[2]):
                mods_tree.change_state(mods_tree.get_children(mod[2])[-1], "checked")
            progressbar.config(value=progressbar["value"] + 1)
        progressbar.config(value=0)

        mods = []
        for mod in tools.mods_list:
            if mod["name"] not in mods_tree.get_tree_item_names():
                mods.append(mod["name"])
        print(" "*300)
        print(f"{len(mods)} mods are not available for minecraft {tools.minecraft_version} for the {tools.mod_loader} mod loader: {mods}")

        try:
            commands.minecraft_version_combo["state"] = "readonly"
            commands.minecraft_loader_combo["state"] = "readonly"
        except RuntimeError:
            print("error in Mods.update_tree")

        mods_menu.state("normal")

        self.autocomplete_entry["state"] = "normal"
        tree_item_names = mods_tree.get_tree_item_names()
        for category_index in enumerate(categories):
            tree_item_names.remove(mods_tree.item(category_index[0], "text"))
        self.autocomplete_entry.set_completion_list(tree_item_names)

    def validation_mod(self):
        tree_item_names = mods_tree.get_tree_item_names()
        for category_index in enumerate(tools.categories):
            tree_item_names.remove(mods_tree.item(category_index[0], "text"))
        if self.autocomplete_entry.get() in tree_item_names:
            return True
        return False

    def add_widgets(self):
        global mods_tree

        self.autocomplete_entry = AutocompleteEntry(self, completevalues=[], validatecommand=self.validation_mod)
        self.autocomplete_entry.pack(fill="x", pady=(0, 10))
        self.autocomplete_entry.bind('<Return>', self.autocomplete_entry.validate)
        Tooltip(self.autocomplete_entry, text="Search the mod you want to find")

        self.mods_scrollbar = AutoHideScrollbar(self)
        self.mods_scrollbar.pack(side="right", fill="y")

        mods_tree = CheckboxTreeview(
            self,
            columns="mod_latest_version",
            height=11,
            show="tree headings",
            yscrollcommand=self.mods_scrollbar.set
        )
        self.mods_scrollbar.config(command=mods_tree.yview)

        mods_tree.pack(side="left", expand=True, fill="both")

        mods_tree.heading('#0', text='Mods (0/0)', command=mods_tree.check_uncheck_all_tree)
        mods_tree.heading('mod_latest_version', text='Mods Version')

        mods_tree.column("#0", anchor="w", width=300)
        mods_tree.column("mod_latest_version", anchor="w")

        categories = tools.categories
        for index, category in enumerate(categories):
            mods_tree.insert(parent="", index="end", iid=str(index), text=f"{category} (0/0)")

        mods_tree.set_selection("0")

        threading.Thread(target=self.update_tree, daemon=True).start()


class ModsList(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=15, text="Mods Lists")

        self.columnconfigure(0, weight=1)

        self.parent = parent
        self.add_widgets()

    def get_file_name(self, file):
        file_pieces = []
        for index, piece in enumerate(file.split(".")):
            if index != len(file.split(".")):
                file_pieces.append(piece)
        return ".".join(file_pieces)

    def update_tree(self, item_added=None):
        directory = tools.lists_directory

        if tools.check_directory(directory, silence=True):
            selection_iids = mods_list_tree.get_checked()
            selection_names = []
            for iid in selection_iids:
                selection_names.append(mods_list_tree.item(iid, "text"))

            for iid in mods_list_tree.get_children():
                mods_list_tree.delete(iid)

            index = 1
            for file in os.listdir(directory):
                if file.split(".")[-1] == "json":
                    mods_list_tree.insert(parent="", index="end", iid=str(index), text=self.get_file_name(file))
                    index += 1

            if item_added is not None:
                selection_names.append(item_added)
                for iid in mods_list_tree.get_tree_items():
                    if mods_list_tree.item(iid, "text") == item_added:
                        mods_list_tree.selection_set(iid)

            mods_list_tree.check_selection_name(selection_names)

            if mods_tree is not None:
                mods_list_tree.check_uncheck_tree()

    def validation_mods_list_directory_on_return(self, self2):
        self.directory_entry.validate()

    def add_widgets(self):
        global mods_list_tree

        self.directory_label = ttk.Label(self)
        self.directory_label.pack(fill="x", padx=10, pady=(10, 0))

        self.directory_button = ttk.Button(self.directory_label, text="...", command=lambda: tools.find_directory(self))
        self.directory_button.pack(side="right")
        Tooltip(self.directory_button, text="Write the directory where you want to manage your lists of mods")

        self.directory_entry = ttk.Entry(self.directory_label, validatecommand=lambda: tools.validation_directory(self, "mods_list_directory"))
        self.directory_entry.pack(padx=(0, 10), fill="both", expand=True)
        self.directory_entry.bind('<Return>', self.validation_mods_list_directory_on_return)
        Tooltip(self.directory_entry, text="Choose the directory where you want to manage your lists of mods")

        self.list_label = ttk.Label(self)
        self.list_label.pack(padx=10, pady=(10, 0), expand=True, fill="both")

        self.mods_list_scrollbar = AutoHideScrollbar(self.list_label)
        self.mods_list_scrollbar.pack(side="right", fill="y")

        mods_list_tree = CheckboxTreeview(self.list_label, height=0, show="tree",
                                          yscrollcommand=self.mods_list_scrollbar.set)
        mods_list_tree.pack(side="left", expand=True, fill="both")

        self.mods_list_scrollbar.config(command=mods_list_tree.yview)
        self.list = mods_list_tree

        self.directory_entry.insert(0, tools.lists_directory)
        tools.validation_directory(self, "mods_list_directory")

        self.create_list_button = ttk.Button(self, text="Create a new mods list", command=lambda: tools.save_list_directory(mods_tree, self, text=f"Save a list with {len(mods_tree.get_checked())} mods as"))
        self.create_list_button.pack(padx=10, pady=(10, 0), fill="x")
        Tooltip(self.create_list_button, text="Create a nes list of mods")


def change_theme(root):
    sv_ttk.toggle_theme()
    mods_list_tree.update_theme()
    mods_tree.update_theme()
    set_title_bar(root)


def set_title_bar(root):
    if sv_ttk.get_theme() == "dark":
        ntkutils.dark_title_bar(root)
    else:
        light_title_bar(root)


def light_title_bar(window):
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ctypes.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 0x00
    value = ctypes.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ctypes.byref(value), ctypes.sizeof(value))


def on_closing(root):
    for file in os.listdir("config/mods"):
        mods_list = []
        with open(f"config/mods/{file}", "r") as mods:
            mods = json.loads(mods.read())
            for mod in mods:
                for mod_info in tools.mods_list:
                    if mod["name"] == mod_info["name"]:
                        mod["id"] = mod_info["id"]
                        mod["site"] = mod_info["site"]
                        mods_list.append(mod)
        with open(f"config/mods/{file}", "w") as outfile:
            outfile.write(json.dumps(mods_list, indent=4))

    with open(f"config/config.json", "r") as config:
        config = json.loads(config.read())
        config["mods_directory"] = tools.mods_directory
        config["minecraft_version"] = tools.minecraft_version
        config["mod_loader"] = tools.mod_loader
        config["allow_compatible_versions"] = tools.allow_compatible_versions.get()
        config["lists_directory"] = tools.lists_directory
    with open(f"config/config.json", "w") as outfile:
        outfile.write(json.dumps(config, indent=4))

        root.destroy()


class App(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root

        Commands(self).pack(fill="x")
        ModsList(self).pack(pady=(10, 0), side="right", fill="y")
        Mods(self).pack(padx=(0, 20), pady=(10, 0), expand=True, fill="both")

        if darkdetect.theme() == "Dark":
            sv_ttk.set_theme("dark")
            ntkutils.dark_title_bar(root)
        else:
            light_title_bar(root)
            sv_ttk.set_theme("light")
        mods_list_tree.update_theme()
        mods_tree.update_theme()

        self.mods = ["Mods", len(mods_tree.get_checked()), len(mods_tree.get_children())]
        self.categories = []
        categories = tools.categories
        for index, category in enumerate(categories):
            self.categories.append(
                [category, len(mods_tree.get_checked(str(index))), len(mods_tree.get_children(str(index)))])

        self.tick()

    def tick(self):
        checked = len(mods_tree.get_checked())
        children = len(mods_tree.get_children_())
        if self.mods[1] != checked or self.mods[2] != children:
            mods_tree.heading('#0', text=f"{self.mods[0]} ({checked}/{children})")
            self.mods[1] = checked
            self.mods[2] = children

        for i, checked_and_children in enumerate(self.categories):
            checked = len(mods_tree.get_checked(str(i)))
            children = len(mods_tree.get_children(str(i)))
            if checked_and_children[1] != checked or checked_and_children[2] != children:
                mods_tree.item(str(i), text=f"{checked_and_children[0]} ({checked}/{children})")
                checked_and_children[1] = checked
                checked_and_children[2] = children
        self.root.after(1, self.tick)


class Menu(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)

        global progressbar
        progressbar = ttk.Progressbar(self)
        progressbar.pack(fill="x")

        menubar = sun_valley_titlebar.Menubar(self)

        self.options_menu = sun_valley_titlebar.Menu(menubar, "File  ")
        self.options_menu.add_command("Switch Theme", lambda: change_theme(root))
        self.options_menu.add_separator()
        self.options_menu.add_command("Exit", lambda: on_closing(root))

        global mods_menu
        mods_menu = sun_valley_titlebar.Menu(menubar, "Mods  ")
        tools.allow_compatible_versions = tk.BooleanVar(self, tools.allow_compatible_versions)
        mods_menu.add_checkbutton("Allow Compatible Versions", tools.allow_compatible_versions, command=lambda: commands.update_tree())
