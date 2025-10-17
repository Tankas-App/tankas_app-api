from typing import List

class GamificationSystem:
    POINTS = {
        "report_issue": 10,
        "volunteer": 5,
        "complete_easy": 50,
        "complete_medium": 150,
        "complete_hard": 300,
        "first_to_complete": 50,  # Bonus
        "pledge_reward": 20,
        "comment": 2,
        "verified_gps": 10,  # When GPS matches report location
        "team_complete": 25,  # When multiple volunteers complete together
    }
    
    LEVELS = [
        {"level": 1, "name": "Newbie", "min_points": 0, "badge": "🌱"},
        {"level": 2, "name": "Helper", "min_points": 100, "badge": "🤝"},
        {"level": 3, "name": "Volunteer", "min_points": 500, "badge": "💪"},
        {"level": 4, "name": "Champion", "min_points": 1000, "badge": "🏆"},
        {"level": 5, "name": "Legend", "min_points": 5000, "badge": "⭐"},
        {"level": 6, "name": "Hero", "min_points": 10000, "badge": "🦸"},
    ]
    
    BADGES = {
        "first_reporter": {
            "name": "First Reporter",
            "description": "Reported your first issue",
            "icon": "📝",
            "condition": lambda user: user["tasks_reported"] >= 1
        },
        "team_player": {
            "name": "Team Player",
            "description": "Volunteered for 5+ issues",
            "icon": "👥",
            "condition": lambda user: user.get("volunteer_count", 0) >= 5
        },
        "cleanup_veteran": {
            "name": "Cleanup Veteran",
            "description": "Completed 10+ tasks",
            "icon": "🧹",
            "condition": lambda user: user["tasks_completed"] >= 10
        },
        "generous_supporter": {
            "name": "Generous Supporter",
            "description": "Pledged rewards for 5+ issues",
            "icon": "💝",
            "condition": lambda user: user.get("pledges_made", 0) >= 5
        },
        "gps_master": {
            "name": "GPS Master",
            "description": "All reports with verified GPS",
            "icon": "📍",
            "condition": lambda user: user.get("gps_verified_count", 0) >= 10
        },
        "speed_demon": {
            "name": "Speed Demon",
            "description": "Resolved issue within 24 hours",
            "icon": "⚡",
            "condition": lambda user: user.get("fast_completions", 0) >= 1
        }
    }
    
    @staticmethod
    def calculate_level(points: int) -> dict:
        """Calculate user level based on points"""
        for level in reversed(GamificationSystem.LEVELS):
            if points >= level["min_points"]:
                return level
        return GamificationSystem.LEVELS[0]
    
    @staticmethod
    def get_earned_badges(user: dict) -> List[dict]:
        """Get all badges user has earned"""
        earned = []
        for badge_id, badge in GamificationSystem.BADGES.items():
            if badge["condition"](user):
                earned.append({
                    "id": badge_id,
                    **badge
                })
        return earned