# -*- coding: utf-8 -*-
"""
Author: RenardElectric
License: GNU GPLv3
Source: ModsSelect
"""

import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import gui_elements
import modsSelector
import API

minecraft_versions = []
minecraft_versions_compatible = []
mods_directory = f"{os.getenv('APPDATA')}/.minecraft/mods".replace('\\', '/')
minecraft_version = "1.19.3"
minecraft_version_compatible = []
mod_loader = "fabric"
allow_compatible_versions = False
lists_directory = f"{os.getcwd()}/lists".replace('\\', '/')
mods_list = []
categories = []
mods_list_length = ""
categories_length = ""


def check_directory(directory, silence=None):
    if not directory == "":
        if os.path.isdir(directory):
            return True
        if silence is None:
            print()
            print("the directory does not exist")
    return False


def check_mods_in_directory(_directory):
    for file in os.listdir(_directory):
        if file.split(".")[-1] == "jar":
            return True
    print()
    print("no mods in this directory")
    return False


def validation_directory(self, directory):
    _directory = self.directory_entry.get()
    if directory == "mods_directory":
        global mods_directory
        mods_directory = _directory
    elif directory == "mods_list_directory":
        global lists_directory
        lists_directory = _directory
        self.update_tree()

    if check_directory(_directory):
        return True
    return False


def find_directory(self):
    global mods_directory
    if str(self.directory_entry.winfo_parent()) == ".!app.!commands":
        mods_directory_ = filedialog.askdirectory(initialdir=mods_directory)
    else:
        mods_directory_ = filedialog.askdirectory(initialdir=lists_directory)
    if not mods_directory_ == "":
        mods_directory = mods_directory_
        self.directory_entry.delete(0, tk.END)
        self.directory_entry.insert(0, mods_directory)
        self.directory_entry.validate()


def save_list_directory(mods_tree, modslist, text=None):
    selection = gui_elements.mods_list_tree.get_mods_selection()

    file = tk.filedialog.asksaveasfile(initialfile='Untitled.json', filetypes=[('Json Document', '*.json')], defaultextension=".json", title=text, initialdir=lists_directory)
    if file is None:
        mods_tree.uncheck_selection_name(selection)
        modslist.update_tree()
        return

    mods_tree_ = mods_tree.get_checked()

    file.write("[\n")
    for index, iid in enumerate(mods_tree_):
        if index + 1 == len(mods_tree_):
            file.write(f'  "{mods_tree.item(iid, "text")}"\n')
        else:
            file.write(f'  "{mods_tree.item(iid, "text")}",\n')
    file.write("]")
    file.close()

    print()
    print(f"Saved a list with {len(mods_tree_)} mods in it")

    modslist.update_tree(file.name.split("/")[-1])


def delete_mods():
    if not check_directory(mods_directory):
        messagebox.showerror("Unknown directory", "The selected directory does not exist")
    else:
        answer = messagebox.askyesnocancel("Delete mods", "Delete only the mods you selected instead of all of them ?")
        if answer:
            if not check_mods_in_directory(mods_directory):
                messagebox.showerror("Empty directory", "The selected directory has no mods in it")
            else:
                mods = []
                for mod in gui_elements.mods_tree.get_checked_name():
                    mods.append([mod, ""])
                modsSelector.delete_mods(mods_directory, mods)
        elif answer is not None:
            modsSelector.delete_mods(mods_directory)
        else:
            print()
            print("deletion canceled")


def update_mods(self):
    self.update_button["state"] = "disabled"
    if not check_directory(mods_directory):
        messagebox.showerror("Unknown directory", "The selected directory does not exist")
    elif not check_mods_in_directory(mods_directory):
        messagebox.showerror("Empty directory", "The selected directory has no mods in it")
    else:
        modsSelector.update_mods(mods_directory, minecraft_version)
    self.update_button["state"] = "enabled"


def download_mods(self):
    self.download_button["state"] = "disabled"
    selected_mods = gui_elements.mods_tree.get_checked_name()
    if not check_directory(mods_directory):
        messagebox.showerror("Unknown directory", "The selected directory does not exist")
    elif not selected_mods:
        messagebox.showerror("No selection", "There is no mods selected")
    else:
        answer = messagebox.askyesnocancel("Download dependencies", "Do you want to download the dependencies ?")
        selected_mods_and_site = []
        for mod in selected_mods:
            selected_mods_and_site.append([mod, API.get_mod_site(mod, minecraft_version, mod_loader)])
        if answer:
            modsSelector.download_mods_and_dependencies(selected_mods_and_site, minecraft_version, mods_directory)
        elif answer is not None:
            modsSelector.download_mods(selected_mods_and_site, minecraft_version, mods_directory)
        else:
            print()
            print("download canceled")
    self.download_button["state"] = "enabled"
