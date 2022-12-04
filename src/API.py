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

import tools


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
            time.sleep(int(e.headers.get("X-Ratelimit-Reset")) + 5)
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


def get_mod_id(mod_name):
    mod_list = get_list("config/mods.json")
    if mod_name_in_list(mod_name):
        for mod in mod_list:
            if mod[0] == mod_name and mod[1] != "modrinth":
                return mod[1]
        return False
    return None


def get_mod_id_from_name_curseforge(mod_name):
    headers = [
        ['Accept', 'application/json'],
        ['x-api-key', '$2a$10$6kjcBapbGzJ1VCgpjmPjpu.5bBndofdMdl.ovdoIgEifyovJYw7Ee']
    ]
    url = f"https://api.curseforge.com/v1/mods/search?gameId=432&slug={mod_name}&sortOrder=desc"
    request = open_url(url, headers)
    if request is None:
        return
    return json.loads(request.read())["data"][0]["id"]


def get_mod_info_forge(mod_name):
    headers = [
        ['Accept', 'application/json'],
        ['x-api-key', '$2a$10$6kjcBapbGzJ1VCgpjmPjpu.5bBndofdMdl.ovdoIgEifyovJYw7Ee']
    ]
    mod_id = get_mod_id_from_name_curseforge(mod_name)
    url = f"https://api.curseforge.com/v1/mods/{mod_id}/files"
    request = open_url(url, headers)
    if request is None:
        return
    mod_versions = json.loads(request.read())["data"]
    mod_info = []
    for mod_version in mod_versions:
        game_versions = []
        loaders = []
        for game_version in mod_version["gameVersions"]:
            if game_version[0] == "1":
                game_versions.append(game_version)
            else:
                loaders.append(game_version.lower())
        dependencies = []
        for dependency in mod_version["dependencies"]:
            dependency = json.loads(str(dependency).replace("'", '"').replace("None", '"None"'))
            if dependency["relationType"] == 3 and dependency["modId"] != "None":
                dependencies.append(dependency["modId"])
        mod_info.append([mod_version["id"], game_versions,
                         mod_version["displayName"].replace(" ", "-").replace("\\", '-').replace("/", '-'),
                         mod_version["downloadUrl"], dependencies, loaders])
    return mod_info


def get_mod_info_modrinth(mod_name):
    """ returns the mod's minecraft and the version's ids, if the mod does not exist throws an error """
    request = open_url(f"https://api.modrinth.com/v2/project/{mod_name}/version")
    if request is None:
        return
    mod_versions = json.loads(request.read())
    mod_info = []
    for mod_version in mod_versions:
        dependencies = []
        for dependency in mod_version["dependencies"]:
            dependency = json.loads(str(dependency).replace("'", '"').replace("None", '"None"'))
            if dependency["dependency_type"] == "required" and dependency["project_id"] != "None":
                dependencies.append(dependency["project_id"])
        mod_info.append([mod_version["id"], mod_version["game_versions"],
                         mod_version["version_number"].replace("\\", '-').replace("/", '-'),
                         mod_version["files"][0]["url"], dependencies, mod_version["loaders"]])
    return mod_info


def get_mod_info(mod_and_site):
    if mod_and_site[1] == "curseforge":
        return get_mod_info_forge(mod_and_site[0])
    elif mod_and_site[1] == "modrinth":
        return get_mod_info_modrinth(mod_and_site[0])


def get_latest_mod_info(mod_and_site, minecraft_version):
    """ returns the version's ids, if the mod does not exist throws an error """
    for mod_info in get_mod_info(mod_and_site):
        if minecraft_version in mod_info[1] and tools.get_minecraft_loader() in mod_info[5]:
            return mod_info


def get_latest_mod_version_id(mod_and_site, minecraft_version):
    """ returns the id of the latest mod's minecraft version, if it cannot find throws an error """
    latest_mod_info = get_latest_mod_info(mod_and_site, minecraft_version)
    if latest_mod_info is None:
        return
    return latest_mod_info[0]


def get_latest_mod_version(mod_and_site, minecraft_version):
    """ returns the version of the latest mod's minecraft version, if it cannot find throws an error """
    latest_mod_info = get_latest_mod_info(mod_and_site, minecraft_version)
    if latest_mod_info is None:
        return None
    return latest_mod_info[1]


def get_latest_mod_version_name(mod_and_site, minecraft_version):
    """ returns the version of the latest mod's minecraft version, if it cannot find throws an error """
    latest_mod_info = get_latest_mod_info(mod_and_site, minecraft_version)
    if latest_mod_info is None:
        return None
    return latest_mod_info[2]


def get_latest_mod_version_url(mod_and_site, minecraft_version):
    """ returns the version of the latest mod's minecraft version, if it cannot find throws an error """
    latest_mod_info = get_latest_mod_info(mod_and_site, minecraft_version)
    if latest_mod_info is None:
        return None
    return latest_mod_info[3]


def get_latest_mod_dependencies(mod_and_site, minecraft_version):
    latest_mod_info = get_latest_mod_info(mod_and_site, minecraft_version)
    if latest_mod_info is None:
        return None
    dependencies = []
    for dependency in latest_mod_info[4]:
        dependencies.append([get_mod_name(dependency, mod_and_site[1]), mod_and_site[1]])
    return dependencies


def get_latest_mod_info_separated(mod_and_site, minecraft_version):
    t0 = time.time()
    latest_mod_info = get_latest_mod_info(mod_and_site, minecraft_version)
    if latest_mod_info is None:
        return None, None, None, None, None, mod_and_site, time.time() - t0
    return latest_mod_info[0], latest_mod_info[1], latest_mod_info[2], latest_mod_info[3], latest_mod_info[
        4], mod_and_site, time.time() - t0


def get_mod_name(mod_id, site):
    if site == "curseforge":
        if get_mod_id(mod_id) is False:
            return mod_id
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


def get_mod_site(mod_name):
    mod_list = get_list("config/mods.json")
    for mod in mod_list:
        if mod[0] == mod_name:
            return mod[1]
    try:
        open_url(f"https://api.modrinth.com/v2/project/{mod_name}")
        return "modrinth"
    except urllib.error.HTTPError:
        try:
            get_mod_id_from_name_curseforge(mod_name)
            return "curseforge"
        except urllib.error.HTTPError:
            return


def get_mod_platform(mod_name):
    mod_list = get_list("config/mods.json")
    for mod in mod_list:
        if mod[0] == mod_name:
            return mod[2]


def returns_download_mod_url(mod_and_platform, minecraft_version):
    """ returns the url to download the mod and the mod's file name """
    mod_version_id, minecraft_versions, mod_version_name, mod_version_url, mod_dependencies, mod_and_platform, _time = \
        get_latest_mod_info_separated(mod_and_platform, minecraft_version)
    print(mod_version_name)
    return mod_version_url, f"{mod_and_platform[0]}~{minecraft_version}~{mod_version_name}.jar"
