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

# Инициализация сменного журнала
if "journal" not in st.session_state:
    st.session_state.journal = []

# Инициализация буфера мутности
if "transfer_M" not in st.session_state:
    st.session_state.transfer_M = None

# Вкладки
tab1, tab2, tab3, tab4 = st.tabs([
    "🧪 Дозирование КИМ", 
    "🔬 Мутность (ПЭ-5300ВИ)", 
    "⚙️ Настройка плунжера", 
    "📋 Сменный журнал"
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
            if trans_col1.button("Подставить в Сырую"):
                st.session_state.t1_M_raw = st.session_state.transfer_M
            if trans_col2.button("Подставить в Осветлитель"):
                st.session_state.t1_M_clar = st.session_state.transfer_M
            if trans_col3.button("Подставить в Готовую"):
                st.session_state.t1_M_fin = st.session_state.transfer_M

        M_raw = st.number_input("Показатель М (Сырая вода)", value=default_M_raw, step=0.1, key="t1_M_raw")
        M_clar = st.number_input("Показатель М (Осветлители)", value=default_M_clar, step=0.1, key="t1_M_clar")
        
    with col2:
        M_fin = st.number_input("Показатель М (Готовая вода)", value=default_M_fin, step=0.1, key="t1_M_fin")
        D_coag_curr = st.number_input("Текущая доза коагулянта, мг/л", value=13.8, step=0.1, key="t1_D_coag")
        C_coag = st.number_input("Концентрация коагулянта, %", value=1.0, step=0.1, key="t1_C_coag")

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

        D_floc_target = round(D_coag_target / 22.0, 2)
        if D_floc_target > 0.75:
            D_floc_target = 0.75
            alerts.append("• Доза флокулянта ограничена 0.75 мг/л (защита фильтров).")

        q_coag = (Q * D_coag_target) / (10 * C_coag * rho_coag)
        q_floc = (Q * D_floc_target) / (10 * C_floc * rho_floc)

        if M_fin > 10.0:
            alerts.append(f"• ВНИМАНИЕ: Мутность готовой воды М={M_fin}! Проверьте фильтры на проскок.")

        st.markdown("---")
        st.subheader("Рекомендуемые параметры")
        r_col1, r_col2 = st.columns(2)
        r_col1.metric("Доза коагулянта ('Эпоха')", f"{D_coag_target:.2f} мг/л")
        r_col2.metric("Доза флокулянта ('ЭкоПлюс')", f"{D_floc_target:.2f} мг/л")
        r_col1.metric("Расход насоса коагулянта", f"{q_coag:.1f} л/ч")
        r_col2.metric("Расход насоса флокулянта", f"{q_floc:.1f} л/ч")

        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("Параметры в норме.")

        st.session_state.journal.append({
            "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "Модуль": "Дозирование КИМ",
            "Входные данные": f"Q={Q}, M_сыр={M_raw}, M_осв={M_clar}, M_гот={M_fin}",
            "Результат": f"Эпоха: {D_coag_target:.2f} мг/л ({q_coag:.1f} л/ч); ЭкоПлюс: {D_floc_target:.2f} мг/л ({q_floc:.1f} л/ч)",
            "Статус": "Предупреждение" if alerts else "В норме"
        })
        st.toast("Запись добавлена в сменный журнал!")

# =============================================================================
# ВКЛАДКА 2: МУТНОСТЬ (ПЭ-5300ВИ)
# =============================================================================
with tab2:
    st.subheader("Данные спектрофотометра (ПЭ-5300ВИ)")
    D_val = st.number_input("Оптическая плотность (D), 520 нм / 50 мм", value=0.165, format="%.4f", key="t2_D")
    
    with st.expander("Градуировочные константы (ПНД Ф 14.1:2:4.213-05)"):
        K_val = st.number_input("Коэффициент K", value=0.009347066, format="%.9f", key="t2_K")
        D0_val = st.number_input("Смещение D₀", value=0.002417294, format="%.9f", key="t2_D0")

    if st.button("РАССЧИТАТЬ МУТНОСТЬ (C)", key="btn_calc_turbidity"):
        C_val = 0.0 if D_val <= D0_val else (D_val - D0_val) / K_val
        st.session_state.transfer_M = C_val
        st.metric("Рассчитанная мутность (C)", f"{C_val:.2f} ЕМ/дм³")
        
        if C_val <= 2.0:
            status = "Отличное качество (готовая вода)"
            st.success(status)
        elif C_val <= 8.0:
            status = "Норма для осветлителей"
            st.info(status)
        elif C_val <= 15.0:
            status = "Повышенная мутность"
            st.warning(status)
        else:
            status = "КРИТИЧЕСКАЯ МУТНОСТЬ / Вынос взвеси"
            st.error(status)

        st.session_state.journal.append({
            "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "Модуль": "Мутность ПЭ-5300ВИ",
            "Входные данные": f"D={D_val:.4f}",
            "Результат": f"C={C_val:.2f} ЕМ/дм³",
            "Статус": status
        })
        st.toast("Результат сохранен!")

# =============================================================================
# ВКЛАДКА 3: НАСТРОЙКА ПЛУНЖЕРА
# =============================================================================
with tab3:
    st.subheader("Показания КИМ АДКФ и лимба насоса Ареопаг")
    S_curr = st.number_input("Текущее положение лимба плунжера (S), %", value=30.0, step=1.0, key="t3_S")
    f_curr = st.number_input("Текущая частота КИМ / ПЧ (f), Гц", value=48.0, step=0.5, key="t3_f")

    if st.button("РАССЧИТАТЬ НОВОЕ ПОЛОЖЕНИЕ ЛИМБА", key="btn_calc_plunger"):
        target_f = 35.0
        S_new = S_curr * (f_curr / target_f)
        S_new_clamped = min(max(round(S_new), 10), 100)

        st.metric("Рекомендуемый ход плунжера", f"{S_new_clamped}% (на лимбе)")

        if f_curr >= 42.0:
            msg = f"⚠️ Высокая частота КИМ ({f_curr:.1f} Гц)! Увеличьте ход плунжера с {S_curr:.0f}% до {S_new_clamped}%, чтобы сбросить частоту к ~35 Гц."
            st.warning(msg)
            status_log = "Требуется подстройка (высокая f)"
        elif f_curr <= 25.0:
            msg = f"⚠️ Низкая частота КИМ ({f_curr:.1f} Гц)! Уменьшите ход плунжера с {S_curr:.0f}% до {S_new_clamped}%, чтобы поднять частоту к ~35 Гц."
            st.warning(msg)
            status_log = "Требуется подстройка (низкая f)"
        else:
            msg = "✅ КИМ АДКФ работает в нормальном диапазоне (20-50 Гц)."
            st.success(msg)
            status_log = "В норме"

        st.session_state.journal.append({
            "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "Модуль": "Настройка плунжера",
            "Входные данные": f"S={S_curr:.0f}%, f={f_curr:.1f} Гц",
            "Результат": f"Реком. ход плунжера: {S_new_clamped}%",
            "Статус": status_log
        })
        st.toast("Запись добавлена в сменный журнал!")

# =============================================================================
# ВКЛАДКА 4: СМЕННЫЙ ЖУРНАЛ
# =============================================================================
with tab4:
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

st.markdown("---")
st.caption("ТМК СинТЗ Энергоцех Чемезов")