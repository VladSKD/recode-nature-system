

import math
import pandas as pd
import os
from typing import Dict

# -------------------------
# Параметри 
# -------------------------
# --- Тижневі діапазони металу (т/тиждень) ---
weekly_metal_ranges = [
    (0, 200),
    (200, 480),
    (480, 800),
    (800, 1200),
    (1200, 1800),
    (1800, 2600),
    (2600, math.inf)
]

# --- CAPEX компоненти (умовні €/тонна/рік — можна коригувати) ---
base_capex_components = {
    "crusher": 300,             
    "sorting_line": 250,        
    "induction_furnace": 500,   
    "press": 200,               
    "overhead_crane": 150,      # кран-балка
    "storage": 100,             
    "electrical": 120,          
    "engineering": 80,          
    "contingency": 0.10         
}

# --- Зарплати (€/тиждень) ---
staff_roles = {
    "Worker": 900,     # оператори/робітники
    "Engineer": 1300,  # інженери/технічні фахівці
    "Manager": 2000    # менеджмент/керування
}

# --- Ціна основного продукту (метал) ---
PRICE_METAL = 300.0  # €/тонна

# --- Побічні доходи і коефіцієнти (припущення) ---
# Для кожної тонни металу:
# - шлаки/відходи, які можна продати: 0.10 т/т металу * PRICE_SLAG
# - вторинні сплави/концентрати: 0.05 т/т металу * PRICE_ALLOY
# - енергетичний ефект від печі (економія/продаж енергії): ENERGY_VALUE €/т
PRICE_SLAG = 30.0    # €/т (приблизно)
PRICE_ALLOY = 200.0  # €/т (вища ціна за концентрати)
ENERGY_VALUE_PER_T = 10.0  # €/т (взаємозалік/реалізація енергії/економія)

# --- Інші параметри OPEX ---
OPEX_WAGES_MULTIPLIER = 1.25  # множник для перетворення зарплат->річний OPEX (інші експл. витрати)
NON_WAGE_OPEX_PER_T = 25.0    # €/т/рік інші операційні витрати (спецхімія, електро, паливо, обслуг.)

# -------------------------
# Утиліти
# -------------------------
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nНатисніть Enter для продовження...")

# -------------------------
# Логіка персоналу, площі, CAPEX
# -------------------------
def get_staff_count(annual_tonnage: float) -> Dict[str,int]:
    if annual_tonnage <= 200*52:
        return {"Worker": 6, "Engineer": 2, "Manager": 1}
    elif annual_tonnage <= 800*52:
        return {"Worker": 14, "Engineer": 4, "Manager": 2}
    elif annual_tonnage <= 1800*52:
        return {"Worker": 26, "Engineer": 6, "Manager": 3}
    elif annual_tonnage <= 2600*52:
        return {"Worker": 36, "Engineer": 8, "Manager": 4}
    else:
        return {"Worker": 48, "Engineer": 10, "Manager": 5}

def estimate_area(annual_tonnage: float) -> float:
    return round(annual_tonnage * 1.2 + 2500, 0)

def calc_capex(annual_tonnage: float) -> Dict[str,float]:
    unit_sum = (
        base_capex_components["crusher"] +
        base_capex_components["sorting_line"] +
        base_capex_components["induction_furnace"] +
        base_capex_components["press"] +
        base_capex_components["overhead_crane"] +
        base_capex_components["storage"] +
        base_capex_components["electrical"] +
        base_capex_components["engineering"]
    )
    capex_sum = annual_tonnage * unit_sum
    capex_total = capex_sum * (1 + base_capex_components["contingency"])
    return {
        "Conservative": capex_total * 1.15,
        "Base": capex_total,
        "Optimistic": capex_total * 0.9
    }

# -------------------------
# OPEX та дохід
# -------------------------
def calc_weekly_wages(staff_count: Dict[str,int]) -> float:
    return sum(staff_roles[role] * count for role, count in staff_count.items())

def calc_annual_opex(weekly_wages: float, annual_tonnage: float) -> float:
    wages_annual = weekly_wages * 52 * OPEX_WAGES_MULTIPLIER
    other_opex = annual_tonnage * NON_WAGE_OPEX_PER_T
    return wages_annual + other_opex

def calc_annual_revenue(annual_tonnage: float) -> float:
    revenue_metal = annual_tonnage * PRICE_METAL
    # Побічні доходи:
    slag_tons = annual_tonnage * 0.10   # 0.10 т шлаків на 1 т металу 
    alloy_tons = annual_tonnage * 0.05  # 0.05 т вторинних сплавів на 1 т металу
    revenue_slag = slag_tons * PRICE_SLAG
    revenue_alloy = alloy_tons * PRICE_ALLOY
    revenue_energy = annual_tonnage * ENERGY_VALUE_PER_T
    total = revenue_metal + revenue_slag + revenue_alloy + revenue_energy
    return total

# -------------------------
# Обчислення для діапазону
# -------------------------
def compute_range(weekly_range: tuple):
    clear_console()
    if weekly_range[1] == math.inf:
        weekly_tonnage = weekly_range[0] * 1.5 if weekly_range[0] > 0 else 3000
    else:
        weekly_tonnage = (weekly_range[0] + weekly_range[1]) / 2

    annual_tonnage = weekly_tonnage * 52
    capex = calc_capex(annual_tonnage)
    staff_count = get_staff_count(annual_tonnage)
    weekly_wages = calc_weekly_wages(staff_count)
    annual_opex = calc_annual_opex(weekly_wages, annual_tonnage)
    annual_revenue = calc_annual_revenue(annual_tonnage)
    payback_base = capex["Base"] / (annual_revenue - annual_opex) if annual_revenue > annual_opex else math.inf
    area = estimate_area(annual_tonnage)

    print(f"\n--- Розрахунок для діапазону {weekly_range[0]} – {weekly_range[1] if weekly_range[1]!=math.inf else '∞'} т/тиждень металу ---")
    print(f"Середній тижневий обсяг: {round(weekly_tonnage,1)} т/тиждень")
    print(f"Річний обсяг: {round(annual_tonnage,1)} т/рік")
    print(f"Площа заводу (прибл.): {area} м²")
    print(f"Щотижневі зарплати: {weekly_wages} €")
    print(f"Щорічний OPEX: {round(annual_opex,2)} €")
    print(f"Очікуваний щорічний дохід: {round(annual_revenue,2)} €")
    print(f"Прогнозована окупність (роки, base CAPEX): {round(payback_base,1) if payback_base!=math.inf else '∞ (негативний прибуток)'}")
    print("Персонал:")
    for role, count in staff_count.items():
        print(f"  {role}: {count} осіб")
    print("CAPEX (€):")
    for scen, val in capex.items():
        print(f"  {scen}: {round(val,2)}")
    pause()

# -------------------------
# Кластерні обчислення (4% металу від усіх відходів)
# -------------------------
def compute_cluster():
    clear_console()
    try:
        df = pd.read_csv("cost_all_clusters.csv")
        required = {'cluster_id','region','waste_tonnes_week'}
        if not required.issubset(set(df.columns)):
            raise Exception(f"Файл повинен містити колонки: {required}")
    except Exception as e:
        print(f"Помилка при завантаженні файлу: {e}")
        pause()
        return

    min_cluster = df['cluster_id'].min()
    max_cluster = df['cluster_id'].max()
    print(f"\nДоступні кластери: від Cluster {min_cluster} до Cluster {max_cluster}")

    choice = input("Введіть номер  кластера: ")
    if not choice.isdigit():
        print("Невірний ввід.")
        pause()
        return
    choice = int(choice)
    if 0 <= choice <= len(df):
        row = df.iloc[choice]
        total_weekly_waste = row['waste_tonnes_week']
        weekly_metal = total_weekly_waste * 0.04  # 4% металу
        annual_tonnage = weekly_metal * 52

        capex = calc_capex(annual_tonnage)
        staff_count = get_staff_count(annual_tonnage)
        weekly_wages = calc_weekly_wages(staff_count)
        annual_opex = calc_annual_opex(weekly_wages, annual_tonnage)
        annual_revenue = calc_annual_revenue(annual_tonnage)
        payback_base = capex["Base"] / (annual_revenue - annual_opex) if annual_revenue > annual_opex else math.inf
        area = estimate_area(annual_tonnage)

        print(f"\n--- Розрахунок для Cluster {row['cluster_id']} ---")
        print(f"Region: {row['region']}")
        print(f"Тижневий обсяг відходів (всього): {round(total_weekly_waste,1)} т")
        print(f"Тижневий обсяг металу (4%): {round(weekly_metal,3)} т")
        print(f"Річний обсяг металу: {round(annual_tonnage,1)} т/рік")
        print(f"Площа заводу (прибл.): {area} м²")
        print(f"Щотижневі зарплати: {weekly_wages} €")
        print(f"Щорічний OPEX: {round(annual_opex,2)} €")
        print(f"Очікуваний щорічний дохід: {round(annual_revenue,2)} €")
        print(f"Прогнозована окупність (роки, base CAPEX): {round(payback_base,1) if payback_base!=math.inf else '∞ (негативний прибуток)'}")
        print("Персонал:")
        for role, count in staff_count.items():
            print(f"  {role}: {count} осіб")
        print("CAPEX (€):")
        for scen, val in capex.items():
            print(f"  {scen}: {round(val,2)}")
    else:
        print("Неправильний номер кластера.")
    pause()

# -------------------------
# Показати всі кластери
# -------------------------
def show_all_clusters():
    clear_console()
    try:
        df = pd.read_csv("cost_all_clusters.csv")
        if 'waste_tonnes_week' not in df.columns:
            raise Exception("Відсутня колонка 'waste_tonnes_week'")
        df2 = df[['cluster_id','region','waste_tonnes_week']].copy()
        df2['weekly_metal_tonnes'] = df2['waste_tonnes_week'] * 0.04
    except Exception as e:
        print(f"Помилка при завантаженні файлу: {e}")
        pause()
        return

    print("\n--- Інформація про всі кластери (метал 4%) ---")
    print(df2.to_string(index=False))
    pause()

# -------------------------
# Обчислити всі кластери і зберегти
# -------------------------
def compute_all_clusters_to_file():
    clear_console()
    try:
        df = pd.read_csv("cost_all_clusters.csv")
        if 'waste_tonnes_week' not in df.columns:
            raise Exception("Відсутня колонка 'waste_tonnes_week'")
    except Exception as e:
        print(f"Помилка при завантаженні файлу: {e}")
        pause()
        return

    results = []
    for idx, row in df.iterrows():
        weekly_metal = row['waste_tonnes_week'] * 0.04
        annual_tonnage = weekly_metal * 52

        capex = calc_capex(annual_tonnage)
        staff_count = get_staff_count(annual_tonnage)
        weekly_wages = calc_weekly_wages(staff_count)
        annual_opex = calc_annual_opex(weekly_wages, annual_tonnage)
        annual_revenue = calc_annual_revenue(annual_tonnage)
        payback_base = capex["Base"] / (annual_revenue - annual_opex) if annual_revenue > annual_opex else math.inf

        results.append({
            "cluster_id": row.get('cluster_id', idx+1),
            "region": row.get('region', ''),
            "annual_opex": round(annual_opex,2),
            "annual_revenue": round(annual_revenue,2),
            "payback_base_years": round(payback_base,1) if payback_base!=math.inf else None,
            "CAPEXC": round(capex["Conservative"],2),
            "CAPEXB": round(capex["Base"],2),
            "CAPEXO": round(capex["Optimistic"],2)
        })

    out_df = pd.DataFrame(results)
    out_df.to_csv("cost_metal.csv", index=False)
    print("\nРозрахунки завершено. Файл 'cost_metal.csv' створено.")
    pause()

# -------------------------
# Меню
# -------------------------
def menu():
    while True:
        clear_console()
        print("\n=== Головне меню ===")
        print("1. Обчислити для тижневого діапазону металу")
        print("2. Обчислити для кластера ")
        print("3. Показати інформацію про всі кластери ")
        print("4. Обрахувати всі кластери та зберегти у файл")
        print("5. Вийти")
        choice = input("Введіть номер: ").strip()
        if choice == "5":
            print("Вихід...")
            break
        elif choice == "1":
            clear_console()
            print("\nВиберіть тижневий діапазон металу:")
            for i, r in enumerate(weekly_metal_ranges, 1):
                hi = r[1] if r[1] != math.inf else '∞'
                print(f"{i}. {r[0]} – {hi} т/тиждень")
            sub_choice = input("Введіть номер діапазону: ").strip()
            if not sub_choice.isdigit():
                continue
            sub_choice = int(sub_choice)
            if 1 <= sub_choice <= len(weekly_metal_ranges):
                compute_range(weekly_metal_ranges[sub_choice-1])
            else:
                print("Неправильний номер діапазону.")
                pause()
        elif choice == "2":
            compute_cluster()
        elif choice == "3":
            show_all_clusters()
        elif choice == "4":
            compute_all_clusters_to_file()
        else:
            print("Неправильний номер меню.")
            pause()

if __name__ == "__main__":
    menu()
