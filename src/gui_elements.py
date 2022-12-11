# -*- coding: utf-8 -*-
"""
Author: RenardElectric
License: GNU GPLv3
Source: ModsSelect
"""

import ctypes
import os
import tkinter
import tkinter as tk
from tkinter import ttk
import threading

import ntkutils
import sv_ttk

import API
import parallel_API
import tools
from CheckboxTreeview import CheckboxTreeview

# mc.debugging = True

mods_list_tree = None
mods_tree = None
commands = None

lock = threading.Lock()


def get_mods_list_tree():
    return mods_list_tree


def get_mods_tree():
    return mods_tree


class Commands(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=15, text="Tools")

        global commands
        commands = self

        self.columnconfigure(0, weight=1)

        self.minecraft_versions = API.get_list("config/minecraft_versions.json")
        self.parent = parent

        self.add_widgets()

    def validation_mods_directory(self):
        return tools.validation_directory(self, "mods_directory")

    def validation_mods_directory_on_return(self, event):
        self.directory_entry.validate()

    def change_minecraft_version(self, event):
        tools.update_minecraft_version(self, self.parent.children.get('!mods'))

    def change_minecraft_loader(self, event):
        tools.update_minecraft_loader(self, self.parent.children.get('!mods'))

    def add_widgets(self):
        self.directory_entry = ttk.Entry(self, validatecommand=self.validation_mods_directory)
        self.directory_entry.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        self.directory_entry.bind('<Return>', self.validation_mods_directory_on_return)

        self.directory_button = ttk.Button(self, text="...", command=lambda: tools.find_directory(self))
        self.directory_button.grid(row=0, column=1, padx=10, pady=(10, 0))

        self.mods_version_label = ttk.Label(self)
        self.mods_version_label.grid(row=0, column=3, padx=(0, 10))

        self.minecraft_version_combo = ttk.Combobox(self.mods_version_label, state="disabled",
                                                    values=self.minecraft_versions, width=5)
        self.minecraft_version_combo.pack()
        self.minecraft_version_combo.current(0)
        self.minecraft_version_combo.bind('<<ComboboxSelected>>', self.change_minecraft_version)

        self.minecraft_loader_combo = ttk.Combobox(self.mods_version_label, state="readonly",
                                                   values=["fabric", "forge", "quilt"], width=5)
        self.minecraft_loader_combo.pack(pady=(10, 0), fill="x")
        self.minecraft_loader_combo.current(0)
        self.minecraft_loader_combo.bind('<<ComboboxSelected>>', self.change_minecraft_loader)

        self.mods_management_label = ttk.Label(self)
        self.mods_management_label.grid(row=0, column=4)

        self.download_button = ttk.Button(self.mods_management_label, text="Download Mods",
                                          command=lambda: threading.Thread(target=tools.download_mods, args=(self,),
                                                                           daemon=True).start()
                                          )
        self.download_button.pack()

        self.delete_button = ttk.Button(self.mods_management_label, text="Delete Mods",
                                        command=lambda: tools.delete_mods(self))
        self.delete_button.pack(pady=(10, 0), fill="x")

        self.update_button = ttk.Button(self, text="Update Mods",
                                        command=lambda: threading.Thread(target=tools.update_mods, args=(self,),
                                                                         daemon=True).start())
        self.update_button.grid(row=0, column=5, padx=10, pady=(10, 0))

        self.switch = ttk.Checkbutton(self, text="Dark theme", style="Switch.TCheckbutton",
                                      variable=tkinter.BooleanVar(self, sv_ttk.get_theme() == "dark"),
                                      command=self.parent.change_theme)
        self.switch.grid(row=0, column=6, columnspan=2, pady=10)

        self.change_minecraft_version("")
        self.change_minecraft_loader("")


class Mods(ttk.LabelFrame):

    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=15, text="Mods")

        self.columnconfigure(1, weight=0)

        self.add_widgets()

    def update_tree(self):

        commands.minecraft_version_combo["state"] = "disabled"
        commands.minecraft_loader_combo["state"] = "disabled"

        mod_list = API.get_list("config/mods.json")
        categories = API.get_list("config/categories.json")

        for i, category in enumerate(categories):
            if mods_tree.get_children(str(i)) is not None:
                for item in mods_tree.get_children(str(i)):
                    mods_tree.delete(item)

        for i, category in enumerate(categories):
            inputs = []

            for mod in mod_list:
                if mod["category"] == category:
                    inputs.append(([mod["name"], API.get_mod_site(mod["name"], tools.get_minecraft_version(), tools.get_minecraft_loader())], tools.get_minecraft_version()))

            mod_name_list = []
            mod_name_and_version_list = []

            if len(inputs) != 0:
                for result in parallel_API.get_latest_mods_info_separated_parallel(inputs):
                    mod_name_list.append(result[5][0])
                    mod_name_and_version_list.append([result[5][0], result[2]])

                mod_name_list_sorted = sorted(mod_name_list)

                index = 3
                for mod in mod_name_list_sorted:
                    for mod_and_version in mod_name_and_version_list:
                        if mod_and_version[0] == mod and mod_and_version[1] is not None:
                            mods_tree.insert(parent=str(i), index="end", iid=len(mods_tree.get_tree_items()), text=mod_and_version[0],
                                             values=mod_and_version[1])
                            if mods_tree.tag_has("checked_focus", str(i)) or mods_tree.tag_has("checked", str(i)):
                                mods_tree.change_state(mods_tree.get_children(str(i))[-1], "checked")
                            index += 1

        commands.minecraft_version_combo["state"] = "readonly"
        commands.minecraft_loader_combo["state"] = "readonly"

    def add_widgets(self):
        global mods_tree

        self.mods_scrollbar = ttk.Scrollbar(self)
        self.mods_scrollbar.pack(side="right", fill="y")

        mods_tree = CheckboxTreeview(
            self,
            columns="mod_latest_version",
            height=11,
            show="tree headings",
            yscrollcommand=self.mods_scrollbar.set
        )
        self.mods_scrollbar.config(command=mods_tree.yview)

        mods_tree.pack(expand=True, fill="both")

        mods_tree.heading('#0', text='Mods (0/0)', command=lambda: mods_tree.check_uncheck_all_tree())
        mods_tree.heading('mod_latest_version', text='Mods Version')

        mods_tree.column("#0", anchor="w", width=300)
        mods_tree.column("mod_latest_version", anchor="w")

        categories = API.get_list("config/categories.json")
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
        directory = tools.get_mods_list_directory()

        if tools.check_directory(directory):
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

    def validation_mods_list_directory(self):
        return tools.validation_directory(self, "mods_list_directory")

    def validation_mods_list_directory_on_return(self, self2):
        self.directory_entry.validate()

    def add_widgets(self):
        global mods_list_tree

        self.directory_label = ttk.Label(self)
        self.directory_label.pack(fill="x")

        self.directory_button = ttk.Button(self.directory_label, text="...", command=lambda: tools.find_directory(self))
        self.directory_button.pack(padx=10, pady=(10, 0), fill="x", side="right")

        self.directory_entry = ttk.Entry(self.directory_label, validatecommand=self.validation_mods_list_directory)
        self.directory_entry.pack(padx=10, pady=(10, 0), fill="x")
        self.directory_entry.bind('<Return>', self.validation_mods_list_directory_on_return)

        self.list_label = ttk.Label(self)
        self.list_label.pack(padx=10, pady=(10, 0), expand=True, fill="y")

        self.mods_list_scrollbar = ttk.Scrollbar(self.list_label)
        self.mods_list_scrollbar.pack(side="right", fill="y")

        mods_list_tree = CheckboxTreeview(self.list_label, height=21, show="tree",
                                          yscrollcommand=self.mods_list_scrollbar.set)
        mods_list_tree.pack(expand=True, fill="y")

        self.mods_list_scrollbar.config(command=mods_list_tree.yview)
        self.list = mods_list_tree

        self.directory_entry.insert(0, f"{os.getcwd()}\\lists".replace('\\', '/'))
        tools.validation_directory(self, "mods_list_directory")

        self.create_list_button = ttk.Button(self, text="Create a new mods list",
                                             command=lambda: tools.save_list_directory(mods_tree, self,
                                                                                       text=f"Save a list with {len(mods_tree.get_checked())} mods as"))
        self.create_list_button.pack(padx=10, pady=(10, 0), fill="x")


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


class App(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        # API.cleat_data()

        Commands(self).pack(fill="x")
        ModsList(self).pack(pady=(10, 0), side="right", fill="y")
        Mods(self).pack(padx=(0, 10), pady=(10, 0), expand=True, fill="both")

        self.root = root

        self.mods = ["Mods", len(mods_tree.get_checked()), len(mods_tree.get_children())]
        self.categories = []
        categories = API.get_list("config/categories.json")
        for index, category in enumerate(categories):
            self.categories.append(
                [category, len(mods_tree.get_checked(str(index))), len(mods_tree.get_children(str(index)))])

        self.tick()

    def change_theme(self):
        sv_ttk.toggle_theme()
        self.set_title_bar()
        get_mods_list_tree().update_theme()
        get_mods_tree().update_theme()

    def set_title_bar(self):
        if sv_ttk.get_theme() == "dark":
            ntkutils.dark_title_bar(self.root)
        else:
            light_title_bar(self.root)

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