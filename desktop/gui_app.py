import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import pandas as pd

class TMKWaterAppDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("ТМК СинТЗ — Энергоцех Чемезов | Комплекс водоподготовки")
        self.root.geometry("900x700")
        
        # Хранилище журнала и последних результатов
        self.journal = []
        self.last_res_t1 = None
        self.last_res_t2 = None
        self.last_res_t3 = None
        self.last_res_t4 = None

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
        self.tab_turbidity = ttk.Frame(self.notebook)
        self.tab_plunger = ttk.Frame(self.notebook)
        self.tab_journal = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_dosing, text="🧪 Дозирование КИМ")
        self.notebook.add(self.tab_prep, text="🛢 Приготовление раствора")
        self.notebook.add(self.tab_turbidity, text="🔬 Мутность (ПЭ-5300ВИ)")
        self.notebook.add(self.tab_plunger, text="⚙️ Настройка плунжера")
        self.notebook.add(self.tab_journal, text="📋 Сменный журнал")
        
        # Построение интерфейсов
        self.build_dosing_tab()
        self.build_prep_tab()
        self.build_turbidity_tab()
        self.build_plunger_tab()
        self.build_journal_tab()

    # =========================================================================
    # 1. ВКЛАДКА: ДОЗИРОВАНИЕ КИМ
    # =========================================================================
    def build_dosing_tab(self):
        frame = ttk.LabelFrame(self.tab_dosing, text=" Показатели системы ", padding=15)
        frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(frame, text="Расход воды (Q), м³/ч:").grid(row=0, column=0, sticky='w', pady=4)
        self.entry_Q = ttk.Entry(frame, width=15)
        self.entry_Q.insert(0, "431.9")
        self.entry_Q.grid(row=0, column=1, padx=10, pady=4)
        
        ttk.Label(frame, text="Мутность Осветлители (М_осв):").grid(row=1, column=0, sticky='w', pady=4)
        self.entry_M_clar = ttk.Entry(frame, width=15)
        self.entry_M_clar.insert(0, "18.1")
        self.entry_M_clar.grid(row=1, column=1, padx=10, pady=4)
        
        ttk.Label(frame, text="Текущая доза коагулянта, мг/л:").grid(row=2, column=0, sticky='w', pady=4)
        self.entry_D_curr = ttk.Entry(frame, width=15)
        self.entry_D_curr.insert(0, "13.8")
        self.entry_D_curr.grid(row=2, column=1, padx=10, pady=4)

        ttk.Label(frame, text="Концентрация коагулянта (%):").grid(row=3, column=0, sticky='w', pady=4)
        self.entry_C_coag = ttk.Entry(frame, width=15)
        self.entry_C_coag.insert(0, "1.0")
        self.entry_C_coag.grid(row=3, column=1, padx=10, pady=4)

        ttk.Label(frame, text="Пропорция Коаг. / Флок. (1 : N):").grid(row=4, column=0, sticky='w', pady=4)
        self.entry_ratio = ttk.Entry(frame, width=15)
        self.entry_ratio.insert(0, "22.0")
        self.entry_ratio.grid(row=4, column=1, padx=10, pady=4)
        
        btn_calc = ttk.Button(self.tab_dosing, text="РАССЧИТАТЬ ДОЗИРОВКУ", command=self.calc_dosing)
        btn_calc.pack(pady=8)
        
        self.lbl_dosing_res = ttk.Label(self.tab_dosing, text="", font=('Segoe UI', 10, 'bold'), justify='center')
        self.lbl_dosing_res.pack(pady=5)

        self.btn_log_t1 = ttk.Button(self.tab_dosing, text="📋 Добавить запись в журнал", command=self.add_journal_t1, state='disabled')
        self.btn_log_t1.pack(pady=5)

    def calc_dosing(self):
        try:
            Q = float(self.entry_Q.get())
            M_clar = float(self.entry_M_clar.get())
            D_curr = float(self.entry_D_curr.get())
            C_coag = float(self.entry_C_coag.get())
            ratio = float(self.entry_ratio.get())

            rho_coag = 1.010 if C_coag <= 1.0 else 1.013
            
            alerts = []
            if M_clar > 8.0:
                delta_M = M_clar - 8.0
                coag_step = round((delta_M / 2.0) * 0.3, 2)
                D_coag = min(D_curr + max(coag_step, 0.5), 18.0)
                alerts.append(f"Повышенная мутность (М={M_clar}). Доза увеличена.")
            else:
                D_coag = D_curr

            D_floc = round(D_coag / ratio, 2)
            if D_floc > 0.75:
                D_floc = 0.75
                alerts.append("Доза флокулянта ограничена 0.75 мг/л.")

            q_coag = (Q * D_coag) / (10 * C_coag * rho_coag)
            q_floc = (Q * D_floc) / (10 * 0.04 * 0.991)

            res_text = f"Доза Эпоха: {D_coag:.2f} мг/л ({q_coag:.1f} л/ч)\n" \
                       f"Доза ЭкоПлюс (1:{ratio:.0f}): {D_floc:.2f} мг/л ({q_floc:.1f} л/ч)"
            if alerts:
                res_text += "\n⚠️ " + "\n⚠️ ".join(alerts)

            self.lbl_dosing_res.config(text=res_text, foreground="#107C41" if not alerts else "#D83B01")
            
            self.last_res_t1 = {
                "Время": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "Модуль": "Дозирование КИМ",
                "Входные данные": f"Q={Q}, M_осв={M_clar}, Соотношение=1:{ratio:.0f}",
                "Результат": f"Эпоха: {D_coag:.2f} мг/л ({q_coag:.1f} л/ч); ЭкоПлюс: {D_floc:.2f} мг/л ({q_floc:.1f} л/ч)",
                "Статус": "Предупреждение" if alerts else "В норме"
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
        frame = ttk.LabelFrame(self.tab_prep, text=" Затворение по рулетке (Бак 2.8 х 2.8 х 2.4 м) ", padding=15)
        frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(frame, text="Расстояние от края бака до воды (см):").grid(row=0, column=0, sticky='w', pady=4)
        self.entry_h = ttk.Entry(frame, width=15)
        self.entry_h.insert(0, "100")
        self.entry_h.grid(row=0, column=1, padx=10, pady=4)
        
        ttk.Label(frame, text="Целевая концентрация раствора (%):").grid(row=1, column=0, sticky='w', pady=4)
        self.var_conc = tk.DoubleVar(value=1.0)
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
            h_cm = float(self.entry_h.get())
            c_target = self.var_conc.get()
            c_tov = float(self.entry_C_tov.get())
            rho_tov = float(self.entry_rho_tov.get())
            
            V_add = h_cm * 78.4
            V_remain = 18816.0 - V_add
            
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
    # 3. ВКЛАДКА: МУТНОСТЬ
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
            D = float(self.entry_D.get())
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
    # 4. ВКЛАДКА: НАСТРОЙКА ПЛУНЖЕРА
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
        self.entry_f.insert(0, "48.0")
        self.entry_f.grid(row=1, column=1, padx=10, pady=4)
        
        btn_calc = ttk.Button(self.tab_plunger, text="РАССЧИТАТЬ ПОЛОЖЕНИЕ", command=self.calc_plunger)
        btn_calc.pack(pady=8)
        
        self.lbl_plunger_res = ttk.Label(self.tab_plunger, text="", font=('Segoe UI', 10, 'bold'), justify='center')
        self.lbl_plunger_res.pack(pady=5)

        self.btn_log_t4 = ttk.Button(self.tab_plunger, text="📋 Добавить запись в журнал", command=self.add_journal_t4, state='disabled')
        self.btn_log_t4.pack(pady=5)

    def calc_plunger(self):
        try:
            S = float(self.entry_S.get())
            f = float(self.entry_f.get())
            
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
    # 5. ВКЛАДКА: СМЕННЫЙ ЖУРНАЛ
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

if __name__ == "__main__":
    root = tk.Tk()
    app = TMKWaterAppDesktop(root)
    root.mainloop()