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
from urllib.parse import quote


def open_url(url):
    """ returns the request from the url, wats if the server asks, throws an error if the link does not exist """
    try:
        request = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f'    sleeping for: {e.headers.get("X-Ratelimit-Reset")}s')
            time.sleep(int(e.headers.get("X-Ratelimit-Reset")) + 5)
            request = urllib.request.urlopen(url)
        else:
            # print("error")
            raise
    return request


def check_mod_name(mod_name):
    try:
        open_url(f"https://api.modrinth.com/v2/project/{mod_name}/version?loaders=" + quote('["fabric"]'))
    except urllib.error.HTTPError:
        print(f"    {mod_name} does not exist for the fabric loader")
        return False
    return True


def get_mod_request(mod_name):
    try:
        request = open_url(f"https://api.modrinth.com/v2/project/{mod_name}/version?loaders=" + quote('["fabric"]'))
    except urllib.error.HTTPError:
        print(f"    {mod_name} does not exist for the fabric loader")
        return
    return request


def check_minecraft_version(mod_name, minecraft_version):
    request = open_url(
        f'https://api.modrinth.com/v2/project/{mod_name}/version?game_versions=' + quote(f'["{minecraft_version}"]'))
    if request.read() == b'[]':
        print(f"    {mod_name} is not available for minecraft {minecraft_version}")
        return False
    return True


def check_mod_name_and_minecraft_version(mod_name, minecraft_version):
    """ checks if the mod or the mod's minecraft version exist, if one or the other does not exist, prints it  """
    if not check_mod_name(mod_name):
        return False
    if not check_minecraft_version(mod_name, minecraft_version):
        return False
    return True


def get_mod_info(mod_name):
    """ returns the mod's minecraft and the version's ids, if the mod does not exist throws an error """
    request = get_mod_request(mod_name)
    if request is None:
        return []
    mod_versions = json.loads(request.read())
    mod_info = []
    for mod_version in mod_versions:
        version = [mod_version["id"], mod_version["game_versions"], mod_version["version_number"],
                   mod_version["files"][0]["url"]]
        mod_info.append(version)
    return mod_info


def get_mod_versions_id(mod_name):
    mod_versions_id = []
    for mod_minecraft_versions_id in get_mod_info(mod_name):
        version = mod_minecraft_versions_id[1]
        if version not in mod_versions_id:
            mod_versions_id.append(version)
    return mod_versions_id, mod_name


def get_mod_versions(mod_name):
    mod_versions = []
    for mod_minecraft_versions_id in get_mod_info(mod_name):
        version = mod_minecraft_versions_id[1]
        if version not in mod_versions:
            mod_versions.append(version)
    return mod_versions, mod_name


def get_mod_versions_name(mod_name):
    mod_versions_name = []
    for mod_minecraft_versions_id in get_mod_info(mod_name):
        version = mod_minecraft_versions_id[2]
        if version not in mod_versions_name:
            mod_versions_name.append(version)
    return mod_versions_name


def get_mod_info_separated(mod_name):
    t0 = time.time()
    return get_mod_versions_id(mod_name), get_mod_versions(mod_name), get_mod_versions_name(
        mod_name), mod_name, time.time() - t0


def get_latest_mod_info(mod_name, minecraft_version):
    """ returns the version's ids, if the mod does not exist throws an error """
    mod_info = get_mod_info(mod_name)
    for mod_version in mod_info:
        if minecraft_version in mod_version[1]:
            return mod_version


def get_latest_mod_version_id(mod_name, minecraft_version):
    """ returns the id of the latest mod's minecraft version, if it cannot find throws an error """
    mod_info = get_latest_mod_info(mod_name, minecraft_version)
    if mod_info is None:
        return None
    return mod_info[0]


def get_latest_mod_version(mod_name, minecraft_version):
    """ returns the version of the latest mod's minecraft version, if it cannot find throws an error """
    mod_info = get_latest_mod_info(mod_name, minecraft_version)
    if mod_info is None:
        return None
    return mod_info[1]


def get_latest_mod_version_name(mod_name, minecraft_version):
    """ returns the version of the latest mod's minecraft version, if it cannot find throws an error """
    mod_info = get_latest_mod_info(mod_name, minecraft_version)
    if mod_info is None:
        return None
    return mod_info[2]


def get_latest_mod_version_url(mod_name, minecraft_version):
    """ returns the version of the latest mod's minecraft version, if it cannot find throws an error """
    mod_info = get_latest_mod_info(mod_name, minecraft_version)
    if mod_info is None:
        return None
    return mod_info[3]


def get_latest_mod_info_separated(mod_name, minecraft_version):
    t0 = time.time()
    mod_info = get_latest_mod_info(mod_name, minecraft_version)
    if mod_info is None:
        return None, None, None, mod_name, time.time() - t0
    return mod_info[0], mod_info[1], mod_info[2], mod_info[3], mod_name, time.time() - t0


def get_mod_version_and_url(version_id):
    """ returns the mod's version, if the id does not exist throws an error """
    mod_version_link = f"https://api.modrinth.com/v2/version/{version_id}"
    page = open_url(mod_version_link).read()
    return json.loads(page)["version_number"], json.loads(page)["files"][0]["url"]


def get_mod_dependencies(mod_name):
    mod_dependencies = []
    mod_dependencies_link = f"https://api.modrinth.com/v2/project/{mod_name}/dependencies"
    dependencies = json.loads(open_url(mod_dependencies_link).read())["projects"]
    for dependency in dependencies:
        mod_dependencies.append(dependency["slug"])
    return mod_dependencies


def returns_mod_dependencies(mod_name):
    t0 = time.time()
    return get_mod_dependencies(mod_name), mod_name, time.time() - t0


def get_list(directory):
    f = open(directory, "r").read()
    return json.loads(f)


def returns_download_mod_url(mod_name, minecraft_version):
    """ returns the url to download the mod and the mod's file name """
    mod_version_id, minecraft_versions, mod_version, mod_version_url, mod_name, time = get_latest_mod_info_separated(
        mod_name, minecraft_version)
    return mod_version_url, f"{mod_name}~{minecraft_version}~{mod_version}.jar"
