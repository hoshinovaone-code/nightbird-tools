"""
NB-001 Orbit v10 — ФИНАЛЬНЫЙ FIX

ROOT CAUSE (найдено через RC API):
  scale=5000, base sphere r≈50 → planet_radius ≈ 250,000 units
  Старый RADIUS_MULT=8 → R=40,000 << 250,000 → камера ВНУТРИ планеты!
  Подтверждено: при R=1,500,000 планета чётко видна в кадре.

ИСПРАВЛЕНИЯ vs v8-v9:
  RADIUS_MULT: 8 → 300  (R = 5000 × 300 = 1,500,000 units)
  Channels:    [3]=Roll [4]=Pitch [5]=Yaw  ← UE стандарт (X/Y/Z оси)
               (v6 работал с этим маппингом; Jules [3]=Pitch был неверен)
  Yaw:         yaw_monotonic = degrees(ang) + 180  (180→540°, без flip)
  Interp:      AUTO (кубические кривые)
"""
import unreal, math

PLANET_NAME      = "BP_Planet_Terran"
RADIUS           = 0            # 0 = S * RADIUS_MULT
RADIUS_MULT      = 300.0        # R = scale * 300 → снаружи планеты
DURATION_SECONDS = 60
FPS              = 24
N_KEYFRAMES      = 48           # каждые 7.5° орбиты
FOCAL_LENGTH     = 50.0         # мм
SEQ_NAME         = "SQ_NB_001_Orbit"
SEQ_PATH         = "/Game/Temp"

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ML  = unreal.MathLibrary

# 1. ЗАКРЫТЬ SEQUENCER (иначе он сразу переопределяет камеру!)
try:
    unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
    unreal.log("[v10] Sequencer закрыт")
except: pass

# 2. ПЛАНЕТА
planet = None
for a in EAS.get_all_level_actors():
    if PLANET_NAME in a.get_actor_label() or PLANET_NAME in a.get_class().get_name():
        planet = a
        break
if not planet:
    unreal.log_error("[v10] Планета не найдена!")
    raise SystemExit

P = planet.get_actor_location()
S = planet.get_actor_scale3d().x
R = RADIUS if RADIUS > 0 else S * RADIUS_MULT
unreal.log(f"[v10] Планета: ({P.x:.0f},{P.y:.0f},{P.z:.0f})  scale={S:.0f}  R={R:.0f}")
unreal.log(f"[v10] Ожидаемый радиус планеты ≈ {S*50:.0f} uu (sphere r=50)")
unreal.log(f"[v10] Камера снаружи на расстоянии {R - S*50:.0f} uu от поверхности")

# 3. КАМЕРА
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
    unreal.log("[v10] Камера создана")
else:
    cam.detach_from_actor(
        unreal.DetachmentRule.KEEP_WORLD,
        unreal.DetachmentRule.KEEP_WORLD,
        unreal.DetachmentRule.KEEP_WORLD
    )
    unreal.log("[v10] Камера detached")

cam.get_cine_camera_component().current_focal_length = FOCAL_LENGTH
unreal.log(f"[v10] Камера: {cam.get_actor_label()}  focal={FOCAL_LENGTH}mm")

# 4. LEVEL SEQUENCE
FRAMES    = DURATION_SECONDS * FPS
full_path = f"{SEQ_PATH}/{SEQ_NAME}"

if unreal.EditorAssetLibrary.does_asset_exist(full_path):
    if unreal.EditorAssetLibrary.delete_asset(full_path):
        unreal.log("[v10] Старая секвенция удалена")
        seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            SEQ_NAME, SEQ_PATH, unreal.LevelSequence, unreal.LevelSequenceFactoryNew()
        )
    else:
        unreal.log_warning("[v10] delete заблокирован — очищаем существующую")
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
    unreal.log_error("[v10] seq=None! Закрой Sequencer вручную и перезапусти.")
    raise SystemExit

seq.set_display_rate(unreal.FrameRate(FPS, 1))
seq.set_playback_start(0)
seq.set_playback_end(FRAMES)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
unreal.log(f"[v10] Секвенция: {FRAMES}fr @ {FPS}fps = {DURATION_SECONDS}s")

# 5. CAMERA CUT TRACK
cam_binding = seq.add_possessable(cam)
cut_track   = seq.add_track(unreal.MovieSceneCameraCutTrack)
cut_sec     = cut_track.add_section()
cut_sec.set_start_frame(0)
cut_sec.set_end_frame(FRAMES)
try:
    cut_sec.set_camera_binding_id(cam_binding.binding_id)
    unreal.log("[v10] Camera Cut OK")
except Exception as e:
    unreal.log_warning(f"[v10] Camera Cut: {e}")

# 6. TRANSFORM TRACK
transform_track = cam_binding.add_track(unreal.MovieScene3DTransformTrack)
transform_sec   = transform_track.add_section()
transform_sec.set_start_frame(0)
transform_sec.set_end_frame(FRAMES)
channels = transform_sec.get_all_channels()
unreal.log(f"[v10] Transform channels: {len(channels)}")

# 7. КЛЮЧИ ОРБИТЫ
# UE стандарт: [3]=RotX=Roll  [4]=RotY=Pitch  [5]=RotZ=Yaw
# Pitch=0 (экваториальная орбита), Roll=0, Yaw монотонный 180→540°
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

    # Yaw монотонный: 180→540° без flip
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
        add_k(3, rot.roll)        # Rotation X = Roll   ← UE стандарт
        add_k(4, rot.pitch)       # Rotation Y = Pitch  ← UE стандарт
        add_k(5, yaw_monotonic)   # Rotation Z = Yaw    ← монотонный 180→540°

unreal.log(f"[v10] Ключей: {N_KEYFRAMES+1}")
unreal.log(f"[v10] Channels: [3]=Roll [4]=Pitch [5]=Yaw (UE X/Y/Z стандарт)")
unreal.log(f"[v10] Yaw: {180.0:.0f}°→{180.0 + 360.0:.0f}° монотонно")

unreal.EditorAssetLibrary.save_loaded_asset(seq)
unreal.log("=" * 60)
unreal.log(f"[v10] ГОТОВО! R={R:.0f} (={RADIUS_MULT:.0f}×scale)")
unreal.log(f"[v10] Нажми Пробел → камера плавно облетает планету!")
