# CURSOR TASK: Fix SKYBOX_16K — LV_Saturn_Photorealistic

## Status: OPEN
## Priority: HIGH
## Assigned: Cursor

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

**Option A (preferred)**: Set scale X to negative to flip normals:
```python
comp.set_editor_property("relative_scale3d", unreal.Vector(-800000, 800000, 800000))
```

**Option B**: Find a proper inverted-sphere mesh in Space_Creator_Pro content:
- Check `/Game/Space_Creator_Pro/` for meshes named like `SM_Sky*`, `SM_Dome*`, `SM_Skybox*`
- Or use `SM_SkySphere` from Engine content
- Apply that mesh instead of Sphere

**Option C**: Set material to Two-Sided if MI_Skybox_MilkyWay supports it.

---

## Script requirements
File: `fix_skybox_pr.py`

```python
import unreal
# Find SKYBOX_16K
# Fix normals (Option A or B or C)
# Verify by logging mesh name + mat name + scale
# Write log to: C:/Users/centu/UEProjects/fix_skybox_log.txt
```

---

## How to run
Via RC API (PowerShell):
```powershell
$body = @'
{"objectPath":"/Script/PythonScriptPlugin.Default__PythonScriptLibrary","functionName":"ExecutePythonCommand","parameters":{"PythonCommand":"exec(open(r'C:/Users/centu/UEProjects/fix_skybox_pr.py').read())"}}
'@
Invoke-RestMethod -Method Put -Uri "http://localhost:30010/remote/object/call" -ContentType "application/json" -Body $body
```

---

## Output
When done:
1. Save script to: `InEditorAIAssistant/scripts/fix_skybox_pr.py` in this repo
2. Update this file: change `Status: OPEN` → `Status: DONE` and add result notes
3. Log file at: `C:/Users/centu/UEProjects/fix_skybox_log.txt`

---

## Context
- UE 5.7
- RC API: localhost:30010
- Level: LV_Saturn_Photorealistic (must be open in editor)
- Python via `ExecutePythonCommand`
- get_all_channels() NOT get_channels() in UE5.7
- unreal.Rotator(pitch=, yaw=, roll=) — named params required
