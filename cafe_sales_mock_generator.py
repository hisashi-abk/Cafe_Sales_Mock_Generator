from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
import random
import json
import csv
import pandas as pd
import yaml
from pathlib import Path


class Weather(Enum):
    SUNNY = 1
    CLOUDY = 2
    RAINY = 3

    @classmethod
    def get_name(cls, value: int) -> str:
        weather_names = {1: "晴れ", 2: "曇り", 3: "雨"}
        return weather_names[value]


class TimeSlot(Enum):
    MORNING = 1
    LUNCH = 2
    TEATIME = 3
    REGULAR = 4

    @classmethod
    def get_name(cls, value: int) -> str:
        timeslot_names = {1: "モーニング", 2: "ランチ", 3: "ティータイム", 4: "レギュラー"}
        return timeslot_names[value]


class Gender(Enum):
    MALE = 1
    FEMALE = 2

    @classmethod
    def get_name(cls, value: int) -> str:
        gender_names = {1: "男", 2: "女"}
        return gender_names[value]


class OrderType(Enum):
    FOR_HERE = 1
    TAKEOUT = 2

    @classmethod
    def get_name(cls, value: int) -> str:
        order_type_names = {1: "店内", 2: "テイクアウト"}
        return order_type_names[value]


@dataclass
class MenuItem:
    id: int
    name: str
    price: int
    category_id: int


@dataclass
class MenuCategory:
    id: int
    name: str


@dataclass
class TimeSlotConfig:
    hours: List[Tuple[int, int]]
    customer_range: Tuple[int, int]


class CafeMockGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        # Load configuration
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # 生成期間の設定を取得
        self.generate_year = self.config.get("generate_period", {}).get("year", 2024)
        self.generate_month = self.config.get("generate_period", {}).get("month", 4)

        # Menu Categories
        self.categories = [MenuCategory(cat["id"], cat["name"]) for cat in self.config["categories"]]

        # Menu Items
        self.menu_items = {}
        for category_name, category_data in self.config["menu_items"].items():
            category_id = category_data["category_id"]
            self.menu_items[category_id] = [
                MenuItem(item["id"], item["name"], item["price"], category_id) for item in category_data["items"]
            ]

        # Business Hours
        self.BUSINESS_HOURS = {
            "start": (self.config["business_hours"]["start"]["hour"], self.config["business_hours"]["start"]["minute"]),
            "end": (self.config["business_hours"]["end"]["hour"], self.config["business_hours"]["end"]["minute"]),
        }

        # Customer and Weather Settings
        self.MAX_DAILY_CUSTOMERS = self.config["max_daily_customers"]
        self.WEATHER_FACTORS = {
            Weather.SUNNY: self.config["weather_factors"]["sunny"],
            Weather.CLOUDY: self.config["weather_factors"]["cloudy"],
            Weather.RAINY: self.config["weather_factors"]["rainy"],
        }

        # Time Slots Configuration
        self.time_slots = {}
        for slot_name, slot_data in self.config["time_slots"].items():
            slot_enum = TimeSlot[slot_name.upper()]
            hours = []
            if slot_data["hours"]:
                hours = [(h[0], h[1]) for h in slot_data["hours"]]
            self.time_slots[slot_enum] = TimeSlotConfig(hours=hours, customer_range=tuple(slot_data["customer_range"]))

    def _get_random_timestamp(self, base_time: datetime) -> datetime:
        random_minutes = random.random() * 15
        random_seconds = random.random() * 60
        return base_time + timedelta(minutes=random_minutes, seconds=random_seconds)

    def _get_time_slot(self, dt: datetime) -> TimeSlot:
        """時間帯を判定"""
        time = dt.hour + dt.minute / 60

        for slot, config in self.time_slots.items():
            if not config.hours:  # REGULAR の場合はスキップ
                continue

            start_hour, start_minute = config.hours[0]
            end_hour, end_minute = config.hours[1]

            start_time = start_hour + start_minute / 60
            end_time = end_hour + end_minute / 60

            if start_time <= time < end_time:
                return slot

        return TimeSlot.REGULAR

    def _generate_order(self, date: datetime, order_id: int, time_slot: TimeSlot, is_takeout: bool) -> Dict[str, Any]:
        selected_items = []
        original_total = 0

        # OrderType の設定
        order_type = OrderType.TAKEOUT if is_takeout else OrderType.FOR_HERE

        # Set menu pricing from config
        set_menu_pricing = self.config["set_menu_pricing"]

        if time_slot == TimeSlot.MORNING and not is_takeout:
            # モーニングはドリンクとサンドイッチを選択
            drink = random.choice(self.menu_items[1])
            sandwich = random.choice(self.menu_items[2])
            selected_items.extend(
                [
                    {"menu_item_id": drink.id, "price": drink.price},
                    {"menu_item_id": sandwich.id, "price": sandwich.price},
                ]
            )
            original_total = drink.price + sandwich.price
            final_price = min(set_menu_pricing["morning"]["max_price"], original_total)

        elif time_slot == TimeSlot.LUNCH and not is_takeout:
            # ランチタイムはドリンク、サンドイッチ、ケーキを選択
            drink = random.choice(self.menu_items[1])
            sandwich = random.choice(self.menu_items[2])
            cake = random.choice(self.menu_items[3])
            selected_items.extend(
                [
                    {"menu_item_id": drink.id, "price": drink.price},
                    {"menu_item_id": sandwich.id, "price": sandwich.price},
                    {"menu_item_id": cake.id, "price": cake.price},
                ]
            )
            original_total = drink.price + sandwich.price + cake.price
            final_price = min(set_menu_pricing["lunch"]["max_price"], original_total)

        elif time_slot == TimeSlot.TEATIME and not is_takeout:
            # ティータイムはドリンク、ケーキを選択
            drink = random.choice(self.menu_items[1])
            cake = random.choice(self.menu_items[3])
            selected_items.extend(
                [{"menu_item_id": drink.id, "price": drink.price}, {"menu_item_id": cake.id, "price": cake.price}]
            )
            original_total = drink.price + cake.price
            final_price = min(set_menu_pricing["teatime"]["max_price"], original_total)

        else:
            # 通常注文の生成
            if is_takeout:
                num_items = random.randint(1, 5)
                for _ in range(num_items):
                    category_id = random.randint(1, 3)
                    item = random.choice(self.menu_items[category_id])
                    selected_items.append({"menu_item_id": item.id, "price": item.price})
            else:
                # 必ずドリンクを含める
                drink = random.choice(self.menu_items[1])
                selected_items.append({"menu_item_id": drink.id, "price": drink.price})

                # サンドイッチとケーキはランダムで追加
                if random.random() < 0.35:
                    sandwich = random.choice(self.menu_items[2])
                    selected_items.append({"menu_item_id": sandwich.id, "price": sandwich.price})
                if random.random() < 0.6:
                    cake = random.choice(self.menu_items[3])
                    selected_items.append({"menu_item_id": cake.id, "price": cake.price})

            original_total = sum(item["price"] for item in selected_items)
            final_price = original_total

        order_data = {
            "id": f"{date.strftime('%Y%m%d')}-{order_id:03d}",
            "timestamp": date.strftime("%Y-%m-%d %H:%M:%S"),
            "gender_id": random.choice([g.value for g in Gender]),
            "order_type_id": order_type.value,
            "weather_id": random.choice([w.value for w in Weather]),
            "time_slot_id": time_slot.value,
            "total_price": final_price,
            "discount": max(0, original_total - final_price),
        }

        # 注文詳細を追加
        order_data["items"] = selected_items

        return order_data

    def generate_daily_sales(self, date: datetime) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """1日の売上データを生成し、orders と order_items を返す"""
        # 天気を1日の最初に1回だけ設定
        daily_weather = random.choice([w for w in Weather])

        # 変数の初期化
        daily_orders: List[Dict[str, Any]] = []
        daily_order_items: List[Dict[str, Any]] = []
        order_counter: int = 1
        takeout_counter: int = 0

        # 時間帯ごとの注文をバッファリング
        time_slot_orders: Dict[TimeSlot, List[Dict[str, Any]]] = {slot: [] for slot in TimeSlot}

        # テイクアウトの上限設定
        weather_settings = self.config["weather"]
        takeout_limit = weather_settings[daily_weather.name.lower()]["takeout_limit"]

        # 時間帯ごとの客数を計算
        customers_by_slot = {}
        total_customers = 0

        for slot, config in self.time_slots.items():
            min_customers, max_customers = config.customer_range
            adjusted_min = int(min_customers * self.WEATHER_FACTORS[daily_weather])
            adjusted_max = int(max_customers * self.WEATHER_FACTORS[daily_weather])

            slot_customers = random.randint(max(1, adjusted_min), max(adjusted_min, adjusted_max))
            customers_by_slot[slot] = slot_customers
            total_customers += slot_customers

        # 最大客数の制限
        if total_customers > self.MAX_DAILY_CUSTOMERS:
            factor = self.MAX_DAILY_CUSTOMERS / total_customers
            customers_by_slot = {slot: int(count * factor) for slot, count in customers_by_slot.items()}

        # 営業時間内で注文を生成
        current_time = datetime.combine(
            date.date(),
            datetime.strptime(
                f"{self.BUSINESS_HOURS['start'][0]:02d}:{self.BUSINESS_HOURS['start'][1]:02d}", "%H:%M"
            ).time(),
        )
        end_time = datetime.combine(
            date.date(),
            datetime.strptime(
                f"{self.BUSINESS_HOURS['end'][0]:02d}:{self.BUSINESS_HOURS['end'][1]:02d}", "%H:%M"
            ).time(),
        )

        # 各時間帯の注文をバッファリング
        time_slot_orders = {slot: [] for slot in TimeSlot}

        while current_time < end_time:
            current_slot = self._get_time_slot(current_time)
            if customers_by_slot[current_slot] > 0:
                is_takeout = random.random() < 0.2 and takeout_counter < takeout_limit
                if is_takeout:
                    takeout_counter += 1

                # ランダムな時間を生成
                random_time = self._get_random_timestamp(current_time)

                order = self._generate_order(random_time, order_counter, current_slot, is_takeout)

                # 注文アイテムの処理
                order_items = []
                for idx, item in enumerate(order["items"], 1):
                    order_item = {
                        "id": f"{order['id']}-{idx:02d}",
                        "order_id": order["id"],
                        "menu_item_id": item["menu_item_id"],
                        "price": item["price"],
                    }
                    order_items.append(order_item)

                # items キーを削除（normalized_ordersのため）
                order_data = order.copy()
                del order_data["items"]

                # 1日の最初に設定した天気をオーダーに追加
                order_data["weather_id"] = daily_weather.value

                time_slot_orders[current_slot].append(order_data)
                daily_order_items.extend(order_items)
                order_counter += 1
                customers_by_slot[current_slot] -= 1

            current_time += timedelta(minutes=15)

        # 各時間帯の注文を時間でソート
        for slot in TimeSlot:
            slot_orders = sorted(
                time_slot_orders[slot], key=lambda x: datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S")
            )
            daily_orders.extend(slot_orders)

        return daily_orders, daily_order_items

    def generate_monthly_orders(self, year: int, month: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """1ヶ月分の売上データを生成"""
        monthly_orders = []
        monthly_order_items = []
        current_date = datetime(year, month, 1)

        while current_date.month == month:
            daily_orders, daily_order_items = self.generate_daily_sales(current_date)
            monthly_orders.extend(daily_orders)
            monthly_order_items.extend(daily_order_items)
            current_date += timedelta(days=1)

        return monthly_orders, monthly_order_items

    def save_to_files(self, order_data: Tuple[List[Dict[str, Any]], List[Dict[str, Any]]], year: int, month: int):
        """データを各形式で保存 - 正規化されたスキーマで保存"""
        orders, order_items = order_data

        # Master Data generation
        master_data = {
            "categories": [{"id": cat.id, "name": cat.name} for cat in self.categories],
            "menu_items": [
                {"id": item.id, "name": item.name, "price": item.price, "category_id": item.category_id}
                for category in self.menu_items.values()
                for item in category
            ],
            "genders": [{"id": g.value, "name": g.get_name(g.value)} for g in Gender],
            "order_types": [{"id": ot.value, "name": ot.get_name(ot.value)} for ot in OrderType],
            "weather_types": [{"id": w.value, "name": w.get_name(w.value)} for w in Weather],
            "time_slots": [{"id": ts.value, "name": ts.get_name(ts.value)} for ts in TimeSlot],
        }

        # Save master data
        with open(f"master_data_{year}-{month:02d}.json", "w", encoding="utf-8") as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)

        # Save normalized data
        with open(f"orders_{year}-{month:02d}.json", "w", encoding="utf-8") as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)

        with open(f"order_items_{year}-{month:02d}.json", "w", encoding="utf-8") as f:
            json.dump(order_items, f, ensure_ascii=False, indent=2)

        # マスターデータの読み込み
        with open(f"master_data_{year}-{month:02d}.json", "r", encoding="utf-8") as f:
            master_data = json.load(f)

        # 既存のExcel出力コード
        def export_original_excel(year: int, month: int, orders: List[Dict[str, Any]], master_data: Dict):
            with pd.ExcelWriter(f"cafe_data_{year}_{month:02d}.xlsx") as writer:
                # 元のシート形式を維持
                orders_with_details = []
                for order in orders:
                    order_details = order.copy()

                    # マスターデータから名称を取得
                    order_details["gender"] = next(
                        (g["name"] for g in master_data["genders"] if g["id"] == order["gender_id"]), "Unknown"
                    )
                    order_details["order_type"] = next(
                        (ot["name"] for ot in master_data["order_types"] if ot["id"] == order["order_type_id"]),
                        "Unknown",
                    )
                    order_details["weather"] = next(
                        (w["name"] for w in master_data["weather_types"] if w["id"] == order["weather_id"]), "Unknown"
                    )
                    order_details["time_slot"] = next(
                        (ts["name"] for ts in master_data["time_slots"] if ts["id"] == order["time_slot_id"]), "Unknown"
                    )

                    orders_with_details.append(order_details)

                pd.DataFrame(orders_with_details).to_excel(writer, sheet_name="Orders", index=False)

                # メニューデータ
                # Drinks
                pd.DataFrame(
                    [
                        {"id": item["id"], "name": item["name"], "price": item["price"]}
                        for item in master_data["menu_items"]
                        if item["category_id"] == 1
                    ]
                ).to_excel(writer, sheet_name="Drinks", index=False)

                # Sandwiches
                pd.DataFrame(
                    [
                        {"id": item["id"], "name": item["name"], "price": item["price"]}
                        for item in master_data["menu_items"]
                        if item["category_id"] == 2
                    ]
                ).to_excel(writer, sheet_name="Sandwiches", index=False)

                # Cakes
                pd.DataFrame(
                    [
                        {"id": item["id"], "name": item["name"], "price": item["price"]}
                        for item in master_data["menu_items"]
                        if item["category_id"] == 3
                    ]
                ).to_excel(writer, sheet_name="Cakes", index=False)

        # 新しいマルチシート形式のExcelファイル出力
        def export_comprehensive_excel(
            year: int, month: int, orders: List[Dict[str, Any]], order_items: List[Dict[str, Any]], master_date: Dict
        ):
            with pd.ExcelWriter(f"cafe_comprehensive_data_{year}_{month:02d}.xlsx") as writer:
                # 注文データ
                pd.DataFrame(orders).to_excel(writer, sheet_name="Orders", index=False)

                # 注文アイテム
                pd.DataFrame(order_items).to_excel(writer, sheet_name="Order Items", index=False)

                # マスターデータシート
                pd.DataFrame(master_data["categories"]).to_excel(writer, sheet_name="Categories", index=False)
                pd.DataFrame(master_data["menu_items"]).to_excel(writer, sheet_name="Menu Items", index=False)
                pd.DataFrame(master_data["genders"]).to_excel(writer, sheet_name="Genders", index=False)
                pd.DataFrame(master_data["order_types"]).to_excel(writer, sheet_name="Order Types", index=False)
                pd.DataFrame(master_data["weather_types"]).to_excel(writer, sheet_name="Weather Types", index=False)
                pd.DataFrame(master_data["time_slots"]).to_excel(writer, sheet_name="Time Slots", index=False)

        # 両方のエクスポートを実行
        export_original_excel(year, month, orders, master_data)
        export_comprehensive_excel(year, month, orders, order_items, master_data)

        # CSV出力
        order_fields = [
            "id",
            "order_id",
            "timestamp",
            "gender_id",
            "gender_name",
            "order_type_id",
            "order_type_name",
            "weather_id",
            "weather_name",
            "time_slot_id",
            "time_slot_name",
            "total_price",
            "discount",
        ]

        def enrich_order_with_names(order, master_data):
            enriched_order = order.copy()

            # マスターデータから名称を取得
            enriched_order["gender_name"] = next(
                (g["name"] for g in master_data["genders"] if g["id"] == order["gender_id"]), "Unknown"
            )
            enriched_order["order_type_name"] = next(
                (ot["name"] for ot in master_data["order_types"] if ot["id"] == order["order_type_id"]),
                "Unknown",
            )
            enriched_order["weather_name"] = next(
                (w["name"] for w in master_data["weather_types"] if w["id"] == order["weather_id"]), "Unknown"
            )
            enriched_order["time_slot_name"] = next(
                (ts["name"] for ts in master_data["time_slots"] if ts["id"] == order["time_slot_id"]), "Unknown"
            )

            return enriched_order

        # 注文データのCSV出力
        csv_orders = [enrich_order_with_names(order, master_data) for order in orders]
        with open(f"orders_{year}_{month:02d}.csv", "w", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=order_fields)
            writer.writeheader()
            writer.writerows(csv_orders)

    def generate_test_data(self, year: int = 2024, month: int = 4) -> None:
        """テストデータを生成して各形式で保存"""
        print(f"{year}年{month}月のカフェ売上データを生成します...")
        order_data = self.generate_monthly_orders(year, month)
        self.save_to_files(order_data, year, month)
        print("\nデータ生成が完了しました。")


def main():
    """メイン実行関数"""
    try:
        print("カフェ売上データジェネレーターを開始します...")
        generator = CafeMockGenerator()
        generator.generate_test_data(
            year=generator.generate_test_year,
            month=generator.generate_test_month,
        )
        print("データ生成が完了しました。")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise


if __name__ == "__main__":
    main()
