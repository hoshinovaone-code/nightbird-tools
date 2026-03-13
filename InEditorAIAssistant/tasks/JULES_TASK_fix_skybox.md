# JULES TASK: Fix SKYBOX_16K — LV_Saturn_Photorealistic

## Status: OPEN
## Priority: HIGH
## Assigned: Jules

---

## Problem
SKYBOX_16K actor in UE5.7 level `LV_Saturn_Photorealistic` shows **black background**.
- Actor: `SKYBOX_16K` (StaticMeshActor)
- Location: (0, 0, 0)
- Scale: (800000, 800000, 800000)
- Mesh: `Sphere` (Engine/BasicShapes/Sphere)
- Material: `MI_Skybox_MilkyWay`

**Root cause**: Engine `Sphere` mesh has outward-facing normals. Camera is INSIDE the sphere → black.

---

## Solution
Write Python script `fix_skybox_pr.py` that runs via UE5.7 RC API (localhost:30010).

**Option A (preferred)**: Flip normals via negative X scale:
```python
comp.set_editor_property("relative_scale3d", unreal.Vector(-800000, 800000, 800000))
```

**Option B**: Find inverted-sphere mesh in Space_Creator_Pro:
- Check `/Game/Space_Creator_Pro/` for `SM_Sky*`, `SM_Dome*`, `SM_Skybox*`
- Apply that mesh to SKYBOX_16K component

**Option C**: Two-Sided material flag on MI_Skybox_MilkyWay.

---

## Script template
```python
import unreal

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
log = []

sky = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "SKYBOX_16K"), None)
if sky:
    comps = sky.get_components_by_class(unreal.StaticMeshComponent)
    for comp in comps:
        # Apply fix here
        pass
    log.append("SKYBOX fixed")
else:
    log.append("ERROR: SKYBOX_16K not found")

open("C:/Users/centu/UEProjects/fix_skybox_log.txt", "w").write("\n".join(log))
unreal.log("\n".join(log))
```

---

## UE5.7 API Notes (critical!)
- `get_all_channels()` — CORRECT (NOT `get_channels()`)
- `unreal.Rotator(pitch=, yaw=, roll=)` — named params required
- RC API: `localhost:30010`
- Run via: `ExecutePythonCommand` on `/Script/PythonScriptPlugin.Default__PythonScriptLibrary`

---

## How to run (PowerShell)
```powershell
$body = @'
{"objectPath":"/Script/PythonScriptPlugin.Default__PythonScriptLibrary","functionName":"ExecutePythonCommand","parameters":{"PythonCommand":"exec(open(r'C:/Users/centu/UEProjects/fix_skybox_pr.py').read())"}}
'@
Invoke-RestMethod -Method Put -Uri "http://localhost:30010/remote/object/call" -ContentType "application/json" -Body $body
```

---

## OUTPUT REQUIRED
When done, **push to this repo**:
1. Script → `InEditorAIAssistant/scripts/fix_skybox_pr.py`
2. Update this file: `Status: OPEN` → `Status: DONE`, add notes about which option worked
3. Log file locally: `C:/Users/centu/UEProjects/fix_skybox_log.txt`

Claude (project manager) will read results from GitHub and run the script.
