

# -------------------------------
# Імпорти 
# -------------------------------

import csv
import ast
import math
import logging
import os
import sys
import json
import datetime
from itertools import product
from typing import Optional, Dict, List, Any, Tuple
import pandas as pd


# Бібліотеки 
try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.ticker import FuncFormatter
except Exception:
    plt = None
    np = None

# -------------------------------
# Логгер
# -------------------------------

LOGGING_LEVEL = logging.INFO

logging.basicConfig(
    level=LOGGING_LEVEL,
    format="[%(levelname)s] %(asctime)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("WasteTransportOptimizerExtended")

# -------------------------------
# Константи (технічні та фінансові)
# -------------------------------

TRUCKS = {
    "mcneilus_volterra_zsl": {
        "name": "McNeilus Volterra ZSL Electric Side Loader",
        "capacity": 18,
        "speed_kmh": 50,
        "fuel_consumption_l_per_100km": 0,
        "electricity_consumption_kwh_per_100km": 3.5,
        "electricity_cost_per_kwh": 0.25,
        "co2_per_kwh": 0.5,
        "noise_db": 70,
    },
    "hyzon_econic": {
        "name": "Hyzon Econic Hydrogen Refuse Truck",
        "capacity": 18,
        "speed_kmh": 55,
        "fuel_consumption_l_per_100km": 0,
        "electricity_consumption_kwh_per_100km": 3.8,
        "electricity_cost_per_kwh": 0.25,
        "co2_per_kwh": 0.5,
        "noise_db": 68,
    },
    "volvo_fe_electric": {
        "name": "Volvo FE Electric",
        "capacity": 18,
        "speed_kmh": 45,
        "fuel_consumption_l_per_100km": 0,
        "electricity_consumption_kwh_per_100km": 3.2,
        "electricity_cost_per_kwh": 0.25,
        "co2_per_kwh": 0.5,
        "noise_db": 65,
    },
    "peterbilt_520ev": {
        "name": "Peterbilt Model 520EV",
        "capacity": 18,
        "speed_kmh": 50,
        "fuel_consumption_l_per_100km": 0,
        "electricity_consumption_kwh_per_100km": 4.0,
        "electricity_cost_per_kwh": 0.25,
        "co2_per_kwh": 0.5,
        "noise_db": 72,
    },
    "mack_md_electric": {
        "name": "Mack MD Electric",
        "capacity": 12,
        "speed_kmh": 40,
        "fuel_consumption_l_per_100km": 0,
        "electricity_consumption_kwh_per_100km": 2.5,
        "electricity_cost_per_kwh": 0.25,
        "co2_per_kwh": 0.5,
        "noise_db": 75,
    },
    "lion8": {
        "name": "Lion8 Refuse Truck",
        "capacity": 18,
        "speed_kmh": 50,
        "fuel_consumption_l_per_100km": 0,
        "electricity_consumption_kwh_per_100km": 4.2,
        "electricity_cost_per_kwh": 0.25,
        "co2_per_kwh": 0.5,
        "noise_db": 69,
    },
    "heil_revamp": {
        "name": "Heil RevAMP Electric Side Loader",
        "capacity": 18,
        "speed_kmh": 45,
        "fuel_consumption_l_per_100km": 0,
        "electricity_consumption_kwh_per_100km": 3.6,
        "electricity_cost_per_kwh": 0.25,
        "co2_per_kwh": 0.5,
        "noise_db": 71,
    },
    "man_eTGM_18t": {
        "name": "MAN eTGM 18т електро",
        "capacity": 18,
        "speed_kmh": 40,
        "fuel_consumption_l_per_100km": 0,  # електро
        "electricity_consumption_kwh_per_100km": 3.0,  # середнє значення
        "electricity_cost_per_kwh": 0.25,  # євро/кВт·год
        "co2_per_kwh": 0.5,  # кг CO2 на кВт·год
        "noise_db": 65,
    },
    "volvo_FE_electric_18t": {
        "name": "Volvo FE Electric 18т",
        "capacity": 18,
        "speed_kmh": 38,
        "fuel_consumption_l_per_100km": 0,  # електро
        "electricity_consumption_kwh_per_100km": 3.2,  # середнє значення
        "electricity_cost_per_kwh": 0.25,
        "co2_per_kwh": 0.5,
        "noise_db": 65,
    },
    "mack_LR_electric_18t": {
        "name": "Mack LR Electric 18т",
        "capacity": 18,
        "speed_kmh": 35,
        "fuel_consumption_l_per_100km": 0,
        "electricity_consumption_kwh_per_100km": 3.5,
        "electricity_cost_per_kwh": 0.25,
        "co2_per_kwh": 0.5,
        "noise_db": 65,
    },
    "peterbilt_520EV_18t": {
        "name": "Peterbilt 520EV 18т",
        "capacity": 18,
        "speed_kmh": 37,
        "fuel_consumption_l_per_100km": 0,
        "electricity_consumption_kwh_per_100km": 3.8,
        "electricity_cost_per_kwh": 0.25,
        "co2_per_kwh": 0.5,
        "noise_db": 65,
    }
}

CONTAINERS = {
    "5t": {
        "capacity": 5,          # тонна
        "cost": 600,            # євро (приблизно 20 000 грн → 600 €)
        "life_weeks": 520       # тижнів служби (~10 років)
    },
    "7t": {
        "capacity": 7,
        "cost": 750,            
        "life_weeks": 520
    },
    "10t": {
        "capacity": 10,
        "cost": 900,            
        "life_weeks": 520
    },
    "15t": {
        "capacity": 15,
        "cost": 9000,           
        "life_weeks": 520
    },
    "20t": {
        "capacity": 20,
        "cost": 10500,          
        "life_weeks": 520
    }
}

# Зарплати (приклади — в євро)
SALARY_OPTIONS = [2200, 2750, 2900]  # € / місяць 
WORK_HOURS_OPTIONS = [6, 7, 8, 9, 10]  # год/день
WORK_DAYS_PER_WEEK = 5

DATA_FILE = "clusters_data.csv"
REPORTS_DIR = "reports"



# -------------------------------
# Допоміжні утиліти вводу/виводу
# -------------------------------

def clear_console():
    """Очистити консоль для зручності інтерфейсу"""
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\nНатисніть Enter для продовження...")






import re
_number_regex = re.compile(r"^\d+(\.\d+)?$") 

def safe_input(prompt: str, valid_options: Optional[List[str]] = None, allow_empty=False) -> str:
    """
    Безпечний ввід рядка з перевіркою на перелік допустимих варіантів.
    Якщо valid_options заданий — перевіряємо точну відповідність.
    """
    while True:
        val = input(prompt).strip()
        if allow_empty and val == "":
            return val
        if valid_options:
            if val in valid_options:
                return val
            else:
                print(f"❌ Некоректне значення. Дозволені варіанти: {valid_options}")
                continue
        return val

def safe_input_number(prompt: str, allow_empty: bool = False, integer: bool = False, minimum: Optional[float] = 0.0, maximum: Optional[float] = None) -> Optional[float]:
   
    while True:
        val = input(prompt).strip()
        if allow_empty and val == "":
            return None

        if val.startswith("-"):
            print("❌ Введіть число більше або рівне 0 (мінуси заборонені).")
            continue
       
        if not _number_regex.match(val):
            print("❌ Введіть коректне число у форматі 123 або 123.45 (букви/символи не дозволені).")
            continue
        
        try:
            num = float(val)
        except ValueError:
            print("❌ Помилка перетворення — введіть число ще раз.")
            continue
        
        if minimum is not None and num < minimum:
            print(f"❌ Значення повинно бути >= {minimum}.")
            continue
        if maximum is not None and num > maximum:
            print(f"❌ Значення повинно бути <= {maximum}.")
            continue
        if integer:
            return int(num)
        return num


def safe_input_choice(prompt: str, allowed: list[str]) -> Optional[str]:
    allowed_set = set(allowed)
    while True:
        val = input(prompt).strip()
        if val in allowed_set:
            return val
        print(f"❌ Неправильний вибір. Дозволені варіанти: {', '.join(allowed)}.")


def safe_input_multiple_choices(prompt: str, allowed: List[str], allow_empty: bool = False) -> List[str]:
    while True:
        s = input(prompt).strip()
        if allow_empty and s == "":
            return []
        parts = [p.strip() for p in s.split(",") if p.strip()]
        invalid = [p for p in parts if p not in allowed]
        if invalid:
            print(f"❌ Некоректні опції: {invalid}. Допустимі: {allowed}")
            continue
        unique = []
        for p in parts:
            if p not in unique:
                unique.append(p)
        return unique

# -------------------------------
# Клас для роботи з кластерами
# -------------------------------

class ClusterData:
    def __init__(self, filename: str):
        self.filename = filename
        self.clusters = self.load_clusters()

    def load_clusters(self) -> Dict[str, dict]:
        clusters = {}
        if not os.path.exists(self.filename):
            logger.error(f"Файл з кластерами не знайдено: {self.filename}")
            return clusters
        try:
            with open(self.filename, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cluster_id = row.get("cluster_id") or row.get("id") or row.get("ClusterID")
                    if cluster_id is None:
                        continue
                    try:
                        clusters[str(cluster_id)] = {
                            "region": row.get("region", "unknown"),
                            "center_lat": float(row.get("center_lat", 0) or 0),
                            "center_lon": float(row.get("center_lon", 0) or 0),
                            "area_km2": float(row.get("area_km2", 0) or 0),
                            "waste_tonnes_week": float(row.get("waste_tonnes_week", 0) or 0),
                            "waste_from_population": float(row.get("waste_from_population", 0) or 0),
                            "waste_from_objects": float(row.get("waste_from_objects", 0) or 0),
                            "polygon": ast.literal_eval(row.get("polygon", "[]") or "[]"),
                        }
                    except Exception as e:
                        logger.warning(f"Проблема з рядком кластеру {cluster_id}: {e}")
                        continue
            logger.info(f"Завантажено {len(clusters)} кластерів з {self.filename}")
        except Exception as e:
            logger.error(f"Помилка при завантаженні {self.filename}: {e}")
            sys.exit(1)
        return clusters

    def get_cluster_ids(self) -> List[str]:
        return list(self.clusters.keys())

    def get_cluster(self, cluster_id: str) -> Optional[dict]:
        return self.clusters.get(cluster_id, None)

    def get_cluster_data_row(self, cluster_id: str) -> dict:
        """Повертає дані кластера як словник, включаючи його ID."""
        cluster = self.get_cluster(cluster_id)
        if not cluster:
            return {}
        return {"cluster_id": cluster_id, **cluster}


    

# -------------------------------
# Клас для обчислень конфігурацій
# -------------------------------

class ConfigCalculator:
    def __init__(self, cluster_data: dict):
        self.cluster_data = cluster_data
        self.waste = cluster_data.get("waste_tonnes_week", 0.0)
        self.area = cluster_data.get("area_km2", 0.0)
        self.radius = self.calc_radius(self.area)

    @staticmethod
    def calc_radius(area_km2: float) -> float:
        try:
            if area_km2 <= 0:
                return 0.0
            return math.sqrt(area_km2 / math.pi)
        except Exception:
            return 0.0

    @staticmethod
    def calc_num_containers(waste_tonnes_week: float, container_capacity: float) -> int:
        if container_capacity <= 0:
            return math.inf
        return math.ceil(waste_tonnes_week / container_capacity)

    @staticmethod
    def calc_loading_time_hours(container_capacity: float = 5.0) -> float:
        base = 0.5  
        try:
            extra = max(0.0, (container_capacity - 5) / 5.0) * 0.05
            return base + extra
        except Exception:
            return base

    @staticmethod
    def calc_trip_time_hours(radius_km: float, speed_kmh: float, loading_time_hours: float) -> float:
        """
        Час одного рейсу: туди і назад до середньої точки регіону + час завантаження.
        radius_km: максимальний радіус регіону
        """
        if speed_kmh <= 0:
            return math.inf
        average_distance = radius_km / 2  # середня відстань
        travel = 2.0 * (average_distance / speed_kmh)  # туди і назад
        return travel + loading_time_hours

    @staticmethod
    def calc_trips_per_day(trip_time_hours: float, work_hours_per_day: int, max_trips: int = 4) -> int:
        if trip_time_hours <= 0:
            return 0
        trips = work_hours_per_day // trip_time_hours
        return min(trips, max_trips)


    @staticmethod
    def calc_num_trucks(total_trips_per_week: int, trips_per_day: int) -> int:
        if trips_per_day <= 0:
            return math.inf
        return math.ceil(total_trips_per_week / (WORK_DAYS_PER_WEEK * trips_per_day))

    def calc_energy_cost_per_trip(self, truck: dict) -> float: 
        radius = self.radius
        if truck.get("fuel_consumption_l_per_100km", 0) > 0:
            liters = truck["fuel_consumption_l_per_100km"] * 2 * radius / 100
            cost = liters * truck.get("fuel_cost_per_l", 0)
            logger.debug(f"Рейс: {liters:.2f} л палива, вартість (умовно) {cost:.2f}")
            return cost 
        else: kwh = truck.get("electricity_consumption_kwh_per_100km", 0) * 2 * radius / 100 
        # використовуємо внутрішню ставку electric 
        cost = kwh * truck.get("electricity_cost_per_kwh", 0) 
        logger.debug(f"Рейс: {kwh:.2f} кВт·год, вартість (умовно) {cost:.2f}") 
        return cost  


    def calc_co2_per_trip(self, truck: dict) -> float:
        radius = self.radius
        if truck.get("fuel_consumption_l_per_100km", 0) > 0:
            liters = truck["fuel_consumption_l_per_100km"] * 2 * radius / 100
            co2 = liters * truck.get("co2_per_l", 2.68)
            return co2
        else:
            kwh = truck.get("electricity_consumption_kwh_per_100km", 0) * 2 * radius / 100
            co2 = kwh * truck.get("co2_per_kwh", 0.5)
            return co2

    @staticmethod
    def calc_salary_per_week(monthly_salary_eur: float, hours_per_day: float, days_per_week: int) -> float:
        if not monthly_salary_eur or not hours_per_day or not days_per_week:
            return 0.0

        # Середня кількість тижнів у місяці: 4.33
        total_hours_per_month = hours_per_day * days_per_week * 4.33
        hourly_rate = monthly_salary_eur / total_hours_per_month
        weekly_salary = hourly_rate * hours_per_day * days_per_week

        return round(weekly_salary, 2)

    @staticmethod
    def calc_container_amortization(container_cost: float, life_weeks: int, num_containers: int) -> float:
        if life_weeks <= 0:
            return math.inf
        amortization_per_week = container_cost / life_weeks
        return amortization_per_week * num_containers

    def calculate_cost(self, truck: dict, container: dict, salary_eur: float,
                       work_hours: int, frequency: int, force_num_containers: Optional[int] = None) -> Optional[dict]:
        # Вхідні перевірки
        try:
            if frequency <= 0:
                return None
        except Exception:
            return None

        # Кількість контейнерів
        if force_num_containers is not None:
            if force_num_containers <= 0:
                return None
            num_containers = int(force_num_containers)
        else:
            num_containers = self.calc_num_containers(self.waste, container["capacity"])

        # Загальна кількість рейсів на тиждень
        total_trips_per_week = num_containers * frequency

        # Час одного рейсу
        loading_time = self.calc_loading_time_hours(container["capacity"])
        trip_time = self.calc_trip_time_hours(self.radius, truck["speed_kmh"], loading_time)
        trips_per_day = self.calc_trips_per_day(trip_time, work_hours)
        num_trucks = self.calc_num_trucks(total_trips_per_week, trips_per_day)

        if num_trucks == math.inf or trips_per_day <= 0:
            logger.warning("Неможливо обробити рейси з такою конфігурацією (немає рейсів/дробова робота)")
            return None

        # Вартість енергії (умовно — в грн або внутрішніх одиницях)
        fuel_cost_per_week_internal = self.calc_energy_cost_per_trip(truck) * total_trips_per_week

        # Зарплата на тиждень (євро) — множимо на кількість машин
        salary_per_week_eur = self.calc_salary_per_week(salary_eur, work_hours, WORK_DAYS_PER_WEEK) * num_trucks


        # Амортизація контейнерів на тиждень — тут container["cost"] припускаємо в гривнях;
        amortization_per_week_internal = self.calc_container_amortization(container["cost"], container["life_weeks"], num_containers)

        # CO2 за тиждень
        co2_per_week = self.calc_co2_per_trip(truck) * total_trips_per_week

        # Умовний шумовий вплив: шум(dB) * кількість машин (проста метрика)
        noise_impact = truck.get("noise_db", 0) * num_trucks

        # Сумарна вартість за тиждень: щоб бути послідовним, повертаємо внутрішню вартість у "грн" (як було) і також окремо в євро
        # Тут ми вважаємо: fuel_cost_per_week_internal (умовно в грн), amortization_per_week_internal (грн), salary_per_week_eur (євро)
        
        fuel_cost_week_eur = fuel_cost_per_week_internal
        amortization_week_eur = amortization_per_week_internal
        total_cost_eur = fuel_cost_week_eur + amortization_week_eur + salary_per_week_eur

        return {
            "num_containers": num_containers,
            "total_trips_per_week": total_trips_per_week,
            "trip_time_hours": trip_time,
            "trips_per_day": trips_per_day,
            "num_trucks": num_trucks,
            "fuel_cost_per_week_internal": fuel_cost_per_week_internal,
            "fuel_cost_per_week": fuel_cost_week_eur,
            "salary_per_week": salary_per_week_eur,
            "amortization_per_week_internal": amortization_per_week_internal,
            "amortization_per_week": amortization_week_eur,
            "co2_per_week": co2_per_week,
            "noise_impact": noise_impact,
            "total_cost": total_cost_eur,
            "radius_km": self.radius,
            "truck_name": truck["name"],
            "truck_key": None,  # буде встановлено зовні
            "container_key": None,
            "container_capacity": container["capacity"],
            "work_hours": work_hours,
            "frequency": frequency,
            "salary": salary_eur,
        }

    def recommend_frequency(self, container_capacity_tonnes: float = None, max_fill_ratio: float = 0.85) -> int:
        if container_capacity_tonnes is None:
            # fallback на стару логіку
            if self.waste <= 50:
                return 1
            elif self.waste <= 200:
                return 2
            elif self.waste <= 500:
                return 3
            else:
                return 4
        
        # нова логіка
        if container_capacity_tonnes <= 0:
            return 1
        
        daily_waste = self.waste / WORK_DAYS_PER_WEEK
        days_to_fill = (container_capacity_tonnes * max_fill_ratio) / daily_waste
        
        if days_to_fill >= 7:
            return 1
        elif days_to_fill >= 3.5:
            return 2
        elif days_to_fill >= 2:
            return 3
        else:
            return 4


# -------------------------------
# Критерії оптимізації
# -------------------------------

CRITERIA = {
    "1": "Мінімальна загальна вартість",
    "2": "Мінімальна кількість вантажівок",
    "3": "Мінімальна зарплата водіїв",
    "4": "Оптимальний баланс вартості з обмеженням кількості вантажівок",
    "5": "Мінімальна амортизація контейнерів",
    "6": "Мініміалізація викидів CO₂",
    "7": "Мінімальний шумовий вплив",
    "8": "Мінімальний час одного рейсу",
    "9": "Максимальна кількість рейсів на день",
    "10": "Оптимальний баланс зарплати і вартості",
    "11": "Мінімальний час роботи водія на день",
    "12": "Баланс викидів CO₂ і вартості",
    "13": "Баланс шуму та вартості",
    "14": "Максимальна вантажність вантажівки",
    "15": "Мінімальна кількість контейнерів",
}

# -------------------------------
# Пошук кращої конфігурації
# -------------------------------

def find_best_config(calculator: ConfigCalculator, criterion: str, user_constraints: dict) -> Optional[dict]:
    results = []

    # автоматично рекомендована частота (якщо користувач не зафіксував)
    default_frequency = calculator.recommend_frequency()

    # Перебір по всіх комбінаціях
    for truck_key, truck in TRUCKS.items():
        for container_key, container in CONTAINERS.items():
            # Salary: якщо користувач зафіксував — використовуємо тільки його
            salary_list = SALARY_OPTIONS
            if "force_salary" in user_constraints and user_constraints["force_salary"] is not None:
                salary_list = [user_constraints["force_salary"]]
            # Work hours
            work_hours_list = WORK_HOURS_OPTIONS
            if "force_work_hours" in user_constraints and user_constraints["force_work_hours"] is not None:
                work_hours_list = [user_constraints["force_work_hours"]]
            # Frequency
            # freq_list = [default_frequency]
            # if "force_frequency" in user_constraints and user_constraints["force_frequency"] is not None:
            #     freq_list = [user_constraints["force_frequency"]]
            if "force_frequency" in user_constraints and user_constraints["force_frequency"] is not None:
                freq_list = [user_constraints["force_frequency"]]
            else:
                freq_list = [1, 2, 3, 4]
            # Force truck
            if "force_truck_key" in user_constraints and user_constraints["force_truck_key"] is not None:
                if user_constraints["force_truck_key"] != truck_key:
                    continue  # пропускаємо інші типи вантажівок

            for salary in salary_list:
                for work_hours in work_hours_list:
                    for frequency in freq_list:
                        # force_num_containers — якщо вказано, передаємо в calculate_cost
                        force_num_containers = user_constraints.get("force_num_containers", None)
                        cost_data = calculator.calculate_cost(truck, container, salary, work_hours, frequency, force_num_containers=force_num_containers)
                        if cost_data is None:
                            continue
                        # встановлюємо ключі
                        cost_data["truck_key"] = truck_key
                        cost_data["container_key"] = container_key

                        # Фільтруємо по обмеженнях користувача
                        if user_constraints:
                            if "max_trucks" in user_constraints and user_constraints["max_trucks"] is not None and cost_data["num_trucks"] > user_constraints["max_trucks"]:
                                continue
                            if "max_salary_per_week" in user_constraints and user_constraints["max_salary_per_week"] is not None and cost_data["salary_per_week"] > user_constraints["max_salary_per_week"]:
                                continue
                            if "max_total_cost" in user_constraints and user_constraints["max_total_cost"] is not None and cost_data["total_cost"] > user_constraints["max_total_cost"]:
                                continue
                            if "max_co2_per_week" in user_constraints and user_constraints["max_co2_per_week"] is not None and cost_data["co2_per_week"] > user_constraints["max_co2_per_week"]:
                                continue
                            if "max_noise_impact" in user_constraints and user_constraints["max_noise_impact"] is not None and cost_data["noise_impact"] > user_constraints["max_noise_impact"]:
                                continue
                            if "max_work_hours" in user_constraints and user_constraints["max_work_hours"] is not None and cost_data["work_hours"] > user_constraints["max_work_hours"]:
                                continue

                        results.append({
                            "truck_key": truck_key,
                            "container_key": container_key,
                            "salary": salary,
                            **cost_data,
                        })

    if not results:
        logger.warning("Неможливо знайти конфігурацію, що задовольняє обмеження.")
        return None

    # Вибір за критерієм
    if criterion == "1":
        best = min(results, key=lambda x: x["total_cost"] + 0.1 * x["fuel_cost_per_week"])
    elif criterion == "2":
        best = min(results, key=lambda x: x["num_trucks"])
    elif criterion == "3":
        best = min(results, key=lambda x: x["salary_per_week"])
    elif criterion == "4":
        max_trucks = user_constraints.get("max_trucks", math.inf)
        filtered = [r for r in results if r["num_trucks"] <= max_trucks]
        if not filtered:
            return None
        best = min(filtered, key=lambda x: x["total_cost"])
    elif criterion == "5":
        best = min(results, key=lambda x: x["amortization_per_week"])
    elif criterion == "6":
        best = min(results, key=lambda x: x["co2_per_week"])
    elif criterion == "7":
        best = min(results, key=lambda x: x["noise_impact"])
    elif criterion == "8":
        best = min(results, key=lambda x: x["trip_time_hours"])
    elif criterion == "9":
        best = max(results, key=lambda x: x["trips_per_day"])
    elif criterion == "10":
        best = min(results, key=lambda x: 0.7 * x["total_cost"] + 0.3 * x["salary_per_week"])
    elif criterion == "11":
        best = min(results, key=lambda x: x["work_hours"])
    elif criterion == "12":
        best = min(results, key=lambda x: 0.5 * x["co2_per_week"] + 0.5 * x["total_cost"])
    elif criterion == "13":
        best = min(results, key=lambda x: 0.5 * x["noise_impact"] + 0.5 * x["total_cost"])
    elif criterion == "14":
        best = max(results, key=lambda x: TRUCKS[x["truck_key"]]["capacity"])
    elif criterion == "15":
        best = min(results, key=lambda x: x["num_containers"])
    else:
        best = min(results, key=lambda x: x["total_cost"] + 0.1 * x["fuel_cost_per_week"])


    return best

# -------------------------------
# Вивід результатів та збереження
# -------------------------------

def print_result_summary(result: dict):
    if not result:
        print("❌ Конфігурацію не знайдено.")
        return

    print("\n✅ Результати оптимізації:")
    print(f"  Вантажівка: {result['truck_name']}")
    print(f"  Контейнер: {result['container_capacity']} т")
    print(f"  Зарплата водія: {result['salary']:.2f} € / місяць")
    print(f"  Робочі години на день: {result['work_hours']}")
    print(f"  Частота збору відходів: {result['frequency']} раз/тиждень")
    print(f"  Кількість контейнерів: {result['num_containers']}")
    print(f"  Кількість рейсів на тиждень: {result['total_trips_per_week']}")
    print(f"  Час одного рейсу: {result['trip_time_hours']:.2f} год")
    print(f"  Рейсів за день: {result['trips_per_day']}")
    print(f"  Кількість вантажівок: {result['num_trucks']}")
    print(f"  Вартість палива на тиждень: {result['fuel_cost_per_week']:.2f} €")
    print(f"  Зарплата водіїв на тиждень: {result['salary_per_week']:.2f} €")
    print(f"  Амортизація контейнерів на тиждень: {result['amortization_per_week']:.2f} €")
    print(f"  Загальна вартість на тиждень: {result['total_cost']:.2f} €")
    print(f"  Викиди CO2 на тиждень: {result['co2_per_week']:.2f} кг")
    print(f"  Умовний шумовий вплив: {result['noise_impact']:.2f} дБ")
    print(f"  Середній шлях в одну сторону: {result['radius_km']:.2f} км")

def save_report(result: dict, filename: Optional[str] = None):
    if not filename:
        filename = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(REPORTS_DIR, filename)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Приведемо всі значення в стрічки адекватно
    flat = {}
    for k, v in result.items():
        try:
            flat[k] = str(v)
        except Exception:
            flat[k] = json.dumps(v)

    try:
        with open(filepath, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(flat.keys()))
            writer.writeheader()
            writer.writerow(flat)
        logger.info(f"Звіт збережено у {filepath}")
    except Exception as e:
        logger.error(f"Помилка при збереженні звіту: {e}")

def load_report(filepath: str) -> Optional[dict]:
    try:
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                return {k: _parse_value(v) for k, v in row.items()}
    except Exception as e:
        logger.error(f"Помилка при завантаженні звіту: {e}")
    return None

def _parse_value(val: str) -> Any:
    if val == "" or val is None:
        return None
    try:
        if "." in val:
            return float(val)
        else:
            return int(val)
    except Exception:
        return val

# -------------------------------
# Візуалізації 
# -------------------------------

class Visualization:
    @staticmethod
    def plot_cost_breakdown(result: dict):
        if plt is None or np is None:
            print("Графіки недоступні (не встановлено matplotlib/numpy).")
            return

        labels = ["Паливо", "Зарплата водіїв", "Амортизація контейнерів"]
        sizes = [result.get("fuel_cost_per_week", 0),
                 result.get("salary_per_week", 0),
                 result.get("amortization_per_week", 0)]
        total = sum(sizes)
        if total == 0:
            print("Немає даних для побудови графіка.")
            return

        sizes = [x/total*100 for x in sizes]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig.gca().add_artist(centre_circle)
        ax.axis('equal')
        plt.title("Розподіл витрат на тиждень (в %) — євро")
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_stacked_costs(results: List[dict]):
        if plt is None or np is None:
            print("Графіки недоступні.")
            return

        labels = [f"{r['truck_name']} ({r['container_capacity']}т)" for r in results[:10]]
        fuel = [r.get("fuel_cost_per_week", 0) for r in results[:10]]
        salary = [r.get("salary_per_week", 0) for r in results[:10]]
        amort = [r.get("amortization_per_week", 0) for r in results[:10]]

        x = np.arange(len(labels))
        width = 0.6

        plt.figure(figsize=(12,6))
        plt.bar(x, fuel, width, label='Паливо')
        plt.bar(x, salary, width, bottom=fuel, label='Зарплата')
        plt.bar(x, amort, width, bottom=np.array(fuel)+np.array(salary), label='Амортизація')

        plt.xticks(x, labels, rotation=45, ha='right')
        plt.ylabel("Загальні витрати, €")
        plt.title("Структура витрат по конфігураціях")
        plt.legend()
        plt.tight_layout()
        plt.grid(axis='y')
        plt.show()




# -------------------------------
# Рекомендації
# -------------------------------

def generate_recommendations(result: dict) -> List[str]:
    recs = []
    if not result:
        return ["❌ Немає результату для аналізу."]
    if result.get("num_trucks", 0) > 5:
        recs.append("Розгляньте використання більших вантажівок або збільшення робочих годин для зменшення кількості машин.")
    if result.get("total_cost", 0) > 1000:  # у євро - поріг прикладний
        recs.append("Вартість висока. Можливо варто оптимізувати зарплати або частоту збору.")
    if result.get("co2_per_week", 0) > 500:
        recs.append("Викиди CO2 великі. Розгляньте перехід на електро-вантажівки або оптимізацію маршрутів.")
    if result.get("noise_impact", 0) > 400:
        recs.append("Шумовий вплив суттєвий. Впроваджуйте заходи зниження шуму (звукоізоляція, графіки роботи).")
    if result.get("trip_time_hours", 0) > 3:
        recs.append("Час одного рейсу довгий. Можливо, потрібно розглянути зміну розташування контейнерів або оптимізацію маршрутів.")
    if not recs:
        recs.append("Поточна конфігурація оптимальна за всіма параметрами.")
    return recs

def print_recommendations(recs: List[str]):
    print("\n📋 Рекомендації для покращення конфігурації:")
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec}")

# -------------------------------
# Два робочі воркфлоу: Auto та Manual
# -------------------------------

def automatic_optimization_workflow():
    clear_console()
    print_header = lambda title: (print("="*60), print(title.center(60)), print("="*60))
    print_header("Автоматична оптимізація — стандарт")

    cluster_data_obj = ClusterData(DATA_FILE)
    cluster_ids = cluster_data_obj.get_cluster_ids()
    if not cluster_ids:
        print("❌ Немає кластерів. Перевірте файл clusters_data.csv")
        pause()
        return

    cluster_id = safe_input(f"Введіть ID кластера ({', '.join(cluster_ids[:5])} ...): ", valid_options=cluster_ids)
    cluster = cluster_data_obj.get_cluster(cluster_id)
    calc = ConfigCalculator(cluster)

    print("\nОберіть критерій оптимізації:")
    for key, desc in CRITERIA.items():
        print(f"  {key}. {desc}")
    criterion = safe_input("Ваш вибір: ", valid_options=list(CRITERIA.keys()))

    # У автоматичному режимі не питаємо зайві речі — лише базові мінімальні опції
    constraints = {}
    # # Дозволимо користувачу задати максимум вантажівок за бажанням, але за замовчуванням — немає
    # ask = safe_input("Бажаєте вказати максимальну кількість вантажівок? (y/n): ", valid_options=["y","n"])
    # if ask == "y":
    #     max_trucks = safe_input_number("Максимальна кількість вантажівок (ціле число, Enter для пропуску): ", allow_empty=True, integer=True, minimum=1)
    #     if max_trucks is not None:
    #         constraints["max_trucks"] = int(max_trucks)

    print("\n🕒 Обчислюємо конфігурації...")
    best_config = find_best_config(calc, criterion, constraints)

    # Вивід та рекомендації
    print_result_summary(best_config)
    recs = generate_recommendations(best_config)
    print_recommendations(recs)

    # Візуалізація (опціонально)
    if plt is not None and best_config is not None:
        vis = Visualization()
        vis.plot_cost_breakdown(best_config)
    else:
        print("Графічна візуалізація пропущена (matplotlib не встановлено).")

    
    # Збереження звіту
    save_opt = safe_input("\nЗберегти звіт? (y/n): ", valid_options=["y", "n"])
    if save_opt == "y" and best_config is not None:
        filename = safe_input("Ім'я файлу для звіту (.csv або Enter): ", allow_empty=True)
        if filename == "":
            save_report(best_config)
        else:
            save_report(best_config, filename)

    pause()
    clear_console()


def manual_optimization_workflow():
    clear_console()
    print_header = lambda title: (print("="*60), print(title.center(60)), print("="*60))
    print_header("Вручну — гнучка оптимізація")

    cluster_data_obj = ClusterData(DATA_FILE)
    cluster_ids = cluster_data_obj.get_cluster_ids()
    if not cluster_ids:
        print("❌ Немає кластерів. Перевірте файл clusters_data.csv")
        pause()
        return

    cluster_id = safe_input(f"Введіть ID кластера ({', '.join(cluster_ids[:5])} ...): ", valid_options=cluster_ids)
    cluster = cluster_data_obj.get_cluster(cluster_id)
    calc = ConfigCalculator(cluster)

    print("\nОберіть один критерій оптимізації:")
    for key, desc in CRITERIA.items():
        print(f" {key}. {desc}")

    chosen = safe_input_choice("Ваш вибір (1,2,...): ", allowed=list(CRITERIA.keys()))

    if not chosen:
        print("❌ Ви не обрали жодного критерію. Спробуйте ще раз.")
        pause()
        return

    primary_criterion = chosen


    print("\nТепер вкажіть, які параметри ви хочете зафіксувати (натисніть Enter для пропуску):")
    constraints = {}

    # Зарплата (євро/місяць)
    salary = safe_input_number("Фіксована зарплата водія (€/місяць) або Enter для пропуску: ", allow_empty=True, integer=False, minimum=0)
    if salary is not None:
        constraints["force_salary"] = salary

    # Тип вантажівки
    print("\nДоступні типи вантажівок:")
    for k, v in TRUCKS.items():
        print(f"  {k} — {v['name']} ({v['capacity']} т)")
    truck_choice = safe_input("Вкажіть ключ вантажівки (наприклад 'electric_10t') або Enter для пропуску: ", allow_empty=True)
    if truck_choice:
        if truck_choice in TRUCKS:
            constraints["force_truck_key"] = truck_choice
        else:
            print("❌ Некоректний ключ вантажівки — ігноруємо.")

    # Робочі години
    wh = safe_input_number("Фіксована кількість робочих годин на день (ціле число) або Enter для пропуску: ", allow_empty=True, integer=True, minimum=1)
    if wh is not None:
        constraints["force_work_hours"] = int(wh)

    # Кількість контейнерів (фіксована)
    fnc = safe_input_number("Фіксована кількість контейнерів (ціле число) або Enter для пропуску: ", allow_empty=True, integer=True, minimum=1)
    if fnc is not None:
        constraints["force_num_containers"] = int(fnc)

    # Максимальна кількість вантажівок
    mt = safe_input_number("Максимальна кількість вантажівок або Enter для пропуску: ", allow_empty=True, integer=True, minimum=1)
    if mt is not None:
        constraints["max_trucks"] = int(mt)

    # Частота збору
    fq = safe_input_number("Фіксована частота збору (разів/тиждень) або Enter для пропуску: ", allow_empty=True, integer=True, minimum=1, maximum=7)
    if fq is not None:
        constraints["force_frequency"] = int(fq)

    # Додаткові обмеження (CO2, шум, бюджет)
    want_extra = safe_input("Бажаєте задати додаткові обмеження (макс CO2, макс шум, макс загальна вартість)? (y/n): ", valid_options=["y","n"])
    if want_extra == "y":
        max_co2 = safe_input_number("Максимальні викиди CO2 на тиждень (кг) або Enter для пропуску: ", allow_empty=True, minimum=0)
        if max_co2 is not None:
            constraints["max_co2_per_week"] = max_co2
        max_noise = safe_input_number("Максимальний шумовий індекс (умовна метрика) або Enter для пропуску: ", allow_empty=True, minimum=0)
        if max_noise is not None:
            constraints["max_noise_impact"] = max_noise
        max_total_cost = safe_input_number("Максимальна загальна вартість на тиждень (€) або Enter для пропуску: ", allow_empty=True, minimum=0)
        if max_total_cost is not None:
            constraints["max_total_cost"] = max_total_cost

    print("\n🕒 Обчислюємо конфігурації з вашими обмеженнями...")
    best_config = find_best_config(calc, primary_criterion, constraints)

    if best_config:
        print_result_summary(best_config)
        recs = generate_recommendations(best_config)
        print_recommendations(recs)

        # Візуалізація та симуляції (опціонально)
        if plt is not None:
            vis = Visualization()
            vis.plot_cost_breakdown(best_config)
        
    else:
        print("❌ Конфігурацію з такими параметрами знайти неможливо. Спробуйте інші обмеження або зменшіть вимоги.")
    # Збереження
    save_opt = safe_input("\nЗберегти звіт? (y/n): ", valid_options=["y","n"])
    if save_opt == "y" and best_config is not None:
        filename = safe_input("Ім'я файлу для звіту (.csv або Enter): ", allow_empty=True)
        if filename == "":
            save_report(best_config)
        else:
            save_report(best_config, filename)

    pause()
    clear_console()


def automatic_optimization_all_clusters():
    import time
    import csv

    clear_console()
    print("="*60)
    print("Автоматична оптимізація — всі кластери".center(60))
    print("="*60)

    cluster_data_obj = ClusterData(DATA_FILE)
    cluster_ids = cluster_data_obj.get_cluster_ids()
    if not cluster_ids:
        print("❌ Немає кластерів. Перевірте файл clusters_data.csv")
        pause()
        return

    # Беремо перший критерій
    first_criterion = list(CRITERIA.keys())[0]
    print(f"\n⚙ Використовується критерій оптимізації: {first_criterion} — {CRITERIA[first_criterion]}")

    total_clusters = len(cluster_ids)
    results_all = []

    start_time = time.time()

    for idx, cluster_id in enumerate(cluster_ids, start=1):

        #time.sleep(0.5)
        print(f"\n[{idx}/{total_clusters}] 🕒 Обчислюємо конфігурацію для кластера {cluster_id}...")

        cluster = cluster_data_obj.get_cluster(cluster_id)
        if cluster is None:
            print(f"❌ Кластер {cluster_id} не знайдено в даних")
            continue

        calc = ConfigCalculator(cluster)
        best_config = find_best_config(calc, first_criterion, {})

        if best_config is None:
            print("❌ Конфігурацію не знайдено для цього кластера.")
            continue

        print_result_summary(best_config)

        # Об'єднуємо дані кластера та результат оптимізації
        merged_data = {"cluster_id": cluster_id, **cluster, **best_config}
        results_all.append(merged_data)

        # Приблизний час завершення
        elapsed = time.time() - start_time
        remaining = (elapsed / idx) * (total_clusters - idx)
        print(f"⏱ Час виконання: {elapsed:.1f} с, прогнозований залишок: {remaining:.1f} с")



    # Збереження CSV
    if results_all:
        output_file = "cost_all_clusters.csv"


        desired_fields = [
            "cluster_id",
            "region",
            "waste_tonnes_week",
            "total_cost",
            "area_km2"
        ]

        with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=desired_fields)
            writer.writeheader()
            for r in results_all:
                # Створюємо словник лише з потрібними ключами
                row = {k: r.get(k, "") for k in desired_fields}
                writer.writerow(row)

        print(f"\n✅ Результати збережено у файл: {output_file}")
    else:
        print("\n❌ Жодних результатів для збереження немає.")


    pause()
    clear_console()







# -------------------------------
# Додаткові допоміжні функції меню
# -------------------------------

def print_header(title: str):
    clear_console()
    print("=" * 80)
    print(title.center(80))
    print("=" * 80)

def setup_file_logging(logfile="optimizer_extended.log"):
    file_handler = logging.FileHandler(logfile, mode='w', encoding='utf-8')
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

setup_file_logging()

# -------------------------------
# Головне інтерактивне меню
# -------------------------------

def interactive_menu_extended():
    print_header("Waste Transport Optimizer v3.0 — Extended")
    while True:
        print("\nОберіть режим:")
        print("  1. Показати інформацію про кластери")
        print("  2. Автоматично — Оптимізувати конфігурацію (стандарт)")
        print("  3. Вручну — Гнучка оптимізація (фіксуйте параметри)")
        print("  4. Зберегти інформацію про всі кластера")
        print("  5. Завантажити і показати звіт")
        print("  6. Вийти")
        choice = safe_input("Ваш вибір: ", valid_options=["1","2","3","4","5","6"])

        cluster_data_obj = ClusterData(DATA_FILE)
        cluster_ids = cluster_data_obj.get_cluster_ids()

        if choice == "1":
            print_header("Інформація про кластери")
            if not cluster_ids:
                print("❌ Немає кластера для відображення.")
            else:
                print(f"Всього кластерів: {len(cluster_ids)}")
                for cid in cluster_ids:
                    c = cluster_data_obj.get_cluster(cid)
                    print(f"  ID: {cid} | Регіон: {c.get('region')} | Відходи: {c.get('waste_tonnes_week')} т/тиж | Площа: {c.get('area_km2')} км²")
            pause()
            clear_console()

        elif choice == "2":
            automatic_optimization_workflow()

        elif choice == "3":
            manual_optimization_workflow()

        elif choice == "4":
            automatic_optimization_all_clusters()

        elif choice == "5":
            print_header("Завантаження звіту")
            files = os.listdir(REPORTS_DIR) if os.path.exists(REPORTS_DIR) else []
            if not files:
                print("❌ Немає збережених звітів.")
                pause()
                clear_console()
                continue
            print("Доступні звіти:")
            for idx, f in enumerate(files):
                print(f"  {idx + 1}. {f}")
            file_choice = safe_input_number(f"Введіть номер звіту (1-{len(files)}): ", allow_empty=False, integer=True, minimum=1, maximum=len(files))
            if file_choice is None:
                print("❌ Некоректний вибір.")
                pause()
                clear_console()
                continue
            report = load_report(os.path.join(REPORTS_DIR, files[int(file_choice)-1]))
            if report:
                print_result_summary(report)
            else:
                print("❌ Не вдалося завантажити звіт.")
            pause()
            clear_console()

        elif choice == "6":
            print("\nДякую, що користуєтесь Waste Transport Optimizer! До зустрічі.")
            break

# -------------------------------
# Запуск
# -------------------------------

if __name__ == "__main__":
    try:
        interactive_menu_extended()
    except KeyboardInterrupt:
        print("\nНадрукодано Ctrl-C — вихід.")
    except Exception as e:
        logger.exception(f"Непередбачена помилка: {e}")
