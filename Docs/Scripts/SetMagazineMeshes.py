# Points each weapon data asset at its dropped-magazine mesh from ExtractMagazine.py. Rerunnable:
#   UnrealEditor-Cmd.exe Other5.uproject -run=pythonscript -script="<this file>"
import unreal

GUNS = ["Pistol"]

for gun in GUNS:
    data = unreal.load_asset("/Other5Combat/Weapons/%s/DA_%s" % (gun, gun))
    mesh = unreal.load_asset("/Other5Combat/Weapons/%s/Mesh/SM_%s_Magazine" % (gun, gun))
    data.set_editor_property("magazine_mesh", mesh)
    unreal.EditorAssetLibrary.save_loaded_asset(data, False)
    unreal.log_warning("SetMagazineMeshes: DA_%s -> %s" % (gun, mesh.get_path_name()))
