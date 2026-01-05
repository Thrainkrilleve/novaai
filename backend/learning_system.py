"""
Learning System for Nova - Memory, preferences, and adaptive behavior
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
from pathlib import Path

class LearningSystem:
    """Manages Nova's learning and memory capabilities"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Memory storage
        self.user_profiles = {}  # user_id -> profile data
        self.learned_facts = {}  # user_id -> list of facts
        self.preferences = {}    # user_id -> preferences
        self.interaction_stats = {}  # user_id -> stats
        self.topics_of_interest = {}  # user_id -> topics
        self.conversation_patterns = {}  # user_id -> patterns
        
        # Learning settings
        self.learning_enabled = True
        self.max_facts_per_user = 100
        self.max_topics_per_user = 50
        
        # Load existing data
        self._load_all_data()
    
    def _get_user_file(self, user_id: int) -> Path:
        """Get the file path for a user's data"""
        return self.data_dir / f"user_{user_id}.json"
    
    def _load_all_data(self):
        """Load all user data from disk"""
        for file in self.data_dir.glob("user_*.json"):
            try:
                user_id = int(file.stem.split('_')[1])
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_profiles[user_id] = data.get('profile', {})
                    self.learned_facts[user_id] = data.get('facts', [])
                    self.preferences[user_id] = data.get('preferences', {})
                    self.interaction_stats[user_id] = data.get('stats', {})
                    self.topics_of_interest[user_id] = data.get('topics', {})
                    self.conversation_patterns[user_id] = data.get('patterns', {})
            except Exception as e:
                print(f"⚠️ Error loading user data from {file}: {e}")
    
    def _save_user_data(self, user_id: int):
        """Save a user's data to disk"""
        if not self.learning_enabled:
            return
        
        try:
            data = {
                'profile': self.user_profiles.get(user_id, {}),
                'facts': self.learned_facts.get(user_id, []),
                'preferences': self.preferences.get(user_id, {}),
                'stats': self.interaction_stats.get(user_id, {}),
                'topics': self.topics_of_interest.get(user_id, {}),
                'patterns': self.conversation_patterns.get(user_id, {}),
                'last_updated': datetime.now().isoformat()
            }
            
            file_path = self._get_user_file(user_id)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error saving user data: {e}")
    
    def learn_fact(self, user_id: int, fact: str, category: str = "general"):
        """Learn a new fact about a user"""
        if not self.learning_enabled:
            return False
        
        if user_id not in self.learned_facts:
            self.learned_facts[user_id] = []
        
        # Check if fact already exists
        existing_facts = [f['fact'].lower() for f in self.learned_facts[user_id]]
        if fact.lower() in existing_facts:
            return False
        
        # Add new fact
        fact_entry = {
            'fact': fact,
            'category': category,
            'learned_at': datetime.now().isoformat(),
            'confidence': 1.0
        }
        
        self.learned_facts[user_id].append(fact_entry)
        
        # Limit number of facts
        if len(self.learned_facts[user_id]) > self.max_facts_per_user:
            self.learned_facts[user_id] = self.learned_facts[user_id][-self.max_facts_per_user:]
        
        self._save_user_data(user_id)
        return True
    
    def get_facts(self, user_id: int, category: Optional[str] = None) -> List[str]:
        """Get learned facts about a user"""
        if user_id not in self.learned_facts:
            return []
        
        facts = self.learned_facts[user_id]
        
        if category:
            facts = [f for f in facts if f['category'] == category]
        
        return [f['fact'] for f in facts]
    
    def set_preference(self, user_id: int, key: str, value):
        """Set a user preference"""
        if user_id not in self.preferences:
            self.preferences[user_id] = {}
        
        self.preferences[user_id][key] = value
        self._save_user_data(user_id)
    
    def get_preference(self, user_id: int, key: str, default=None):
        """Get a user preference"""
        if user_id not in self.preferences:
            return default
        
        return self.preferences[user_id].get(key, default)
    
    def track_interaction(self, user_id: int, interaction_type: str):
        """Track an interaction with a user"""
        if user_id not in self.interaction_stats:
            self.interaction_stats[user_id] = {
                'total_messages': 0,
                'first_interaction': datetime.now().isoformat(),
                'last_interaction': datetime.now().isoformat(),
                'interaction_types': {}
            }
        
        stats = self.interaction_stats[user_id]
        stats['total_messages'] += 1
        stats['last_interaction'] = datetime.now().isoformat()
        
        if interaction_type not in stats['interaction_types']:
            stats['interaction_types'][interaction_type] = 0
        stats['interaction_types'][interaction_type] += 1
        
        # Save periodically (every 10 messages)
        if stats['total_messages'] % 10 == 0:
            self._save_user_data(user_id)
    
    def add_topic_interest(self, user_id: int, topic: str, weight: float = 1.0):
        """Track a topic the user is interested in"""
        if user_id not in self.topics_of_interest:
            self.topics_of_interest[user_id] = {}
        
        topic = topic.lower()
        
        if topic in self.topics_of_interest[user_id]:
            # Increase weight (with diminishing returns)
            current = self.topics_of_interest[user_id][topic]
            self.topics_of_interest[user_id][topic] = min(10.0, current + weight * 0.5)
        else:
            self.topics_of_interest[user_id][topic] = weight
        
        # Limit topics
        if len(self.topics_of_interest[user_id]) > self.max_topics_per_user:
            # Remove lowest weighted topics
            sorted_topics = sorted(
                self.topics_of_interest[user_id].items(),
                key=lambda x: x[1],
                reverse=True
            )
            self.topics_of_interest[user_id] = dict(sorted_topics[:self.max_topics_per_user])
        
        self._save_user_data(user_id)
    
    def get_top_topics(self, user_id: int, limit: int = 10) -> List[tuple]:
        """Get user's top topics of interest"""
        if user_id not in self.topics_of_interest:
            return []
        
        topics = self.topics_of_interest[user_id]
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        return sorted_topics[:limit]
    
    def update_profile(self, user_id: int, **kwargs):
        """Update user profile information"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        
        self.user_profiles[user_id].update(kwargs)
        self._save_user_data(user_id)
    
    def get_profile(self, user_id: int) -> Dict:
        """Get user profile"""
        return self.user_profiles.get(user_id, {})
    
    def get_conversation_context(self, user_id: int) -> str:
        """Generate conversation context based on learned information"""
        context_parts = []
        
        # Basic profile info
        profile = self.get_profile(user_id)
        if profile.get('name'):
            context_parts.append(f"User's name: {profile['name']}")
        
        # Learned facts
        facts = self.get_facts(user_id)
        if facts:
            recent_facts = facts[-5:]  # Last 5 facts
            context_parts.append("What I know about them:")
            context_parts.extend([f"- {fact}" for fact in recent_facts])
        
        # Preferences
        prefs = self.preferences.get(user_id, {})
        if prefs:
            pref_str = ", ".join([f"{k}: {v}" for k, v in prefs.items() if k != 'internal'])
            if pref_str:
                context_parts.append(f"Preferences: {pref_str}")
        
        # Topics of interest
        topics = self.get_top_topics(user_id, limit=5)
        if topics:
            topic_str = ", ".join([t[0] for t in topics])
            context_parts.append(f"Interested in: {topic_str}")
        
        # Interaction history
        stats = self.interaction_stats.get(user_id, {})
        if stats.get('total_messages', 0) > 0:
            context_parts.append(f"We've talked {stats['total_messages']} times")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def extract_learnable_info(self, message: str) -> List[tuple]:
        """
        Extract potentially learnable information from a message
        Returns list of (fact, category) tuples
        """
        learnable = []
        message_lower = message.lower()
        
        # Personal facts
        personal_indicators = [
            ("my name is", "name"),
            ("i'm called", "name"),
            ("call me", "name"),
            ("i live in", "location"),
            ("i'm from", "location"),
            ("i work as", "occupation"),
            ("i'm a", "occupation"),
            ("my favorite", "preference"),
            ("i love", "preference"),
            ("i like", "preference"),
            ("i hate", "preference"),
            ("i have", "possession"),
            ("i own", "possession"),
        ]
        
        for indicator, category in personal_indicators:
            if indicator in message_lower:
                # Extract the fact
                start = message_lower.index(indicator) + len(indicator)
                fact_part = message[start:].strip()
                # Take up to first sentence end
                for end_char in ['.', '!', '?', '\n']:
                    if end_char in fact_part:
                        fact_part = fact_part[:fact_part.index(end_char)]
                        break
                
                if len(fact_part) > 2 and len(fact_part) < 100:
                    learnable.append((fact_part.strip(), category))
        
        return learnable
    
    def get_stats_summary(self, user_id: int) -> str:
        """Get a summary of what Nova knows about a user"""
        facts_count = len(self.learned_facts.get(user_id, []))
        prefs_count = len(self.preferences.get(user_id, {}))
        topics_count = len(self.topics_of_interest.get(user_id, {}))
        stats = self.interaction_stats.get(user_id, {})
        
        summary = f"📊 **Learning Profile**\n\n"
        summary += f"**Facts Learned:** {facts_count}\n"
        summary += f"**Preferences:** {prefs_count}\n"
        summary += f"**Topics of Interest:** {topics_count}\n"
        summary += f"**Total Interactions:** {stats.get('total_messages', 0)}\n"
        
        if stats.get('first_interaction'):
            first = datetime.fromisoformat(stats['first_interaction'])
            summary += f"**First Met:** {first.strftime('%Y-%m-%d')}\n"
        
        return summary
    
    def forget_user(self, user_id: int):
        """Forget all learned information about a user"""
        self.user_profiles.pop(user_id, None)
        self.learned_facts.pop(user_id, None)
        self.preferences.pop(user_id, None)
        self.interaction_stats.pop(user_id, None)
        self.topics_of_interest.pop(user_id, None)
        self.conversation_patterns.pop(user_id, None)
        
        # Delete file
        file_path = self._get_user_file(user_id)
        if file_path.exists():
            file_path.unlink()

# Global instance
learning_system = LearningSystem()
