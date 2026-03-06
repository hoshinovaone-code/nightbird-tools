"""Диагностика Transform трека в SQ_NB_001_Orbit"""
import unreal

seq = unreal.load_asset('/Game/Temp/SQ_NB_001_Orbit')
if not seq:
    unreal.log_error("Секвенция не найдена!")
    raise SystemExit

unreal.log(f"[DIAG] Bindings: {len(seq.get_bindings())}")

for b in seq.get_bindings():
    unreal.log(f"[DIAG] Binding: '{b.get_display_name()}'")
    for t in b.get_tracks():
        unreal.log(f"[DIAG]   Track: {type(t).__name__}")
        for s in t.get_sections():
            channels = s.get_all_channels()
            unreal.log(f"[DIAG]   Channels: {len(channels)}")
            for i, ch in enumerate(channels[:9]):
                ch_type = type(ch).__name__
                try:
                    keys = ch.get_keys()
                    n_keys = len(keys)
                    if keys:
                        # Первый и последний ключ
                        k0 = keys[0]
                        kN = keys[-1]
                        t0 = k0.get_time().frame_number.value
                        tN = kN.get_time().frame_number.value
                        v0 = k0.get_value()
                        vN = kN.get_value()
                        unreal.log(f"[DIAG]     [{i}] {ch_type}: {n_keys} keys | frame {t0}={v0:.1f} .. frame {tN}={vN:.1f}")
                    else:
                        unreal.log(f"[DIAG]     [{i}] {ch_type}: 0 keys")
                except Exception as e:
                    unreal.log(f"[DIAG]     [{i}] {ch_type}: err={e}")
