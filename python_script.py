import pandas as pd
import numpy as np
from scipy import stats

# 1. Загрузка данных
df = pd.read_csv('results_graph_traverse.csv')

# Разделяем на прогревочные и основные запуски
warmup_df = df[df['run_id'].astype(str).str.startswith('warmup')]
main_df = df[~df['run_id'].astype(str).str.startswith('warmup')].copy()
main_df['run_id'] = main_df['run_id'].astype(int)

print("=== АНАЛИЗ ПРОГРЕВА (WARMUP) ===")
for op in ['read', 'write']:
    print(f"\nОперация: {op.upper()}")
    op_warmup = warmup_df[warmup_df['op'] == op]
    op_main = main_df[main_df['op'] == op]

    for idx, row in op_warmup.iterrows():
        print(f"  {row['run_id']}: Wall time = {row['wall_time_s']} c, Major faults = {row['majflt']}, Minor faults = {row['minflt']}")
    print(f"  Основные запуски (среднее): {op_main['wall_time_s'].mean():.4f} c")

print("\n" + "="*40 + "\n")
print("=== СТАТИСТИКА И РАСЧЕТ ДОПОЛНИТЕЛЬНЫХ ИЗМЕРЕНИЙ (N) ===")

# Уровень значимости для 95% доверительного интервала
confidence = 0.95
alpha = 1 - confidence

# Варианты относительной точности E (в процентах от среднего)
precision_levels = [0.01, 0.05, 0.10]  # 1%, 5%, 10%

for op in ['read', 'write']:
    op_data = main_df[main_df['op'] == op]['wall_time_s']

    n_pilot = len(op_data)
    mean_val = op_data.mean()
    s_val = op_data.std(ddof=1)  # Выборочное СКО (несмещенное, ddof=1)

    # Квантиль t-распределения Стьюдента для текущего числа степеней свободы
    df_deg = n_pilot - 1
    t_student = stats.t.ppf(1 - alpha / 2, df_deg)

    print(f"\nОперация: {op.upper()}")
    print(f"  Число пилотных измерений (n): {n_pilot}")
    print(f"  Среднее время (mean): {mean_val:.4f} c")
    print(f"  Выборочное СКО (s): {s_val:.6f} c")
    print(f"  Коэффициент вариации (s/mean): {s_val/mean_val:.2%}")
    print(f"  Квантиль t-Стьюдента (df={df_deg}): {t_student:.3f} (вместо грубого 1.96)")

    print(f"  Расчет необходимого N:")
    for p in precision_levels:
        E = mean_val * p  # Абсолютная целевая полуширина интервала

        # Расчет по формуле из методички с уточнением через t-Стьюдента
        N_required = ((t_student * s_val) / E) ** 2
        N_rounded = int(np.ceil(N_required))

        # Сколько еще добрать измерений
        additional = max(0, N_rounded - n_pilot)

        print(f"    Точность {p*100:>2.0f}% (E = {E:.5f} c) -> Нужно N ≈ {N_rounded} "
              f"(добрать еще {additional} измерений)")
