import unreal
# Find all Saturn-related assets in /Game/SolarSystem
AR = unreal.AssetRegistryHelpers.get_asset_registry()
f = unreal.ARFilter(recursive_paths=True, package_paths=['/Game/SolarSystem'])
assets = AR.get_assets(f)
saturn_assets = [a for a in assets if 'saturn' in str(a.asset_name).lower() or 'saturn' in str(a.package_name).lower()]
log = [f'Saturn assets in /Game/SolarSystem: {len(saturn_assets)}']
for a in saturn_assets:
    log.append(f'  [{a.asset_class_path.asset_name}] {a.package_name}')
result = '\n'.join(log)
open('C:/Users/centu/UEProjects/solarsystem_saturn.txt', 'w').write(result)
unreal.log(result)
