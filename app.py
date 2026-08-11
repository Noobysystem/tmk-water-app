# --- КАЛЬКУЛЯТОР ЗАТВОРЕНИЯ РАБОЧЕГО РАСТВОРА ПО РУЛЕТКЕ ---
    st.markdown("---")
    with st.expander("📏 Затворение коагулянта по рулетке (Расходный бак 2.8х2.8х2.4 м)", expanded=True):
        st.caption("Расчет добавления концентрата и воды для сохранения целевой концентрации в резервуаре.")
        
        prep_col1, prep_col2 = st.columns(2)
        
        with prep_col1:
            h_measured_cm = st.number_input(
                "Расстояние от края бака до зеркала воды (по рулетке), см", 
                value=100.0, 
                step=5.0, 
                min_value=0.0, 
                max_value=240.0,
                key="h_measured"
            )
            
            # Выбор целевой рабочей концентрации в резервуаре
            C_target_prep = st.radio(
                "Целевая концентрация раствора в резервуаре, %",
                options=[1.0, 1.2],
                index=0,
                horizontal=True,
                key="c_prep_radio"
            )
        
        with prep_col2:
            C_tov = st.number_input(
                "Содержание Al³+ в еврокубе (из паспорта № 644), %", 
                value=9.2, 
                step=0.1, 
                key="c_tov_p"
            )
            rho_tov = st.number_input(
                "Плотность концентрата в еврокубе, г/см³", 
                value=1.24, 
                step=0.01, 
                key="rho_tov_p"
            )

        # Геометрические константы расходного резервуара
        AREA_TANK = 2.8 * 2.8  # 7.84 м²
        V_PER_CM = AREA_TANK * 10.0  # 78.4 литра на 1 см высоты
        V_TOTAL_TANK = AREA_TANK * 2.4 * 1000.0  # 18 816 литров при 2.4 м

        # Объемы
        V_add_l = h_measured_cm * V_PER_CM  # Пустой объем, который нужно заполнить
        V_remain_l = V_TOTAL_TANK - V_add_l  # Остаток готового раствора в баке
        
        if V_add_l > 0 and C_tov > 0:
            # Плотность рабочего раствора при 1.0% (~1.010 г/см³) и 1.2% (~1.012 г/см³)
            rho_work = 1.010 if C_target_prep == 1.0 else 1.012
            
            # Расчет требуемого количества сухого вещество Al3+ для объёма долива V_add_l
            M_dry_req = V_add_l * (C_target_prep / 100.0) * rho_work
            
            # Масса и объем товарного концентрата «Эпоха» из еврокуба
            M_tov_req = M_dry_req / (C_tov / 100.0)
            V_tov_req_l = M_tov_req / rho_tov
            
            # Объем воды для доведения до верха
            V_water_add_l = V_add_l - V_tov_req_l

            st.markdown(f"### 📊 Результат расчета (Целевая концентрация: **{C_target_prep}%**):")
            
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Остаток растворен в баке", f"{V_remain_l:.0f} л", help=f"Уровень остатка: {240 - h_measured_cm:.0f} см от дна")
            m_col2.metric("Общий объем доведения", f"{V_add_l:.0f} л")
            m_col3.metric("КОНЦЕНТРАТ из Еврокуба", f"{V_tov_req_l:.1f} л", delta=f"{M_tov_req:.1f} кг")

            st.info(f"💦 **Долить обычной воды:** **{V_water_add_l:.0f} литров**")

            st.markdown("#### 📝 Инструкция для машиниста:")
            st.markdown(f"""
            1. Замерить по шкале еврокуба и залить в расходный бак **{V_tov_req_l:.0f} л** (или **{M_tov_req:.0f} кг**) концентрата «Эпоха».
            2. Долить обычную воду до верхнего края резервуара (добавить **{V_water_add_l:.0f} л** воды).
            3. Включить **барботаж** и перемешивать весь резервуар не менее 15–20 минут для выравнивания плотности по всему объему.
            """)