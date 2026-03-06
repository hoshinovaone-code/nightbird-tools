"""
NB-001 Orbit v9 — ИСПРАВЛЕН ПОРЯДОК КАНАЛОВ (Jules fix)

НАЙДЕННЫЙ БАГ (v6-v8):
  Неправильный порядок каналов Transform Track.
  Реальный порядок (по анализу Jules / UE Rotator convention):
    channels[3] = Rotation PITCH  (не Roll!)
    channels[4] = Rotation YAW    (не Pitch!)
    channels[5] = Rotation ROLL   (не Yaw!)
  В v6-v8 канал Yaw [4] всегда получал rot.pitch = 0°
  → камера смотрела вдоль +X и видела планету только случайно (~ang=π).

ИСПРАВЛЕНИЯ:
  add_k(3, rot.pitch)     ← Pitch в канал Pitch ✓
  add_k(4, yaw_monotonic) ← Yaw в канал Yaw ✓ + монотонный (без flip)
  add_k(5, rot.roll)      ← Roll в канал Roll ✓
"""
import unreal, math

PLANET_NAME      = "BP_Planet_Terran"
RADIUS           = 0
RADIUS_MULT      = 8.0
DURATION_SECONDS = 60
FPS              = 24
N_KEYFRAMES      = 48
FOCAL_LENGTH     = 50.0
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
    unreal.log_error("[v9] Планета не найдена!")
    raise SystemExit

P = planet.get_actor_location()
S = planet.get_actor_scale3d().x
R = RADIUS if RADIUS > 0 else S * RADIUS_MULT
unreal.log(f"[v9] Планета: ({P.x:.0f},{P.y:.0f},{P.z:.0f})  scale={S:.2f}  R={R:.0f}")

# 2. КАМЕРА
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
else:
    cam.detach_from_actor(
        unreal.DetachmentRule.KEEP_WORLD,
        unreal.DetachmentRule.KEEP_WORLD,
        unreal.DetachmentRule.KEEP_WORLD
    )
cam.get_cine_camera_component().current_focal_length = FOCAL_LENGTH
unreal.log(f"[v9] Камера: {cam.get_actor_label()}  focal={FOCAL_LENGTH}mm")

# 3. LEVEL SEQUENCE
FRAMES    = DURATION_SECONDS * FPS
try:
    unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
except: pass

full_path = f"{SEQ_PATH}/{SEQ_NAME}"
if unreal.EditorAssetLibrary.does_asset_exist(full_path):
    if unreal.EditorAssetLibrary.delete_asset(full_path):
        unreal.log("[v9] Старая секвенция удалена")
        seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            SEQ_NAME, SEQ_PATH, unreal.LevelSequence, unreal.LevelSequenceFactoryNew()
        )
    else:
        unreal.log_warning("[v9] delete заблокирован — загружаем и очищаем")
        seq = unreal.load_asset(full_path)
        for t in list(seq.get_tracks()):
            seq.remove_track(t)
        for b in list(seq.get_bindings()):
            for t in list(b.get_tracks()):
                b.remove_track(t)
else:
    seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        SEQ_NAME, SEQ_PATH, unreal.LevelSequence, unreal.LevelSequenceFactoryNew()
    )

if not seq:
    unreal.log_error("[v9] seq=None. Закрой Sequencer вручную и перезапусти.")
    raise SystemExit

seq.set_display_rate(unreal.FrameRate(FPS, 1))
seq.set_playback_start(0)
seq.set_playback_end(FRAMES)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
unreal.log(f"[v9] Секвенция: {FRAMES}fr @ {FPS}fps = {DURATION_SECONDS}s")

# 4. CAMERA CUT TRACK
cam_binding = seq.add_possessable(cam)
cut_track   = seq.add_track(unreal.MovieSceneCameraCutTrack)
cut_sec     = cut_track.add_section()
cut_sec.set_start_frame(0)
cut_sec.set_end_frame(FRAMES)
try:
    cut_sec.set_camera_binding_id(cam_binding.binding_id)
    unreal.log("[v9] Camera Cut OK")
except Exception as e:
    unreal.log_warning(f"[v9] Camera Cut bind: {e}")

# 5. TRANSFORM TRACK
transform_track = cam_binding.add_track(unreal.MovieScene3DTransformTrack)
transform_sec   = transform_track.add_section()
transform_sec.set_start_frame(0)
transform_sec.set_end_frame(FRAMES)
channels = transform_sec.get_all_channels()
unreal.log(f"[v9] Каналов: {len(channels)}")

# 6. КЛЮЧИ ОРБИТЫ — ПРАВИЛЬНЫЙ ПОРЯДОК КАНАЛОВ
# [3]=Pitch [4]=Yaw [5]=Roll  (Jules / UE Rotator convention)
for i in range(N_KEYFRAMES + 1):
    t   = i / N_KEYFRAMES
    fr  = int(t * FRAMES)
    ang = 2.0 * math.pi * t

    cx = P.x + R * math.cos(ang)
    cy = P.y + R * math.sin(ang)
    cz = P.z

    cam_pos    = unreal.Vector(cx, cy, cz)
    planet_pos = unreal.Vector(P.x, P.y, P.z)
    rot = ML.find_look_at_rotation(cam_pos, planet_pos)

    # Монотонный Yaw: 180° → 540° (без flip на 0/360)
    yaw_monotonic = math.degrees(ang) + 180.0

    fn = unreal.FrameNumber(fr)

    def add_k(ch_idx, value):
        channels[ch_idx].add_key(
            time=fn,
            new_value=value,
            sub_frame=0.0,
            interpolation=unreal.MovieSceneKeyInterpolation.AUTO
        )

    if len(channels) >= 6:
        add_k(0, cx)              # Translation X
        add_k(1, cy)              # Translation Y
        add_k(2, cz)              # Translation Z
        add_k(3, rot.pitch)       # PITCH  [3] ← исправлено (было rot.roll)
        add_k(4, yaw_monotonic)   # YAW    [4] ← исправлено (было rot.pitch=0!)
        add_k(5, rot.roll)        # ROLL   [5] ← исправлено (было rot.yaw)

unreal.log(f"[v9] Ключей: {N_KEYFRAMES+1}  Channels: [3]=Pitch [4]=Yaw [5]=Roll")
unreal.log(f"[v9] Yaw: 180→540° монотонно, interp=AUTO")

unreal.EditorAssetLibrary.save_loaded_asset(seq)
unreal.log("=" * 55)
unreal.log(f"[v9] ГОТОВО! Запусти Пробел → планета всегда в центре кадра!")
