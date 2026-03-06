"""
NB-001 Orbit v8 — минимальный фикс от v6
ИЗМЕНЕНИЯ vs v6 (который работал):
  - Yaw монотонный (ang*deg + 180°) — без flip на 0°/360°
  - Pitch и Roll берём от find_look_at_rotation (он правильно считает)
  - Interpolation AUTO вместо LINEAR
  - Focal 50mm (компромисс: 35 было широко, 85 слишком узко)
  - Длительность 60s / 1440 кадров (было 10s)
  - N_KEYFRAMES 48 (каждые 7.5° орбиты)
  - Radius S*8 (возвращаем рабочий радиус из v6)
  - Нет elevation (убираем переменную, которая сломала v7)
"""
import unreal, math

PLANET_NAME      = "BP_Planet_Terran"
RADIUS           = 0        # 0 = S * RADIUS_MULT
RADIUS_MULT      = 8.0      # проверено в v6: работает
DURATION_SECONDS = 60       # 1 минута на полный оборот
FPS              = 24
N_KEYFRAMES      = 48       # каждые 7.5°
FOCAL_LENGTH     = 50.0     # мм (между 35 и 85)
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
    unreal.log_error("[v8] Планета не найдена!")
    raise SystemExit

P = planet.get_actor_location()
S = planet.get_actor_scale3d().x
R = RADIUS if RADIUS > 0 else S * RADIUS_MULT
unreal.log(f"[v8] Планета: ({P.x:.0f},{P.y:.0f},{P.z:.0f})  scale={S:.2f}  R={R:.0f}")

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
unreal.log(f"[v8] Камера: {cam.get_actor_label()}  focal={FOCAL_LENGTH}mm")

# 3. LEVEL SEQUENCE
FRAMES    = DURATION_SECONDS * FPS

# Закрыть, если открыта
try:
    unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
except: pass

# Стратегия: загрузить существующую ИЛИ создать новую
# (delete_asset ненадёжен пока UE держит нативные ссылки)
full_path = f"{SEQ_PATH}/{SEQ_NAME}"
if unreal.EditorAssetLibrary.does_asset_exist(full_path):
    # Попробовать удалить
    if unreal.EditorAssetLibrary.delete_asset(full_path):
        unreal.log("[v8] Старая секвенция удалена")
        seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            SEQ_NAME, SEQ_PATH, unreal.LevelSequence, unreal.LevelSequenceFactoryNew()
        )
    else:
        # Удаление заблокировано UE — загружаем существующую и очищаем треки
        unreal.log_warning("[v8] delete заблокирован, загружаем и очищаем существующую")
        seq = unreal.load_asset(full_path)
        # Очистить все master tracks (Camera Cuts и др.)
        for t in list(seq.get_tracks()):
            seq.remove_track(t)
        # Очистить все bindings (camera, rail и др.)
        for b in list(seq.get_bindings()):
            for t in list(b.get_tracks()):
                b.remove_track(t)
        unreal.log("[v8] Треки очищены, секвенция перезаписывается")
else:
    seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        SEQ_NAME, SEQ_PATH, unreal.LevelSequence, unreal.LevelSequenceFactoryNew()
    )

if not seq:
    unreal.log_error("[v8] КРИТИЧНО: секвенция = None. Закрой Sequencer вручную и перезапусти.")
    raise SystemExit

seq.set_display_rate(unreal.FrameRate(FPS, 1))
seq.set_playback_start(0)
seq.set_playback_end(FRAMES)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
unreal.log(f"[v8] Секвенция: {FRAMES} кадров @ {FPS}fps = {DURATION_SECONDS}s")

# 4. CAMERA CUT TRACK
cam_binding = seq.add_possessable(cam)
cut_track   = seq.add_track(unreal.MovieSceneCameraCutTrack)
cut_sec     = cut_track.add_section()
cut_sec.set_start_frame(0)
cut_sec.set_end_frame(FRAMES)
try:
    cut_sec.set_camera_binding_id(cam_binding.binding_id)
    unreal.log("[v8] Camera Cut привязан OK")
except Exception as e:
    unreal.log_warning(f"[v8] Camera Cut bind: {e}")

# 5. TRANSFORM TRACK
transform_track = cam_binding.add_track(unreal.MovieScene3DTransformTrack)
transform_sec   = transform_track.add_section()
transform_sec.set_start_frame(0)
transform_sec.set_end_frame(FRAMES)

channels = transform_sec.get_all_channels()
unreal.log(f"[v8] Transform каналов: {len(channels)}")

# 6. КЛЮЧИ ОРБИТЫ
# СТРАТЕГИЯ: find_look_at_rotation для Pitch+Roll (они не флипают),
#            Yaw считаем вручную монотонным (FIX из v7)
for i in range(N_KEYFRAMES + 1):
    t   = i / N_KEYFRAMES
    fr  = int(t * FRAMES)
    ang = 2.0 * math.pi * t      # 0 → 2π

    # Позиция: та же орбита что в v6 (без elevation)
    cx = P.x + R * math.cos(ang)
    cy = P.y + R * math.sin(ang)
    cz = P.z

    cam_pos    = unreal.Vector(cx, cy, cz)
    planet_pos = unreal.Vector(P.x, P.y, P.z)

    # Pitch и Roll — берём от find_look_at (работало в v6)
    rot = ML.find_look_at_rotation(cam_pos, planet_pos)

    # Yaw — монотонный, без flip (FIX vs v6)
    # ang идёт 0→2π, yaw 180°→540° непрерывно
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
        add_k(3, rot.roll)        # Roll  (из find_look_at)
        add_k(4, rot.pitch)       # Pitch (из find_look_at)
        add_k(5, yaw_monotonic)   # Yaw   (монотонный FIX)

unreal.log(f"[v8] Ключей: {N_KEYFRAMES+1}, Yaw 180→540° монотонно, interp=AUTO")

unreal.EditorAssetLibrary.save_loaded_asset(seq)
unreal.log("=" * 55)
unreal.log(f"[v8] ГОТОВО! 60s орбита, 50mm, R=S*8, без flip!")
unreal.log("[v8] Пробел → плавная орбита вокруг планеты!")
