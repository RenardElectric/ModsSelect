import os
from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox

import gui_elements
import modsSelector
import threading

mods_directory = ""
mods_list_directory = ""
minecraft_version = ""

def get_mods_directory():
    return mods_directory


def get_mods_list_directory():
    return mods_list_directory


def get_minecraft_version():
    return minecraft_version


def check_directory(directory):
    if not directory == "":
        if os.path.isdir(directory):
            return True
        print("the directory does not exist")
    return False


def check_mods_in_directory(_directory):
    for file in os.listdir(_directory):
        if file.split(".")[-1] == "jar":
            return True
    print("no mods in this directory")
    return False


def validation_directory(self, directory):
    _directory = self.directory_entry.get()
    if directory == "mods_directory":
        global mods_directory
        mods_directory = _directory
    elif directory == "mods_list_directory":
        global mods_list_directory
        mods_list_directory = _directory
        self.update_tree()

    if check_directory(_directory):
        return True
    return False


def find_directory(self):
    global mods_directory
    if str(self.directory_entry.winfo_parent()) == ".!app.!commands":
        mods_directory = filedialog.askdirectory(initialdir=mods_directory)
    else:
        mods_directory = filedialog.askdirectory(initialdir=mods_list_directory)
    if not mods_directory == "":
        self.directory_entry.delete(0, tk.END)
        self.directory_entry.insert(0, mods_directory)
        self.directory_entry.validate()


def save_list_directory(mods_tree, modslist, text=None):
    selection = gui_elements.get_mods_list_tree().get_mods_selection()

    file = tk.filedialog.asksaveasfile(initialfile='Untitled.json', filetypes=[('Json Document', '*.json')], defaultextension=".json", title=text, initialdir=mods_list_directory)
    if file is None:
        mods_tree.uncheck_selection_name(selection)
        modslist.update_tree()
        return

    Mods_Tree = mods_tree.get_checked()

    file.write("[\n")
    for index, iid in enumerate(Mods_Tree):
        if index + 1 == len(Mods_Tree):
            file.write(f'  "{mods_tree.item(iid, "text")}"\n')
        else:
            file.write(f'  "{mods_tree.item(iid, "text")}",\n')
    file.write("]")
    file.close()

    print()
    print(f"Saved a list with {len(Mods_Tree)} mods in it")

    modslist.update_tree()


def update_minecraft_version(commands, mods_class):
    commands.minecraft_version_combo["state"] = "disabled"
    commands.update_button["state"] = "disabled"
    commands.download_button["state"] = "disabled"

    global minecraft_version
    if not minecraft_version == commands.minecraft_version_combo.get():
        minecraft_version = commands.minecraft_version_combo.get()
        if mods_class is not None:
            threading.Thread(target=mods_class.update_tree, daemon=True).start()

    commands.download_button["state"] = "enabled"
    commands.update_button["state"] = "enabled"
    commands.minecraft_version_combo["state"] = "readonly"


def delete_mods(self):
    self.delete_button["state"] = "disabled"
    if not check_directory(mods_directory):
        messagebox.showerror("Unknown directory", "The selected directory does not exist")
    else:
        answer = messagebox.askyesnocancel("Delete mods", "Do you want to delete all the mods in this directory instead of the ones selected ?")
        if answer:
            modsSelector.delete_mods(mods_directory)
        elif answer is not None:
            if not check_mods_in_directory(mods_directory):
                messagebox.showerror("Empty directory", "The selected directory has no mods in it")
            else:
                modsSelector.delete_mods(mods_directory, gui_elements.get_mods_tree().get_checked_name())
        else:
            print()
            print("deletion canceled")
    self.delete_button["state"] = "enabled"


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
    selected_mods = gui_elements.get_mods_tree().get_checked_name()
    if not check_directory(mods_directory):
        messagebox.showerror("Unknown directory", "The selected directory does not exist")
    elif not selected_mods:
        messagebox.showerror("No selection", "There is no mods selected")
    else:
        answer = messagebox.askyesnocancel("Download dependencies", "Do you want to download the dependencies ?")
        if answer:
            modsSelector.download_mods_and_dependencies(selected_mods, minecraft_version, mods_directory)
        elif answer is not None:
            modsSelector.download_mods(selected_mods, minecraft_version, mods_directory)
        else:
            print()
            print("download canceled")
    self.download_button["state"] = "enabled"
