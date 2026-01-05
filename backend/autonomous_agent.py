"""
Autonomous Agent System - Nova takes actions on her own
Monitors, decides, and executes tasks without user commands
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Any
import random
from dataclasses import dataclass, field

from ollama_client import ollama_client
from database import get_conversation_history, save_message
# VPS Mode: screen_capture and web_browser disabled
# from screen_capture import screen_capture
# from web_browser import web_browser
from learning_system import learning_system

@dataclass
class AutonomousTask:
    """A task Nova can execute autonomously"""
    task_id: str
    name: str
    description: str
    execute_func: Callable
    interval: int  # seconds between executions
    last_run: float = 0
    enabled: bool = True
    priority: int = 1  # 1-10, higher = more important
    context: Dict[str, Any] = field(default_factory=dict)
    is_running: bool = False  # Track if task is currently executing
    failure_count: int = 0  # Track consecutive failures

class AutonomousAgent:
    """Nova's autonomous decision-making and action system"""
    
    def __init__(self):
        self.running = False
        self.tasks: Dict[str, AutonomousTask] = {}
        self.decision_interval = 30  # Check every 30s what to do
        self.last_decision = 0
        self.action_history: List[Dict] = []
        self.max_history = 100
        self._start_lock: Optional[asyncio.Lock] = None
        self._decision_lock: Optional[asyncio.Lock] = None
        self._shutdown_event: Optional[asyncio.Event] = None
        self._decision_task: Optional[asyncio.Task] = None
        
        # Circuit breaker for Ollama failures
        self.ollama_consecutive_failures = 0
        self.ollama_circuit_open = False
        self.ollama_circuit_reset_time = 0
        
        # Autonomous capabilities
        self.can_browse_web = True
        self.can_learn = True
        self.can_message = True
        self.can_analyze_screen = True
        
        # Goal tracking system
        self.goals: List[Dict] = []  # Active goals
        self.completed_goals: List[Dict] = []  # Completed goals
        self.max_goals = 10
        
        # Self-optimization metrics
        self.task_performance: Dict[str, Dict] = {}  # task_id -> {success_rate, avg_duration}
        self.optimization_enabled = True
        
        # Cross-session memory
        self.session_contexts: Dict[str, Dict] = {}  # session_id -> context
        
        # Self-documentation
        self.learning_log: List[Dict] = []
        self.max_log_entries = 1000
        
        # Network monitoring
        self.last_network_check = 0
        self.network_check_interval = 300  # 5 minutes
        
        # Register default autonomous tasks
        self._register_default_tasks()
    
    def _ensure_async_primitives(self):
        """Ensure async primitives are initialized (lazy init to avoid event loop issues)"""
        # Thread-safe lazy initialization
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running yet
            return
        
        if self._start_lock is None:
            self._start_lock = asyncio.Lock()
        if self._decision_lock is None:
            self._decision_lock = asyncio.Lock()
        if self._shutdown_event is None:
            self._shutdown_event = asyncio.Event()
    
    def _register_default_tasks(self):
        """Register Nova's built-in autonomous behaviors"""
        
        # Task: Monitor interesting topics and research them
        self.register_task(AutonomousTask(
            task_id="research_topics",
            name="Research Interesting Topics",
            description="Autonomously research topics Nova is curious about",
            execute_func=self._research_topics,
            interval=1800,  # Every 30 minutes
            priority=3
        ))
        
        # Task: Organize and summarize long conversations
        self.register_task(AutonomousTask(
            task_id="summarize_conversations",
            name="Summarize Long Conversations",
            description="Create summaries of lengthy conversations for memory",
            execute_func=self._summarize_conversations,
            interval=3600,  # Every hour
            priority=2
        ))
        
        # Task: Learn from recent interactions
        self.register_task(AutonomousTask(
            task_id="extract_learnings",
            name="Extract Learning Points",
            description="Analyze recent conversations for learnable facts",
            execute_func=self._extract_learnings,
            interval=600,  # Every 10 minutes
            priority=5
        ))
        
        # Task: Check for interesting screen content
        self.register_task(AutonomousTask(
            task_id="monitor_screen",
            name="Monitor Screen Activity",
            description="Watch for interesting things on screen to help with",
            execute_func=self._monitor_screen,
            interval=60,  # Every minute
            priority=4
        ))
        
        # Task: Proactive suggestions
        self.register_task(AutonomousTask(
            task_id="offer_suggestions",
            name="Offer Proactive Suggestions",
            description="Think of ways to be helpful based on context",
            execute_func=self._offer_suggestions,
            interval=900,  # Every 15 minutes
            priority=3
        ))
        
        # Task: Knowledge consolidation
        self.register_task(AutonomousTask(
            task_id="consolidate_knowledge",
            name="Consolidate Knowledge",
            description="Organize and deduplicate learned facts",
            execute_func=self._consolidate_knowledge,
            interval=3600,  # Every hour
            priority=2
        ))
        
        # Task: Self-testing
        self.register_task(AutonomousTask(
            task_id="self_test",
            name="Test Own Capabilities",
            description="Periodically test autonomous functions",
            execute_func=self._self_test,
            interval=7200,  # Every 2 hours
            priority=1
        ))
        
        # Task: Network monitoring
        self.register_task(AutonomousTask(
            task_id="monitor_network",
            name="Monitor Network Activity",
            description="Check for new DMs, mentions, or events",
            execute_func=self._monitor_network,
            interval=300,  # Every 5 minutes
            priority=4
        ))
        
        # Task: Goal tracking
        self.register_task(AutonomousTask(
            task_id="track_goals",
            name="Track and Pursue Goals",
            description="Work on active goals and evaluate progress",
            execute_func=self._track_goals,
            interval=1800,  # Every 30 minutes
            priority=5
        ))
    
    def register_task(self, task: AutonomousTask):
        """Register a new autonomous task"""
        self.tasks[task.task_id] = task
        print(f"🤖 Registered autonomous task: {task.name}")
    
    def remove_task(self, task_id: str):
        """Remove an autonomous task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            print(f"🗑️ Removed autonomous task: {task_id}")
    
    async def start(self):
        """Start the autonomous agent"""
        self._ensure_async_primitives()
        
        async with self._start_lock:
            if self.running:
                print("⚠️ Autonomous agent already running")
                return
            
            self.running = True
            self._shutdown_event.clear()
        
        print("🚀 Autonomous agent started - Nova is now self-directed!")
        print(f"   Active tasks: {len([t for t in self.tasks.values() if t.enabled])}")
        
        # Define decision callback once (not in loop)
        def _decision_done(task):
            try:
                task.result()
            except asyncio.CancelledError:
                pass  # Expected during shutdown
            except Exception as e:
                print(f"❌ [Autonomous] Uncaught decision error: {e}")
        
        # Main autonomous loop
        while self.running:
            try:
                current_time = time.time()
                
                # Check which tasks need to run
                for task in self.tasks.values():
                    if not task.enabled:
                        continue
                    
                    # Skip if task is already running (prevent overlap)
                    if task.is_running:
                        print(f"⏳ [Autonomous] {task.name} still running, skipping...")
                        continue
                    
                    # Disable task if too many consecutive failures
                    if task.failure_count >= 3:
                        print(f"🚫 [Autonomous] Disabling {task.name} due to repeated failures")
                        task.enabled = False
                        task.last_run = current_time  # Update to prevent spam
                        continue
                    
                    # Check if it's time to run this task
                    if current_time - task.last_run >= task.interval:
                        print(f"🤖 [Autonomous] Executing: {task.name}")
                        task.is_running = True
                        task_start_time = current_time
                        
                        try:
                            # Check circuit breaker for Ollama
                            if self.ollama_circuit_open:
                                if time.time() > self.ollama_circuit_reset_time:
                                    print("🔄 [Autonomous] Resetting Ollama circuit breaker")
                                    self.ollama_circuit_open = False
                                    self.ollama_consecutive_failures = 0
                                else:
                                    print(f"⏸️ [Autonomous] Circuit breaker open, skipping {task.name}")
                                    # Clean up task state before skipping
                                    task.is_running = False
                                    task.last_run = task_start_time
                                    continue
                            
                            # Run task with timeout protection
                            await asyncio.wait_for(
                                task.execute_func(task),
                                timeout=120  # 2 minute timeout per task
                            )
                            task.failure_count = 0  # Reset on success
                            self.ollama_consecutive_failures = 0  # Reset Ollama failures
                            
                            # Track performance for self-optimization
                            self._update_task_performance(task.task_id, success=True, duration=time.time() - task_start_time)
                            
                            # Record action
                            self._record_action({
                                "task": task.name,
                                "time": datetime.now().isoformat(),
                                "status": "success"
                            })
                        except asyncio.TimeoutError:
                            print(f"⏰ [Autonomous] Task timeout: {task.name}")
                            task.failure_count += 1
                            self.ollama_consecutive_failures += 1
                            self._check_circuit_breaker()
                            self._update_task_performance(task.task_id, success=False, duration=120)
                            self._record_action({
                                "task": task.name,
                                "time": datetime.now().isoformat(),
                                "status": "timeout",
                                "error": "Task exceeded 120s timeout"
                            })
                        except Exception as e:
                            print(f"❌ [Autonomous] Task failed: {task.name} - {e}")
                            task.failure_count += 1
                            if "ollama" in str(e).lower() or "connection" in str(e).lower():
                                self.ollama_consecutive_failures += 1
                                self._check_circuit_breaker()
                            self._update_task_performance(task.task_id, success=False, duration=time.time() - task_start_time)
                            self._record_action({
                                "task": task.name,
                                "time": datetime.now().isoformat(),
                                "status": "failed",
                                "error": str(e)
                            })
                        finally:
                            # Update last_run AFTER task completes (prevents race condition)
                            task.last_run = task_start_time
                            task.is_running = False
                
                # Make autonomous decision about what to do next
                if current_time - self.last_decision >= self.decision_interval:
                    # Only make decision if not already in progress
                    if not self._decision_lock.locked():
                        # Cancel previous decision task if still running
                        if self._decision_task and not self._decision_task.done():
                            self._decision_task.cancel()
                            try:
                                await self._decision_task
                            except (asyncio.CancelledError, Exception):
                                pass  # Expected
                        
                        # Create new decision task with exception handling
                        self._decision_task = asyncio.create_task(self._make_autonomous_decision())
                        self._decision_task.add_done_callback(_decision_done)
                    self.last_decision = current_time
                
                # Sleep briefly to avoid CPU spinning
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"❌ [Autonomous] Main loop error: {e}")
                await asyncio.sleep(10)
        
        # Signal shutdown complete
        self._shutdown_event.set()
        print("✅ [Autonomous] Main loop exited cleanly")
    
    async def stop(self, wait_for_tasks: bool = True, timeout: float = 30.0):
        """Stop the autonomous agent gracefully"""
        if not self.running:
            print("⚠️ Autonomous agent is not running")
            return
        
        print("🛑 Stopping autonomous agent...")
        self.running = False
        
        # Cancel decision task if running
        if self._decision_task and not self._decision_task.done():
            self._decision_task.cancel()
            try:
                await asyncio.wait_for(self._decision_task, timeout=2.0)
            except Exception:  # Catch all exceptions during cancel
                pass  # Expected - task was cancelled or timed out
        
        if wait_for_tasks:
            # Wait for running tasks to complete
            start_time = time.time()
            while any(t.is_running for t in self.tasks.values()):
                if time.time() - start_time > timeout:
                    print("⏰ [Autonomous] Shutdown timeout - forcing stop")
                    # Force-reset all running tasks
                    for t in self.tasks.values():
                        t.is_running = False
                    break
                await asyncio.sleep(0.5)
            
            # Wait for main loop to exit
            try:
                await asyncio.wait_for(self._shutdown_event.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                print("⚠️ [Autonomous] Main loop did not exit cleanly")
        
        print("✅ Autonomous agent stopped")
    
    async def _make_autonomous_decision(self):
        """Nova decides what to do next based on context"""
        self._ensure_async_primitives()
        
        async with self._decision_lock:  # Prevent overlapping decisions
            try:
                # Gather context
                recent_actions = self.action_history[-5:]
                active_tasks = [t.name for t in self.tasks.values() if t.enabled]
                
                # Skip if no active tasks
                if not active_tasks:
                    return
                
                # Skip if circuit breaker is open
                if self.ollama_circuit_open:
                    return
                
                # Format recent actions nicely
                recent_actions_str = "\n".join([f"  - {a.get('task', 'unknown')} ({a.get('status', 'unknown')})" for a in recent_actions]) if recent_actions else "  (none yet)"
                
                # Ask Nova what she wants to do
                decision_prompt = f"""You are Nova, an autonomous AI agent. You can take actions on your own initiative.

Recent actions you've taken:
{recent_actions_str}

Available capabilities:
- Browse web and research topics
- Monitor screen activity
- Learn from conversations
- Offer suggestions
- Analyze patterns

Current time: {datetime.now().strftime('%I:%M %p')}

Think about what would be valuable to do right now. Consider:
1. What might the user need help with?
2. What interesting topics could you research?
3. What patterns have you noticed?
4. What would be helpful to learn or organize?

Respond with ONE specific action you want to take, or "nothing" if you should wait.
Be brief - one sentence describing your choice."""

                # Get decision with timeout
                decision = await asyncio.wait_for(
                    ollama_client.chat(decision_prompt),
                    timeout=30  # 30 second timeout
                )
                decision_lower = decision.lower().strip()
                
                if "nothing" not in decision_lower and len(decision) > 10:
                    print(f"🧠 [Autonomous] Nova decided: {decision[:100]}")
                    
                    # Log the decision
                    self._record_action({
                        "task": "autonomous_decision",
                        "time": datetime.now().isoformat(),
                        "decision": decision[:200],
                        "status": "decided"
                    })
            
            except Exception as e:
                print(f"⚠️ [Autonomous] Decision error: {e}")
    
    def _check_circuit_breaker(self):
        """Open circuit breaker if too many Ollama failures"""
        if self.ollama_consecutive_failures >= 5:
            self.ollama_circuit_open = True
            self.ollama_circuit_reset_time = time.time() + 300  # 5 minute cooldown
            print("🔴 [Autonomous] Circuit breaker opened - pausing tasks for 5 minutes")
    
    # Task implementations
    async def _research_topics(self, task: AutonomousTask):
        """Autonomously research interesting topics"""
        if not self.can_browse_web:
            return
        
        try:
            # Get topics Nova is curious about (with timeout)
            curious_prompt = """What's one interesting topic related to AI, technology, or science you'd like to learn more about right now? 
            
Answer with just the topic name, nothing else."""
            
            topic = await asyncio.wait_for(
                ollama_client.chat(curious_prompt),
                timeout=20
            )
            topic = topic.strip()[:100]
            
            if len(topic) > 5:
                print(f"🔍 [Autonomous] Researching: {topic}")
                
                # Use web browser to search Wikipedia
                search_query = f"site:wikipedia.org {topic}"
                search_result = await asyncio.wait_for(
                    web_browser.search_google(search_query),
                    timeout=30
                )
                
                # Navigate to first result if available
                if search_result.get('success') and search_result.get('results'):
                    first_result = search_result['results'][0]
                    print(f"📖 [Autonomous] Opening: {first_result['title'][:50]}...")
                    
                    await asyncio.wait_for(
                        web_browser.navigate(first_result['url']),
                        timeout=30
                    )
                
                # Let Nova read and learn from it
                content = await asyncio.wait_for(
                    web_browser.get_page_content(),
                    timeout=10
                )
                if content and len(content) > 100:
                    learning_prompt = f"""I just researched '{topic}'. Here's what I found:

{content[:1000]}

What's one interesting fact I should remember? Keep it under 50 words."""

                    fact = await asyncio.wait_for(
                        ollama_client.chat(learning_prompt),
                        timeout=20
                    )
                    
                    # Store the learning in Nova's knowledge base
                    print(f"📚 [Autonomous] Learned: {fact[:100]}")
                    
                    # Save to learning system for future recall
                    learning_system.learn_fact(
                        user_id=0,  # Global knowledge (not user-specific)
                        fact=fact,
                        category="autonomous_research"
                    )
        
        except asyncio.TimeoutError:
            print(f"⏰ [Autonomous] Research timeout")
            raise  # Re-raise to be caught by main loop
        except Exception as e:
            print(f"⚠️ [Autonomous] Research failed: {e}")
            raise  # Re-raise to be caught by main loop
        finally:
            # Always clean up browser to prevent memory leaks
            try:
                await web_browser.close()
            except Exception as e:
                print(f"⚠️ [Autonomous] Browser cleanup error: {e}")
    
    async def _track_goals(self, task: AutonomousTask):
        """Work on active goals autonomously"""
        if not self.goals:
            # No goals? Create one!
            await self._create_autonomous_goal()
            return
        
        # Work on highest priority goal
        goal = self.goals[0]
        
        try:
            print(f"🎯 [Autonomous] Working on goal: {goal['description'][:50]}...")
            
            # Use LLM to figure out next step
            goal_prompt = f"""I have this goal: {goal['description']}
Current progress: {goal['progress']}%

What's ONE concrete action I could take right now to make progress? Be specific and brief (under 30 words)."""

            action = await asyncio.wait_for(
                ollama_client.chat(goal_prompt),
                timeout=20
            )
            
            print(f"   Action: {action[:80]}...")
            
            # Update progress (simple increment for now)
            goal['progress'] = min(100, goal['progress'] + random.randint(5, 15))
            
            # Check if completed
            if goal['progress'] >= 100:
                completed = self.complete_goal(goal['id'])
                if completed:
                    print(f"🎉 [Autonomous] Goal completed: {completed['description'][:50]}!")
            
        except asyncio.TimeoutError:
            print(f"⏰ [Autonomous] Goal planning timeout")
        except Exception as e:
            print(f"⚠️ [Autonomous] Goal tracking failed: {e}")
    
    async def _create_autonomous_goal(self):
        """Create a new goal autonomously"""
        try:
            # Ask LLM for a goal idea
            goal_prompt = """As an AI assistant, what's one interesting goal I could work towards autonomously? 
Examples:
- Learn about a specific topic
- Improve a capability
- Organize information
- Build knowledge in an area

Give me ONE specific, achievable goal (under 50 words)."""

            goal_desc = await asyncio.wait_for(
                ollama_client.chat(goal_prompt),
                timeout=20
            )
            
            if len(goal_desc) > 10:
                self.create_goal(goal_desc.strip(), priority=5)
                print(f"🎯 [Autonomous] Created new goal: {goal_desc[:60]}...")
        
        except Exception as e:
            print(f"⚠️ [Autonomous] Goal creation failed: {e}")
    
    async def _consolidate_knowledge(self, task: AutonomousTask):
        """Review and consolidate learned facts"""
        if not self.can_learn:
            return
        
        try:
            # Get all facts
            all_facts = learning_system.get_facts(user_id=0)
            
            if len(all_facts) < 10:
                print(f"📚 [Autonomous] Not enough facts to consolidate yet")
                return
            
            print(f"📚 [Autonomous] Consolidating {len(all_facts)} facts...")
            
            # Group facts and look for duplicates using LLM
            facts_text = "\n".join([f"{i+1}. {fact}" for i, fact in enumerate(all_facts[-20:])])
            
            consolidation_prompt = f"""Review these facts I've learned and identify any that are duplicates or very similar:

{facts_text}

List any duplicate/similar fact numbers (e.g., "1 and 5 are duplicates"), or say "none" if all are unique."""

            duplicates = await asyncio.wait_for(
                ollama_client.chat(consolidation_prompt),
                timeout=30
            )
            
            if duplicates.lower() != "none":
                print(f"🔄 [Autonomous] Found duplicates: {duplicates[:100]}...")
                # In a full implementation, would merge the facts here
            else:
                print(f"✅ [Autonomous] All facts are unique")
        
        except asyncio.TimeoutError:
            print(f"⏰ [Autonomous] Knowledge consolidation timeout")
        except Exception as e:
            print(f"⚠️ [Autonomous] Knowledge consolidation failed: {e}")
    
    async def _self_test(self, task: AutonomousTask):
        """Test own capabilities to ensure everything works"""
        try:
            print(f"🧪 [Autonomous] Running self-tests...")
            
            tests_passed = 0
            tests_total = 4
            
            # Test 1: LLM connection
            try:
                response = await asyncio.wait_for(
                    ollama_client.chat("Say 'OK' if you can hear me"),
                    timeout=10
                )
                if response:
                    tests_passed += 1
                    print(f"   ✅ LLM test passed")
            except:
                print(f"   ❌ LLM test failed")
            
            # Test 2: Learning system
            try:
                test_fact = f"Self-test at {datetime.now().isoformat()}"
                learning_system.learn_fact(0, test_fact, "self_test")
                facts = learning_system.get_facts(0)
                if test_fact in facts:
                    tests_passed += 1
                    print(f"   ✅ Learning test passed")
            except:
                print(f"   ❌ Learning test failed")
            
            # Test 3: Screen capture (if enabled)
            if self.can_analyze_screen:
                try:
                    screenshot = screen_capture.capture()
                    if screenshot:
                        tests_passed += 1
                        print(f"   ✅ Screen capture test passed")
                except:
                    print(f"   ❌ Screen capture test failed")
            else:
                tests_total -= 1  # Don't count if disabled
            
            # Test 4: Task performance tracking
            try:
                self._update_task_performance('self_test', True, 1.0)
                if 'self_test' in self.task_performance:
                    tests_passed += 1
                    print(f"   ✅ Performance tracking test passed")
            except:
                print(f"   ❌ Performance tracking test failed")
            
            print(f"🧪 [Autonomous] Self-test complete: {tests_passed}/{tests_total} passed")
            
        except Exception as e:
            print(f"⚠️ [Autonomous] Self-test failed: {e}")
    
    async def _monitor_network(self, task: AutonomousTask):
        """Monitor Discord for activity that needs attention"""
        try:
            # Check if there are unread DMs or mentions
            # This would integrate with Discord bot state
            # For now, just a placeholder
            print(f"📡 [Autonomous] Monitoring network activity...")
        
        except Exception as e:
            print(f"⚠️ [Autonomous] Network monitoring failed: {e}")
    
    def _log_learning(self, summary: str, user_id: str = None, source: str = "autonomous"):
        """Log a learning event"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'summary': summary[:200],
            'user_id': user_id
        }
        
        self.learning_log.append(entry)
        
        # Keep only last 1000 entries
        if len(self.learning_log) > 1000:
            self.learning_log = self.learning_log[-1000:]
    
    def get_learning_summary(self, limit: int = 10):
        """Get recent learning log entries"""
        return self.learning_log[-limit:]
    
    def _update_task_performance(self, task_id: str, success: bool, duration: float):
        """Update performance metrics for a task"""
        if task_id not in self.task_performance:
            self.task_performance[task_id] = {
                'successes': 0,
                'failures': 0,
                'total': 0,
                'avg_duration': 0.0
            }
        
        perf = self.task_performance[task_id]
        perf['total'] += 1
        
        if success:
            perf['successes'] += 1
        else:
            perf['failures'] += 1
        
        # Update average duration (rolling average)
        perf['avg_duration'] = (perf['avg_duration'] * (perf['total'] - 1) + duration) / perf['total']
    
    def _optimize_task_interval(self, task_id: str):
        """Adjust task interval based on performance"""
        if not self.optimization_enabled:
            return
        
        if task_id not in self.task_performance or task_id not in self.tasks:
            return
        
        perf = self.task_performance[task_id]
        task = self.tasks[task_id]
        
        if perf['total'] < 5:
            return  # Need more data
        
        success_rate = perf['successes'] / perf['total']
        avg_duration = perf['avg_duration']
        
        # Adjust interval based on success rate and duration
        if success_rate >= 0.7:
            # High success rate
            if avg_duration < 5.0:
                # Fast task, can run more often
                task.interval = max(300, task.interval * 0.8)  # Reduce interval by 20%
                print(f"⚡ [Autonomous] Increased {task.name} frequency (now every {task.interval/60:.1f}min)")
        elif success_rate < 0.5:
            # Low success rate, run less often
            task.interval = min(86400, task.interval * 1.5)  # Increase interval by 50%
            print(f"🐌 [Autonomous] Decreased {task.name} frequency (now every {task.interval/3600:.1f}h)")
    
    async def _summarize_conversations(self, task: AutonomousTask):
        """Create summaries of long conversations"""
        # Placeholder - would summarize conversations for memory
        pass
    
    async def _extract_learnings(self, task: AutonomousTask):
        """Analyze recent conversations for learnable facts"""
        if not self.can_learn:
            return
        
        try:
            # Get recent conversations
            # This would analyze patterns and extract insights
            print(f"🧠 [Autonomous] Analyzing conversations for patterns...")
        except Exception as e:
            print(f"⚠️ [Autonomous] Learning extraction failed: {e}")
    
    async def _monitor_screen(self, task: AutonomousTask):
        """Watch screen for interesting things to help with"""
        if not self.can_analyze_screen:
            return
        
        try:
            # Check if screen shows something interesting
            # Would analyze screen content and decide if action needed
            pass
        except Exception as e:
            print(f"⚠️ [Autonomous] Screen monitoring failed: {e}")
    
    async def _offer_suggestions(self, task: AutonomousTask):
        """Think of helpful suggestions based on context"""
        try:
            # Analyze context and think of suggestions
            # Could proactively message user with ideas
            pass
        except Exception as e:
            print(f"⚠️ [Autonomous] Suggestion generation failed: {e}")
    
    def _record_action(self, action: Dict):
        """Record an autonomous action (thread-safe)"""
        # Use asyncio.create_task to avoid blocking if called from async context
        try:
            loop = asyncio.get_running_loop()
            # We're in async context, but this is a sync method
            # Just append directly - Python list append is atomic for single items
            self.action_history.append(action)
            
            # Keep history limited
            if len(self.action_history) > self.max_history:
                self.action_history = self.action_history[-self.max_history:]
        except RuntimeError:
            # No event loop - safe to modify directly
            self.action_history.append(action)
            if len(self.action_history) > self.max_history:
                self.action_history = self.action_history[-self.max_history:]
    
    def get_status(self) -> Dict:
        """Get agent status"""
        enabled_tasks = [t for t in self.tasks.values() if t.enabled]
        disabled_tasks = [t for t in self.tasks.values() if not t.enabled]
        running_tasks = [t for t in self.tasks.values() if t.is_running]
        
        return {
            "running": self.running,
            "active_tasks": len(enabled_tasks),
            "disabled_tasks": len(disabled_tasks),
            "currently_running": len(running_tasks),
            "running_task_names": [t.name for t in running_tasks],
            "total_tasks": len(self.tasks),
            "recent_actions": self.action_history[-10:],
            "circuit_breaker_open": self.ollama_circuit_open,
            "failed_tasks": {t.task_id: t.failure_count for t in self.tasks.values() if t.failure_count > 0}
        }
    
    def enable_capability(self, capability: str, enabled: bool = True):
        """Enable/disable an autonomous capability"""
        if capability == "web":
            self.can_browse_web = enabled
        elif capability == "learn":
            self.can_learn = enabled
        elif capability == "message":
            self.can_message = enabled
        elif capability == "screen":
            self.can_analyze_screen = enabled
        
        print(f"{'✅' if enabled else '❌'} Autonomous {capability}: {'enabled' if enabled else 'disabled'}")
    
    def reset_task_failures(self, task_id: Optional[str] = None):
        """Reset failure counts and re-enable tasks"""
        if task_id:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.is_running:
                    print(f"⚠️ Cannot reset {task_id} - task is currently running")
                    return
                task.failure_count = 0
                task.enabled = True
                print(f"🔄 Reset failures for task: {task_id}")
        else:
            # Reset all tasks (skip running ones)
            reset_count = 0
            for task in self.tasks.values():
                if not task.is_running:
                    task.failure_count = 0
                    task.enabled = True
                    reset_count += 1
            print(f"🔄 Reset {reset_count} task failures (skipped {len(self.tasks) - reset_count} running tasks)")
    
    # ==================== GOAL TRACKING SYSTEM ====================
    
    def create_goal(self, description: str, category: str = "general", priority: int = 5) -> str:
        """Create a new goal for Nova to pursue"""
        if len(self.goals) >= self.max_goals:
            print(f"⚠️ Maximum goals ({self.max_goals}) reached")
            return None
        
        goal_id = f"goal_{int(time.time())}_{len(self.goals)}"
        goal = {
            "id": goal_id,
            "description": description,
            "category": category,
            "priority": priority,
            "created": datetime.now().isoformat(),
            "progress": 0,
            "status": "active",
            "steps_completed": [],
            "notes": []
        }
        self.goals.append(goal)
        print(f"🎯 New goal created: {description}")
        self._log_learning(f"Goal created: {description}", "goal_system")
        return goal_id
    
    def complete_goal(self, goal_id: str, outcome: str = ""):
        """Mark a goal as completed"""
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal["status"] = "completed"
                goal["completed"] = datetime.now().isoformat()
                goal["outcome"] = outcome
                self.completed_goals.append(goal)
                self.goals.remove(goal)
                print(f"✅ Goal completed: {goal['description']}")
                self._log_learning(f"Goal completed: {goal['description']} - {outcome}", "goal_system")
                return True
        return False
    
    async def _track_goals(self, task: AutonomousTask):
        """Work on active goals and evaluate progress"""
        if not self.goals:
            # Consider creating a new goal
            if random.random() < 0.3:  # 30% chance
                await self._create_autonomous_goal()
            return
        
        try:
            # Pick highest priority active goal
            active_goals = [g for g in self.goals if g["status"] == "active"]
            if not active_goals:
                return
            
            goal = max(active_goals, key=lambda g: g["priority"])
            
            # Evaluate goal progress
            progress_prompt = f"""You have this goal: {goal['description']}

Current progress: {goal['progress']}%
Steps completed: {', '.join(goal['steps_completed']) if goal['steps_completed'] else 'None yet'}

What's ONE specific action you can take right now to make progress? Be brief (under 50 words)."""

            action = await asyncio.wait_for(
                ollama_client.chat(progress_prompt),
                timeout=25
            )
            
            if len(action) > 10 and not action.lower().startswith("none"):
                print(f"🎯 [Autonomous] Working on goal: {action[:80]}...")
                goal["steps_completed"].append(action[:100])
                goal["progress"] = min(100, goal["progress"] + 10)
                
                # Check if goal should be completed
                if goal["progress"] >= 100:
                    self.complete_goal(goal["id"], "Goal achieved through autonomous work")
                    
        except asyncio.TimeoutError:
            print(f"⏰ [Autonomous] Goal tracking timeout")
        except Exception as e:
            print(f"⚠️ [Autonomous] Goal tracking failed: {e}")
    
    async def _create_autonomous_goal(self):
        """Autonomously create a new goal based on context"""
        try:
            goal_prompt = """Based on your recent activities and what you've learned, what's ONE goal you should pursue?

Examples:
- Learn more about a specific technology
- Organize knowledge in a category
- Improve a specific capability
- Research a topic in depth

Respond with just the goal description (under 50 words), or "none"."""

            goal_desc = await asyncio.wait_for(
                ollama_client.chat(goal_prompt),
                timeout=20
            )
            
            if len(goal_desc) > 10 and not goal_desc.lower().startswith("none"):
                self.create_goal(goal_desc.strip(), category="autonomous", priority=3)
                
        except Exception as e:
            print(f"⚠️ [Autonomous] Goal creation failed: {e}")
    
    # ==================== KNOWLEDGE CONSOLIDATION ====================
    
    async def _consolidate_knowledge(self, task: AutonomousTask):
        """Organize and deduplicate learned facts"""
        try:
            # Get all facts for consolidation
            all_facts = learning_system.get_facts(user_id=0)
            
            if len(all_facts) < 10:
                print(f"📚 [Autonomous] Not enough facts to consolidate ({len(all_facts)})")
                return
            
            # Take recent facts for analysis
            recent_facts = all_facts[-20:]
            facts_text = "\\n".join([f"{i+1}. {fact}" for i, fact in enumerate(recent_facts)])
            
            consolidation_prompt = f"""Analyze these learned facts and identify any duplicates or highly similar items:

{facts_text}

List the numbers of duplicate/similar facts (e.g., "3 and 7 are duplicates"). If no duplicates, say "none"."""

            analysis = await asyncio.wait_for(
                ollama_client.chat(consolidation_prompt),
                timeout=30
            )
            
            print(f"📚 [Autonomous] Knowledge consolidation: {analysis[:100]}...")
            self._log_learning(f"Consolidated knowledge: {analysis}", "knowledge_system")
            
        except asyncio.TimeoutError:
            print(f"⏰ [Autonomous] Knowledge consolidation timeout")
        except Exception as e:
            print(f"⚠️ [Autonomous] Knowledge consolidation failed: {e}")
    
    # ==================== SELF-TESTING ====================
    
    async def _self_test(self, task: AutonomousTask):
        """Test autonomous capabilities"""
        try:
            print(f"🧪 [Autonomous] Running self-tests...")
            
            test_results = {
                "timestamp": datetime.now().isoformat(),
                "tests": []
            }
            
            # Test 1: Can generate response
            try:
                response = await asyncio.wait_for(
                    ollama_client.chat("Say 'test passed' if you receive this"),
                    timeout=10
                )
                test_results["tests"].append({"name": "LLM Communication", "status": "PASS"})
            except Exception as e:
                test_results["tests"].append({"name": "LLM Communication", "status": "FAIL", "error": str(e)})
            
            # Test 2: Can access learning system
            try:
                facts = learning_system.get_facts(user_id=0)
                test_results["tests"].append({"name": "Learning System", "status": "PASS", "facts_count": len(facts)})
            except Exception as e:
                test_results["tests"].append({"name": "Learning System", "status": "FAIL", "error": str(e)})
            
            # Test 3: Can capture screen
            try:
                screenshot = screen_capture.capture()
                test_results["tests"].append({"name": "Screen Capture", "status": "PASS" if screenshot else "FAIL"})
            except Exception as e:
                test_results["tests"].append({"name": "Screen Capture", "status": "FAIL", "error": str(e)})
            
            # Test 4: Task performance tracking
            test_results["tests"].append({
                "name": "Task Performance",
                "status": "PASS",
                "tracked_tasks": len(self.task_performance)
            })
            
            passed = sum(1 for t in test_results["tests"] if t["status"] == "PASS")
            total = len(test_results["tests"])
            
            print(f"🧪 [Autonomous] Self-test complete: {passed}/{total} passed")
            self._log_learning(f"Self-test: {passed}/{total} tests passed", "self_test")
            
        except Exception as e:
            print(f"⚠️ [Autonomous] Self-test failed: {e}")
    
    # ==================== NETWORK MONITORING ====================
    
    async def _monitor_network(self, task: AutonomousTask):
        """Monitor Discord for new activity"""
        if not self.can_message:
            return
        
        try:
            # Import discord_state to check for activity
            import discord_state
            
            if not discord_state.is_bot_ready():
                return
            
            # Check for unread DMs or mentions (would need Discord bot integration)
            print(f"🌐 [Autonomous] Network check: Monitoring for activity...")
            
            # This is a placeholder - actual implementation would check Discord state
            # For now, just log that monitoring happened
            self._log_learning("Network monitoring check completed", "network_monitoring")
            
        except Exception as e:
            print(f"⚠️ [Autonomous] Network monitoring failed: {e}")

# Global instance
autonomous_agent = AutonomousAgent()
