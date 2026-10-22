# Aim down sights on right mouse (left trigger on a gamepad): maps IA_ADS in the default mapping contexts, binds it to
# InputTag.Weapon.ADS on BP_Other5ProjectileCharacter's ability input component, and gives every gun
# UOther5AimAbility with that tag. Rerunnable:
#   UnrealEditor-Cmd.exe Other5.uproject -run=pythonscript -script="<this file>"
import unreal

IA_ADS = unreal.load_asset("/Other5Combat/Input/Actions/IA_ADS")
TAG = unreal.GameplayTag()
TAG.import_text('(TagName="InputTag.Weapon.ADS")')
saved = []


def map_key(imc_path, key_name):
    imc = unreal.load_asset(imc_path)
    for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings"):
        if m.get_editor_property("action") == IA_ADS:
            return
    key = unreal.Key()
    key.set_editor_property("key_name", key_name)
    imc.map_key(IA_ADS, key)
    unreal.EditorAssetLibrary.save_loaded_asset(imc, False)
    saved.append("%s: IA_ADS on %s" % (imc_path, key_name))


map_key("/Other5Combat/Input/Mappings/IMC_Default_KBM", "RightMouseButton")
map_key("/Other5Combat/Input/Mappings/IMC_Default_Gamepad", "Gamepad_LeftTriggerAxis")

# The character's ability input component: IA_ADS -> InputTag.Weapon.ADS.
bp = unreal.load_asset("/Other5Combat/Characters/BP_Other5ProjectileCharacter")
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for handle in subsystem.k2_gather_subobject_data_for_blueprint(bp):
    data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
    comp = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
    if isinstance(comp, unreal.Other5AbilityInputComponent):
        inputs = list(comp.get_editor_property("ability_inputs"))
        if not any(i.get_editor_property("input_action") == IA_ADS for i in inputs):
            entry = unreal.Other5AbilityInput()
            entry.set_editor_property("input_action", IA_ADS)
            entry.set_editor_property("input_tag", TAG)
            inputs.append(entry)
            comp.set_editor_property("ability_inputs", inputs)
            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
            unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
            saved.append("BP_Other5ProjectileCharacter: IA_ADS -> InputTag.Weapon.ADS")

for gun in ("Pistol", "Rifle", "Shotgun"):
    data = unreal.load_asset("/Other5Combat/Weapons/%s/DA_%s" % (gun, gun))
    abilities = list(data.get_editor_property("abilities"))
    if any(a.get_editor_property("ability") == unreal.Other5AimAbility.static_class() for a in abilities):
        continue
    entry = unreal.Other5GrantedAbility()
    entry.set_editor_property("ability", unreal.Other5AimAbility.static_class())
    entry.set_editor_property("input_tag", TAG)
    abilities.append(entry)
    data.set_editor_property("abilities", abilities)
    unreal.EditorAssetLibrary.save_loaded_asset(data, False)
    saved.append("DA_%s: Other5AimAbility" % gun)

unreal.log_warning("SetupAim: " + ("; ".join(saved) if saved else "nothing to do"))
