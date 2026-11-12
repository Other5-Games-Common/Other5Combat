# Other5Combat

Everything for a shooter in an Other5 Creation: a hero with guns, grenades and health packs, pickups, abilities (dash,
melee, emote, aim down sights, heal, jump, respawn), a HUD (`WBP_Other5CombatHUD`), damage and heal effects, and input
mappings for keyboard, mouse and gamepad. Pick `BP_Other5CombatGameMode` in World Settings. It needs
**Other5Characters**.

## What's real here, and what's a stand-in
- **Other5's own:** the game modes, projectile Blueprints and characters (`BP_Other5*`), ammo and weapon data (`DA_*`),
  pickups, the HUD widgets, the fighter stats and attribute set, input mappings, the test map.
- **Real, from Unreal Engine's own templates** (shareable): the pistol, rifle and grenade-launcher meshes, materials
  and the fire sound, under `Template/`.
- **Stand-ins** for what came from **Lyra Starter Game** (Epic's licence doesn't let anyone share those source files):
  - the abilities, weapon and gameplay-effect Blueprints are empty Blueprints with the same parent classes;
  - the sounds are soft tones, the effects are empty Niagara systems, the textures are magenta/grey checks;
  - the input actions keep their value types, so controls work.

  `StandIns.json` lists each one.

  Until you bring in the real ones, weapons and abilities that come from Lyra don't do anything. Everything loads and
  compiles, and Other5's own C++ combat (damage, ammo, loot, fighter stats) still works.

To get the real look and behaviour, use **Tools > Other5 Setup** in the Other5 Creator. It takes you to **Lyra Starter
Game** on Fab (free) to get it with your own Epic account, then brings the Lyra parts into place from your copy. Your
Creation's paks then ship them, cooked, under your own licence. The real files live in your **Other5 library** (by
default a folder `Other5Library` next to your project folder), never in this repository.
