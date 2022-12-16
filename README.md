# ModsSelect
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/RenardElectric/ModsSelect)](https://github.com/RenardElectric/ModsSelect/releases/latest)
[![GitHub all releases](https://img.shields.io/github/downloads/RenardElectric/ModsSelect/total?color=green)](https://github.com/RenardElectric/ModsSelect)
[![GitHub issues](https://img.shields.io/github/issues/RenardElectric/ModsSelect?color=yellow)](https://github.com/RenardElectric/ModsSelect/issues)
[![GitHub](https://img.shields.io/github/license/RenardElectric/ModsSelect)](https://github.com/RenardElectric/ModsSelect/blob/master/LICENSE.md)

<img src="/ModsSelect.png" width="700"/>


## Table of Content
<!-- TOC -->
* [ModsSelect](#modsselect)
  * [Table of Content](#table-of-content)
  * [Description](#description)
  * [Installation](#installation)
  * [Usage](#usage)
    * [Modifying config files](#modifying-config-files)
      * [Adding another minecraft version to the app](#adding-another-minecraft-version-to-the-app)
      * [Adding your own mods to the app](#adding-your-own-mods-to-the-app)
  * [Support](#support)
  * [Roadmap](#roadmap)
  * [Contributing](#contributing)
  * [Authors and acknowledgment](#authors-and-acknowledgment)
  * [License](#license)
<!-- TOC -->


## Description
ModsSelect is a Python app for minecraft mods.


## Installation
1. Download the latest release [here](https://github.com/RenardElectric/ModsSelect/releases/download/latest/ModsSelect-setup.exe)
2. Go to your download folder and run the file named ``ModsSelect-setup.exe``
3. Go through the installation prompt
4. Done !


## Usage
With this app you can:
* Download the mods from Modrinth and CurseForge you selected in any loader and minecraft version
* Update them to their latest version in minecraft version you choose
* Make list of mods so that you can reselect them faster


### Modifying config files
- You can change the config files to add other minecraft versions or add other mods

    > **Warning**
    > As of now, when you update the app, the config files are reset. Be sure to save them before updating if you changed them

    ### Adding another minecraft version to the app
    ``{ModsSelect Location}/config/minecraft_versions.json``
  * Add here all the minecraft versions you want

  ### Adding your own mods to the app
  ``{ModsSelect Location}/config/mods.json``
  ```json
   {
     "name": "Mod name", 
      "category":null, 
     "id":null, 
     "site":null
   }
  ```
  * name: Put the name of the mod you want to add
  * category: The category you want your mod to be in, if null the mod will be placed in the other category
  * id: The id of the mod in Modrinth or CurseForge. Leave it null, the app will fill it automatically
  * site: The website were the mod comes from, only supports Modrinth and CurseForge. Leave it null, the app will fill it automatically


## Support
If you have any issues, feel free to open an issue. I will make sure that I respond in a short time.


## Roadmap
* Cleanup the code and add comments
* Keep the changes of the config files when updating
* Make the app faster


## Contributing
Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.


## Authors and acknowledgment
ttkwidgets for the CheckboxTreeview that I modified

sv_ttk for the sun valley theme


## License
This work is licensed under the GNU General Public License v3.0
