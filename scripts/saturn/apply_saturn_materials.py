import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sat = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == 'SATURN'), None)
if sat:
    comps = sat.get_components_by_class(unreal.StaticMeshComponent)
    mat_planet = unreal.load_asset('/Game/Space_Creator_Pro/Planet_Creator_2_V2/Materials/Material_Instances/MI_Gas_Planet_2')
    mat_atm = unreal.load_asset('/Game/Space_Creator_Pro/Planet_Creator_2_V2/Materials/Material_Instances/MI_Atmosphere')
    mat_rings = unreal.load_asset('/Game/Space_Creator_Pro/Planet_Creator_2_V2/Materials/Material_Instances/MI_Rings_1')
    if mat_planet and len(comps) > 0: comps[0].set_material(0, mat_planet)
    if mat_atm and len(comps) > 1: comps[1].set_material(0, mat_atm)
    if mat_rings and len(comps) > 2: comps[2].set_material(0, mat_rings)
    unreal.log('Saturn: MI_Gas_Planet_2 + MI_Atmosphere + MI_Rings_1 applied')
else:
    unreal.log('ERROR: SATURN not found')
