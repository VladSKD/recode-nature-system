import pandas as pd
import os

# ---------------------------
# Утиліти
# ---------------------------
def clear_console():
    """Очистити консоль для зручності інтерфейсу"""
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    """Зупинка для читання виводу користувачем"""
    input("\nНатисніть Enter для продовження...")

# ---------------------------
# Функції для завантаження та сумування даних
# ---------------------------
def load_clusters(file="cost_all_clusters.csv"):
    if not os.path.exists(file):
        raise FileNotFoundError(f"Файл {file} не знайдено!")
    df = pd.read_csv(file)
    df['annual_opex_total'] = 0
    df['annual_revenue_total'] = 0
    df['CAPEXB_total'] = 0
    return df

def merge_waste_files(df, files):
    for file in files:
        if not os.path.exists(file):
            print(f"Файл {file} не знайдено, пропускаємо...")
            continue
        df_waste = pd.read_csv(file)
        if not all(col in df_waste.columns for col in ['cluster_id','region','annual_opex','annual_revenue','CAPEXB']):
            print(f"Файл {file} пропущено, немає потрібних колонок")
            continue
        df_grouped = df_waste.groupby(['cluster_id','region'], as_index=False)[['annual_opex','annual_revenue','CAPEXB']].sum()
        df = df.merge(df_grouped, on=['cluster_id','region'], how='left', suffixes=('','_y'))
        df['annual_opex_total'] += df['annual_opex'].fillna(0)
        df['annual_revenue_total'] += df['annual_revenue'].fillna(0)
        df['CAPEXB_total'] += df['CAPEXB'].fillna(0)
        df.drop(columns=['annual_opex','annual_revenue','CAPEXB'], inplace=True)
    return df

def add_logistics(df):
    df['annual_opex_total'] += df['total_cost'] * 52
    return df

def calculate_payback(df):
    df['profit'] = df['annual_revenue_total'] - df['annual_opex_total']
    df['payback_years'] = df.apply(
        lambda row: row['CAPEXB_total'] / row['profit']
        if row['profit']>0 and row['CAPEXB_total']>0 else pd.NA,
        axis=1
    )
    df.drop(columns=['profit'], inplace=True)
    return df

# ---------------------------
# Функції виводу
# ---------------------------
def show_overall(df):
    clear_console()
    total_CAPEX = df['CAPEXB_total'].sum()
    total_opex = df['annual_opex_total'].sum()
    total_revenue = df['annual_revenue_total'].sum()
    payback = total_CAPEX / (total_revenue - total_opex) if (total_revenue - total_opex)>0 else pd.NA
    print("\n=== Загальні цифри по всіх кластерах ===")
    print(f"Потрібно інвестувати: {total_CAPEX:,.0f} €")
    print(f"Річні витрати: {total_opex:,.0f} €")
    print(f"Річні прибутки: {total_revenue:,.0f} €")
    print(f"Окупність: {payback:.2f} років" if pd.notna(payback) else "Окупність: N/A")
    pause()

def show_top_clusters(df):
    clear_console()
    print("\n=== Топ-10 кластерів за прибутком ===")
    top_revenue = df.sort_values('annual_revenue_total', ascending=False).head(10)
    for idx, row in top_revenue.iterrows():
        print(f"Cluster {row['cluster_id']} | {row['region']} | Revenue: {row['annual_revenue_total']:,.0f} € | "
              f"OPEX: {row['annual_opex_total']:,.0f} € | CAPEXB: {row['CAPEXB_total']:,.0f} € | "
              f"Payback: {row['payback_years']:.2f} років" if pd.notna(row['payback_years']) else "N/A")
    
    print("\n=== Топ-10 кластерів за швидкою окупністю ===")
    df_valid = df.dropna(subset=['payback_years'])
    top_payback = df_valid.sort_values('payback_years').head(10)
    for idx, row in top_payback.iterrows():
        print(f"Cluster {row['cluster_id']} | {row['region']} | CAPEXB: {row['CAPEXB_total']:,.0f} € | "
              f"Revenue: {row['annual_revenue_total']:,.0f} € | OPEX: {row['annual_opex_total']:,.0f} € | "
              f"Payback: {row['payback_years']:.2f} років")
    pause()

def show_cluster(df, cluster_id):
    clear_console()
    cluster = df[df['cluster_id'] == cluster_id]
    if cluster.empty:
        print(f"Кластер {cluster_id} не знайдено")
    else:
        row = cluster.iloc[0]
        print(f"\nCluster {row['cluster_id']} | {row['region']} | "
              f"Waste: {row['waste_tonnes_week']:,.0f} т/тиждень | "
              f"Logistics: {row['total_cost']:,.0f} €/тиждень | "
              f"Area: {row['area_km2']:,.0f} м² | "
              f"OPEX: {row['annual_opex_total']:,.0f} €/рік | "
              f"Revenue: {row['annual_revenue_total']:,.0f} €/рік | "
              f"CAPEXB: {row['CAPEXB_total']:,.0f} € | "
              f"Payback: {row['payback_years']:.2f} років" if pd.notna(row['payback_years']) else "N/A")
    pause()

def save_to_file(df):
    df.to_csv("financial_summary_by_cluster.csv", index=False)
    print("Фінансова таблиця збережена у 'financial_summary_by_cluster.csv'")
    pause()


def simulate_sequential_build(df, start_year=2025, output_file="sequential_build_plan.csv"):
    print("Розпочато процес симуляції...")
    
    df_sorted = df.sort_values('payback_years')
    
    cash = 0
    year = start_year
    active_plants = []
    plan = []

    for idx, row in df_sorted.iterrows():
        cluster_id = row['cluster_id']
        CAPEX = row['CAPEXB_total']
        annual_profit = row['annual_revenue_total'] - row['annual_opex_total']

        # Розрахунок років до накопичення на будівництво з урахуванням прибутку всіх активних заводів
        if cash >= CAPEX:
            build_year = year
        elif annual_profit + sum(p['annual_profit'] for p in active_plants) > 0:
            total_profit = annual_profit + sum(p['annual_profit'] for p in active_plants)
            years_needed = -(-(CAPEX - cash) // total_profit) 
            build_year = year + int(years_needed)
        else:
            build_year = None


        plan.append({
            'cluster_id': cluster_id,
            'start_year': year,
            'build_year': build_year,
            'CAPEX': CAPEX,
            'annual_profit': annual_profit
        })


        if build_year is not None:
            years_until_build = build_year - year
            cash += years_until_build * sum(p['annual_profit'] for p in active_plants)
            cash -= CAPEX
            active_plants.append({'cluster_id': cluster_id, 'annual_profit': annual_profit})
            year = build_year  
        else:
            print(f"Завод {cluster_id} не може бути побудований (недостатній прибуток).")

    # Зберігаємо план у CSV
    df_plan = pd.DataFrame(plan)
    df_plan.to_csv(output_file, index=False)
    print("Процес завершено. План збережено у", output_file)









# ---------------------------
# Меню
# ---------------------------
def main_menu(df):
    while True:
        clear_console()
        print("\n=== Меню Фінансового Аналізу ===")
        print("1 - Загальна статистика")
        print("2 - Топ-10 кластерів")
        print("3 - Перегляд конкретного кластера")
        print("4 - Зберегти фінансову таблицю")
        print("5 - Вихід")
        print("6 - Симуляція послідовного будівництва заводів")
        choice = input("Вибір: ").strip()
        if choice=="1":
            show_overall(df)
        elif choice=="2":
            show_top_clusters(df)
        elif choice=="3":
            cid = input("Введіть cluster_id: ").strip()
            if cid.isdigit():
                show_cluster(df, int(cid))
            else:
                print("Неправильний cluster_id")
                pause()
        elif choice=="4":
            save_to_file(df)
        elif choice=="5":
            print("Вихід...")
            break
        elif choice=="6":
            simulate_sequential_build(df)
        else:
            print("Невірний вибір")
            pause()




# ---------------------------
# Головна програма
# ---------------------------
if __name__ == "__main__":
    try:
        df = load_clusters("cost_all_clusters.csv")
        
        
        folder = "cost_fab"
        
        
        files = [os.path.join(folder, filename) for filename in [
            "cost_bio.csv", "cost_glass.csv", "cost_metal.csv", "cost_paper.csv",
            "cost_plastic.csv", "cost_rdf.csv", "cost_rubber.csv", "cost_weee.csv", "cost_sort.csv"
        ]]
        
        df = merge_waste_files(df, files)
        df = add_logistics(df)
        df = calculate_payback(df)
        main_menu(df)
        
    except Exception as e:
        print(f"Помилка: {e}")
        pause()

