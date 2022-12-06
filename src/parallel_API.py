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
import tools


def get_latest_mod_info_separated(args):
    t0 = time.time()
    mod_and_site, minecraft_version = args[0], args[1]
    latest_mod_info = API.get_latest_mod_info(mod_and_site, minecraft_version, tools.get_minecraft_loader())
    if not latest_mod_info:
        return None, None, None, None, None, mod_and_site, time.time() - t0
    return latest_mod_info[0], latest_mod_info[1], latest_mod_info[2], latest_mod_info[3], latest_mod_info[
        4], mod_and_site, time.time() - t0


def get_latest_mods_info_separated_parallel(args):
    result = ThreadPool(len(args)).imap_unordered(get_latest_mod_info_separated, args)
    return result


def returns_mod_dependencies(args):
    mod_name, minecraft_version = args[0], args[1]
    t0 = time.time()
    return API.get_latest_mod_dependencies(mod_name, minecraft_version), mod_name, time.time() - t0


def get_dependencies_parallel(args):
    result = ThreadPool(len(args)).imap_unordered(returns_mod_dependencies, args)
    return result


def returns_mods_update_list(args):
    """ returns the name of the mod to update and the time it took to get it """
    t0 = time.time()
    mod_file, minecraft_version = args[0], args[1]
    mod_components = mod_file.split("~")
    latest_mod_version_name = API.get_latest_mod_version_name([mod_components[0], API.get_mod_site(mod_components[0], tools.get_minecraft_version(), tools.get_minecraft_loader())],
                                                              minecraft_version)
    if not mod_components[2].replace(".jar", "", 1) == latest_mod_version_name and latest_mod_version_name is not None:
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
    mod_and_site, minecraft_version, directory = args[0], args[1], args[2]
    url, fn = API.returns_download_mod_url(mod_and_site, minecraft_version)
    if url is None:
        print(f"    {mod_and_site[0]} is not available for minecraft {minecraft_version}")
        return
    download_dir = Path(directory)
    download_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, stream=True)
    download_dir.joinpath(fn).write_bytes(response.content)
    return fn, time.time() - t0


def download_mods_parallel(args):
    """ downloads the mod in parallel, returns the mod's name and the time each threads took to download it """
    result = ThreadPool(len(args)).imap_unordered(download_parallel, args)
    return result
