# Asset Inventory — InEditorAIAssistant
Scanned: 2026-03-13

## /Game/SolarSystem — 167 assets (Makemake Solar System)
### Key Saturn assets:
- `BP_Saturn` (in blueprints x17)
- `MI_Atmosphere_Saturn` ✅
- `MI_Atmosphere_Titan` ✅
- `SQ_Saturn_Orbit_Final` ✅
- `SQ_Saturn_Orbit_v2` ✅
- `SM_PlanetSphere`, `SM_Atmosphere`, `SM_OrbitLane`
- Textures x89 (T_Saturn_* etc)

### All Blueprints x17:
BP_Callisto, BP_Earth, BP_Europa, BP_Ganymede, BP_Io, BP_Jupiter, BP_Mars, BP_Mercury, BP_Moon, BP_Neptune, BP_Saturn, BP_Titan, BP_Uranus, BP_Venus...

### MaterialInstances x19:
MI_Atmosphere_Earth, MI_Atmosphere_Jupiter, MI_Atmosphere_Mars, MI_Atmosphere_Neptune,
**MI_Atmosphere_Saturn**, MI_Atmosphere_Titan, MI_Atmosphere_Venus,
MI_Callisto, MI_Europa, MI_Ganymede + 9 more

### Levels x5:
LV_CelestialsShowcase, LV_SolarSystem, LV_SolarSystem_Acclerated,
LV_SystemVisualization, LV_SystemVisualization_NoMoons

---

## /Game/Space_Creator_Pro — 785 assets (Makemake)
- BP_Gas_Planet_Creator_2_V2
- MI x185: MI_Gas_Planet_1-6, MI_Rings_1-6, MI_Atmosphere, MI_Skybox_16K_001-010
- TextureCube x162: T_CUBE_Skybox_011-016K
- Worlds x86: Planet Creator demo levels

---

## /Game/Cinematics — 23 assets
### Active sequences:
- `LS_Saturn_Ambient` — current, NB_Saturn_Cam orbit
- SEQ_EarthFlyIn (x9 versions)

### Levels:
- `LV_Saturn_Photorealistic` — current working level
- `LV_PlanetParade`
- `finaltestbeforedeleting`

---

## Current Level: LV_Saturn_Photorealistic (9 actors)
| Actor | Class | Location | Scale |
|-------|-------|----------|-------|
| SATURN | BP_Saturn | 0,0,0 | 8,8,8 |
| TITAN | BP_Titan | 120000,0,0 | 0.3,0.3,0.3 |
| SUN_DirectionalLight | DirectionalLight | -500000,0,200000 | 2.5,2.5,2.5 |
| SKYBOX_16K | StaticMeshActor | 0,0,0 | 800000x3 |
| SkyLight_Ambient | SkyLight | 0,0,0 | 1,1,1 |
| CAM_Saturn_Main | CineCameraActor | 800,-600,300 | 1,1,1 |
| PP_Saturn | PostProcessVolume | 0,0,0 | 1,1,1 |
| NB_Saturn_Pivot | Actor | 0,0,0 | 1,1,1 |
| NB_Saturn_Cam | CineCameraActor | 1149,314,147 | 1,1,1 |
