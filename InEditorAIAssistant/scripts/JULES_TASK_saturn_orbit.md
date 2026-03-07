# TASK FOR JULES: Saturn Orbit Camera Script — UE5.7 Python

## Goal
Create a Python script for Unreal Engine 5.7 that sets up a cinematic orbital camera
around Saturn in the level `LV_SolarSystem` for an 8-hour ambient video render.

## Repository
`InEditorAIAssistant/scripts/orbit_saturn_lv_solarsystem.py`

## Context
- Project: NovaDays, UE5.7
- Level: `/Game/SolarSystem/Maps/LV_SolarSystem`
- BP_SolarSystem actor contains all planets as procedural components (no standalone actors)
- Saturn is `SM_PlanetSphere` with relative_scale3d ≈ 6.03 inside BP_SolarSystem
- Saturn ring is `Plane` mesh with scale ≈ 30.13 (ring outer edge ≈ 3013 UU)
- Saturn world position at editor time (via socket_transform): X=3387322, Y=12872125, Z=5281746
- Orbital simulation is LIVE — planets move during gameplay

## Working Approach (CONFIRMED in v19 for other levels)
**Pivot + Attach method:**
1. Spawn empty Actor (`NB_Saturn_Pivot`) at Saturn's position
2. Spawn CineCameraActor (`NB_Saturn_Cam`) at distance ORBIT_RADIUS from pivot
3. Attach camera to pivot (KEEP_WORLD location/rotation)
4. Set camera relative rotation: Pitch=CAM_PITCH, Yaw=180° (faces planet), Roll=0
5. Create LevelSequence with 2 keyframes on pivot:
   - Positions X/Y/Z: CONSTANT (fixed)
   - Rotation ch[3]=PITCH: CONSTANT (orbit inclination)
   - Rotation ch[4]=YAW: CONSTANT (= 0)
   - Rotation ch[5]=ROLL: LINEAR 0° → -360° (this IS the orbit)

## UE5.7 Python Critical Notes
```python
# Channel order for MovieScene3DTransformTrack:
# ch[0]=TransX  ch[1]=TransY  ch[2]=TransZ
# ch[3]=RotPITCH  ch[4]=RotYAW  ch[5]=RotROLL

# add_key MUST use named params:
ch.add_key(time=unreal.FrameNumber(fr), new_value=val, sub_frame=0.0,
           interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)

# Get Saturn position (works in editor mode):
for a in EAS.get_all_level_actors():
    if 'BP_SolarSystem' in a.get_actor_label():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            sm  = c.get_editor_property('static_mesh')
            sc3 = c.get_editor_property('relative_scale3d')
            if sm and 'PlanetSphere' in sm.get_name() and 5.5 < sc3.x < 6.5:
                t = c.get_socket_transform(unreal.Name('None'))
                saturn_pos = t.translation  # X=3387322, Y=12872125, Z=5281746
```

## Required Parameters
```python
ORBIT_RADIUS    = 7000.0    # UU from Saturn center (outside rings ~3013u)
INCLINATION_DEG = 30.0      # above ring plane → rings visible as ellipse
CAM_PITCH_LOCAL = -20.0     # camera tilts down toward Saturn
DURATION_SEC    = 720       # 12 min per orbit loop (extend to 8hr in MRQ)
FPS             = 24
FOCAL_LENGTH    = 85.0      # telephoto → Saturn fills frame nicely
SEQ_NAME        = "SQ_Saturn_Orbit_v1"
SEQ_PATH        = "/Game/Temp"
```

## What Script Must Do
1. Find Saturn's world position via socket_transform on SM_PlanetSphere sc≈6.03
2. Delete old NB_Saturn_Pivot if exists
3. Spawn NB_Saturn_Pivot at Saturn pos with roll=-INCLINATION_DEG
4. Spawn or reuse NB_Saturn_Cam at (Saturn.X + ORBIT_RADIUS, Saturn.Y, Saturn.Z)
5. Set camera filmback 36×20.25mm (16:9), focal=FOCAL_LENGTH
6. Attach cam to pivot KEEP_WORLD
7. Set cam relative rotation (PITCH=CAM_PITCH_LOCAL, YAW=180, ROLL=0)
8. Create/clear LevelSequence SQ_Saturn_Orbit_v1 in /Game/Temp
9. Add Camera Cuts track bound to NB_Saturn_Cam
10. Add Transform track to pivot: positions CONSTANT, ch[5] ROLL 0→-360 LINEAR
11. Save sequence
12. Log: Saturn pos, orbit radius, confirmation

## Reference Script (partially working, needs cleanup)
See: `InEditorAIAssistant/scripts/orbit_v19_lv11.py` — this is the CONFIRMED working
version for a different level. The Saturn version needs the Saturn position finder
(socket_transform method) instead of actor search by name.

## How to Run
```
# In UE5 Output Log → Python:
exec(open(r'C:/Users/centu/UEProjects/nightbird-tools/InEditorAIAssistant/scripts/orbit_saturn_lv_solarsystem.py').read())
```
Or via Remote Control API (ExecuteConsoleCommand now enabled in project settings).

## Known Issues in Current orbit_v1_saturn.py
- Script works correctly (confirmed: camera at correct position, Saturn visible in viewport)
- Editor viewport shows Saturn dark (no editor ambient light) — NORMAL, render will be lit
- Camera Cut binding may return warning from Python — fix manually in Sequencer UI if needed
