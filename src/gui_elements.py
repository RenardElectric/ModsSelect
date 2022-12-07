# -*- coding: utf-8 -*-
"""
Author: RenardElectric
License: GNU GPLv3
Source: ModsSelect
"""

import ctypes
import os
import threading
import tkinter
import tkinter as tk
from tkinter import ttk

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

        self.fabric_versions = API.get_list("config/fabric_versions.json")
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
                                                    values=self.fabric_versions, width=5)
        self.minecraft_version_combo.pack()
        self.minecraft_version_combo.current(0)
        self.minecraft_version_combo.bind('<<ComboboxSelected>>', self.change_minecraft_version)

        self.minecraft_loader_combo = ttk.Combobox(self.mods_version_label, state="readonly",
                                                   values=["fabric", "forge"], width=5)
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
        commands.update_button["state"] = "disabled"
        commands.download_button["state"] = "disabled"

        mod_list = API.get_list("config/mods.json")

        inputs = []

        for mod in mod_list:
            inputs.append(([mod["name"], API.get_mod_site(mod["name"], tools.get_minecraft_version(), tools.get_minecraft_loader())], tools.get_minecraft_version()))

        mod_name_list = []
        mod_name_and_version_list = []

        for item in mods_tree.get_children("0"):
            mods_tree.delete(item)

        for result in parallel_API.get_latest_mods_info_separated_parallel(inputs):
            mod_name_list.append(result[5][0])
            mod_name_and_version_list.append([result[5][0], result[2]])

        mod_name_list_sorted = sorted(mod_name_list)

        index = 1
        for mod in mod_name_list_sorted:
            for mod_and_version in mod_name_and_version_list:
                if mod_and_version[0] == mod and mod_and_version[1] is not None:
                    mods_tree.insert(parent="0", index="end", iid=index, text=mod_and_version[0],
                                     values=mod_and_version[1])
                    index += 1

        commands.download_button["state"] = "enabled"
        commands.update_button["state"] = "enabled"
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

        mods_tree.heading('#0', text='Mod Name')
        mods_tree.heading('mod_latest_version', text='Mod Latest Version')

        mods_tree.column("#0", anchor="w", width=300)
        mods_tree.column("mod_latest_version", anchor="w")

        mods_tree.insert(parent="", index="end", iid="0", text="Selected Mods")

        mods_tree.item("0", open=True)

        mods_tree.set_selection("0")

        mods_tree.insert(parent="0", index="end", iid="1", text="initializing")

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

    def update_tree(self):
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

        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)
        # Commands(self).grid(row=0, column=0, padx=10, pady=(10, 0), sticky="new")
        # Tree(self).grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")
        Commands(self).pack(fill="x")
        ModsList(self).pack(pady=(10, 0), side="right", fill="y")
        Mods(self).pack(padx=(0, 10), pady=(10, 0), expand=True, fill="both")
        # self.configure(bg='blue')

        self.root = root

    def change_theme(self):
        sv_ttk.toggle_theme()
        self.set_title_bar()
        get_mods_list_tree().update_theme()
        get_mods_tree().update_theme()
        # bg_color = ttk.Style().lookup(".", "background")
        # self.root.wm_attributes("-transparent", bg_color)

    def set_title_bar(self):
        if sv_ttk.get_theme() == "dark":
            ntkutils.dark_title_bar(self.root)
        else:
            light_title_bar(self.root)
