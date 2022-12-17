# -*- coding: utf-8 -*-
"""
Author: RenardElectric
License: GNU GPLv3
Source: ModsSelect
"""

import threading
import time
from multiprocessing.pool import ThreadPool
from pathlib import Path

import requests
from tqdm import tqdm

import API
import tools
import gui_elements

lock = threading.Lock()


def get_latest_mod_info_separated(args):
    mod_and_site, minecraft_version = args[0], args[1]
    latest_mod_info = API.get_latest_mod_info(mod_and_site, minecraft_version, tools.minecraft_loader)
    if not latest_mod_info:
        return None, None, None, None, None, mod_and_site
    return latest_mod_info[0], latest_mod_info[1], latest_mod_info[2], latest_mod_info[3], latest_mod_info[4], mod_and_site


def returns_mod_dependencies(args):
    mod_name, minecraft_version = args[0], args[1]
    t0 = time.time()
    return API.get_latest_mod_dependencies(mod_name, minecraft_version), mod_name, time.time() - t0


def returns_mods_update_list(args):
    """ returns the name of the mod to update and the time it took to get it """
    mod_file, minecraft_version = args[0], args[1]
    mod_components = mod_file.split("~")
    latest_mod_version_name = API.get_latest_mod_version_name([mod_components[0], API.get_mod_site(mod_components[0], tools.minecraft_version, tools.minecraft_loader)], minecraft_version)
    if not mod_components[2].replace(".jar", "", 1) == latest_mod_version_name and latest_mod_version_name is not None:
        return mod_components[0], minecraft_version


def download_parallel(args):
    """ downloads the mod in a directory, if the directory does not exist, creates it,
    if the mod or the minecraft version does not exist, does nothing

    returns the mod's name and the time it took to download it """
    mod_and_site, minecraft_version, directory = args[0], args[1], args[2]
    url, fn = API.returns_download_mod_url(mod_and_site, minecraft_version)
    if url is None:
        print(f"    {mod_and_site[0]} is not available for minecraft {minecraft_version}")
        return
    download_dir = Path(directory)
    download_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, stream=True)
    download_dir.joinpath(fn).write_bytes(response.content)


def update_tree_parallel(args):
    category, parent = args[0], args[1]
    mod_list = tools.mods_list

    mods_tree = gui_elements.mods_tree
    inputs = []

    for mod in mod_list:
        if mod["category"] == category:
            inputs.append(([mod["name"], API.get_mod_site(mod["name"], tools.minecraft_version, tools.minecraft_loader)], tools.minecraft_version))
        elif mod["category"] is None and category == "Other":
            inputs.append(([mod["name"], API.get_mod_site(mod["name"], tools.minecraft_version, tools.minecraft_loader)], tools.minecraft_version))

    mod_name_list = []
    mod_name_and_version_list = []

    if len(inputs) != 0:
        for result in tqdm(ThreadPool(len(inputs)).imap_unordered(get_latest_mod_info_separated, inputs), total=len(inputs)):
            gui_elements.progressbar.config(value=gui_elements.progressbar["value"] + 1)
            mod_name_list.append(result[5][0])
            mod_name_and_version_list.append([result[5][0], result[2]])

        mod_name_list_sorted = sorted(mod_name_list)

        lock.acquire()
        for mod in mod_name_list_sorted:
            for mod_and_version in mod_name_and_version_list:
                if mod_and_version[0] == mod and mod_and_version[1] is not None:
                    mods_tree.insert(parent=str(parent), index="end", iid=len(mods_tree.get_tree_items()), text=mod_and_version[0], values=mod_and_version[1])
                    if mods_tree.tag_has("checked_focus", str(parent)) or mods_tree.tag_has("checked", str(parent)):
                        mods_tree.change_state(mods_tree.get_children(str(parent))[-1], "checked")
        lock.release()
