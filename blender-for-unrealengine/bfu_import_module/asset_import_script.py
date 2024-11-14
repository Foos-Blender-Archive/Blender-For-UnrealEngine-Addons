# This script was generated with the addons Unreal Engine Assets Exporter.
# This script should be run in Unreal Engine to import into Unreal Engine 4 and 5 assets.
# The assets are exported from from Unreal Engine Assets Exporter. More detail here. https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# Use the following command in Unreal Engine cmd consol to import assets: 
# py "[ScriptLocation]\asset_import_script.py"

import importlib
import importlib.util
import os
from . import import_module_utils


def RunImportScriptWithJsonData():
    # Prepare process import
    json_data_file = 'ImportAssetData.json'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    import_file_path = os.path.join(dir_path, json_data_file)
    assets_data = import_module_utils.JsonLoadFile(import_file_path)
    
    file_path = os.path.join(assets_data["info"]["addon_path"],'run_unreal_import_script.py')
    spec = importlib.util.spec_from_file_location("__import_assets__", file_path)
    module = importlib.util.module_from_spec(spec)

    # Run script module function
    spec.loader.exec_module(module)
    module.run_from_asset_import_script(import_file_path)

if __name__ == "__main__":
    RunImportScriptWithJsonData()

