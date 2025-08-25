import math
import pandas as pd
import os

# --- Тижневі діапазони органіки (т/тиждень) ---
weekly_organic_ranges = [
    (0, 1750),
    (1751, 4200),
    (4201, 7000),
    (7001, 10500),
    (10501, 15750),
    (15751, 22750),
    (22751, math.inf)
]

# --- Базові компоненти CAPEX (€/т/рік) ---
base_capex_components = {
    "digester": 450, "CHP": 120, "pre_treatment": 80,
    "storage": 60, "civil_works": 200, "electrical": 90,
    "engineering": 70, "contingency": 0.1
}

# --- Зарплати на тиждень ---
staff_roles = {"Operator":600,"Technician":750,"Manager":1000}

# --- Ціни на продукцію/енергію ---
PRICE_ELECTRICITY = 0.10
PRICE_HEAT = 0.05
PRICE_DIGESTATE = 50
GAS_YIELD_PER_TON = 1000
ELEC_EFFICIENCY = 2.0
HEAT_EFFICIENCY = 1.5

# --- Утиліти ---
def clear_console():
    """Очистити консоль для зручності інтерфейсу"""
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    """Зупинка для читання виводу користувачем"""
    input("\nНатисніть Enter для продовження...")

# --- Персонал та розрахунки ---
def get_staff_count(annual_tonnage):
    if annual_tonnage <= 1750*52:
        return {"Operator": 4, "Technician": 2, "Manager": 1}
    elif annual_tonnage <= 7000*52:
        return {"Operator": 8, "Technician": 4, "Manager": 2}
    elif annual_tonnage <= 15750*52:
        return {"Operator": 12, "Technician": 6, "Manager": 3}
    elif annual_tonnage <= 22750*52:
        return {"Operator": 16, "Technician": 8, "Manager": 4}
    else:
        return {"Operator": 20, "Technician": 10, "Manager": 5}

def estimate_area(annual_tonnage):
    return round(annual_tonnage*1.5 + 1500,0)

def calc_capex(annual_tonnage):
    capex_sum = annual_tonnage * (
        base_capex_components["digester"] +
        base_capex_components["CHP"] +
        base_capex_components["pre_treatment"] +
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
    gas_volume = annual_tonnage * GAS_YIELD_PER_TON
    electricity = gas_volume * ELEC_EFFICIENCY
    heat = gas_volume * HEAT_EFFICIENCY
    digestate = annual_tonnage
    revenue = electricity*PRICE_ELECTRICITY + heat*PRICE_HEAT + digestate*PRICE_DIGESTATE
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

# --- Розрахунок для кластера ---
def compute_cluster():
    clear_console()
    try:
        df = pd.read_csv("cost_all_clusters.csv")
        df = df[['cluster_id','region','waste_tonnes_week']]
    except Exception as e:
        print(f"Помилка при завантаженні файлу: {e}")
        pause()
        return

    min_cluster = df['cluster_id'].min()
    max_cluster = df['cluster_id'].max()
    print(f"\nДоступні кластери: від Cluster {min_cluster} до Cluster {max_cluster}")

    choice = input("Введіть номер кластера: ")
    if not choice.isdigit(): return
    choice = int(choice)
    if 0 <= choice <= len(df):
        weekly_tonnage = df.loc[choice,'waste_tonnes_week'] * 0.35  
        annual_tonnage = weekly_tonnage * 52

        capex = calc_capex(annual_tonnage)
        staff_count = get_staff_count(annual_tonnage)
        weekly_wages = calc_weekly_wages(staff_count)
        annual_opex = calc_annual_opex(weekly_wages)
        annual_revenue = calc_annual_revenue(annual_tonnage)
        payback_base = capex["Base"] / (annual_revenue - annual_opex) if annual_revenue>annual_opex else math.inf
        area = estimate_area(annual_tonnage)

        print(f"\n--- Розрахунок для Cluster {df.loc[choice,'cluster_id']} ---")
        print(f"Region: {df.loc[choice,'region']}")
        print(f"Тижневий обсяг органіки: {round(weekly_tonnage)} т")
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
    else:
        print("Неправильний номер кластера.")
    pause()



# --- Вивід всіх кластерів ---
def show_all_clusters():
    clear_console()
    try:
        df = pd.read_csv("cost_all_clusters.csv")
        df = df[['cluster_id','region','waste_tonnes_week']]
        df['weekly_organic_tonnes'] = df['waste_tonnes_week'] * 0.35
    except Exception as e:
        print(f"Помилка при завантаженні файлу: {e}")
        pause()
        return

    print("\n--- Інформація про всі кластери (тільки органіка) ---")
    print(df.to_string(index=False))
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
        weekly_tonnage = row['waste_tonnes_week'] * 0.35  
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
    out_df.to_csv("cost_bio.csv", index=False)
    print("\nРозрахунки завершено. Файл 'cost_bio.csv' створено.")
    pause()



# --- Меню ---
def menu():
    while True:
        clear_console()
        print("\n=== Головне меню ===")
        print("1. Перейти до вибору тижневого діапазону органіки")
        print("2. Перейти до вибору кластера")
        print("3. Показати інформацію про всі кластери")
        print("4. Обрахувати всі кластери та зберегти у файл")
        print("5. Вихід")
        choice = input("Введіть номер: ")
        if choice=="5":
            print("Вихід...")
            break
        elif choice=="1":
            clear_console()
            print("\nВиберіть тижневий діапазон органіки:")
            for i, r in enumerate(weekly_organic_ranges,1):
                print(f"{i}. {r[0]} – {r[1] if r[1]!=math.inf else '∞'} т/тиждень")
            sub_choice = input("Введіть номер діапазону: ")
            if not sub_choice.isdigit(): continue
            sub_choice = int(sub_choice)
            if 1 <= sub_choice <= len(weekly_organic_ranges):
                compute_range(weekly_organic_ranges[sub_choice-1])
            else:
                print("Неправильний номер діапазону.")
                pause()
        elif choice=="2":
            compute_cluster()
        elif choice=="3":
            show_all_clusters()
        elif choice=="4":
            compute_all_clusters_to_file()
        else:
            print("Неправильний номер меню.")
            pause()


if __name__=="__main__":
    menu()
