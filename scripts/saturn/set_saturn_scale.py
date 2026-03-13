import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sat = next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == 'SATURN'), None)
if sat:
    sat.set_actor_scale3d(unreal.Vector(8, 8, 8))
    scale = sat.get_actor_scale3d()
    unreal.log(f'SATURN scale set to: {scale.x}, {scale.y}, {scale.z}')
else:
    unreal.log('ERROR: SATURN not found')
