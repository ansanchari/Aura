import json
import os
from datetime import datetime, date

class UserProfile:
    def __init__(self, filepath="user_profile.json"):
        self.filepath = filepath

    def lock_in_start_date(self, start_date: date):
        data = {"cycle_start_date": start_date.strftime("%Y-%m-%d")}
        with open(self.filepath, "w") as f:
            json.dump(data, f)

    def get_current_cycle_day(self) -> int:
        if not os.path.exists(self.filepath):
            return None 
        with open(self.filepath, "r") as f:
            data = json.load(f)
        start_date = datetime.strptime(data["cycle_start_date"], "%Y-%m-%d").date()
        today = date.today()
        delta = today - start_date
        return delta.days + 1

class CycleScheduler:
    def __init__(self):
        self.phases = {
            "Menstrual": {
                "days": range(1, 6),
                "energy": "Low / Restorative",
                "optimal_tasks": ["rest", "reflection", "admin", "low-effort", "planning"],
                "advice": "Energy is lowest. Focus on light admin work and self-care. Avoid high-stress tasks.",
                "diet": "Focus on iron-rich foods (spinach, lentils, red meat) and magnesium (dark chocolate, pumpkin seeds) to replenish lost nutrients. Warm, comforting foods like soups and stews are best.",
                "well_being": "Prioritize extra sleep. Stick to gentle movements like restorative yoga or walking. Use heat therapy for cramps."
            },
            "Follicular": {
                "days": range(6, 14),
                "energy": "Rising / Creative",
                "optimal_tasks": ["brainstorming", "creativity", "new projects", "learning", "problem-solving"],
                "advice": "Estrogen is rising. Your brain is primed for creativity and tackling complex new problems.",
                "diet": "Support rising estrogen with fresh, light foods. Incorporate fermented foods (kimchi, kombucha) for gut health, and lean proteins (chicken, tofu, eggs).",
                "well_being": "Your stamina is returning. This is a great week to try a new workout class, do some cardio, or socialize."
            },
            "Ovulatory": {
                "days": range(14, 18),
                "energy": "Peak / Social",
                "optimal_tasks": ["presentations", "networking", "meetings", "collaboration", "high-impact", "pitch"],
                "advice": "Testosterone and estrogen peak. You are at your most articulate and social. Great time for pitches!",
                "diet": "Help your body metabolize high estrogen levels with anti-inflammatory foods. Focus on raw veggies, berries, nuts, and omega-3s (salmon, chia seeds).",
                "well_being": "Your energy is at its absolute peak. Push yourself with high-intensity workouts (HIIT, heavy lifting) and schedule community events."
            },
            "Luteal": {
                "days": range(18, 35),
                "energy": "Winding Down / Detail-Oriented",
                "optimal_tasks": ["deep work", "editing", "wrapping up", "organizing", "solo work", "coding"],
                "advice": "Progesterone rises. You are highly detail-oriented. Great time for heads-down, focused solo work.",
                "diet": "Combat PMS cravings by stabilizing blood sugar. Eat complex carbs (sweet potatoes, brown rice, quinoa), foods high in calcium, and B-vitamins.",
                "well_being": "Transition away from intense cardio. Focus on Pilates, strength training, and eventually journaling and winding down as your cycle restarts."
            }
        }

    def get_current_phase(self, cycle_day: int):
        if not cycle_day or cycle_day < 1 or cycle_day > 35:
            return "Unknown", None
        for phase, data in self.phases.items():
            if cycle_day in data["days"]:
                return phase, data
        return "Unknown", None

    def optimize_tasks(self, cycle_day: int, task_list: list) -> dict:
        phase_name, phase_data = self.get_current_phase(cycle_day)
        if not phase_data:
            return {"error": "Invalid cycle day. Please log your cycle start date."}
        optimized = {
            "current_phase": phase_name,
            "biological_context": phase_data["advice"],
            "highly_recommended": [],
            "do_if_necessary": [],
        }
        for task in task_list:
            if not task.strip():
                continue
            task_lower = task.lower()
            if any(keyword in task_lower for keyword in phase_data["optimal_tasks"]):
                optimized["highly_recommended"].append(task)
            else:
                optimized["do_if_necessary"].append(task)
        return optimized