# -*- coding: utf-8 -*-
"""
Author: RenardElectric
License: GNU GPLv3
Source: ModsSelect
"""

import os
import time

import parallel_API
import API
import tools


def get_latest_mods_info_separated(mod_list, minecraft_version):
    t0 = time.time()
    mods_versions_id_list = []
    mods_versions_list = []
    mods_versions_name_list = []
    inputs = []

    print()
    print()
    print("Time to get the list of the latest mod's information:")
    print()

    for mod in mod_list:
        inputs.append((mod, minecraft_version))

    for result in parallel_API.get_latest_mods_info_separated_parallel(inputs):
        print(f"    {result[3]} ", end="")
        mods_versions_id_list.append(result[0])
        mods_versions_list.append(result[1])
        mods_versions_name_list.append(result[2])
        print(f" in {result[6]}s")

    print()
    print(f"Total time to get the list of the latest mod's information: {time.time() - t0}s")

    return [mods_versions_id_list, mods_versions_list, mods_versions_name_list]


def get_dependencies(mod_and_site_list, minecraft_version):
    """ returns the list of the mod's dependencies in a given directory """
    t0 = time.time()
    mods_dependencies_list = []
    inputs = []

    print()
    print()
    print("Time to get the list of the mod's dependencies:")
    print()

    for mod in mod_and_site_list:
        inputs.append((mod, minecraft_version))

    for result in parallel_API.get_dependencies_parallel(inputs):
        if result[0]:
            print(f"    {result[1][0]} : ", end="")
            for mod_and_platform in result[0]:
                if mod_and_platform[0] not in mod_and_site_list and [mod_and_platform[0], 'modrinth'] not in \
                        mods_dependencies_list and [mod_and_platform[0], 'curseforge'] not in mods_dependencies_list:
                    mods_dependencies_list.append(mod_and_platform)
            print(f"{result[0]}", end="")
            print(f" in {result[2]}s")

    print()
    print(f"Found {len(mods_dependencies_list)} new mods : {mods_dependencies_list}")
    print()
    print(f"Total time to get the list of the mod's dependencies: {time.time() - t0}s")

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
    print()

    for file in os.listdir(directory):
        if file.split(".")[-1] == "jar" and file.split("~")[0] not in mod_names:
            mod_names.append(file.split("~")[0])
            inputs.append((file, minecraft_version))

    if not len(inputs) == 0:
        for result in parallel_API.mods_update_list_parallel(inputs):
            if result is not None:
                if not result[0] in mods_update_list:
                    mods_update_list.append([result[0], result[1]])
                print(f"    {result[0]} : {result[2]}s")

        print()
        print(f"Total time to get the list of mods to update: {time.time() - t0}s")

        return mods_update_list
    else:
        print()
        print("No mods found")
        return mods_update_list


def delete_mods(directory, mod_and_loader_list=None):
    """ deletes the mods listed in a given directory, prints the time it took to delete them

    returns the version of the mods """
    t0 = time.time()

    for file in os.listdir(directory):
        if mod_and_loader_list is not None:
            for mod in mod_and_loader_list:
                if file.split("~")[0] == mod[0]:
                    os.remove(f"{directory}/{file}")
        else:
            os.remove(f"{directory}/{file}")

    print()
    print()
    print(f"Mods deleted in: {time.time() - t0}s")


def download_mods(mods_update_list, minecraft_version, directory):
    """ downloads the mods, prints the time each mod took to download and the total time """
    t0 = time.time()
    inputs = []

    for index in range(len(mods_update_list)):
        inputs.append((mods_update_list[index], minecraft_version, directory))

    print()
    print()
    print("Time to download the mods:")
    print()

    for result in parallel_API.download_mods_parallel(inputs):
        if result is not None:
            name = result[0].split("~")[0]
            print(f"    {name} : {result[1]}s")

    print()
    print(f"Total time to download the mods: {time.time() - t0}s")


def update_mods(directory, minecraft_version):
    """ updates all the mods in a given directory, prints the time it took to update them """
    t0 = time.time()
    update_mod_name_and_platform = []
    mod_update_list = get_mods_update_list(directory, minecraft_version)
    if not len(mod_update_list) == 0:
        for mods in mod_update_list:
            update_mod_name_and_platform.append([mods[0], API.get_mod_site(mods[0], tools.get_minecraft_version(), tools.get_minecraft_loader())])
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
