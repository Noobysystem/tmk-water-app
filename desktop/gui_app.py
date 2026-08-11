import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class TMKWaterAppDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("ТМК СинТЗ — Энергоцех Чемезов | Комплекс водоподготовки")
        self.root.geometry("850x650")
        
        # Стилизация
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[10, 5])
        
        # Панель вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Инициализация вкладок
        self.tab_dosing = ttk.Frame(self.notebook)
        self.tab_prep = ttk.Frame(self.notebook)
        self.tab_turbidity = ttk.Frame(self.notebook)
        self.tab_plunger = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_dosing, text="🧪 Дозирование КИМ")
        self.notebook.add(self.tab_prep, text="🛢 Приготовление раствора")
        self.notebook.add(self.tab_turbidity, text="🔬 Мутность (ПЭ-5300ВИ)")
        self.notebook.add(self.tab_plunger, text="⚙️ Настройка плунжера")
        
        # Построение интерфейсов
        self.build_dosing_tab()
        self.build_prep_tab()
        self.build_turbidity_tab()
        self.build_plunger_tab()

    # 1. ВКЛАДКА: ДОЗИРОВАНИЕ КИМ
    def build_dosing_tab(self):
        frame = ttk.LabelFrame(self.tab_dosing, text=" Показатели системы ", padding=15)
        frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(frame, text="Расход воды (Q), м³/ч:").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_Q = ttk.Entry(frame)
        self.entry_Q.insert(0, "431.9")
        self.entry_Q.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(frame, text="Мутность Осветлители (М_осв):").grid(row=1, column=0, sticky='w', pady=5)
        self.entry_M_clar = ttk.Entry(frame)
        self.entry_M_clar.insert(0, "18.1")
        self.entry_M_clar.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(frame, text="Текущая доза коагулянта, мг/л:").grid(row=2, column=0, sticky='w', pady=5)
        self.entry_D_curr = ttk.Entry(frame)
        self.entry_D_curr.insert(0, "13.8")
        self.entry_D_curr.grid(row=2, column=1, padx=10, pady=5)
        
        btn_calc = ttk.Button(self.tab_dosing, text="РАССЧИТАТЬ ДОЗИРОВКУ", command=self.calc_dosing)
        btn_calc.pack(pady=10)
        
        self.lbl_dosing_res = ttk.Label(self.tab_dosing, text="", font=('Segoe UI', 10, 'bold'))
        self.lbl_dosing_res.pack(pady=10)

    def calc_dosing(self):
        try:
            Q = float(self.entry_Q.get())
            M_clar = float(self.entry_M_clar.get())
            D_curr = float(self.entry_D_curr.get())
            
            D_coag = D_curr + max((M_clar - 8.0) / 2.0 * 0.3, 0.5) if M_clar > 8.0 else D_curr
            D_coag = min(D_coag, 18.0)
            D_floc = min(round(D_coag / 22.0, 2), 0.75)
            
            q_coag = (Q * D_coag) / (10 * 1.0 * 1.010)
            q_floc = (Q * D_floc) / (10 * 0.04 * 0.991)
            
            res_text = f"Рекомендуемая доза Эпоха: {D_coag:.2f} мг/л | Расход насоса: {q_coag:.1f} л/ч\n" \
                       f"Рекомендуемая доза ЭкоПлюс: {D_floc:.2f} мг/л | Расход насоса: {q_floc:.1f} л/ч"
            self.lbl_dosing_res.config(text=res_text, foreground="green")
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте корректность введенных чисел")

    # 2. ВКЛАДКА: ПРИГОТОВЛЕНИЕ РАСТВОРА
    def build_prep_tab(self):
        frame = ttk.LabelFrame(self.tab_prep, text=" Затворение по рулетке (Бак 2.8 х 2.8 х 2.4 м) ", padding=15)
        frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(frame, text="Расстояние от края бака до воды (см):").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_h = ttk.Entry(frame)
        self.entry_h.insert(0, "100")
        self.entry_h.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(frame, text="Целевая концентрация (%):").grid(row=1, column=0, sticky='w', pady=5)
        self.var_conc = tk.DoubleVar(value=1.0)
        rb1 = ttk.Radiobutton(frame, text="1.0%", variable=self.var_conc, value=1.0)
        rb2 = ttk.Radiobutton(frame, text="1.2%", variable=self.var_conc, value=1.2)
        rb1.grid(row=1, column=1, sticky='w')
        rb2.grid(row=1, column=1, padx=60, sticky='w')
        
        btn_calc = ttk.Button(self.tab_prep, text="РАССЧИТАТЬ ОБЪЕМЫ", command=self.calc_prep)
        btn_calc.pack(pady=10)
        
        self.lbl_prep_res = ttk.Label(self.tab_prep, text="", font=('Segoe UI', 10))
        self.lbl_prep_res.pack(pady=10)

    def calc_prep(self):
        try:
            h_cm = float(self.entry_h.get())
            c_target = self.var_conc.get()
            
            V_add = h_cm * 78.4
            rho_work = 1.010 if c_target == 1.0 else 1.012
            M_dry = V_add * (c_target / 100.0) * rho_work
            M_tov = M_dry / 0.092
            V_tov = M_tov / 1.24
            V_water = V_add - V_tov
            
            res_text = f"Залить концентрата 'Эпоха' из еврокуба: {V_tov:.1f} л ({M_tov:.1f} кг)\n" \
                       f"Долить обычной воды: {V_water:.0f} л\n" \
                       f"Общий объем доведения: {V_add:.0f} л"
            self.lbl_prep_res.config(text=res_text, font=('Segoe UI', 10, 'bold'), foreground="blue")
        except ValueError:
            messagebox.showerror("Ошибка", "Введены неверные данные")

    # 3. ВКЛАДКА: МУТНОСТЬ
    def build_turbidity_tab(self):
        frame = ttk.LabelFrame(self.tab_turbidity, text=" Измерение на ПЭ-5300ВИ ", padding=15)
        frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(frame, text="Оптическая плотность (D):").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_D = ttk.Entry(frame)
        self.entry_D.insert(0, "0.165")
        self.entry_D.grid(row=0, column=1, padx=10, pady=5)
        
        btn_calc = ttk.Button(self.tab_turbidity, text="РАССЧИТАТЬ МУТНОСТЬ", command=self.calc_turbidity)
        btn_calc.pack(pady=10)
        
        self.lbl_turb_res = ttk.Label(self.tab_turbidity, text="", font=('Segoe UI', 11, 'bold'))
        self.lbl_turb_res.pack(pady=10)

    def calc_turbidity(self):
        try:
            D = float(self.entry_D.get())
            K, D0 = 0.009347066, 0.002417294
            C = 0.0 if D <= D0 else (D - D0) / K
            self.lbl_turb_res.config(text=f"Рассчитанная мутность (C): {C:.2f} ЕМ/дм³", foreground="darkgreen")
        except ValueError:
            messagebox.showerror("Ошибка", "Ошибка ввода плотности")

    # 4. ВКЛАДКА: НАСТРОЙКА ПЛУНЖЕРА
    def build_plunger_tab(self):
        frame = ttk.LabelFrame(self.tab_plunger, text=" Лимб насоса Ареопаг (0–60 делений) ", padding=15)
        frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(frame, text="Текущее положение (делений 0–60):").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_S = ttk.Entry(frame)
        self.entry_S.insert(0, "30")
        self.entry_S.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(frame, text="Текущая частота КИМ (Гц):").grid(row=1, column=0, sticky='w', pady=5)
        self.entry_f = ttk.Entry(frame)
        self.entry_f.insert(0, "48.0")
        self.entry_f.grid(row=1, column=1, padx=10, pady=5)
        
        btn_calc = ttk.Button(self.tab_plunger, text="РАССЧИТАТЬ ПОЛОЖЕНИЕ", command=self.calc_plunger)
        btn_calc.pack(pady=10)
        
        self.lbl_plunger_res = ttk.Label(self.tab_plunger, text="", font=('Segoe UI', 10, 'bold'))
        self.lbl_plunger_res.pack(pady=10)

    def calc_plunger(self):
        try:
            S = float(self.entry_S.get())
            f = float(self.entry_f.get())
            
            S_new = min(max(round(S * (f / 35.0)), 0), 60)
            self.lbl_plunger_res.config(text=f"Рекомендуемый ход плунжера: {S_new} делений (по шкале)", foreground="darkred")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные параметры плунжера")

if __name__ == "__main__":
    root = tk.Tk()
    app = TMKWaterAppDesktop(root)
    root.mainloop()