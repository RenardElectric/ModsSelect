# -*- coding: utf-8 -*-
"""
Author: RenardElectric
License: GNU GPLv3
Source: ModsSelect
"""

import os
import time
from multiprocessing.pool import ThreadPool
from tqdm import tqdm

import parallel_API
import API
import tools
import gui_elements


def get_dependencies(mod_and_site_list, minecraft_version):
    """ returns the list of the mod's dependencies in a given directory """
    t0 = time.time()
    mods_dependencies_list = []
    inputs = []

    print()
    print()
    print("Time to get the list of the mod's dependencies:")

    for mod in mod_and_site_list:
        inputs.append((mod, minecraft_version))

    gui_elements.progressbar.config(maximum=len(inputs))
    for index, result in enumerate(tqdm(ThreadPool(len(inputs)).imap_unordered(parallel_API.returns_mod_dependencies, inputs), total=len(inputs))):
        gui_elements.progressbar.config(value=index + 1)
        if result[0]:
            for mod_and_platform in result[0]:
                if mod_and_platform[0] not in mod_and_site_list and [mod_and_platform[0], 'modrinth'] not in mods_dependencies_list and [mod_and_platform[0], 'curseforge'] not in mods_dependencies_list:
                    mods_dependencies_list.append(mod_and_platform)
    gui_elements.progressbar.config(value=0)

    print()
    print(f"Found {len(mods_dependencies_list)} new mods : {mods_dependencies_list}")
    print()
    print(f"Time to get the list of the mod's dependencies: {time.time() - t0}s")

    return mods_dependencies_list


def get_mods_update_list(directory, minecraft_version):
    """ returns the list of mods to update in a given directory """
    t0 = time.time()

    mods_update_list = []
    mod_names = []
    inputs = []

    print()
    print()
    print("Time to get the list of mods to update:")

    for file in os.listdir(directory):
        if file.split(".")[-1] == "jar" and file.split("~")[0] not in mod_names:
            mod_names.append(file.split("~")[0])
            inputs.append((file, minecraft_version))

    if not len(inputs) == 0:
        gui_elements.progressbar.config(maximum=len(inputs))
        for index, result in enumerate(tqdm(ThreadPool(len(inputs)).imap_unordered(parallel_API.returns_mods_update_list, inputs), total=len(inputs))):
            gui_elements.progressbar.config(value=index + 1)
            if result is not None:
                if not result[0] in mods_update_list:
                    mods_update_list.append([result[0], result[1]])
        gui_elements.progressbar.config(value=0)

        print()
        print(f"Time to get the list of mods to update: {time.time() - t0}s")

        return mods_update_list
    else:
        print()
        print("No mods found")
        return mods_update_list


def delete_mods(directory, mod_and_loader_list=None):
    """ deletes the mods listed in a given directory, prints the time it took to delete them
    returns the version of the mods """

    for file in os.listdir(directory):
        if mod_and_loader_list is not None:
            for mod in mod_and_loader_list:
                if file.split("~")[0] == mod[0]:
                    os.remove(f"{directory}/{file}")
        else:
            os.remove(f"{directory}/{file}")


def download_mods(mods_update_list, minecraft_version, directory):
    """ downloads the mods, prints the time each mod took to download and the total time """
    t0 = time.time()
    inputs = []

    for index in range(len(mods_update_list)):
        inputs.append((mods_update_list[index], minecraft_version, directory))

    print()
    print()
    print("Time to download the mods:")

    gui_elements.progressbar.config(maximum=len(inputs))
    for index, result in enumerate(tqdm(ThreadPool(len(inputs)).imap_unordered(parallel_API.download_parallel, inputs), total=len(inputs))):
        gui_elements.progressbar.config(value=index + 1)
    gui_elements.progressbar.config(value=0)

    print()
    print(f"Time to download the mods: {time.time() - t0}s")


def update_mods(directory, minecraft_version):
    """ updates all the mods in a given directory, prints the time it took to update them """
    t0 = time.time()
    update_mod_name_and_platform = []
    mod_update_list = get_mods_update_list(directory, minecraft_version)
    if not len(mod_update_list) == 0:
        for mods in mod_update_list:
            update_mod_name_and_platform.append([mods[0], API.get_mod_site(mods[0], tools.minecraft_version, tools.minecraft_loader)])
        delete_mods(directory, update_mod_name_and_platform)
        download_mods(update_mod_name_and_platform, minecraft_version, directory)
        print()
        print()
        print(f"Time to update the mods: {time.time() - t0}s")
    else:
        print()
        print("All mods are uptodate")


def download_mods_and_dependencies(mod_and_site_list, minecraft_version, directory):
    mod_and_site_list += get_dependencies(mod_and_site_list, minecraft_version)
    download_mods(mod_and_site_list, minecraft_version, directory)
