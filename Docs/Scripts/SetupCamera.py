# The chase camera's wall check on BP_Other5ProjectileCharacter's SpringArm: it sweeps a sphere of ProbeSize cm along the
# arm (Camera channel) and pulls the camera in where the sphere hits. At the engine's 12 cm the corners of the view's
# near plane (10 cm out, about 15 cm from the camera at 90 degrees FOV) still poked through walls the sphere touched, so
# walls and ceilings flickered open close up; 24 cm keeps the whole near plane in front of them. Rerunnable:
#   UnrealEditor-Cmd Other5.uproject -run=pythonscript -script="<this file>"
import unreal

PATH = "/Other5Combat/Characters/BP_Other5ProjectileCharacter"
PROBE = 24.0

bp = unreal.load_asset(PATH)
sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
    arm = lib.get_object(lib.get_data(h))
    if isinstance(arm, unreal.SpringArmComponent):
        arm.set_editor_property("probe_size", PROBE)
        unreal.log_warning("SetupCamera: %s probe %s cm, channel %s" % (arm.get_name(), arm.get_editor_property("probe_size"), arm.get_editor_property("probe_channel")))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
