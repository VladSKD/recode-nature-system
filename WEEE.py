import math
import pandas as pd
import os

# --- Тижневі діапазони WEEE (т/тиждень) ---
weekly_weee_ranges = [
    (0, 250),
    (250, 600),
    (600, 1000),
    (1000, 1500),
    (1500, 2250),
    (2250, 3250),
    (3250, math.inf)
]

# --- Базові компоненти CAPEX для WEEE (€/т/рік) ---
base_capex_components = {
    "shredder": 300, 
    "sorter": 180, 
    "battery_recycler": 220,
    "storage": 80, 
    "civil_works": 150, 
    "electrical": 70,
    "engineering": 60, 
    "contingency": 0.1
}

# --- Зарплати на тиждень (€/тиждень) ---
staff_roles = {
    "Operator": 700,
    "Technician": 900,
    "Manager": 1200,
    "SafetyOfficer": 800
}

# --- Ціни на продукцію/ресурси ---
PRICE_RECLAIMED_METALS = 120   # €/т
PRICE_RECLAIMED_BATTERY = 500  # €/т
ELECTRONICS_SHARE = 0.05        # 5% від загального обсягу

# --- Утиліти ---
def clear_console():
    os.system("cls" if os.name=="nt" else "clear")

def pause():
    input("\nНатисніть Enter для продовження...")

# --- Персонал та розрахунки ---
def get_staff_count(annual_tonnage):
    if annual_tonnage <= 250*52:
        return {"Operator": 3, "Technician": 1, "Manager":1, "SafetyOfficer":1}
    elif annual_tonnage <= 1000*52:
        return {"Operator": 6, "Technician": 2, "Manager":2, "SafetyOfficer":1}
    elif annual_tonnage <= 2250*52:
        return {"Operator": 10, "Technician": 4, "Manager":3, "SafetyOfficer":2}
    elif annual_tonnage <= 3250*52:
        return {"Operator": 14, "Technician": 6, "Manager":4, "SafetyOfficer":2}
    else:
        return {"Operator": 18, "Technician": 8, "Manager":5, "SafetyOfficer":3}

def estimate_area(annual_tonnage):
    return round(annual_tonnage*0.8 + 500,0)  # м²

def calc_capex(annual_tonnage):
    capex_sum = annual_tonnage * (
        base_capex_components["shredder"] +
        base_capex_components["sorter"] +
        base_capex_components["battery_recycler"] +
        base_capex_components["storage"] +
        base_capex_components["civil_works"] +
        base_capex_components["electrical"] +
        base_capex_components["engineering"]
    )
    capex_total = capex_sum * (1 + base_capex_components["contingency"])
    return {
        "Conservative": capex_total*1.15,
        "Base": capex_total,
        "Optimistic": capex_total*0.9
    }

def calc_weekly_wages(staff_count):
    return sum(staff_roles[role]*count for role,count in staff_count.items())

def calc_annual_opex(weekly_wages):
    return weekly_wages*52*1.2

def calc_annual_revenue(annual_tonnage):
    electronics_tonnage = annual_tonnage * ELECTRONICS_SHARE
    metals_tonnage = annual_tonnage - electronics_tonnage
    revenue = metals_tonnage*PRICE_RECLAIMED_METALS + electronics_tonnage*PRICE_RECLAIMED_BATTERY
    return revenue

# --- Розрахунок для тижневого діапазону ---
def compute_range(weekly_range):
    clear_console()
    weekly_tonnage = weekly_range[0] if weekly_range[1]==math.inf else (weekly_range[0]+weekly_range[1])/2
    annual_tonnage = weekly_tonnage*52

    capex = calc_capex(annual_tonnage)
    staff_count = get_staff_count(annual_tonnage)
    weekly_wages = calc_weekly_wages(staff_count)
    annual_opex = calc_annual_opex(weekly_wages)
    annual_revenue = calc_annual_revenue(annual_tonnage)
    payback_base = capex["Base"] / (annual_revenue - annual_opex) if annual_revenue>annual_opex else math.inf
    area = estimate_area(annual_tonnage)

    print(f"\n--- Розрахунок для діапазону {weekly_range[0]} – {weekly_range[1] if weekly_range[1]!=math.inf else '∞'} т/тиждень ---")
    print(f"Середній тижневий обсяг: {round(weekly_tonnage)} т/тиждень")
    print(f"Річний обсяг: {round(annual_tonnage)} т/рік")
    print(f"Площа заводу: {area} м²")
    print(f"Щотижневі зарплати: {weekly_wages} €")
    print(f"Щорічний OPEX: {round(annual_opex,2)} €")
    print(f"Очікуваний щорічний дохід: {round(annual_revenue,2)} €")
    print(f"Прогнозована окупність (роки): {round(payback_base,1)}")
    print("Персонал:")
    for role,count in staff_count.items():
        print(f"  {role}: {count} осіб")
    print("CAPEX (€):")
    for scen,val in capex.items():
        print(f"  {scen}: {round(val,2)}")
    pause()


# --- Вивід всіх кластерів ---
def show_all_clusters():
    clear_console()
    try:
        df = pd.read_csv("cost_all_clusters.csv")
        df = df[['cluster_id','region','waste_tonnes_week']]
        df['weekly_electronics_tonnes'] = df['waste_tonnes_week'] * ELECTRONICS_SHARE
    except Exception as e:
        print(f"Помилка при завантаженні файлу: {e}")
        pause()
        return

    print("\n--- Інформація про всі кластери (тільки електроніка 5%) ---")
    print(df.to_string(index=False))
    pause()

# --- Розрахунок для одного кластера ---
def compute_cluster():
    clear_console()
    try:
        df = pd.read_csv("cost_all_clusters.csv")
        df = df[['cluster_id','region','waste_tonnes_week']]
    except Exception as e:
        print(f"Помилка при завантаженні файлу: {e}")
        pause()
        return

    unique_clusters = df['cluster_id'].unique()
    print(f"\nДоступні кластери: {', '.join(map(str, unique_clusters))}")
    choice = input("Введіть номер кластера (cluster_id): ")

    if not choice.isdigit():
        print("Невірне значення.")
        pause()
        return

    choice = int(choice)
    cluster_row = df[df['cluster_id'] == choice]

    if cluster_row.empty:
        print("Кластер з таким ID не знайдено.")
        pause()
        return

    row = cluster_row.iloc[0]
    weekly_tonnage = row['waste_tonnes_week'] * ELECTRONICS_SHARE
    annual_tonnage = weekly_tonnage * 52

    capex = calc_capex(annual_tonnage)
    staff_count = get_staff_count(annual_tonnage)
    weekly_wages = calc_weekly_wages(staff_count)
    annual_opex = calc_annual_opex(weekly_wages)
    annual_revenue = calc_annual_revenue(annual_tonnage)
    payback_base = capex["Base"] / (annual_revenue - annual_opex) if annual_revenue > annual_opex else math.inf
    area = estimate_area(annual_tonnage)

    print(f"\n--- Розрахунок для Cluster {row['cluster_id']} ---")
    print(f"Регіон: {row['region']}")
    print(f"Тижневий обсяг електроніки (5%): {round(weekly_tonnage)} т")
    print(f"Річний обсяг: {round(annual_tonnage)} т/рік")
    print(f"Площа заводу: {area} м²")
    print(f"Щотижневі зарплати: {weekly_wages} €")
    print(f"Щорічний OPEX: {round(annual_opex,2)} €")
    print(f"Очікуваний щорічний дохід: {round(annual_revenue,2)} €")
    print(f"Прогнозована окупність (роки): {round(payback_base,1)}")
    print("Персонал:")
    for role, count in staff_count.items():
        print(f"  {role}: {count} осіб")
    print("CAPEX (€):")
    for scen, val in capex.items():
        print(f"  {scen}: {round(val,2)}")

    pause()


# --- Функція для обрахунку всіх кластерів та збереження в CSV ---
def compute_all_clusters_to_file():
    clear_console()
    try:
        df = pd.read_csv("cost_all_clusters.csv")
        df = df[['cluster_id','region','waste_tonnes_week']]
    except Exception as e:
        print(f"Помилка при завантаженні файлу: {e}")
        pause()
        return

    results = []
    for idx, row in df.iterrows():
        weekly_tonnage = row['waste_tonnes_week'] * ELECTRONICS_SHARE  
        annual_tonnage = weekly_tonnage * 52

        capex = calc_capex(annual_tonnage)
        staff_count = get_staff_count(annual_tonnage)
        weekly_wages = calc_weekly_wages(staff_count)
        annual_opex = calc_annual_opex(weekly_wages)
        annual_revenue = calc_annual_revenue(annual_tonnage)
        payback_base = capex["Base"] / (annual_revenue - annual_opex) if annual_revenue>annual_opex else math.inf

        results.append({
            "cluster_id": row['cluster_id'],
            "region": row['region'],
            "annual_opex": round(annual_opex,2),
            "annual_revenue": round(annual_revenue,2),
            "payback_base": round(payback_base,1),
            "CAPEXC": round(capex["Conservative"],2),
            "CAPEXB": round(capex["Base"],2),
            "CAPEXO": round(capex["Optimistic"],2)
        })

    out_df = pd.DataFrame(results)
    out_df.to_csv("cost_weee.csv", index=False)
    print("\nРозрахунки завершено. Файл 'cost_weee.csv' створено.")
    pause()


# --- Меню ---
def menu():
    while True:
        clear_console()
        print("\n=== Головне меню  ===")
        print("1. Перейти до вибору тижневого діапазону")
        print("2. Показати інформацію про всі кластери")
        print("3. Обрахувати всі кластери WEEE та зберегти у файл")
        print("4. Розрахунок для одного кластера")
        print("5. Вихід")
        choice = input("Введіть номер: ")

        if choice == "5":
            print("Вихід...")
            break
        elif choice == "1":
            clear_console()
            print("\nВиберіть тижневий діапазон WEEE:")
            for i, r in enumerate(weekly_weee_ranges, 1):
                print(f"{i}. {r[0]} – {r[1] if r[1] != math.inf else '∞'} т/тиждень")
            sub_choice = input("Введіть номер діапазону: ")
            if not sub_choice.isdigit():
                pause()
                continue
            sub_choice = int(sub_choice)
            if 1 <= sub_choice <= len(weekly_weee_ranges):
                compute_range(weekly_weee_ranges[sub_choice - 1])
            else:
                print("Неправильний номер діапазону.")
                pause()

        elif choice == "2":
            show_all_clusters()
        elif choice == "3":
            compute_all_clusters_to_file()
        elif choice == "4":
            compute_cluster()
        else:
            print("Неправильний номер меню.")
            pause()

