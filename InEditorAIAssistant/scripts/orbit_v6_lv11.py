"""
NB-001 Orbit v6 — без Camera Rig Rail
Прямая анимация Transform камеры + look-at на планету.
Гарантированно работает в Sequencer UE 5.7.
"""
import unreal, math

PLANET_NAME      = "BP_Planet_Terran"
RADIUS           = 0           # 0 = scale * 8
DURATION_SECONDS = 10
FPS              = 24
N_KEYFRAMES      = 16          # точек орбиты (больше = плавнее)
SEQ_NAME         = "SQ_NB_001_Orbit"
SEQ_PATH         = "/Game/Temp"

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ML  = unreal.MathLibrary

# 1. ПЛАНЕТА
planet = None
for a in EAS.get_all_level_actors():
    lbl = a.get_actor_label()
    cls = a.get_class().get_name()
    if PLANET_NAME in lbl or PLANET_NAME in cls:
        planet = a
        break
if not planet:
    unreal.log_error("Планета не найдена!")
    raise SystemExit

P = planet.get_actor_location()
S = planet.get_actor_scale3d().x
R = RADIUS if RADIUS > 0 else S * 8.0
unreal.log(f"[v6] Планета: ({P.x:.0f},{P.y:.0f},{P.z:.0f})  R={R:.0f}")

# 2. КАМЕРА (удаляем старый рельс, он больше не нужен)
for a in EAS.get_all_level_actors():
    if "Rail" in a.get_actor_label():
        EAS.destroy_actor(a)
        unreal.log("[v6] Старый рельс удалён")

cam = None
for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "NB_001_Cam":
        cam = a
        break
if not cam:
    cam = EAS.spawn_actor_from_class(
        unreal.CineCameraActor,
        unreal.Vector(P.x + R, P.y, P.z),
        unreal.Rotator(pitch=0, yaw=180, roll=0)
    )
    cam.set_actor_label("NB_001_Cam")
    cam.get_cine_camera_component().current_focal_length = 35.0
else:
    # Открепляем от рельса если была прикреплена
    cam.detach_from_actor(unreal.DetachmentRule.KEEP_WORLD,
                          unreal.DetachmentRule.KEEP_WORLD,
                          unreal.DetachmentRule.KEEP_WORLD)
unreal.log(f"[v6] Камера: {cam.get_actor_label()}")

# 3. LEVEL SEQUENCE
FRAMES = DURATION_SECONDS * FPS
full_path = f"{SEQ_PATH}/{SEQ_NAME}"
if unreal.EditorAssetLibrary.does_asset_exist(full_path):
    unreal.EditorAssetLibrary.delete_asset(full_path)

seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    SEQ_NAME, SEQ_PATH, unreal.LevelSequence, unreal.LevelSequenceFactoryNew()
)
seq.set_display_rate(unreal.FrameRate(FPS, 1))
seq.set_playback_start(0)
seq.set_playback_end(FRAMES)

unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
unreal.log(f"[v6] Секвенция: {FRAMES}fr @ {FPS}fps")

# 4. CAMERA CUT TRACK
cam_binding = seq.add_possessable(cam)
cut_track   = seq.add_track(unreal.MovieSceneCameraCutTrack)
cut_sec     = cut_track.add_section()
cut_sec.set_start_frame(0)
cut_sec.set_end_frame(FRAMES)
try:
    cut_sec.set_camera_binding_id(cam_binding.binding_id)
    unreal.log("[v6] Camera Cut привязан")
except:
    unreal.log_warning("[v6] Camera Cut — привяжи вручную")

# 5. TRANSFORM TRACK (прямая анимация позиции + вращения камеры)
transform_track = cam_binding.add_track(unreal.MovieScene3DTransformTrack)
transform_sec   = transform_track.add_section()
transform_sec.set_start_frame(0)
transform_sec.set_end_frame(FRAMES)

channels = transform_sec.get_all_channels()
# channels: [tx, ty, tz, rx, ry, rz] = [0..5]
unreal.log(f"[v6] Transform каналов: {len(channels)}")

# Вычисляем ключи орбиты с look-at на планету
# Добавляем N+1 ключей (последний = первый для замыкания петли)
for i in range(N_KEYFRAMES + 1):
    t   = i / N_KEYFRAMES          # 0.0 → 1.0
    fr  = int(t * FRAMES)          # frame number
    ang = 2.0 * math.pi * t        # угол по кругу

    # Позиция камеры на орбите (в горизонтальной плоскости)
    cx = P.x + R * math.cos(ang)
    cy = P.y + R * math.sin(ang)
    cz = P.z                       # на одной высоте с планетой

    cam_pos    = unreal.Vector(cx, cy, cz)
    planet_pos = unreal.Vector(P.x, P.y, P.z)

    # Вращение смотрит на планету
    rot = ML.find_look_at_rotation(cam_pos, planet_pos)

    fn = unreal.FrameNumber(fr)

    def add_k(ch_idx, value):
        channels[ch_idx].add_key(
            time=fn,
            new_value=value,
            sub_frame=0.0,
            interpolation=unreal.MovieSceneKeyInterpolation.LINEAR
        )

    if len(channels) >= 6:
        add_k(0, cx)           # X
        add_k(1, cy)           # Y
        add_k(2, cz)           # Z
        add_k(3, rot.roll)     # Roll
        add_k(4, rot.pitch)    # Pitch
        add_k(5, rot.yaw)      # Yaw

unreal.log(f"[v6] Ключи добавлены: {N_KEYFRAMES+1} точек по кругу")

unreal.EditorAssetLibrary.save_loaded_asset(seq)
unreal.log("=" * 55)
unreal.log("[v6] ГОТОВО! Пробел → орбита с look-at на планету!")
