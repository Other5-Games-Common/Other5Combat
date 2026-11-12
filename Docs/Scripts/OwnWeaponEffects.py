# Other5Combat: Other5's own weapon effects in place of Lyra's last Blueprints (2026-11-12). Rerunnable.
#  - AN_Melee, AN_Reload: plain anim notifies of Other5's own at Lyra's paths (the melee and reload montages use them;
#    Other5's abilities do their own timing, so they don't need to do anything);
#  - W_Reticle_Pistol1: a Widget Blueprint child of Other5's C++ reticle (UOther5Reticle, drawn in code), at Lyra's path
#    (the HUD and WBP_Reticle use it);
#  - the guns (BP_Other5Pistol/Rifle/Shotgun) need no anim Blueprint: ABP_Weap_* only held the reference pose;
#  - ProjTestMap's display rifle and shotgun become Other5's gun actors;
#  - the weapon data's fire camera shake (Other5's own kick, UOther5FireCameraShake) scaled per weapon;
#  - deletes the Lyra fire cues (GCN_Weapon_*_Fire) and what only they used: the character's own shot effects
#    (Other5WeaponSounds.cpp: muzzle flash, tracer, impact, kick) take over once a fire cue has no notify.
# Before running: delete the Lyra AN_Melee, AN_Reload and W_Reticle_Pistol1 files (they're replaced at the same paths).
# Headless: UnrealEditor-Cmd.exe Other5.uproject -run=pythonscript -script="<this file>"
import unreal

def log(s):
	unreal.log("OwnWeaponEffects: " + s)

R = unreal.AssetRegistryHelpers.get_asset_registry()
R.search_all_assets(True)
Tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
Root = "/Other5Combat"

def Blueprint(Path, Parent, Factory=None):
	if EAL.does_asset_exist(Path):
		return unreal.load_asset(Path)
	F = Factory or unreal.BlueprintFactory()
	F.set_editor_property("parent_class", Parent)
	Folder, Name = Path.rsplit("/", 1)
	Asset = Tools.create_asset(Name, Folder, unreal.WidgetBlueprint if isinstance(F, unreal.WidgetBlueprintFactory) else unreal.Blueprint, F)
	unreal.BlueprintEditorLibrary.compile_blueprint(Asset)
	EAL.save_loaded_asset(Asset, False)
	log("created %s (%s)" % (Path, Parent.__name__))
	return Asset

# ---- Same-path replacements (made first, before anything that uses them loads)
Blueprint(Root + "/Characters/Heroes/Abilities/AN_Melee", unreal.AnimNotify)
Blueprint(Root + "/Characters/Heroes/Abilities/AN_Reload", unreal.AnimNotify)
Blueprint(Root + "/Weapons/Pistol/W_Reticle_Pistol1", unreal.Other5Reticle, unreal.WidgetBlueprintFactory())

# ---- Guns without anim Blueprints
Sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SubLib = unreal.SubobjectDataBlueprintFunctionLibrary
for Name in ("Pistol", "Rifle", "Shotgun"):
	BP = unreal.load_asset("%s/Weapons/%s/BP_Other5%s" % (Root, Name, Name))
	for H in Sub.k2_gather_subobject_data_for_blueprint(BP):
		O = SubLib.get_object(SubLib.get_data(H))
		if isinstance(O, unreal.SkeletalMeshComponent):
			O.set_editor_property("anim_class", None)
			O.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
	unreal.BlueprintEditorLibrary.compile_blueprint(BP)
	EAL.save_loaded_asset(BP, False)
	log("BP_Other5%s: no anim Blueprint" % Name)

# ---- Fire kick per weapon
for Name, Scale in (("Pistol", 1.0), ("Rifle", 0.6), ("Shotgun", 1.8)):
	D = unreal.load_asset("%s/Weapons/%s/DA_%s" % (Root, Name, Name))
	D.set_editor_property("fire_camera_shake", unreal.Other5FireCameraShake)
	D.set_editor_property("fire_camera_shake_scale", Scale)
	EAL.save_loaded_asset(D, False)

# ---- ProjTestMap's display guns
Map = Root + "/Maps/ProjTestMap"
World = unreal.EditorLoadingAndSavingUtils.load_map(Map)
Actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
Swapped = 0
# (The actor subsystem lists nothing in a headless run: walk the loaded world itself.)
for A in unreal.GameplayStatics.get_all_actors_of_class(World, unreal.Actor):
	ClassName = A.get_class().get_name()
	for Lyra, Own in (("B_Rifle_C", "Rifle"), ("B_Shotgun_C", "Shotgun")):
		if ClassName == Lyra:
			Gun = unreal.load_asset("%s/Weapons/%s/BP_Other5%s" % (Root, Own, Own)).generated_class()
			New = Actors.spawn_actor_from_class(Gun, A.get_actor_location(), A.get_actor_rotation())
			New.set_actor_scale3d(A.get_actor_scale3d())
			New.set_actor_label(A.get_actor_label())
			Actors.destroy_actor(A)
			Swapped += 1
# The pickups' display guns (child actors, made from the weapon data's actor class) were saved as B_Rifle/B_Shotgun:
# saving the map again stores them as Other5's guns.
World.modify()
Saved = unreal.EditorLoadingAndSavingUtils.save_map(World, Map)
log("ProjTestMap: %d placed guns swapped, map saved: %s" % (Swapped, Saved))
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)

# ---- Delete Lyra's fire cues and what only they used
Gone = []
# Users before what they use.
for P in ["/Weapons/%s/GCN_Weapon_%s_Fire" % (N, N) for N in ("Pistol", "Rifle", "Shotgun")] + \
		["/Feedback/CameraShakes/CS_Weapon_Fire_%s" % N for N in ("Pistol", "Rifle", "Shotgun")] + \
		["/Audio/Blueprints/WeaponAudioMacros", "/Weapons/Rifle/B_Rifle", "/Weapons/Shotgun/B_Shotgun"] + \
		["/Weapons/%s/Animations/ABP_Weap_%s" % (N, N) for N in ("Pistol", "Rifle", "Shotgun")] + \
		["/Weapons/B_Weapon", "/Effects/Blueprints/B_WeaponFire", "/Effects/Blueprints/B_WeaponImpacts", "/Effects/Blueprints/B_WeaponDecals"]:
	if EAL.does_asset_exist(Root + P) and EAL.delete_asset(Root + P):
		Gone.append(P)
log("deleted %d: %s" % (len(Gone), Gone))
