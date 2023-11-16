from subprocess import check_output
from FloorplanToBlenderLib import (
    IO,
    config,
    const,
)
import os

"""
Create Blender Project from floorplan
This file contains a simple example implementation of creations of 3d models from
floorplans. You will need blender and an image of a floorplan to make this work.

FloorplanToBlender3d
Copyright (C) 2022 Daniel Westberg
"""


def create_blender_project(data_paths, target_folder):
    blender_install_path = ""
    blender_install_path = config.get_default_blender_installation_path()
    program_path = os.path.dirname(os.path.realpath(__file__))
    blender_script_path = const.BLENDER_SCRIPT_PATH

    if not os.path.exists("." + target_folder):
        os.makedirs("." + target_folder)

    target_base = target_folder + const.TARGET_NAME
    target_path = target_base + const.BASE_FORMAT
    target_path = (
        IO.get_next_target_base_name(target_base, target_path) + const.BASE_FORMAT
    )

    # Create blender project
    check_output(
        [
            blender_install_path,
            "-noaudio",  # this is a dockerfile ubuntu hax fix
            "--background",
            "--python",
            blender_script_path,
            '\\'.join(program_path.split('\\')[:-1]),  # Send this as parameter to script
            target_path,
        ]
        + data_paths
    )
    print('-------------------------------')
    outformat = config.get(
        const.SYSTEM_CONFIG_FILE_NAME, "SYSTEM", const.STR_OUT_FORMAT
    ).replace('"', "")
    # Transform .blend project to another format!
    if outformat != ".blend":
        check_output(
            [
                blender_install_path,
                "-noaudio",  # this is a dockerfile ubuntu hax fix
                "--background",
                "--python",
                "./Blender/blender_export_any.py",
                "." + target_path,
                outformat,
                target_base + outformat,
            ]
        )
        print("Object created at:" + program_path + target_base + outformat)

    print("Project created at: " + '/'.join(program_path.split('\\')[:-1]) + target_path)

    return '/'.join(program_path.split('\\')[:-1]) + target_path