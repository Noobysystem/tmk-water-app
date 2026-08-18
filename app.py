import io
import datetime
import pandas as pd
import streamlit as st

# Настройка страницы
st.set_page_config(
    page_title="ТМК СинТЗ — Энергоцех Чемезов",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Корпоративные стили ТМК
st.markdown("""
    <style>
    .main-header {
        background-color: #1E2229;
        padding: 16px 22px;
        border-radius: 8px;
        border-bottom: 4px solid #F37021;
        color: white;
        margin-bottom: 20px;
    }
    .tmk-badge {
        background-color: #F37021;
        color: white;
        padding: 4px 12px;
        font-weight: bold;
        border-radius: 4px;
        font-size: 20px;
        display: inline-block;
        margin-right: 12px;
    }
    .stButton>button {
        background-color: #F37021 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 8px 16px !important;
    }
    .stButton>button:hover {
        background-color: #D95F13 !important;
    }
    </style>
    <div class="main-header">
        <span class="tmk-badge">ТМК</span>
        <span style="font-size: 22px; font-weight: bold;">ЧЕМЕЗОВ ЭНЕРГОЦЕХ</span>
        <div style="font-size: 13px; color: #9CA3AF; margin-top: 4px;">
            Система автоматизации водоочистки • КИМ / УНИТОК / ПЭ-5300ВИ
        </div>
    </div>
""", unsafe_allow_html=True)

# Инициализация глобальных состояний
if "journal" not in st.session_state:
    st.session_state.journal = []

if "transfer_M" not in st.session_state:
    st.session_state.transfer_M = None

if "res_tab1" not in st.session_state: st.session_state.res_tab1 = None
if "res_tab2" not in st.session_state: st.session_state.res_tab2 = None
if "res_tab3" not in st.session_state: st.session_state.res_tab3 = None
if "res_tab4" not in st.session_state: st.session_state.res_tab4 = None
if "res_tab_tanks" not in st.session_state: st.session_state.res_tab_tanks = None

# Вкладки приложения
tab1, tab2, tab_tanks, tab3, tab4, tab5, tab6 = st.tabs([
    "🧪 Дозирование КИМ", 
    "🛢 Приготовление раствора",
    "📏 Замер остатка в резервуарах",
    "🔬 Мутность (ПЭ-5300ВИ)", 
    "⚙️ Настройка плунжера", 
    "📋 Сменный журнал",
    "📚 Памятка и расчеты"
])

# =============================================================================
# ВКЛАДКА 1: ДОЗИРОВАНИЕ КИМ / УНИТОК
# =============================================================================
with tab1:
    st.subheader("Текущие показатели системы")
    col1, col2 = st.columns(2)
    
    with col1:
        Q = st.number_input("Расход воды (Q), м³/ч", value=431.9, step=1.0, key="t1_Q")
        
        default_M_raw = 71.3
        default_M_clar = 18.1
        default_M_fin = 12.65
        
        if st.session_state.transfer_M is not None:
            st.info(f"💡 Доступно рассчитанное значение мутности: **{st.session_state.transfer_M:.2f} ЕМ/дм³**")
            trans_col1, trans_col2, trans_col3 = st.columns(3)
            if trans_col1.button("Подставить в Сырую", key="b_sub_raw"):
                st.session_state.t1_M_raw = st.session_state.transfer_M
            if trans_col2.button("Подставить в Осветлитель", key="b_sub_clar"):
                st.session_state.t1_M_clar = st.session_state.transfer_M
            if trans_col3.button("Подставить в Готовую", key="b_sub_fin"):
                st.session_state.t1_M_fin = st.session_state.transfer_M

        M_raw = st.number_input("Показатель М (Сырая вода)", value=default_M_raw, step=0.1, key="t1_M_raw")
        M_clar = st.number_input("Показатель М (Осветлители)", value=default_M_clar, step=0.1, key="t1_M_clar")
        
    with col2:
        M_fin = st.number_input("Показатель М (Готовая вода)", value=default_M_fin, step=0.1, key="t1_M_fin")
        D_coag_curr = st.number_input("Текущая доза коагулянта, мг/л", value=13.8, step=0.1, key="t1_D_coag")
        C_coag = st.number_input("Концентрация коагулянта, %", value=1.0, step=0.1, key="t1_C_coag")
        
        ratio_coag_floc = st.number_input(
            "Пропорция Коагулянт / Флокулянт (1 : N)", 
            value=22.0, 
            step=1.0, 
            min_value=10.0, 
            max_value=40.0, 
            help="Укажите отношение дозы коагулянта к дозе флокулянта. По умолчанию 22:1",
            key="t1_ratio"
        )

    if st.button("РАССЧИТАТЬ ДОЗИРОВКУ", key="btn_calc_dosing"):
        rho_coag = 1.010 if C_coag <= 1.0 else 1.013
        C_floc, rho_floc = 0.04, 0.991
        
        alerts = []
        target_M_clar = 8.0
        
        if M_clar > target_M_clar:
            delta_M = M_clar - target_M_clar
            coag_step = round((delta_M / 2.0) * 0.3, 2)
            D_coag_target = min(D_coag_curr + max(coag_step, 0.5), 18.0)
            alerts.append(f"• Повышенная мутность осветлителей (М={M_clar}). Доза коагулянта увеличена.")
        else:
            D_coag_target = D_coag_curr

        D_floc_target = round(D_coag_target / ratio_coag_floc, 2)
        if D_floc_target > 0.75:
            D_floc_target = 0.75
            alerts.append("• Доза флокулянта ограничена 0.75 мг/л (защита песчаных фильтров).")

        q_coag = (Q * D_coag_target) / (10 * C_coag * rho_coag)
        q_floc = (Q * D_floc_target) / (10 * C_floc * rho_floc)

        if M_fin > 10.0:
            alerts.append(f"• ВНИМАНИЕ: Мутность готовой воды М={M_fin}! Проверьте фильтры на проскок.")

        st.session_state.res_tab1 = {
            "D_coag_target": D_coag_target,
            "D_floc_target": D_floc_target,
            "q_coag": q_coag,
            "q_floc": q_floc,
            "ratio_coag_floc": ratio_coag_floc,
            "alerts": alerts,
            "log_entry": {
                "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "Модуль": "Дозирование КИМ",
                "Входные данные": f"Q={Q}, M_сыр={M_raw}, M_осв={M_clar}, Соотношение=1:{ratio_coag_floc:.0f}",
                "Результат": f"Эпоха: {D_coag_target:.2f} мг/л ({q_coag:.1f} л/ч); ЭкоПлюс: {D_floc_target:.2f} мг/л ({q_floc:.1f} л/ч)",
                "Статус": "Предупреждение" if alerts else "В норме"
            }
        }

    if st.session_state.res_tab1 is not None:
        res = st.session_state.res_tab1
        st.markdown("---")
        st.subheader("Рекомендуемые параметры")
        r_col1, r_col2 = st.columns(2)
        r_col1.metric("Доза коагулянта ('Эпоха')", f"{res['D_coag_target']:.2f} мг/л")
        r_col2.metric("Доза флокулянта ('ЭкоПлюс')", f"{res['D_floc_target']:.2f} мг/л", help=f"Расчет по пропорции 1:{res['ratio_coag_floc']:.0f}")
        r_col1.metric("Расход насоса коагулянта", f"{res['q_coag']:.1f} л/ч")
        r_col2.metric("Расход насоса флокулянта", f"{res['q_floc']:.1f} л/ч")

        if res['alerts']:
            for alert in res['alerts']:
                st.warning(alert)
        else:
            st.success("Параметры в норме.")

        if st.button("📋 Добавить запись в журнал", key="btn_add_journal_t1"):
            st.session_state.journal.append(res['log_entry'])
            st.toast("Запись успешно добавлена в сменный журнал!")

# =============================================================================
# ВКЛАДКА 2: КАЛЬКУЛЯТОР РАСХОДА КОАГУЛЯНТА ДЛЯ ПРИГОТОВЛЕНИЯ РАСТВОРА
# =============================================================================
with tab2:
    st.subheader("Калькулятор расхода коагулянта для приготовления раствора")
    st.caption("Расчет объемов концентрата из еврокуба и обычной воды для расходного резервуара 2.8 х 2.8 х 2.5 м.")

    prep_col1, prep_col2 = st.columns(2)
    
    with prep_col1:
        h_measured_cm = st.number_input(
            "Расстояние от края бака до зеркала воды (по рулетке), см", 
            value=100.0, 
            step=5.0, 
            min_value=0.0, 
            max_value=250.0,
            key="prep_h_measured"
        )
        
        C_target_prep = st.radio(
            "Целевая концентрация раствора в резервуаре, %",
            options=[1.0, 1.2],
            index=0,
            horizontal=True,
            key="prep_c_target_radio"
        )
    
    with prep_col2:
        C_tov = st.number_input(
            "Содержание Al³+ в еврокубе (из паспорта № 644), %", 
            value=9.2, 
            step=0.1, 
            key="prep_c_tov"
        )
        rho_tov = st.number_input(
            "Плотность концентрата в еврокубе, г/см³", 
            value=1.24, 
            step=0.01, 
            key="prep_rho_tov"
        )

    if st.button("РАССЧИТАТЬ ОБЪЕМЫ", key="btn_calc_prep_tab"):
        AREA_TANK = 2.8 * 2.8  # 7.84 м²
        V_PER_CM = AREA_TANK * 10.0  # 78.4 л на 1 см
        V_TOTAL_TANK = AREA_TANK * 2.5 * 1000.0  # 19 600 литров

        V_add_l = h_measured_cm * V_PER_CM
        V_remain_l = V_TOTAL_TANK - V_add_l
        
        rho_work = 1.010 if C_target_prep == 1.0 else 1.012
        M_dry_req = V_add_l * (C_target_prep / 100.0) * rho_work
        M_tov_req = M_dry_req / (C_tov / 100.0)
        V_tov_req_l = M_tov_req / rho_tov
        V_water_add_l = V_add_l - V_tov_req_l

        st.session_state.res_tab2 = {
            "C_target_prep": C_target_prep,
            "V_remain_l": V_remain_l,
            "h_measured_cm": h_measured_cm,
            "V_add_l": V_add_l,
            "V_tov_req_l": V_tov_req_l,
            "M_tov_req": M_tov_req,
            "V_water_add_l": V_water_add_l,
            "log_entry": {
                "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "Модуль": "Приготовление раствора",
                "Входные данные": f"Замер={h_measured_cm:.0f} см, C_цель={C_target_prep}%, Al³+={C_tov}%",
                "Результат": f"Концентрат: {V_tov_req_l:.1f} л ({M_tov_req:.1f} кг); Вода: {V_water_add_l:.0f} л; Долив: {V_add_l:.0f} л",
                "Статус": "Приготовлено"
            }
        }

    if st.session_state.res_tab2 is not None:
        res2 = st.session_state.res_tab2
        st.markdown("---")
        st.markdown(f"### 📊 Результат расчета (Целевая концентрация: **{res2['C_target_prep']}%**):")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Остаток раствора в баке", f"{res2['V_remain_l']:.0f} л", help=f"Уровень остатка: {250 - res2['h_measured_cm']:.0f} см от дна")
        m_col2.metric("Общий объем доведения", f"{res2['V_add_l']:.0f} л")
        m_col3.metric("КОНЦЕНТРАТ из Еврокуба", f"{res2['V_tov_req_l']:.1f} л", delta=f"{res2['M_tov_req']:.1f} кг")

        st.info(f"💦 **Долить обычной воды:** **{res2['V_water_add_l']:.0f} литров**")

        st.markdown("#### 📝 Инструкция для машиниста:")
        st.markdown(f"""
        1. Замерить по шкале еврокуба и залить в расходный бак **{res2['V_tov_req_l']:.0f} л** (или **{res2['M_tov_req']:.0f} кг**) концентрата «Эпоха».
        2. Долить обычную воду до верхнего края резервуара (добавить **{res2['V_water_add_l']:.0f} л** воды).
        3. Включить **барботаж** и перемешивать весь резервуар не менее 15–20 минут для выравнивания плотности по всему объему.
        """)

        if st.button("📋 Добавить запись в журнал", key="btn_add_journal_t2"):
            st.session_state.journal.append(res2['log_entry'])
            st.toast("Запись приготовления раствора добавлена в сменный журнал!")

# =============================================================================
# ВКЛАДКА 3: ЗАМЕР ОСТАТКА В РЕЗЕРВУАРАХ (ЧИСТЫЙ ОБЪЕМ)
# =============================================================================
with tab_tanks:
    st.subheader("📏 Расчет фактического остаточного объема в резервуарах")
    st.caption("Определение объема жидкости по замеру рулеткой от верхнего края резервуара до зеркала воды.")

    tank_choice = st.selectbox(
        "Выберите резервуар для замера:",
        options=[
            "1. Резервуар расходный (Машинный зал) — 2.8х2.8х2.5 м",
            "2. Резервуар №1 (Склад мокрохранения) — 5.8х5.8 м (h = 2.5...2.8 м)",
            "3. Резервуар №4 (Склад мокрохранения) — 2.8х5.8 м (h = 2.7...3.4 м)"
        ],
        key="tank_select_web"
    )

    if "1. Резервуар расходный" in tank_choice:
        max_depth_m = 2.50
    elif "2. Резервуар №1" in tank_choice:
        max_depth_m = 2.80
    else:
        max_depth_m = 3.40

    h_tape_m = st.number_input(
        f"Замер рулеткой от верхнего края до зеркала воды, МЕТРЫ (0.00 – {max_depth_m:.2f} м)",
        min_value=0.00,
        max_value=max_depth_m,
        value=min(1.00, max_depth_m),
        step=0.05,
        format="%.2f",
        key="tank_tape_input"
    )

    if st.button("РАССЧИТАТЬ ОСТАТОК В РЕЗЕРВУАРЕ", key="btn_calc_tank_vol"):
        V_liters = 0.0
        V_max_liters = 0.0
        h_liquid_m = max_depth_m - h_tape_m
        tank_name = ""

        # Резервуар 1: Машинный зал (2.8 x 2.8 x 2.5)
        if "1. Резервуар расходный" in tank_choice:
            tank_name = "Резервуар расходный (Машзал)"
            V_max_liters = 2.8 * 2.8 * 2.5 * 1000.0  # 19600 л
            V_liters = 2.8 * 2.8 * h_liquid_m * 1000.0

        # Резервуар 2: Склад №1 (5.8 x 5.8 x 2.5...2.8)
        elif "2. Резервуар №1" in tank_choice:
            tank_name = "Резервуар №1 (Склад мокрохранения)"
            V_wedge_full = 0.5 * 5.8 * 5.8 * 0.3 * 1000.0  # 5046 л
            V_max_liters = V_wedge_full + (5.8 * 5.8 * 2.5 * 1000.0)  # 89146 л
            
            y_m = h_liquid_m  # глубина от нижней точки
            if y_m <= 0.3:
                V_liters = 0.5 * (5.8 * y_m / 0.3) * y_m * 5.8 * 1000.0
            else:
                V_liters = V_wedge_full + (5.8 * 5.8 * (y_m - 0.3) * 1000.0)

        # Резервуар 3: Склад №4 (2.8 x 5.8 x 2.7...3.4)
        else:
            tank_name = "Резервуар №4 (Склад мокрохранения)"
            V_wedge_full = 0.5 * 2.8 * 5.8 * 0.7 * 1000.0  # 5684 л
            V_max_liters = V_wedge_full + (2.8 * 5.8 * 2.7 * 1000.0)  # 49532 л
            
            y_m = h_liquid_m  # глубина от нижней точки
            if y_m <= 0.7:
                V_liters = 0.5 * (2.8 * 5.8 / 0.7) * (y_m ** 2) * 1000.0
            else:
                V_liters = V_wedge_full + (2.8 * 5.8 * (y_m - 0.7) * 1000.0)

        V_m3 = V_liters / 1000.0
        fill_pct = (V_liters / V_max_liters) * 100.0 if V_max_liters > 0 else 0.0

        st.session_state.res_tab_tanks = {
            "tank_name": tank_name,
            "h_tape_m": h_tape_m,
            "h_liquid_m": h_liquid_m,
            "V_liters": V_liters,
            "V_m3": V_m3,
            "fill_pct": fill_pct,
            "V_max_liters": V_max_liters,
            "log_entry": {
                "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "Модуль": "Замер остатка в баках",
                "Входные данные": f"{tank_name}, Замер={h_tape_m:.2f} м",
                "Результат": f"Объем: {V_liters:.0f} л ({V_m3:.2f} м³); Заполнение: {fill_pct:.1f}%; Глубина: {h_liquid_m:.2f} м",
                "Статус": "В норме"
            }
        }

    if st.session_state.res_tab_tanks is not None:
        res_t = st.session_state.res_tab_tanks
        st.markdown("---")
        st.markdown(f"### 📊 Результат замера: **{res_t['tank_name']}**")
        
        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("Фактический объем", f"{res_t['V_liters']:.0f} л", help=f"Полная емкость бака: {res_t['V_max_liters']:.0f} л")
        c_m2.metric("Объем в кубических метрах", f"{res_t['V_m3']:.2f} м³")
        c_m3.metric("Уровень заполнения", f"{res_t['fill_pct']:.1f}%", help=f"Фактическая глубина жидкости: {res_t['h_liquid_m']:.2f} м")

        st.progress(min(max(res_t['fill_pct'] / 100.0, 0.0), 1.0))

        if st.button("📋 Добавить запись в журнал", key="btn_add_journal_tanks"):
            st.session_state.journal.append(res_t['log_entry'])
            st.toast(f"Замер остатка в {res_t['tank_name']} успешно сохранен в сменный журнал!")

# =============================================================================
# ВКЛАДКА 4: МУТНОСТЬ (ПЭ-5300ВИ)
# =============================================================================
with tab3:
    st.subheader("Данные спектрофотометра (ПЭ-5300ВИ)")
    D_val = st.number_input("Оптическая плотность (D), 520 нм / 50 мм", value=0.165, format="%.4f", key="t3_D")
    
    with st.expander("Градуировочные константы (ПНД Ф 14.1:2:4.213-05)"):
        K_val = st.number_input("Коэффициент K", value=0.009347066, format="%.9f", key="t3_K")
        D0_val = st.number_input("Смещение D₀", value=0.002417294, format="%.9f", key="t3_D0")

    if st.button("РАССЧИТАТЬ МУТНОСТЬ (C)", key="btn_calc_turbidity"):
        C_val = 0.0 if D_val <= D0_val else (D_val - D0_val) / K_val
        st.session_state.transfer_M = C_val
        
        if C_val <= 2.0:
            status = "Отличное качество (готовая вода)"
            status_type = "success"
        elif C_val <= 8.0:
            status = "Норма для осветлителей"
            status_type = "info"
        elif C_val <= 15.0:
            status = "Повышенная мутность"
            status_type = "warning"
        else:
            status = "КРИТИЧЕСКАЯ МУТНОСТЬ / Вынос взвеси"
            status_type = "error"

        st.session_state.res_tab3 = {
            "C_val": C_val,
            "status": status,
            "status_type": status_type,
            "log_entry": {
                "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "Модуль": "Мутность ПЭ-5300ВИ",
                "Входные данные": f"D={D_val:.4f}",
                "Результат": f"C={C_val:.2f} ЕМ/дм³",
                "Статус": status
            }
        }

    if st.session_state.res_tab3 is not None:
        res3 = st.session_state.res_tab3
        st.markdown("---")
        st.metric("Рассчитанная мутность (C)", f"{res3['C_val']:.2f} ЕМ/дм³")
        
        if res3['status_type'] == "success":
            st.success(res3['status'])
        elif res3['status_type'] == "info":
            st.info(res3['status'])
        elif res3['status_type'] == "warning":
            st.warning(res3['status'])
        else:
            st.error(res3['status'])

        if st.button("📋 Добавить запись в журнал", key="btn_add_journal_t3"):
            st.session_state.journal.append(res3['log_entry'])
            st.toast("Результат измерения мутности добавлен в журнал!")

# =============================================================================
# ВКЛАДКА 5: НАСТРОЙКА ПЛУНЖЕРА
# =============================================================================
with tab4:
    st.subheader("Показания КИМ АДКФ и лимба насоса Ареопаг")
    st.caption("Цена деления шкалы лимба: 0.5 мм. Шкала включает 60 делений.")
    
    S_curr = st.number_input("Текущее положение лимба плунжера (S), делений (0–60)", value=30.0, step=1.0, min_value=0.0, max_value=60.0, key="t4_S")
    f_curr = st.number_input("Текущая частота КИМ / ПЧ (f), Гц", value=48.0, step=0.5, key="t4_f")

    if st.button("РАССЧИТАТЬ НОВОЕ ПОЛОЖЕНИЕ ЛИМБА", key="btn_calc_plunger"):
        target_f = 35.0
        S_new = S_curr * (f_curr / target_f)
        S_new_clamped = min(max(round(S_new), 0), 60)

        if f_curr >= 42.0:
            msg = f"⚠️ Высокая частота КИМ ({f_curr:.1f} Гц)! Увеличьте ход плунжера с {S_curr:.0f} до {S_new_clamped} делений, чтобы сбросить частоту к ~35 Гц."
            status_type = "warning"
            status_log = "Требуется подстройка (высокая f)"
        elif f_curr <= 25.0:
            msg = f"⚠️ Низкая частота КИМ ({f_curr:.1f} Гц)! Уменьшите ход плунжера с {S_curr:.0f} до {S_new_clamped} делений, чтобы поднять частоту к ~35 Гц."
            status_type = "warning"
            status_log = "Требуется подстройка (низкая f)"
        else:
            msg = "✅ КИМ АДКФ работает в нормальном диапазоне (20-50 Гц)."
            status_type = "success"
            status_log = "В норме"

        st.session_state.res_tab4 = {
            "S_new_clamped": S_new_clamped,
            "msg": msg,
            "status_type": status_type,
            "log_entry": {
                "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "Модуль": "Настройка плунжера",
                "Входные данные": f"S={S_curr:.0f} дел., f={f_curr:.1f} Гц",
                "Результат": f"Реком. ход плунжера: {S_new_clamped} дел.",
                "Статус": status_log
            }
        }

    if st.session_state.res_tab4 is not None:
        res4 = st.session_state.res_tab4
        st.markdown("---")
        st.metric("Рекомендуемый ход плунжера", f"{res4['S_new_clamped']} делений (по шкале лимба)")

        if res4['status_type'] == "warning":
            st.warning(res4['msg'])
        else:
            st.success(res4['msg'])

        if st.button("📋 Добавить запись в журнал", key="btn_add_journal_t4"):
            st.session_state.journal.append(res4['log_entry'])
            st.toast("Настройка плунжера добавлена в сменный журнал!")

# =============================================================================
# ВКЛАДКА 6: СМЕННЫЙ ЖУРНАЛ
# =============================================================================
with tab5:
    st.subheader("Записи сменного журнала")
    if st.session_state.journal:
        df_journal = pd.DataFrame(st.session_state.journal)
        st.dataframe(df_journal, use_container_width=True)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_journal.to_excel(writer, index=False, sheet_name='Сменный_журнал')
        
        st.download_button(
            label="💾 Скачать журнал в Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"Сменный_журнал_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        if st.button("🗑 Очистить журнал", key="btn_clear_journal"):
            st.session_state.journal = []
            st.rerun()
    else:
        st.info("Журнал пуст. Выполните расчеты на вкладках, чтобы записи появились здесь.")

# =============================================================================
# ВКЛАДКА 7: ПАМЯТКА И РАСЧЕТЫ (ПОДРОБНЫЙ СПРАВОЧНИК)
# =============================================================================
with tab6:
    st.subheader("📖 Справочная памятка по расчетам водоочистки")
    st.caption("Подробный математический разбор всех технологических модулей ТМК СинТЗ Энергоцех Чемезов")

    with st.expander("📏 1. Подробный геометрический расчет остатка в резервуарах", expanded=True):
        st.markdown("""
        Замер выполняется металлической рулеткой от верхнего горизонтального среза резервуара до зеркала жидкости ($h_{\\text{зам}}$, в метрах). Фактическая глубина жидкости от самой нижней точки дна составляет $y = H_{\\text{макс}} - h_{\\text{зам}}$.

        ---

        #### 1. Резервуар расходный в машинном зале ($2.8 \\times 2.8 \\times 2.5 \\text{ м}$)
        * **Форма:** Прямоугольный параллелепипед с плоским дном.
        * **Площадь зеркала:** $S = 2.8 \\times 2.8 = 7.84 \\text{ м}^2$.
        * **Фактическая глубина жидкости:** $h = 2.50 - h_{\\text{зам}} \\text{ (м)}$.
        * **Формула объема:**
          $$V = 2.8 \\times 2.8 \\times (2.50 - h_{\\text{зам}}) \\times 1000 = 7840 \\times (2.50 - h_{\\text{зам}}) \\text{ (л)}$$
        * **Полная вместимость при $2.50 \\text{ м}$:** $19\\,600 \\text{ литров}$ ($19.60 \\text{ м}^3$).

        ---

        #### 2. Резервуар №1 на складе мокрохранения ($5.8 \\times 5.8 \\text{ м}$, высота $2.50 \\dots 2.80 \\text{ м}$)
        * **Уклон дна:** Перепад высот составляет $\\Delta H = 2.80 - 2.50 = 0.30 \\text{ м}$ ($30 \\text{ см}$).
        * **Глубина жидкости от глубокой точки:** $y = 2.80 - h_{\\text{зам}} \\text{ (м)}$.
        * **Полный объем нижнего клина (при $y = 0.30 \\text{ м}$):**
          $$V_{\\text{клин}} = \\frac{1}{2} \\times 5.8 \\times 5.8 \\times 0.30 \\times 1000 = 5\\,046 \\text{ литров}$$

        * **Случай А: Уровень в пределах уклона дна ($y \\le 0.30 \\text{ м}$):**
          Длина смоченного участка дна $L(y) = 5.8 \\times \\frac{y}{0.30}$. Объем треугольной призмы:
          $$V = \\frac{1}{2} \\times \\left(5.8 \\times \\frac{y}{0.30}\\right) \\times y \\times 5.8 \\times 1000 = 56\\,067 \\times y^2 \\text{ (л)}$$

        * **Случай Б: Уровень выше зоны уклона ($y > 0.30 \\text{ м}$):**
          К полному объему клина ($5\\,046 \\text{ л}$) прибавляется прямоугольная призма высотой $(y - 0.30)$:
          $$V = 5\\,046 + 5.8 \\times 5.8 \\times (y - 0.30) \\times 1000 = 5\\,046 + 33\\,640 \\times (y - 0.30) \\text{ (л)}$$
        * **Полная вместимость при $2.80 \\text{ м}$:** $89\\,146 \\text{ литров}$ ($89.15 \\text{ м}^3$).

        ---

        #### 3. Резервуар №4 на складе мокрохранения ($2.8 \\times 5.8 \\text{ м}$, высота $2.70 \\dots 3.40 \\text{ м}$)
        * **Уклон дна:** Перепад высот составляет $\\Delta H = 3.40 - 2.70 = 0.70 \\text{ м}$ ($70 \\text{ см}$).
        * **Глубина жидкости от глубокой точки:** $y = 3.40 - h_{\\text{зам}} \\text{ (м)}$.
        * **Полный объем нижнего клина (при $y = 0.70 \\text{ м}$):**
          $$V_{\\text{клин}} = \\frac{1}{2} \\times 2.8 \\times 5.8 \\times 0.70 \\times 1000 = 5\\,684 \\text{ литра}$$

        * **Случай А: Уровень в пределах уклона дна ($y \\le 0.70 \\text{ м}$):**
          $$V = \\frac{1}{2} \\times \\left(\\frac{2.8 \\times 5.8}{0.70}\\right) \\times y^2 \\times 1000 = 11\\,600 \\times y^2 \\text{ (л)}$$

        * **Случай Б: Уровень выше зоны уклона ($y > 0.70 \\text{ м}$):**
          $$V = 5\\,684 + 2.8 \\times 5.8 \\times (y - 0.70) \\times 1000 = 5\\,684 + 16\\,240 \\times (y - 0.70) \\text{ (л)}$$
        * **Полная вместимость при $3.40 \\text{ м}$:** $49\\,532 \\text{ литра}$ ($49.53 \\text{ м}^3$).
        """)

    with st.expander("🧪 2. Дозирование реагентов, соотношение 22:1 и Jar Test"):
        st.markdown("""
        * **Коагулянт «Эпоха» ($\text{Al}^{3+}$):** Нейтрализует дзета-потенциал взвешенных частиц (рабочие дозы $10 \\dots 18 \\text{ мг/л}$).
        * **Флокулянт «ЭкоПлюс» (ПАА):** Мостообразование в макрохлопья. Ограничение по СП 31.13330.2012 — **$0.75 \\text{ мг/л}$** (защита фильтров от забивания).
        * **Обоснование $22:1$:** При максимальной рабочей дозе коагулянта $16.5 \\text{ мг/л}$ доза флокулянта составляет $16.5 / 22 = 0.75 \\text{ мг/л}$ (предохранитель от передозировки).
        * **Лабораторный подбор:** Точная пропорция ($15:1 \\dots 30:1$) подбирается методом пробного коагулирования в цилиндрах (Jar Test).
        """)

    with st.expander("🔬 3. Методика спектрофотометрии ПЭ-5300ВИ и насосы «Ареопаг»"):
        st.markdown("""
        * **Мутность (ПНД Ф 14.1:2:4.213-05):** $C = (D - 0.002417294) / 0.009347066$ при $\\lambda = 520 \\text{ нм}$.
        * **Плунжер «Ареопаг»:** Шкала $0 \\dots 60$ делений ($0.5 \\text{ мм/дел}$). Целевая частота КИМ — $35.0 \\text{ Гц}$. Формула: $S_{\\text{нов}} = S_{\\text{тек}} \\times (f_{\\text{тек}} / 35.0)$.
        """)

st.markdown("---")
st.caption("ТМК СинТЗ Энергоцех Чемезов")