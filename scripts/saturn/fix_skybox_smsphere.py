import unreal
# Apply SM_SkySphere (inward normals) to SKYBOX_16K actor
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sky = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == 'SKYBOX_16K'), None)
if sky:
    comps = sky.get_components_by_class(unreal.StaticMeshComponent)
    if comps:
        mesh = unreal.load_asset('/Engine/EngineSky/SM_SkySphere')
        mat = unreal.load_asset('/Game/Space_Creator_Pro/Space_Skybox_Library_16K_1/Material_Instances/MI_Skybox_16K_001')
        if mesh:
            comps[0].set_editor_property('static_mesh', mesh)
            comps[0].set_editor_property('relative_scale3d', unreal.Vector(800000, 800000, 800000))
        if mat:
            comps[0].set_material(0, mat)
        unreal.log('SKYBOX_16K: SM_SkySphere + MI_Skybox_16K_001 applied')
else:
    unreal.log('ERROR: SKYBOX_16K not found')
