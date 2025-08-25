import math
import pandas as pd
import os

# --- Тижневі діапазони макулатури (т/тиждень) ---
weekly_paper_ranges = [
    (0, 600),
    (600, 1440),
    (1441, 2400),
    (2401, 3600),
    (3601, 5400),
    (5401, 7800),
    (7801, math.inf)
]

# --- Базові компоненти CAPEX (€/т/рік) для макулатурного заводу ---
base_capex_components = {
    "shredders": 100,   
    "baling": 100,      
    "sorting": 20,      
    "storage": 50,
    "civil_works": 120,
    "electrical": 60,
    "engineering": 60,
    "contingency": 0.1
}


# --- Персонал: зарплати на тиждень ---
staff_roles = {"Operator":500,"Technician":700,"Manager":900,"Sorter":400}

# --- Ціни на продукцію (макулатура в €/т) ---
PRICE_RECYCLED_PAPER = 170

# --- Утиліти ---
def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\nНатисніть Enter для продовження...")

# --- Розрахунок персоналу ---
def get_staff_count(annual_tonnage):
    if annual_tonnage <= 600*52:
        return {"Operator": 3, "Technician": 1, "Manager": 1, "Sorter": 2}
    elif annual_tonnage <= 2400*52:
        return {"Operator": 6, "Technician": 3, "Manager": 1, "Sorter": 4}
    elif annual_tonnage <= 5400*52:
        return {"Operator": 10, "Technician": 5, "Manager": 2, "Sorter": 6}
    elif annual_tonnage <= 7800*52:
        return {"Operator": 14, "Technician": 7, "Manager": 3, "Sorter": 10}
    else:
        return {"Operator": 20, "Technician": 10, "Manager": 4, "Sorter": 14}

def estimate_area(annual_tonnage):
    return round(annual_tonnage*0.8 + 1000,0)  

def calc_capex(annual_tonnage):
    capex_sum = annual_tonnage * (
        base_capex_components["shredders"] +
        base_capex_components["baling"] +
        base_capex_components["sorting"] +
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
    paper_volume = annual_tonnage * 0.102 
    revenue = paper_volume * PRICE_RECYCLED_PAPER
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
        weekly_tonnage = df.loc[choice,'waste_tonnes_week'] * 0.102  # тільки папір
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
        print(f"Тижневий обсяг паперу: {round(weekly_tonnage)} т")
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
        df['weekly_paper_tonnes'] = df['waste_tonnes_week'] * 0.102
    except Exception as e:
        print(f"Помилка при завантаженні файлу: {e}")
        pause()
        return

    print("\n--- Інформація про всі кластери (тільки папір) ---")
    print(df.to_string(index=False))
    pause()



# --- Додатковий розрахунок для всіх кластерів і збереження у файл ---
def compute_all_clusters_to_file():
    clear_console()
    try:
        df = pd.read_csv("cost_all_clusters.csv")
        df = df[['cluster_id','region','waste_tonnes_week']]
    except Exception as e:
        print(f"Помилка при завантаженні файлу: {e}")
        pause()
        return

    output_rows = []
    for idx, row in df.iterrows():
        weekly_tonnage = row['waste_tonnes_week'] * 0.102  
        annual_tonnage = weekly_tonnage * 52

        capex = calc_capex(annual_tonnage)
        staff_count = get_staff_count(annual_tonnage)
        weekly_wages = calc_weekly_wages(staff_count)
        annual_opex = calc_annual_opex(weekly_wages)
        annual_revenue = calc_annual_revenue(annual_tonnage)
        payback_base = capex["Base"] / (annual_revenue - annual_opex) if annual_revenue>annual_opex else math.inf

        output_rows.append({
            "cluster_id": row['cluster_id'],
            "region": row['region'],
            "annual_opex": round(annual_opex,2),
            "annual_revenue": round(annual_revenue,2),
            "payback_base": round(payback_base,1),
            "CAPEXC": round(capex["Conservative"],2),
            "CAPEXB": round(capex["Base"],2),
            "CAPEXO": round(capex["Optimistic"],2)
        })

    output_df = pd.DataFrame(output_rows)
    output_filename = "cost_paper.csv"
    output_df.to_csv(output_filename, index=False)
    print(f"\nРозрахунки для всіх кластерів збережено у файл '{output_filename}'")
    pause()

# --- Меню ---
def menu():
    while True:
        clear_console()
        print("\n=== Головне меню ===")
        print("1. Перейти до вибору тижневого діапазону макулатури")
        print("2. Перейти до вибору кластера")
        print("3. Показати інформацію про всі кластери")
        print("4. Розрахувати OPEX, дохід, окупність та CAPEX для всіх кластерів і зберегти у файл")
        print("5. Вихід")
        choice = input("Введіть номер: ")
        if choice=="5":
            print("Вихід...")
            break
        elif choice=="1":
            clear_console()
            print("\nВиберіть тижневий діапазон макулатури:")
            for i, r in enumerate(weekly_paper_ranges,1):
                print(f"{i}. {r[0]} – {r[1] if r[1]!=math.inf else '∞'} т/тиждень")
            sub_choice = input("Введіть номер діапазону: ")
            if not sub_choice.isdigit(): continue
            sub_choice = int(sub_choice)
            if 1 <= sub_choice <= len(weekly_paper_ranges):
                compute_range(weekly_paper_ranges[sub_choice-1])
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
