import unreal

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
log = []

sky = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "SKYBOX_16K"), None)

if not sky:
    log.append("ERROR: SKYBOX_16K not found")
else:
    log.append(f"SKYBOX_16K found: {sky.get_class().get_name()}")
    comps = sky.get_components_by_class(unreal.StaticMeshComponent)

    if not comps:
        log.append("ERROR: no StaticMeshComponent found")
    else:
        comp = comps[0]
        old_scale = comp.get_editor_property("relative_scale3d")
        log.append(f"Old scale: ({old_scale.x}, {old_scale.y}, {old_scale.z})")

        # Option A: flip X to invert normals so camera inside sees the texture
        new_scale = unreal.Vector(-800000.0, 800000.0, 800000.0)
        comp.set_editor_property("relative_scale3d", new_scale)

        verify = comp.get_editor_property("relative_scale3d")
        log.append(f"New scale: ({verify.x}, {verify.y}, {verify.z})")

        mat = comp.get_material(0)
        log.append(f"Material: {mat.get_name() if mat else 'None'}")
        log.append("SKYBOX fix applied: normals inverted via negative X scale.")

open("C:/Users/centu/UEProjects/fix_skybox_log.txt", "w").write("\n".join(log))
unreal.log("\n".join(log))
