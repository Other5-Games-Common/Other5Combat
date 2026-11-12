# Other5Combat: Other5's own dash, melee and spawn-in abilities and gun actors, in place of the Lyra-based GA_Hero_Dash1,
# GA_Melee1, GA_SpawnEffect1 and B_Pistol/B_Rifle/B_Shotgun (which public Other5Combat can only ship as stand-ins).
# Makes Blueprint children of the C++ abilities (UOther5DashAbility, UOther5MeleeAbility, UOther5SpawnInAbility) with the
# same settings, simple gun actors (a skeletal mesh with the weapon's mesh and anim Blueprint), and points
# BP_Other5ProjectileCharacter's Starting Abilities and DA_Pistol/DA_Rifle/DA_Shotgun at them. Rerunnable.
# Run headless or in the editor: py "<this file>"
import unreal

def log(s):
	unreal.log("OwnCombat: " + s)

R = unreal.AssetRegistryHelpers.get_asset_registry()
R.search_all_assets(True)
Tools = unreal.AssetToolsHelpers.get_asset_tools()
Lib = unreal.EditorAssetLibrary
Sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SubLib = unreal.SubobjectDataBlueprintFunctionLibrary

def Load(Path):
	A = unreal.load_asset(Path)
	if not A:
		log("missing " + Path)
	return A

def MakeBlueprint(Path, Parent):
	if Lib.does_asset_exist(Path):
		return unreal.load_asset(Path)
	F = unreal.BlueprintFactory()
	F.set_editor_property("parent_class", Parent)
	Folder, Name = Path.rsplit("/", 1)
	BP = Tools.create_asset(Name, Folder, unreal.Blueprint, F)
	log("created " + Path)
	return BP

def Defaults(BP, Values):
	unreal.BlueprintEditorLibrary.compile_blueprint(BP)
	Cdo = unreal.get_default_object(BP.generated_class())
	for K, V in Values.items():
		Cdo.set_editor_property(K, V)
	unreal.BlueprintEditorLibrary.compile_blueprint(BP)
	Lib.save_loaded_asset(BP, only_if_is_dirty=False)

Actions = "/Other5Characters/Mannequin/Animations/Actions/"

# ---- Abilities
Dash = MakeBlueprint("/Other5Combat/Characters/Abilities/BP_Other5Dash", unreal.Other5DashAbility)
Defaults(Dash, {"strength": 1850.0, "push_seconds": 0.25, "seconds": 0.55,
	"forward_montage": Load(Actions + "AM_MM_Dash_Forward"), "back_montage": Load(Actions + "AM_MM_Dash_Backward"),
	"left_montage": Load(Actions + "AM_MM_Dash_Left"), "right_montage": Load(Actions + "AM_MM_Dash_Right")})
Melee = MakeBlueprint("/Other5Combat/Characters/Abilities/BP_Other5Melee", unreal.Other5MeleeAbility)
Defaults(Melee, {"montage": Load("/Other5Combat/Characters/Heroes/Animations/Actions/AM_MM_Pistol_Melee"), "damage": 25.0,
	"distance": 350.0, "radius": 96.0, "half_height": 48.0, "lunge_strength": 2200.0, "lunge_seconds": 0.05})
Spawn = MakeBlueprint("/Other5Combat/Characters/Abilities/BP_Other5SpawnIn", unreal.Other5SpawnInAbility)
Defaults(Spawn, {"montage": Load(Actions + "AM_MM_Pistol_Spawn"), "enable_input_fraction": 0.75})

# ---- Guns: a skeletal mesh (socket "Muzzle" is where shots come from) with the weapon's mesh and anim Blueprint.
def MeshComponent(BP):
	for H in Sub.k2_gather_subobject_data_for_blueprint(BP):
		O = SubLib.get_object(SubLib.get_data(H))
		if O and isinstance(O, unreal.SkeletalMeshComponent):
			return O
	Root = Sub.k2_gather_subobject_data_for_blueprint(BP)[0]
	Handle, Fail = Sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=Root, new_class=unreal.SkeletalMeshComponent, blueprint_context=BP))
	Sub.rename_subobject(Handle, unreal.Text("Mesh"))
	return SubLib.get_object(SubLib.get_data(Handle))

Guns = {}
for Name, Mesh, Anim in (("Pistol", "/Other5Combat/Weapons/Pistol/Mesh/SK_Pistol", "/Other5Combat/Weapons/Pistol/Animations/ABP_Weap_Pistol"),
		("Rifle", "/Other5Combat/Weapons/Rifle/Mesh/SK_Rifle", "/Other5Combat/Weapons/Rifle/Animations/ABP_Weap_Rifle"),
		("Shotgun", "/Other5Combat/Weapons/Shotgun/Mesh/SKM_Shotgun", "/Other5Combat/Weapons/Shotgun/Animations/ABP_Weap_Shotgun")):
	# Each gun is its own Actor with its own Mesh component (no shared parent: setting a child's inherited component edits the parent's template).
	BP = MakeBlueprint("/Other5Combat/Weapons/%s/BP_Other5%s" % (Name, Name), unreal.Actor)
	Comp = MeshComponent(BP)
	Comp.set_skeletal_mesh_asset(Load(Mesh))
	AnimBP = Load(Anim)
	if AnimBP:
		Comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
		Comp.set_editor_property("anim_class", AnimBP.generated_class())
	unreal.BlueprintEditorLibrary.compile_blueprint(BP)
	Lib.save_loaded_asset(BP, only_if_is_dirty=False)
	Guns[Name] = BP

# ---- Point the weapon data and the character at them.
for Name, Data in (("Pistol", "/Other5Combat/Weapons/Pistol/DA_Pistol"), ("Rifle", "/Other5Combat/Weapons/Rifle/DA_Rifle"), ("Shotgun", "/Other5Combat/Weapons/Shotgun/DA_Shotgun")):
	D = Load(Data)
	D.set_editor_property("weapon_actor_class", Guns[Name].generated_class())
	Lib.save_loaded_asset(D, only_if_is_dirty=False)
	log("%s weapon actor = %s" % (Data.rsplit("/", 1)[-1], Guns[Name].get_name()))

Swap = {"GA_Hero_Dash1_C": Dash, "GA_Melee1_C": Melee, "GA_SpawnEffect1_C": Spawn}
Char = Load("/Other5Combat/Characters/BP_Other5ProjectileCharacter")
Cdo = unreal.get_default_object(Char.generated_class())
Entries = list(Cdo.get_editor_property("starting_abilities"))
for E in Entries:
	A = E.get_editor_property("ability")
	if A and A.get_name() in Swap:
		log("starting ability %s -> %s" % (A.get_name(), Swap[A.get_name()].get_name()))
		E.set_editor_property("ability", Swap[A.get_name()].generated_class())
Cdo.set_editor_property("starting_abilities", Entries)
unreal.BlueprintEditorLibrary.compile_blueprint(Char)
Lib.save_loaded_asset(Char, only_if_is_dirty=False)
log("starting abilities now: %s" % [E.get_editor_property("ability").get_name() if E.get_editor_property("ability") else None
	for E in unreal.get_default_object(Char.generated_class()).get_editor_property("starting_abilities")])
