#!/usr/bin/env python3

import json
from typing import Dict, List, Any, Optional


class MeritMoneyCalculator:
    def __init__(
        self,
        config_path: str = "config.json",
        performance_path: str = "weekly_performance.json",
    ):
        self.config = self._load_json(config_path)
        self.performance_data = self._load_json(performance_path)
        self.pool_per_person = self.config.get("pool_per_person", 100)

    def _load_json(self, filepath: str) -> Dict:
        with open(filepath, "r") as f:
            return json.load(f)

    def _hours_to_decimal(self, hours_value: Any) -> float:
        if isinstance(hours_value, dict):
            hours = hours_value.get("hours", 0)
            minutes = hours_value.get("minutes", 0)
            return hours + (minutes / 60.0)
        return float(hours_value)

    def calculate_subcategory_score(
        self,
        subcategory: Dict,
        performance_value: Any,
        ratio_total: Optional[float] = None,
    ) -> float:
        subcategory_type = subcategory.get("type", "boolean")

        if subcategory_type == "boolean":
            return 1.0 if performance_value else 0.0
        elif subcategory_type == "hours":
            requirement = subcategory.get("requirement", 8)
            actual_hours = self._hours_to_decimal(performance_value)
            return actual_hours / requirement
        elif subcategory_type == "ratio":
            if ratio_total is None or ratio_total == 0:
                return 0.0
            return performance_value / ratio_total
        else:
            raise ValueError(f"Unknown subcategory type: {subcategory_type}")

    def calculate_ratio_totals(self) -> Dict[str, float]:
        ratio_totals = {}

        for category in self.config.get("categories", []):
            for subcategory in category.get("subcategories", []):
                if subcategory.get("type") == "ratio":
                    subcategory_name = subcategory["name"]
                    total = 0.0

                    for team_member in self.performance_data.get("team_members", []):
                        performance = team_member.get("performance", {})
                        value = performance.get(subcategory_name, 0)
                        total += value

                    ratio_totals[subcategory_name] = total

        return ratio_totals

    def calculate_category_score(
        self, category: Dict, performance: Dict, ratio_totals: Dict[str, float]
    ) -> float:
        total_score = 0.0

        for subcategory in category.get("subcategories", []):
            subcategory_name = subcategory["name"]
            breakdown_weight = subcategory.get("breakdown_weight", 0)
            performance_value = performance.get(subcategory_name)

            if performance_value is None:
                continue

            ratio_total = (
                ratio_totals.get(subcategory_name)
                if subcategory.get("type") == "ratio"
                else None
            )
            subscore = self.calculate_subcategory_score(
                subcategory, performance_value, ratio_total
            )
            weighted_score = subscore * breakdown_weight
            total_score += weighted_score

        return total_score

    def calculate_merit_money(
        self, team_member: Dict, ratio_totals: Dict[str, float]
    ) -> Dict[str, float]:
        name = team_member.get("name", "Unknown")
        performance = team_member.get("performance", {})

        result = {"name": name, "total": 0.0}

        for category in self.config.get("categories", []):
            total_weight = category.get("total_weight", 0)
            category_score = self.calculate_category_score(
                category, performance, ratio_totals
            )
            category_money = category_score * total_weight * self.pool_per_person
            result["total"] += category_money

        return result

    def calculate_all(self) -> List[Dict]:
        ratio_totals = self.calculate_ratio_totals()
        results = []
        total_score = 0.0

        for team_member in self.performance_data.get("team_members", []):
            result = self.calculate_merit_money(team_member, ratio_totals)
            results.append(result)
            total_score += result["total"]

        if total_score > 0:
            total_pool = self.pool_per_person * len(self.performance_data.get("team_members", []))
            for result in results:
                proportion = result["total"] / total_score
                result["total"] = proportion * total_pool

        return results

    def print_results(self, results: List[Dict]):
        print("\nMerit Money Distribution:")
        print("=" * 40)

        total_distributed = 0.0
        for result in results:
            print(f"{result['name']:30s} ${result['total']:7.2f}")
            total_distributed += result["total"]

        print("=" * 40)
        print(f"{'Total':30s} ${total_distributed:.2f}\n")


def main():
    calculator = MeritMoneyCalculator()
    results = calculator.calculate_all()
    calculator.print_results(results)


if __name__ == "__main__":
    main()
