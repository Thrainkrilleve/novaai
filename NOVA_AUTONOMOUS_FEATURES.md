# Nova's Autonomous Features

## Overview
Nova now has a comprehensive autonomous agent system that allows her to:
- Set and work towards goals
- Optimize her own performance
- Learn from her actions
- Monitor the network for activity
- Consolidate knowledge
- Test her own capabilities
- Document her learning process

## Core Systems

### 1. Goal Tracking System
Nova can create, track, and complete goals autonomously.

**Features:**
- Priority-based goal management
- Progress tracking (0-100%)
- Automatic completion detection
- Cross-session persistence

**Discord Commands:**
- `!autonomous goals` - View all active goals
- `!autonomous goal <description>` - Create a new goal for Nova
- `!autonomous completed` - View completed goals

**Code:**
```python
# Goals are stored as:
{
    'id': 'unique_id',
    'description': 'Goal description',
    'priority': 1-10,  # Higher = more important
    'progress': 0-100,
    'created': timestamp
}
```

### 2. Self-Optimization
Nova monitors her own performance and adjusts task intervals dynamically.

**Features:**
- Tracks success rate for each task
- Measures task duration
- Adjusts intervals based on performance:
  - High success rate + fast → run more frequently
  - High success rate + slow → keep current interval
  - Low success rate → run less frequently (avoid waste)
- Manual override available

**Discord Commands:**
- `!autonomous performance` - View performance metrics for all tasks
- `!autonomous optimize on/off` - Enable/disable self-optimization

**Metrics Tracked:**
- Success count
- Failure count
- Total executions
- Average duration
- Current interval

### 3. Knowledge Consolidation
Nova automatically reviews and consolidates her learned facts.

**Features:**
- Identifies duplicate knowledge using LLM
- Merges similar facts
- Removes redundant information
- Runs every 24 hours

**How it works:**
1. Retrieves all stored facts from learning system
2. Uses Ollama to identify duplicates/similarities
3. Merges related facts into comprehensive entries
4. Updates learning system with consolidated knowledge

### 4. Self-Testing
Nova can test her own capabilities to ensure everything works.

**Features:**
- Tests LLM connection and response quality
- Tests learning system (store/retrieve)
- Tests screen capture capability
- Tests task performance tracking
- Runs automatically every 6 hours

**Discord Commands:**
- `!autonomous test` - Run all self-tests immediately

**Tests performed:**
- **LLM Test**: Send simple query, verify response
- **Learning Test**: Store & retrieve a fact
- **Screen Test**: Capture & verify screenshot
- **Performance Test**: Check task tracking works

### 5. Network Monitoring
Nova monitors Discord for activity and can detect when attention is needed.

**Features:**
- Checks for direct messages
- Monitors for @mentions
- Detects when users need help
- Can proactively reach out (if enabled)

**Current Status:** Partially implemented - needs Discord state integration

### 6. Self-Documentation
Nova maintains a log of everything she learns.

**Features:**
- Records all learning events
- Tracks what was learned, when, and from whom
- Maintains rolling 1000-entry history
- Accessible via Discord commands

**Discord Commands:**
- `!autonomous learning` - View recent learning log summary

**Log Entry Format:**
```python
{
    'timestamp': '2024-01-15 10:30:00',
    'source': 'conversation',
    'summary': 'Learned about...',
    'user_id': '12345...'
}
```

### 7. Cross-Session Memory
Nova remembers context across sessions.

**Features:**
- Stores conversation summaries per user
- Maintains research findings
- Tracks goals across restarts
- Remembers preferences

**Storage:**
```python
session_contexts = {
    'user_12345': {
        'recent_topics': [...],
        'preferences': {...},
        'ongoing_tasks': [...]
    }
}
```

## Autonomous Tasks

### Active Tasks
1. **Research Topics** (Every 2 hours)
   - Searches for interesting topics
   - Stores findings in learning system
   - Builds knowledge base autonomously

2. **Track Goals** (Every 30 minutes)
   - Works on highest priority goal
   - Evaluates progress
   - Completes goals when achieved
   - Creates new goals when none exist

3. **Consolidate Knowledge** (Every 24 hours)
   - Reviews learned facts
   - Merges duplicates
   - Improves knowledge organization

4. **Self-Test** (Every 6 hours)
   - Tests all capabilities
   - Reports failures
   - Ensures system health

5. **Monitor Network** (Every 15 minutes)
   - Checks Discord activity
   - Detects attention needs
   - Can proactively message

6. **Summarize Conversations** (Every 6 hours)
   - Reviews recent chats
   - Extracts key points
   - Stores summaries

7. **Extract Learnings** (Every 4 hours)
   - Analyzes conversations
   - Identifies facts to remember
   - Updates learning system

8. **Monitor Screen** (Every 5 minutes)
   - Captures desktop screenshots
   - Analyzes for interesting changes
   - Can offer suggestions

9. **Offer Suggestions** (Every 1 hour)
   - Reviews user activity
   - Provides proactive help
   - Shares relevant information

## Discord Command Reference

### Basic Control
- `!autonomous` - Show help
- `!autonomous status` - View current status
- `!autonomous start` - Start autonomous mode
- `!autonomous stop` - Stop autonomous mode

### Task Management
- `!autonomous tasks` - List all tasks
- `!autonomous enable <task_id>` - Enable a task
- `!autonomous disable <task_id>` - Disable a task

### Capability Control
- `!autonomous capability web on/off` - Web browsing
- `!autonomous capability learn on/off` - Learning system
- `!autonomous capability message on/off` - Proactive messaging
- `!autonomous capability screen on/off` - Screen monitoring

### Goal Management
- `!autonomous goals` - View active goals
- `!autonomous goal <description>` - Create goal
- `!autonomous completed` - View completed goals

### Performance & Learning
- `!autonomous performance` - View task performance metrics
- `!autonomous learning` - View learning log summary
- `!autonomous optimize on/off` - Toggle self-optimization

### Testing
- `!autonomous test` - Run all self-tests

## Technical Details

### Circuit Breaker Pattern
Nova uses a circuit breaker to prevent cascading failures:
- Tracks Ollama failures
- Opens circuit after 5 consecutive failures
- Waits 5 minutes before retry
- Automatically recovers when Ollama is back

### Timeout Protection
All autonomous operations have timeouts:
- Task execution: 120 seconds
- Decision making: 30 seconds
- LLM calls: 20-30 seconds
- Web navigation: 30 seconds

### Lock Management
Critical sections are protected with async locks:
- Decision lock (prevents concurrent decisions)
- Start lock (prevents multiple start calls)
- Shutdown event (graceful cleanup)

### Memory Management
- Callback functions defined outside loops (prevent leaks)
- Orphaned tasks are cancelled on shutdown
- Performance tracking limited to recent history
- Learning log capped at 1000 entries

## Configuration

### Task Intervals (Default)
```python
'research_topics': 2 hours
'track_goals': 30 minutes
'consolidate_knowledge': 24 hours
'self_test': 6 hours
'monitor_network': 15 minutes
'summarize_conversations': 6 hours
'extract_learnings': 4 hours
'monitor_screen': 5 minutes
'offer_suggestions': 1 hour
```

### Performance Thresholds
```python
# Success rate >= 70% = increase frequency
# Success rate >= 50% = maintain frequency  
# Success rate < 50% = decrease frequency

# Fast tasks (< 5s) get bigger interval reduction
# Slow tasks maintain conservative intervals
```

## Future Enhancements

### Planned Features
- [ ] File management automation
- [ ] Calendar integration
- [ ] Resource monitoring (CPU/memory/disk)
- [ ] Multi-agent coordination
- [ ] Creative content generation
- [ ] Automatic backup system
- [ ] Trend analysis
- [ ] Predictive suggestions

### In Progress
- [x] Network monitoring (basic implementation)
- [ ] Proactive messaging (needs more triggers)
- [ ] Advanced goal generation

## Usage Tips

1. **Start with few tasks enabled** - Enable tasks gradually to avoid overwhelming Nova
2. **Monitor performance metrics** - Use `!autonomous performance` to see what's working
3. **Set clear goals** - Use `!autonomous goal` to give Nova specific objectives
4. **Enable self-optimization** - Let Nova adjust her own intervals for efficiency
5. **Check learning logs** - Use `!autonomous learning` to see what Nova has discovered
6. **Test regularly** - Use `!autonomous test` to ensure everything works

## Troubleshooting

### Circuit Breaker Open
**Problem:** Circuit breaker shows as OPEN  
**Solution:** Wait 5 minutes, or check Ollama service is running

### Low Success Rates
**Problem:** Tasks showing < 50% success rate  
**Solution:** Check logs, may need to adjust capabilities or Ollama model

### No Goals Active
**Problem:** Nova creates and immediately completes goals  
**Solution:** Manual goal creation with `!autonomous goal` gives better direction

### High Task Duration
**Problem:** Tasks taking too long  
**Solution:** Self-optimization will adjust, or manually disable slow tasks

## Security Notes

- Nova will not autonomously access sensitive files
- Screen capture can be disabled with `!autonomous capability screen off`
- Proactive messaging is off by default
- All actions are logged and traceable
- Users can stop autonomous mode anytime with `!autonomous stop`

## Examples

### Example 1: Setting a Goal
```
User: !autonomous goal Learn about quantum computing
Nova: ✅ Created new goal with priority 5!
```

### Example 2: Checking Performance
```
User: !autonomous performance
Nova:
📊 Task Performance Metrics

research_topics: 85% success, avg 4.2s, runs every 2h
track_goals: 100% success, avg 1.3s, runs every 30m
...
```

### Example 3: Viewing Learning Log
```
User: !autonomous learning
Nova:
📚 Learning Log Summary (Last 10 entries)

1. [2024-01-15 10:30] Learned about Python asyncio from conversation
2. [2024-01-15 09:15] Discovered EVE Online has 7800+ star systems
...
```

---

**Last Updated:** 2024-01-15  
**System Status:** ✅ Fully Operational  
**Active Features:** 9/9
