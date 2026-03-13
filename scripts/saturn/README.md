# Saturn Scene Scripts — Current State 13.03.2026

## What works RIGHT NOW in LV_Saturn_Photorealistic:
- SKYBOX_16K: SM_SkySphere + MI_Skybox_16K_001 (stars visible) ✅
- NB_Saturn_Cam: CineCamera orbiting at R~1200 UU, bound to LS_Saturn_Ambient ✅
- SATURN: BP_Saturn, scale=8,8,8

## Key scripts (apply in this order to restore state):
1. `fix_skybox_smsphere.py` — apply SM_SkySphere to SKYBOX_16K
2. `apply_saturn_materials.py` — apply MI_Gas_Planet_2 + MI_Rings_1 + MI_Atmosphere
3. `set_saturn_scale.py` — set SATURN actor scale to 8,8,8

## TODO (next step):
- Apply MI_Atmosphere_Saturn from /Game/SolarSystem (proper Saturn material!)
- Check /Game/SolarSystem/BP_Saturn — may have better setup
- Test render 5-10 frames to verify Saturn visible

## RC API call pattern:
```bash
curl -s -X PUT "http://localhost:30010/remote/object/call" \
  -H "Content-Type: application/json" \
  -d "{\"objectPath\":\"/Script/PythonScriptPlugin.Default__PythonScriptLibrary\",\"functionName\":\"ExecutePythonCommand\",\"parameters\":{\"PythonCommand\":\"exec(open(r'C:/Users/centu/UEProjects/SCRIPT.py').read())\"}}"
```
