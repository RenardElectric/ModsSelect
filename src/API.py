# -*- coding: utf-8 -*-
"""
Author: RenardElectric
License: GNU GPLv3
Source: ModsSelect
"""

import json
import time
import urllib.error
import urllib.request
import pandas as pd
import threading

import tools

lock = threading.Lock()


def open_url(url, headers=None):
    """ returns the request from the url, wats if the server asks, throws an error if the link does not exist """
    try:
        req = urllib.request.Request(url)
        if headers is not None:
            for header in headers:
                req.add_header(header[0], header[1])
        request = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f'    sleeping for: {e.headers.get("X-Ratelimit-Reset")}s')
            time.sleep(int(e.headers.get("X-Ratelimit-Reset")) + 1)
            print(f'    waking up')
            request = urllib.request.urlopen(url)
        else:
            # print("error")
            raise
    return request


def get_list(directory):
    f = open(directory, "r").read()
    return json.loads(f)


def mod_name_in_list(mod_name):
    mod_list = get_list("config/mods.json")
    for mod in mod_list:
        if mod[0] == mod_name:
            return True
    return False


def get_info_in_list(mod_name, minecraft_version, loader):
    mod_list = get_list("config/mods.json")
    for mod in mod_list:
        if mod["name"] == mod_name:
            mod_versions = mod["versions"]
            if mod_versions is not []:
                for version in mod_versions:
                    if minecraft_version in version["minecraft_versions"] and loader in version["loaders"]:
                        mod_info = [mod["id"], version["minecraft_versions"], version["version_name"],
                                    version["version_url"], version["dependencies"], version["loaders"]]
                        return mod_info


# def cleat_data():
#     mods_list = get_list("config/mods.json")
#     for mod in mods_list:
#         mod["versions"] = []
#     file = open('D:\\Antony\\PycharmProjects\\ModsSelect\\config\\mods.json', "w")
#     file.write(
#         pd.DataFrame(mods_list, columns=["name", "category", "id", "site", "versions"]).to_json(
#             orient='records', indent=5))
#     file.close()


def write_mod_info(mod_name, mod_info, site):
    lock.acquire()
    mod_id, minecraft_versions, version_name, version_url, dependencies, loaders = mod_info
    versions = {
        "minecraft_versions": minecraft_versions,
        "version_name": version_name,
        "version_url": version_url,
        "dependencies": dependencies,
        "loaders": loaders
    }
    mods_list = get_list("config/mods.json")
    for mod in mods_list:
        if mod["name"] == mod_name:
            mod["id"] = mod_id
            if mod["site"] is None:
                mod["site"] = site
            # if versions not in mod["versions"]:
            #     mod["versions"].append(versions)
            file = open('D:\\Antony\\PycharmProjects\\ModsSelect\\config\\mods.json', "w")
            file.write(pd.DataFrame(mods_list, columns=["name", "category", "id", "site", "versions"]).to_json(
                orient='records', indent=5))
    lock.release()


def get_mod_id_from_name_curseforge(mod_name, minecraft_version, loader):
    headers = [
        ['Accept', 'application/json'],
        ['x-api-key', '$2a$10$6kjcBapbGzJ1VCgpjmPjpu.5bBndofdMdl.ovdoIgEifyovJYw7Ee']
    ]
    url = f"https://api.curseforge.com/v1/mods/search?pageSize=1&gameVersion={minecraft_version}&modLoaderType={1 if loader == 'forge' else 4 if loader == 'fabric' else 5}&gameId=432&slug={mod_name}&sortOrder=desc"
    request = open_url(url, headers)
    if request is None:
        return
    mod = json.loads(request.read())["data"]
    if len(mod) == 0:
        return
    return mod[0]["id"]


def get_mod_info_curseforge(mod_name, minecraft_version, loader):
    headers = [
        ['Accept', 'application/json'],
        ['x-api-key', '$2a$10$6kjcBapbGzJ1VCgpjmPjpu.5bBndofdMdl.ovdoIgEifyovJYw7Ee']
    ]
    mod_list = get_list("config/mods.json")
    mod_id = None
    for mod in mod_list:
        if mod["name"] == mod_name:
            mod_id = mod["id"]
    if mod_id is None:
        mod_id = get_mod_id_from_name_curseforge(mod_name, minecraft_version, loader)
    if mod_id is None:
        return
    url = f"https://api.curseforge.com/v1/mods/{mod_id}/files?pageSize=1&gameVersion={minecraft_version}&modLoaderType={1 if loader == 'forge' else 4 if loader == 'fabric' else 5}"
    request = open_url(url, headers)
    if request is None:
        return
    mod_versions = json.loads(request.read())["data"]
    if len(mod_versions) == 0:
        return []
    mod_version = mod_versions[0]
    game_versions = []
    loaders = []
    for game_version in mod_version["gameVersions"]:
        if game_version[0] == "1":
            game_versions.append(game_version)
        else:
            loaders.append(game_version.lower())
    if not loaders:
        loaders.append("forge")
    dependencies = []
    for dependency in mod_version["dependencies"]:
        dependency = json.loads(str(dependency).replace("'", '"').replace("None", '"None"'))
        if dependency["relationType"] == 3 and dependency["modId"] != "None":
            dependencies.append(dependency["modId"])
    mod_info = [mod_version["modId"], game_versions,
                mod_version["displayName"].replace(" ", "-").replace("\\", '-').replace("/", '-'),
                mod_version["downloadUrl"], dependencies, loaders]
    write_mod_info(mod_name, mod_info, "curseforge")
    return mod_info


def get_mod_info_modrinth(mod_name, minecraft_version, loader):
    """ returns the mod's minecraft and the version's ids, if the mod does not exist throws an error """
    headers = [
        ['Accept', 'application/json'],
        ['User-Agent', 'RenardElectric/ModsSelect/2.0.0-beta2 (RenardElectric.perso@gmail.com)']
    ]
    url = f"https://api.modrinth.com/v2/project/{mod_name}/version?game_versions=%5B%22{minecraft_version}%22%5D&loaders=%5B%22{loader}%22%5D"
    request = open_url(url, headers)
    if request is None:
        return
    mod_versions = json.loads(request.read())
    if len(mod_versions) == 0:
        return []
    mod_version = mod_versions[0]
    dependencies = []
    for dependency in mod_version["dependencies"]:
        dependency = json.loads(str(dependency).replace("'", '"').replace("None", '"None"'))
        if dependency["dependency_type"] == "required" and dependency["project_id"] != "None":
            dependencies.append(dependency["project_id"])
    mod_info = [mod_version["id"], mod_version["game_versions"],
                mod_version["version_number"].replace("\\", '-').replace("/", '-'),
                mod_version["files"][0]["url"], dependencies, mod_version["loaders"]]
    write_mod_info(mod_name, mod_info, "modrinth")
    return mod_info


def get_latest_mod_info(mod_and_site, minecraft_version, loader, get_from_list=True):
    mod_info = get_info_in_list(mod_and_site[0], minecraft_version, loader)
    if mod_info is not None and get_from_list:
        return mod_info
    if mod_and_site[1] == "curseforge":
        return get_mod_info_curseforge(mod_and_site[0], minecraft_version, loader)
    elif mod_and_site[1] == "modrinth":
        return get_mod_info_modrinth(mod_and_site[0], minecraft_version, loader)


def get_latest_mod_version_name(mod_and_site, minecraft_version):
    """ returns the version of the latest mod's minecraft version, if it cannot find throws an error """
    latest_mod_info = get_latest_mod_info(mod_and_site, minecraft_version, tools.get_minecraft_loader())
    if not latest_mod_info:
        return None
    return latest_mod_info[2]


def get_latest_mod_dependencies(mod_and_site, minecraft_version):
    latest_mod_info = get_latest_mod_info(mod_and_site, minecraft_version, tools.get_minecraft_loader())
    if not latest_mod_info:
        return None
    dependencies = []
    for dependency in latest_mod_info[4]:
        name = get_mod_name(dependency, mod_and_site[1])
        site = get_mod_site(name, minecraft_version, tools.get_minecraft_loader())
        dependencies.append([name, site])
    return dependencies


def get_mod_name(mod_id, site):
    if site == "curseforge":
        headers = [
            ['Accept', 'application/json'],
            ['x-api-key', '$2a$10$6kjcBapbGzJ1VCgpjmPjpu.5bBndofdMdl.ovdoIgEifyovJYw7Ee']
        ]
        url = f"https://api.curseforge.com/v1/mods/{mod_id}"
        request = open_url(url, headers)
        return json.loads(request.read())["data"]["slug"]
    elif site == "modrinth":
        request = open_url(f"https://api.modrinth.com/v2/project/{mod_id}")
        return json.loads(request.read())["slug"]


def get_mod_site(mod_name, minecraft_version, loader, get_id=False):
    mod_list = get_list("config/mods.json")
    for mod in mod_list:
        if mod["name"] == mod_name:
            site = mod["site"]
            if site is not None:
                return site
    try:
        open_url(f"https://api.modrinth.com/v2/project/{mod_name}")
        if get_id:
            return "modrinth", mod_name
        return "modrinth"
    except urllib.error.HTTPError:
        try:
            mod_id = get_mod_id_from_name_curseforge(mod_name, minecraft_version, loader)
            if get_id:
                return "curseforge", mod_id
            return "curseforge"
        except urllib.error.HTTPError:
            return


def returns_download_mod_url(mod_and_site, minecraft_version):
    """ returns the url to download the mod and the mod's file name """
    mod_version_id, minecraft_versions, mod_version_name, mod_version_url, mod_dependencies, loaders = \
        get_latest_mod_info(mod_and_site, minecraft_version, tools.get_minecraft_loader())
    return mod_version_url, f"{mod_and_site[0]}~{minecraft_version}~{mod_version_name}.jar"
