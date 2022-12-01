# -*- coding: utf-8 -*-
"""
Author: RenardElectric
License: GNU GPLv3
Source: ModsSelect
"""

import time
from multiprocessing.pool import ThreadPool
from pathlib import Path

import requests

import API
import gui_elements


def get_latest_mod_info_separated(args):
    mod_name, minecraft_version = args[0], args[1]
    return API.get_latest_mod_info_separated(mod_name, minecraft_version)


def get_latest_mods_info_separated_parallel(args):
    result = ThreadPool(len(args)).imap_unordered(get_latest_mod_info_separated, args)
    return result


def get_mods_info_separated_parallel(args):
    result = ThreadPool(len(args)).imap_unordered(API.get_mod_info_separated, args)
    return result


def get_dependencies_parallel(args):
    result = ThreadPool(len(args)).imap_unordered(API.returns_mod_dependencies, args)
    return result


def returns_mods_update_list(args):
    """ returns the name of the mod to update and the time it took to get it """
    t0 = time.time()
    mod_file, minecraft_version = args[0], args[1]
    mod_components = mod_file.split("~")
    latest_mod_version_name = API.get_latest_mod_version_name(mod_components[0], minecraft_version)
    if not mod_components[2].replace(".jar", "") == latest_mod_version_name and latest_mod_version_name is not None:
        return mod_components[0], minecraft_version, time.time() - t0


def mods_update_list_parallel(args):
    """ get the list of mods to update in parallel, returns the mod's name and the time each threads took to get it """
    result = ThreadPool(len(args)).imap_unordered(returns_mods_update_list, args)
    return result


def download_parallel(args):
    """ downloads the mod in a directory, if the directory does not exist, creates it,
    if the mod or the minecraft version does not exist, does nothing

    returns the mod's name and the time it took to download it """
    t0 = time.time()
    mod_name, minecraft_version, directory = args[0], args[1], args[2]
    if gui_elements.get_mods_tree().item(gui_elements.get_mods_tree().get_item_iid(mod_name), "values") != "":
        url, fn = API.returns_download_mod_url(mod_name, minecraft_version)
        download_dir = Path(directory)
        download_dir.mkdir(parents=True, exist_ok=True)
        response = requests.get(url, stream=True)
        download_dir.joinpath(fn).write_bytes(response.content)
        return fn, time.time() - t0
    else:
        print(f"    {mod_name} is not available for minecraft {minecraft_version}")


def download_mods_parallel(args):
    """ downloads the mod in parallel, returns the mod's name and the time each threads took to download it """
    result = ThreadPool(len(args)).imap_unordered(download_parallel, args)
    return result
