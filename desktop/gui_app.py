import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import datetime
import pandas as pd

class TMKWaterAppDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("ТМК СинТЗ — Энергоцех Чемезов | Комплекс водоподготовки")
        self.root.geometry("960x760")
        
        # Хранилище журнала и последних результатов
        self.journal = []
        self.last_res_t1 = None
        self.last_res_t2 = None
        self.last_res_t3 = None
        self.last_res_t4 = None
        self.last_res_tanks = None

        # Настройка стилей
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[10, 6])
        style.configure('TButton', font=('Segoe UI', 9, 'bold'))
        
        # Заголовок ТМК
        header = tk.Frame(self.root, bg="#1E2229", height=60)
        header.pack(fill='x')
        lbl_badge = tk.Label(header, text=" ТМК ", bg="#F37021", fg="white", font=('Segoe UI', 14, 'bold'))
        lbl_badge.pack(side='left', padx=15, pady=10)
        lbl_title = tk.Label(header, text="ЧЕМЕЗОВ ЭНЕРГОЦЕХ • Водоподготовка", bg="#1E2229", fg="white", font=('Segoe UI', 12, 'bold'))
        lbl_title.pack(side='left', pady=10)

        # Панель вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создание вкладок
        self.tab_dosing = ttk.Frame(self.notebook)
        self.tab_prep = ttk.Frame(self.notebook)
        self.tab_tanks = ttk.Frame(self.notebook)
        self.tab_turbidity = ttk.Frame(self.notebook)
        self.tab_plunger = ttk.Frame(self.notebook)
        self.tab_journal = ttk.Frame(self.notebook)
        self.tab_memo = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_dosing, text="🧪 Дозирование КИМ/УНИТОК")
        self.notebook.add(self.tab_prep, text="🛢 Приготовление раствора")
        self.notebook.add(self.tab_tanks, text="📏 Остаток в резервуарах")
        self.notebook.add(self.tab_turbidity, text="🔬 Мутность (ПЭ-5300ВИ)")
        self.notebook.add(self.tab_plunger, text="⚙️ Настройка плунжера")
        self.notebook.add(self.tab_journal, text="📋 Сменный журнал")
        self.notebook.add(self.tab_memo, text="📚 Памятка и расчеты")
        
        # Построение интерфейсов
        self.build_dosing_tab()
        self.build_prep_tab()
        self.build_tanks_tab()
        self.build_turbidity_tab()
        self.build_plunger_tab()
        self.build_journal_tab()
        self.build_memo_tab()

    # =========================================================================
    # 1. ВКЛАДКА: ДОЗИРОВАНИЕ КИМ / УНИТОК
    # =========================================================================
    def build_dosing_tab(self):
        frame = ttk.LabelFrame(self.tab_dosing, text=" Показатели системы и кинетики УНИТОК ", padding=15)
        frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(frame, text="Расход воды (Q), м³/ч:").grid(row=0, column=0, sticky='w', pady=4)
        self.entry_Q = ttk.Entry(frame, width=15)
        self.entry_Q.insert(0, "459.6")
        self.entry_Q.grid(row=0, column=1, padx=10, pady=4)
        
        ttk.Label(frame, text="Мутность Осветлители (М_осв):").grid(row=1, column=0, sticky='w', pady=4)
        self.entry_M_clar = ttk.Entry(frame, width=15)
        self.entry_M_clar.insert(0, "18.10")
        self.entry_M_clar.grid(row=1, column=1, padx=10, pady=4)

        ttk.Label(frame, text="Скорость ПК УНИТОК (V):").grid(row=2, column=0, sticky='w', pady=4)
        self.entry_V_pk = ttk.Entry(frame, width=15)
        self.entry_V_pk.insert(0, "0.472")
        self.entry_V_pk.grid(row=2, column=1, padx=10, pady=4)
        
        ttk.Label(frame, text="Текущая доза коагулянта, мг/л:").grid(row=3, column=0, sticky='w', pady=4)
        self.entry_D_curr = ttk.Entry(frame, width=15)
        self.entry_D_curr.insert(0, "14.74")
        self.entry_D_curr.grid(row=3, column=1, padx=10, pady=4)

        ttk.Label(frame, text="Концентрация коагулянта (%):").grid(row=4, column=0, sticky='w', pady=4)
        self.entry_C_coag = ttk.Entry(frame, width=15)
        self.entry_C_coag.insert(0, "1.2")
        self.entry_C_coag.grid(row=4, column=1, padx=10, pady=4)

        ttk.Label(frame, text="Пропорция Коаг. / Флок. (1 : N):").grid(row=5, column=0, sticky='w', pady=4)
        self.entry_ratio = ttk.Entry(frame, width=15)
        self.entry_ratio.insert(0, "22.0")
        self.entry_ratio.grid(row=5, column=1, padx=10, pady=4)
        
        btn_calc = ttk.Button(self.tab_dosing, text="РАССЧИТАТЬ ДОЗИРОВКУ", command=self.calc_dosing)
        btn_calc.pack(pady=8)
        
        self.lbl_dosing_res = ttk.Label(self.tab_dosing, text="", font=('Segoe UI', 10, 'bold'), justify='center')
        self.lbl_dosing_res.pack(pady=5)

        self.btn_log_t1 = ttk.Button(self.tab_dosing, text="📋 Добавить запись в журнал", command=self.add_journal_t1, state='disabled')
        self.btn_log_t1.pack(pady=5)

    def calc_dosing(self):
        try:
            Q = float(self.entry_Q.get().replace(',', '.'))
            M_clar = float(self.entry_M_clar.get().replace(',', '.'))
            V_pk = float(self.entry_V_pk.get().replace(',', '.'))
            D_curr = float(self.entry_D_curr.get().replace(',', '.'))
            C_coag = float(self.entry_C_coag.get().replace(',', '.'))
            ratio = float(self.entry_ratio.get().replace(',', '.'))

            rho_coag = 1.010 if C_coag <= 1.0 else 1.013
            
            alerts = []
            D_coag_ideal = D_curr

            if M_clar > 8.0:
                delta_M = M_clar - 8.0
                coag_step = max((delta_M / 2.0) * 0.30, 0.5)
                D_coag_ideal += coag_step
                alerts.append(f"Повышенная мутность (М={M_clar:.1f}). Прибавка: +{coag_step:.2f} мг/л.")

            if V_pk < 0.500:
                D_coag_ideal += 0.90
                alerts.append(f"⚠️ КРИТИЧЕСКИ НИЗКАЯ скорость ПК (V={V_pk:.3f} < 0.50)! Прибавка: +0.90 мг/л.")
            elif V_pk < 0.800:
                D_coag_ideal += 0.40
                alerts.append(f"Скорость ПК (V={V_pk:.3f}) ниже оптимума (0.80). Прибавка: +0.40 мг/л.")

            D_coag_ideal = min(round(D_coag_ideal, 2), 18.0)
            delta_total = D_coag_ideal - D_curr

            MAX_SAFE_STEP = 0.80
            is_stepped = False
            if delta_total > MAX_SAFE_STEP:
                is_stepped = True
                D_coag_apply = round(D_curr + MAX_SAFE_STEP, 2)
                alerts.append(
                    f"🛑 СТУПЕНЧАТЫЙ РАСЧЕТ: Залповый подъем опасен перезарядкой коллоидов и падением pH!\n"
                    f"Установите сейчас (Шаг 1): {D_coag_apply:.2f} мг/л. Выдержите 15–20 мин перед выходом на цель ({D_coag_ideal:.2f} мг/л)."
                )
            else:
                D_coag_apply = D_coag_ideal

            D_floc = round(D_coag_apply / ratio, 2)
            if D_floc > 0.75:
                D_floc = 0.75
                alerts.append("Доза флокулянта ограничена 0.75 мг/л.")

            q_coag_step1 = (Q * D_coag_apply) / (10 * C_coag * rho_coag)
            q_coag_final = (Q * D_coag_ideal) / (10 * C_coag * rho_coag)
            q_floc = (Q * D_floc) / (10 * 0.04 * 0.991)

            if is_stepped:
                res_text = f"👉 ШАГ 1 (Установить сейчас): {D_coag_apply:.2f} мг/л ({q_coag_step1:.1f} л/ч)\n" \
                           f"🎯 Конечная цель: {D_coag_ideal:.2f} мг/л ({q_coag_final:.1f} л/ч)\n" \
                           f"Доза ЭкоПлюс (1:{ratio:.0f}): {D_floc:.2f} мг/л ({q_floc:.1f} л/ч)"
            else:
                res_text = f"Реком. доза Эпоха: {D_coag_apply:.2f} мг/л ({q_coag_step1:.1f} л/ч)\n" \
                           f"Реком. доза ЭкоПлюс (1:{ratio:.0f}): {D_floc:.2f} мг/л ({q_floc:.1f} л/ч)"

            if alerts:
                res_text += "\n⚠️ " + "\n⚠️ ".join(alerts)

            self.lbl_dosing_res.config(text=res_text, foreground="#D83B01" if alerts else "#107C41")
            
            self.last_res_t1 = {
                "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "Модуль": "Дозирование КИМ/УНИТОК",
                "Входные данные": f"Q={Q:.1f}, M_осв={M_clar:.1f}, V_пк={V_pk:.3f}, Д_тек={D_curr:.2f}",
                "Результат": f"Шаг 1: {D_coag_apply:.2f} мг/л ({q_coag_step1:.1f} л/ч); Цель: {D_coag_ideal:.2f} мг/л; ЭкоПлюс: {D_floc:.2f} мг/л",
                "Статус": "Предупреждение (Ступенчато)" if is_stepped else ("Предупреждение" if alerts else "В норме")
            }
            self.btn_log_t1.config(state='normal')
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте корректность введенных чисел")

    def add_journal_t1(self):
        if self.last_res_t1:
            self.add_to_journal(self.last_res_t1)
            messagebox.showinfo("Журнал", "Запись дозирования добавлена в сменный журнал!")

    # =========================================================================
    # 2. ВКЛАДКА: ПРИГОТОВЛЕНИЕ РАСТВОРА
    # =========================================================================
    def build_prep_tab(self):
        frame = ttk.LabelFrame(self.tab_prep, text=" Затворение по рулетке (Бак 2.8 х 2.8 х 2.5 м) ", padding=15)
        frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(frame, text="Расстояние от края бака до воды (см):").grid(row=0, column=0, sticky='w', pady=4)
        self.entry_h = ttk.Entry(frame, width=15)
        self.entry_h.insert(0, "100")
        self.entry_h.grid(row=0, column=1, padx=10, pady=4)
        
        ttk.Label(frame, text="Целевая концентрация раствора (%):").grid(row=1, column=0, sticky='w', pady=4)
        self.var_conc = tk.DoubleVar(value=1.2)
        rb1 = ttk.Radiobutton(frame, text="1.0%", variable=self.var_conc, value=1.0)
        rb2 = ttk.Radiobutton(frame, text="1.2%", variable=self.var_conc, value=1.2)
        rb1.grid(row=1, column=1, sticky='w')
        rb2.grid(row=1, column=1, padx=60, sticky='w')

        ttk.Label(frame, text="Содержание Al³+ в еврокубе (%):").grid(row=2, column=0, sticky='w', pady=4)
        self.entry_C_tov = ttk.Entry(frame, width=15)
        self.entry_C_tov.insert(0, "9.2")
        self.entry_C_tov.grid(row=2, column=1, padx=10, pady=4)

        ttk.Label(frame, text="Плотность концентрата (г/см³):").grid(row=3, column=0, sticky='w', pady=4)
        self.entry_rho_tov = ttk.Entry(frame, width=15)
        self.entry_rho_tov.insert(0, "1.24")
        self.entry_rho_tov.grid(row=3, column=1, padx=10, pady=4)
        
        btn_calc = ttk.Button(self.tab_prep, text="РАССЧИТАТЬ ОБЪЕМЫ", command=self.calc_prep)
        btn_calc.pack(pady=8)
        
        self.lbl_prep_res = ttk.Label(self.tab_prep, text="", font=('Segoe UI', 10, 'bold'), justify='center')
        self.lbl_prep_res.pack(pady=5)

        self.btn_log_t2 = ttk.Button(self.tab_prep, text="📋 Добавить запись в журнал", command=self.add_journal_t2, state='disabled')
        self.btn_log_t2.pack(pady=5)

    def calc_prep(self):
        try:
            h_cm = float(self.entry_h.get().replace(',', '.'))
            c_target = self.var_conc.get()
            c_tov = float(self.entry_C_tov.get().replace(',', '.'))
            rho_tov = float(self.entry_rho_tov.get().replace(',', '.'))
            
            V_add = h_cm * 78.4
            V_remain = 19600.0 - V_add
            
            rho_work = 1.010 if c_target == 1.0 else 1.012
            M_dry = V_add * (c_target / 100.0) * rho_work
            M_tov = M_dry / (c_tov / 100.0)
            V_tov = M_tov / rho_tov
            V_water = V_add - V_tov
            
            res_text = f"Остаток в баке: {V_remain:.0f} л | Объем доведения: {V_add:.0f} л\n" \
                       f"Залить КОНЦЕНТРАТА из Еврокуба: {V_tov:.1f} л ({M_tov:.1f} кг)\n" \
                       f"Долить обычной воды: {V_water:.0f} л\n" \
                       f"Включить барботаж на 15-20 минут!"
            self.lbl_prep_res.config(text=res_text, foreground="#002050")
            
            self.last_res_t2 = {
                "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "Модуль": "Приготовление раствора",
                "Входные данные": f"Замер={h_cm:.0f} см, C_цель={c_target}%, Al³+={c_tov}%",
                "Результат": f"Концентрат: {V_tov:.1f} л ({M_tov:.1f} кг); Вода: {V_water:.0f} л; Долив: {V_add:.0f} л",
                "Статус": "Приготовлено"
            }
            self.btn_log_t2.config(state='normal')
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте параметры затворения")

    def add_journal_t2(self):
        if self.last_res_t2:
            self.add_to_journal(self.last_res_t2)
            messagebox.showinfo("Журнал", "Запись приготовления раствора добавлена в сменный журнал!")

    # =========================================================================
    # 3. ВКЛАДКА: ЗАМЕР ОСТАТКА В РЕЗЕРВУАРАХ
    # =========================================================================
    def build_tanks_tab(self):
        frame = ttk.LabelFrame(self.tab_tanks, text=" Параметры замера в резервуаре ", padding=15)
        frame.pack(fill='x', padx=15, pady=10)

        ttk.Label(frame, text="Выберите резервуар:").grid(row=0, column=0, sticky='w', pady=4)
        self.tank_var = tk.StringVar(value="Резервуар расходный (Машзал 2.8х2.8х2.5 м)")
        tanks = [
            "Резервуар расходный (Машзал 2.8х2.8х2.5 м)",
            "Резервуар №1 (Склад мокрохранения 5.8х5.8 м, h=2.5..2.8 м)",
            "Резервуар №4 (Склад мокрохранения 2.8х5.8 м, h=2.7..3.4 м)"
        ]
        self.cmb_tanks = ttk.Combobox(frame, textvariable=self.tank_var, values=tanks, state='readonly', width=52)
        self.cmb_tanks.grid(row=0, column=1, padx=10, pady=4)

        ttk.Label(frame, text="Замер рулеткой до воды, МЕТРЫ (м):").grid(row=1, column=0, sticky='w', pady=4)
        self.entry_tape = ttk.Entry(frame, width=15)
        self.entry_tape.insert(0, "1.00")
        self.entry_tape.grid(row=1, column=1, sticky='w', padx=10, pady=4)

        btn_calc = ttk.Button(self.tab_tanks, text="РАССЧИТАТЬ ОСТАТОК", command=self.calc_tanks)
        btn_calc.pack(pady=8)

        self.lbl_tanks_res = ttk.Label(self.tab_tanks, text="", font=('Segoe UI', 10, 'bold'), justify='center')
        self.lbl_tanks_res.pack(pady=5)

        self.btn_log_tanks = ttk.Button(self.tab_tanks, text="📋 Добавить запись в журнал", command=self.add_journal_tanks, state='disabled')
        self.btn_log_tanks.pack(pady=5)

    def calc_tanks(self):
        try:
            choice = self.tank_var.get()
            h_tape_m = float(self.entry_tape.get().replace(',', '.'))

            if "Машзал" in choice:
                max_h_m = 2.50
                V_max = 19600.0
                if h_tape_m > max_h_m:
                    messagebox.showwarning("Внимание", f"Замер не может превышать глубину бака ({max_h_m} м)")
                    return
                h_liq_m = max_h_m - h_tape_m
                V = 2.8 * 2.8 * h_liq_m * 1000.0
                t_name = "Резервуар расходный (Машзал)"
            elif "№1" in choice:
                max_h_m = 2.80
                if h_tape_m > max_h_m:
                    messagebox.showwarning("Внимание", f"Замер не может превышать максимальную высоту бака ({max_h_m} м)")
                    return
                V_wedge = 0.5 * 5.8 * 5.8 * 0.3 * 1000.0
                V_max = V_wedge + (5.8 * 5.8 * 2.5 * 1000.0)
                y_m = max_h_m - h_tape_m
                if y_m <= 0.3:
                    V = 0.5 * (5.8 * y_m / 0.3) * y_m * 5.8 * 1000.0
                else:
                    V = V_wedge + (5.8 * 5.8 * (y_m - 0.3) * 1000.0)
                t_name = "Резервуар №1 (Склад)"
            else:
                max_h_m = 3.40
                if h_tape_m > max_h_m:
                    messagebox.showwarning("Внимание", f"Замер не может превышать максимальную высоту бака ({max_h_m} м)")
                    return
                V_wedge = 0.5 * 2.8 * 5.8 * 0.7 * 1000.0
                V_max = V_wedge + (2.8 * 5.8 * 2.7 * 1000.0)
                y_m = max_h_m - h_tape_m
                if y_m <= 0.7:
                    V = 0.5 * (2.8 * 5.8 / 0.7) * (y_m ** 2) * 1000.0
                else:
                    V = V_wedge + (2.8 * 5.8 * (y_m - 0.7) * 1000.0)
                t_name = "Резервуар №4 (Склад)"

            V_m3 = V / 1000.0
            pct = (V / V_max) * 100.0
            h_liquid_m = (2.50 if "Машзал" in choice else (2.80 if "№1" in choice else 3.40)) - h_tape_m

            res_text = f"Резервуар: {t_name}\n" \
                       f"Фактический объем: {V:.0f} л ({V_m3:.2f} м³) | Полная емкость: {V_max:.0f} л\n" \
                       f"Уровень заполнения: {pct:.1f}% (глубина жидкости: {h_liquid_m:.2f} м)"
            self.lbl_tanks_res.config(text=res_text, foreground="#002050")

            self.last_res_tanks = {
                "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "Модуль": "Замер остатка в баках",
                "Входные данные": f"{t_name}, Замер={h_tape_m:.2f} м",
                "Результат": f"Объем: {V:.0f} л ({V_m3:.2f} м³); Заполнение: {pct:.1f}%; Глубина: {h_liquid_m:.2f} м",
                "Статус": "В норме"
            }
            self.btn_log_tanks.config(state='normal')
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте введенные числа")

    def add_journal_tanks(self):
        if self.last_res_tanks:
            self.add_to_journal(self.last_res_tanks)
            messagebox.showinfo("Журнал", "Замер остатка в резервуаре успешно сохранен!")

    # =========================================================================
    # 4. ВКЛАДКА: МУТНОСТЬ
    # =========================================================================
    def build_turbidity_tab(self):
        frame = ttk.LabelFrame(self.tab_turbidity, text=" Измерение на ПЭ-5300ВИ ", padding=15)
        frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(frame, text="Оптическая плотность (D):").grid(row=0, column=0, sticky='w', pady=4)
        self.entry_D = ttk.Entry(frame, width=15)
        self.entry_D.insert(0, "0.165")
        self.entry_D.grid(row=0, column=1, padx=10, pady=4)
        
        btn_calc = ttk.Button(self.tab_turbidity, text="РАССЧИТАТЬ МУТНОСТЬ", command=self.calc_turbidity)
        btn_calc.pack(pady=8)
        
        self.lbl_turb_res = ttk.Label(self.tab_turbidity, text="", font=('Segoe UI', 11, 'bold'))
        self.lbl_turb_res.pack(pady=5)

        self.btn_log_t3 = ttk.Button(self.tab_turbidity, text="📋 Добавить запись в журнал", command=self.add_journal_t3, state='disabled')
        self.btn_log_t3.pack(pady=5)

    def calc_turbidity(self):
        try:
            D = float(self.entry_D.get().replace(',', '.'))
            K, D0 = 0.009347066, 0.002417294
            C = 0.0 if D <= D0 else (D - D0) / K
            
            if C <= 2.0:
                status = "Отличное качество (готовая вода)"
            elif C <= 8.0:
                status = "Норма для осветлителей"
            elif C <= 15.0:
                status = "Повышенная мутность"
            else:
                status = "КРИТИЧЕСКАЯ МУТНОСТЬ / Вынос"

            self.lbl_turb_res.config(text=f"Рассчитанная мутность (C): {C:.2f} ЕМ/дм³\nСтатус: {status}", foreground="#107C41")
            
            self.last_res_t3 = {
                "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "Модуль": "Мутность ПЭ-5300ВИ",
                "Входные данные": f"D={D:.4f}",
                "Результат": f"C={C:.2f} ЕМ/дм³",
                "Статус": status
            }
            self.btn_log_t3.config(state='normal')
        except ValueError:
            messagebox.showerror("Ошибка", "Ошибка ввода плотности D")

    def add_journal_t3(self):
        if self.last_res_t3:
            self.add_to_journal(self.last_res_t3)
            messagebox.showinfo("Журнал", "Результат измерения мутности добавлен в сменный журнал!")

    # =========================================================================
    # 5. ВКЛАДКА: НАСТРОЙКА ПЛУНЖЕРА
    # =========================================================================
    def build_plunger_tab(self):
        frame = ttk.LabelFrame(self.tab_plunger, text=" Лимб насоса Ареопаг (0–60 делений, 0.5 мм/дел) ", padding=15)
        frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(frame, text="Текущее положение (делений 0–60):").grid(row=0, column=0, sticky='w', pady=4)
        self.entry_S = ttk.Entry(frame, width=15)
        self.entry_S.insert(0, "30")
        self.entry_S.grid(row=0, column=1, padx=10, pady=4)
        
        ttk.Label(frame, text="Текущая частота КИМ (Гц):").grid(row=1, column=0, sticky='w', pady=4)
        self.entry_f = ttk.Entry(frame, width=15)
        self.entry_f.insert(0, "45.29")
        self.entry_f.grid(row=1, column=1, padx=10, pady=4)
        
        btn_calc = ttk.Button(self.tab_plunger, text="РАССЧИТАТЬ ПОЛОЖЕНИЕ", command=self.calc_plunger)
        btn_calc.pack(pady=8)
        
        self.lbl_plunger_res = ttk.Label(self.tab_plunger, text="", font=('Segoe UI', 10, 'bold'), justify='center')
        self.lbl_plunger_res.pack(pady=5)

        self.btn_log_t4 = ttk.Button(self.tab_plunger, text="📋 Добавить запись в журнал", command=self.add_journal_t4, state='disabled')
        self.btn_log_t4.pack(pady=5)

    def calc_plunger(self):
        try:
            S = float(self.entry_S.get().replace(',', '.'))
            f = float(self.entry_f.get().replace(',', '.'))
            
            S_new = min(max(round(S * (f / 35.0)), 0), 60)
            
            if f >= 42.0:
                status_log = "Высокая частота (увеличьте ход)"
            elif f <= 25.0:
                status_log = "Низкая частота (уменьшите ход)"
            else:
                status_log = "В норме"

            res_text = f"Рекомендуемый ход плунжера: {S_new} делений (по шкале лимба)\nСтатус: {status_log}"
            self.lbl_plunger_res.config(text=res_text, foreground="#A4262C" if status_log != "В норме" else "#107C41")
            
            self.last_res_t4 = {
                "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "Модуль": "Настройка плунжера",
                "Входные данные": f"S={S:.0f} дел., f={f:.1f} Гц",
                "Результат": f"Реком. ход плунжера: {S_new} дел.",
                "Статус": status_log
            }
            self.btn_log_t4.config(state='normal')
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные параметры плунжера")

    def add_journal_t4(self):
        if self.last_res_t4:
            self.add_to_journal(self.last_res_t4)
            messagebox.showinfo("Журнал", "Настройка плунжера добавлена в сменный журнал!")

    # =========================================================================
    # 6. ВКЛАДКА: СМЕННЫЙ ЖУРНАЛ
    # =========================================================================
    def build_journal_tab(self):
        frame = ttk.Frame(self.tab_journal, padding=10)
        frame.pack(fill='both', expand=True)

        columns = ("Время", "Модуль", "Входные данные", "Результат", "Статус")
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', selectmode='browse')
        
        self.tree.heading("Время", text="Время")
        self.tree.heading("Модуль", text="Модуль")
        self.tree.heading("Входные данные", text="Входные данные")
        self.tree.heading("Результат", text="Результат")
        self.tree.heading("Статус", text="Статус")

        self.tree.column("Время", width=130, anchor='center')
        self.tree.column("Модуль", width=150, anchor='w')
        self.tree.column("Входные данные", width=200, anchor='w')
        self.tree.column("Результат", width=250, anchor='w')
        self.tree.column("Статус", width=120, anchor='center')

        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        btn_frame = ttk.Frame(self.tab_journal, padding=10)
        btn_frame.pack(fill='x')

        btn_export = ttk.Button(btn_frame, text="💾 Скачать журнал в Excel (.xlsx)", command=self.export_excel)
        btn_export.pack(side='left', padx=10)

        btn_clear = ttk.Button(btn_frame, text="🗑 Очистить журнал", command=self.clear_journal)
        btn_clear.pack(side='right', padx=10)

    def add_to_journal(self, entry):
        self.journal.append(entry)
        self.tree.insert("", "end", values=(
            entry["Время"],
            entry["Модуль"],
            entry["Входные данные"],
            entry["Результат"],
            entry["Статус"]
        ))

    def export_excel(self):
        if not self.journal:
            messagebox.showwarning("Предупреждение", "Сменный журнал пуст!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile=f"Сменный_журнал_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        )
        if file_path:
            df = pd.DataFrame(self.journal)
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Успех", f"Файл успешно сохранен:\n{file_path}")

    def clear_journal(self):
        if messagebox.askyesno("Подтверждение", "Очистить весь сменный журнал?"):
            self.journal.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)

    # =========================================================================
    # 7. ВКЛАДКА: ПАМЯТКА И РАСЧЕТЫ
    # =========================================================================
    def build_memo_tab(self):
        txt_area = ScrolledText(self.tab_memo, font=('Consolas', 10), wrap='word', padding=10)
        txt_area.pack(fill='both', expand=True)

        memo_text = """ СПРАВОЧНАЯ ПАМЯТКА И ФОРМУЛЫ ВОДОПОДГОТОВКИ
==============================================================================
ТМК СинТЗ — Энергоцех Чемезов

------------------------------------------------------------------------------
1. ТЕХНОЛОГИЧЕСКИЙ РЕГЛАМЕНТ БЕЗОПАСНОГО ИЗМЕНЕНИЯ ДОЗИРОВОК
------------------------------------------------------------------------------
• Максимальный безопасный разовый шаг: не более +0.50 ... +0.80 мг/л.
• Технологический интервал между шагами: 15–20 минут (время полного отклика).

• Риски резкого залпового увеличения дозировки:
  1) Перезарядка коллоидов (рестабилизация): при избытке Al³+ частицы мути
     приобретают положительный заряд и перестают слипаться, образуя вторичную муть.
  2) Проскок остаточного алюминия: превышение нормы Al_ост > 0.2 мг/л в готовой воде
     и зарастание трубопроводов осадком.
  3) Падение pH: закисление среды и блокировка гидролиза коагулянта.
  4) Кольматация песчаных фильтров: превышение дозы флокулянта > 0.75 мг/л
     образует резинистую пленку на кварцевом песке.

------------------------------------------------------------------------------
2. ПРОБНАЯ КОАГУЛЯЦИЯ (JAR TEST И АВТОМАТИЧЕСКИЙ РЕЖИМ ПК УНИТОК)
------------------------------------------------------------------------------
А. АВТОМАТИЧЕСКИЙ РЕЖИМ ПК УНИТОК (индекс скорости V в строке 3.ПК):
• V >= 0.800 (Норма): быстрое формирование плотных хлопьев, стабильное «одеяло».
• 0.500 <= V < 0.800 (Погранично): вялая кинетика, прибавка +0.40 мг/л.
• V < 0.500 (Критически мало / вынос): прибавка +0.90 мг/л ступенчато (+0.80 мг/л
  на первом шаге) и продувка шламоуплотнителей.

Б. ЛАБОРАТОРНЫЙ JAR TEST:
1. Быстрое перемешивание: 120–180 об/мин (45–60 сек) с «Эпоха».
2. Медленное перемешивание: 30–45 об/мин (10–15 мин) с «ЭкоПлюс».
3. Отстаивание: 0 об/мин (покой, 15–20 мин).

------------------------------------------------------------------------------
3. ДОЗИРОВАНИЕ РЕАГЕНТОВ И СООТНОШЕНИЕ 22:1
------------------------------------------------------------------------------
• Коагулянт «Эпоха» (Al³+): 10–18 мг/л.
• Флокулянт «ЭкоПлюс» (ПАА): предел 0.75 мг/л (СП 31.13330.2012).
• Соотношение 22:1: 16.5 / 22 = 0.75 мг/л (защита фильтров от забивания).
• Формула расхода насоса: q = (Q * D) / (10 * C * rho) л/ч.

------------------------------------------------------------------------------
4. ГЕОМЕТРИЧЕСКИЙ РАСЧЕТ ОСТАТКА В РЕЗЕРВУАРАХ (В МЕТРАХ)
------------------------------------------------------------------------------
Замер рулеткой (h_зам) от верхнего края. Глубина от дна: y = H_макс - h_зам.

• 1. Резервуар расходный (Машзал, 2.8 x 2.8 x 2.5 м):
  V = 7840 * (2.50 - h_зам) л. Полная емкость: 19 600 л (19.60 м³).

• 2. Резервуар №1 (Склад, 5.8 x 5.8 м, уклон 0.30 м):
  - При y <= 0.30 м: V = 56 067 * y² л.
  - При y > 0.30 м: V = 5 046 + 33 640 * (y - 0.30) л.
  Полная емкость: 89 146 л (89.15 м³).

• 3. Резервуар №4 (Склад, 2.8 x 5.8 м, уклон 0.70 м):
  - При y <= 0.70 м: V = 11 600 * y² л.
  - При y > 0.70 м: V = 5 684 + 16 240 * (y - 0.70) л.
  Полная емкость: 49 532 л (49.53 м³).

------------------------------------------------------------------------------
5. ФОТОМЕТРИЯ ПЭ-5300ВИ И НАСОСЫ «АРЕОПАГ»
------------------------------------------------------------------------------
• Мутность (ПНД Ф 14.1:2:4.213-05): C = (D - 0.002417294) / 0.009347066.
• Плунжер «Ареопаг»: Шкала 0–60 делений (0.5 мм/дел). Целевая f = 35.0 Гц.
==============================================================================
"""
        txt_area.insert('1.0', memo_text)
        txt_area.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = TMKWaterAppDesktop(root)
    root.mainloop()