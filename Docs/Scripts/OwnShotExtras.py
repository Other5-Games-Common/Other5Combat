# Makes Other5's own materials for the C++ shot effects' extras (UOther5WeaponData's ShellMaterial and ImpactDecal
# defaults): M_Shell, a brass casing, and M_BulletHole, a dark round decal with a soft edge. Rerunnable: it rebuilds both.
# Headless: UnrealEditor-Cmd Other5.uproject -run=pythonscript -script=<this file> -unattended -nosplash -nullrhi
import unreal

Folder = "/Other5Combat/Effects/Materials"
Tools = unreal.AssetToolsHelpers.get_asset_tools()
Lib = unreal.MaterialEditingLibrary


def Fresh(Name):
	Path = "%s/%s" % (Folder, Name)
	if unreal.EditorAssetLibrary.does_asset_exist(Path):
		M = unreal.EditorAssetLibrary.load_asset(Path)
		Lib.delete_all_material_expressions(M)
		return M
	return Tools.create_asset(Name, Folder, unreal.Material, unreal.MaterialFactoryNew())


def Constant(M, Value, X, Y):
	C = Lib.create_material_expression(M, unreal.MaterialExpressionConstant, X, Y)
	C.set_editor_property("r", Value)
	return C


def Colour(M, R, G, B, X, Y):
	C = Lib.create_material_expression(M, unreal.MaterialExpressionConstant3Vector, X, Y)
	C.set_editor_property("constant", unreal.LinearColor(R, G, B, 1.0))
	return C


# Brass: metallic, fairly smooth.
Shell = Fresh("M_Shell")
Lib.connect_material_property(Colour(Shell, 0.75, 0.52, 0.18, -300, -100), "", unreal.MaterialProperty.MP_BASE_COLOR)
Lib.connect_material_property(Constant(Shell, 1.0, -300, 50), "", unreal.MaterialProperty.MP_METALLIC)
Lib.connect_material_property(Constant(Shell, 0.3, -300, 150), "", unreal.MaterialProperty.MP_ROUGHNESS)
Lib.recompile_material(Shell)
unreal.EditorAssetLibrary.save_loaded_asset(Shell)

# Bullet hole: a deferred decal, opaque near black at the middle fading to nothing at the edge of its box.
Hole = Fresh("M_BulletHole")
Hole.set_editor_property("material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL)
Hole.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
Uv = Lib.create_material_expression(Hole, unreal.MaterialExpressionTextureCoordinate, -900, 200)
Centre = Lib.create_material_expression(Hole, unreal.MaterialExpressionConstant2Vector, -900, 320)
Centre.set_editor_property("r", 0.5)
Centre.set_editor_property("g", 0.5)
Distance = Lib.create_material_expression(Hole, unreal.MaterialExpressionDistance, -700, 250)
Lib.connect_material_expressions(Uv, "", Distance, "A")
Lib.connect_material_expressions(Centre, "", Distance, "B")
# 1 inside radius 0.2, 0 from radius 0.5 out: 1 - saturate((d - 0.2) / 0.3).
Sub = Lib.create_material_expression(Hole, unreal.MaterialExpressionSubtract, -550, 250)
Lib.connect_material_expressions(Distance, "", Sub, "A")
Lib.connect_material_expressions(Constant(Hole, 0.2, -700, 380), "", Sub, "B")
Div = Lib.create_material_expression(Hole, unreal.MaterialExpressionDivide, -420, 250)
Lib.connect_material_expressions(Sub, "", Div, "A")
Lib.connect_material_expressions(Constant(Hole, 0.3, -550, 380), "", Div, "B")
Sat = Lib.create_material_expression(Hole, unreal.MaterialExpressionSaturate, -300, 250)
Lib.connect_material_expressions(Div, "", Sat, "")
Inv = Lib.create_material_expression(Hole, unreal.MaterialExpressionOneMinus, -180, 250)
Lib.connect_material_expressions(Sat, "", Inv, "")
Lib.connect_material_property(Inv, "", unreal.MaterialProperty.MP_OPACITY)
Lib.connect_material_property(Colour(Hole, 0.02, 0.018, 0.015, -300, -100), "", unreal.MaterialProperty.MP_BASE_COLOR)
Lib.connect_material_property(Constant(Hole, 0.9, -300, 50), "", unreal.MaterialProperty.MP_ROUGHNESS)
Lib.recompile_material(Hole)
unreal.EditorAssetLibrary.save_loaded_asset(Hole)
unreal.log("OwnShotExtras: made %s and %s" % (Shell.get_path_name(), Hole.get_path_name()))
