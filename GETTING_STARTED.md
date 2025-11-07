# Getting Started - Task Assignment Guide

## Quick Navigation
- New here? Start with [Project Summary](PROJECT_SUMMARY.md)
- Ready to work? Read this guide
- Need details? See [Task Breakdown](TASK_BREAKDOWN.md)
- Coding? Check [AI Agent Guide](AI_AGENT_GUIDE.md)

---

## For Project Managers

### Initial Setup
1. ✅ Documentation is complete and ready
2. ✅ 20 tasks identified and categorized
3. ✅ Dependencies mapped
4. ⏳ Ready to assign tasks to AI agents

### Assignment Workflow

#### Step 1: Choose Tasks to Assign
Start with **Category 1 (Refactoring)** - these are foundation tasks:
- ✅ Task 1.1: Hardware Layer (READY - has detailed spec)
- Task 1.2: File System
- Task 1.3: Math Engine
- Task 1.5: App State

**Why start here?**
- No dependencies on other tasks
- Can be done in parallel
- Create foundation for all other work
- Reduce main file from 2,395 to ~1,000 lines

#### Step 2: Create Task Assignment
For each task:
1. Read the task file (e.g., `tasks/TASK_1.1_Hardware_Layer.md`)
2. Create a GitHub issue or assignment
3. Include:
   - Link to task file
   - Link to AI_AGENT_GUIDE.md
   - Link to ARCHITECTURE.md for context
   - Expected deliverables
   - Testing requirements

#### Step 3: Track Progress
Update `tasks/README.md` with task status:
- 📝 Ready → 🚧 In Progress → ✅ Complete
- Monitor dependencies
- Unblock dependent tasks when prerequisites complete

#### Step 4: Review Completed Work
When agent reports completion:
1. Check all deliverables present
2. Run syntax checks: `python3 -m py_compile [files]`
3. Verify integration with existing code
4. Check testing criteria met
5. Update status to ✅ Complete

### Sample Task Assignment Message

```
Task Assignment: Extract Hardware Abstraction Layer (Task 1.1)

Please implement Task 1.1 from our calculator project breakdown.

Documentation:
- Task Details: tasks/TASK_1.1_Hardware_Layer.md
- Coding Guide: AI_AGENT_GUIDE.md
- Architecture: ARCHITECTURE.md

Objective:
Extract hardware management classes from calculator.py into a dedicated 
hardware/ module. This will reduce the main file by ~400 lines and create 
a clean hardware abstraction layer.

Deliverables:
- Create hardware/ directory with 5 new files
- Extract 4 classes: SPIManager, DisplayManager, KeypadManager, PowerManager
- Update calculator.py imports
- All tests pass

Dependencies: None (foundation task)
Blocks: Tasks 1.4, 2.1, 2.5, 5.1

Timeline: 4-6 hours
Due: [Your deadline]

Please follow the implementation steps in the task file and test thoroughly!
```

---

## For AI Agents

### Before You Start

#### 1. Read Documentation (30 min)
- [ ] [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Visual overview
- [ ] [AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md) - Quick reference
- [ ] [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [ ] Your specific task file

#### 2. Set Up Environment
```bash
# Navigate to repository
cd /home/runner/work/Calculator/Calculator

# Check current state
ls -la Broken_2.0/
python3 -m py_compile Broken_2.0/calculator.py

# Review task assignment
cat tasks/TASK_1.1_Hardware_Layer.md  # or your task
```

#### 3. Understand the Task
- What needs to be done?
- What files will you create/modify?
- What are the dependencies?
- What are the success criteria?
- What patterns should you follow?

### During Implementation

#### Phase 1: Planning (10 min)
- [ ] List files to create
- [ ] List files to modify
- [ ] Identify code to extract/move
- [ ] Note any potential issues

#### Phase 2: Implementation (90% of time)
- [ ] Create directory structure
- [ ] Extract/create classes
- [ ] Update imports
- [ ] Test syntax frequently
- [ ] Follow existing patterns
- [ ] Add proper docstrings

#### Phase 3: Testing (Critical!)
```bash
# Syntax check all new files
python3 -m py_compile Broken_2.0/hardware/*.py

# Check main file still works
python3 -m py_compile Broken_2.0/calculator.py

# Test imports
python3 -c "from hardware import SPIManager, DisplayManager"

# Verify line counts
wc -l Broken_2.0/calculator.py  # Should be reduced
```

#### Phase 4: Documentation
- [ ] Add module docstrings
- [ ] Add class docstrings
- [ ] Add method docstrings
- [ ] Update any affected README files

### Common Workflow

```bash
# 1. Create directory
mkdir -p Broken_2.0/hardware
touch Broken_2.0/hardware/__init__.py

# 2. Extract class to new file
# Copy code from calculator.py to new file
# Add imports, docstrings

# 3. Test new file
python3 -m py_compile Broken_2.0/hardware/spi_manager.py

# 4. Update main file
# Remove old code, add import

# 5. Test integration
python3 -m py_compile Broken_2.0/calculator.py

# 6. Verify functionality preserved
grep -n "SPIManager" Broken_2.0/calculator.py
```

### Reporting Completion

When done, report:
1. **Completed deliverables** - checklist
2. **Files created** - list with line counts
3. **Files modified** - list with changes
4. **Tests passed** - show test results
5. **Issues encountered** - if any
6. **Deviations from plan** - if any

### Example Completion Report

```
Task 1.1: Hardware Abstraction Layer - COMPLETE ✅

Deliverables:
✓ Created hardware/ directory
✓ Created 5 new files (4 classes + __init__)
✓ Extracted SPIManager (45 lines)
✓ Extracted DisplayManager (177 lines)
✓ Extracted KeypadManager (95 lines)
✓ Extracted PowerManager (78 lines)
✓ Updated calculator.py imports
✓ All syntax checks pass

Files Created:
- Broken_2.0/hardware/__init__.py (25 lines)
- Broken_2.0/hardware/spi_manager.py (60 lines)
- Broken_2.0/hardware/display.py (200 lines)
- Broken_2.0/hardware/keypad.py (110 lines)
- Broken_2.0/hardware/power.py (95 lines)

Files Modified:
- Broken_2.0/calculator.py (-395 lines, now 2000 lines)

Tests Passed:
✓ python3 -m py_compile Broken_2.0/hardware/*.py - OK
✓ python3 -m py_compile Broken_2.0/calculator.py - OK
✓ Import test: from hardware import SPIManager - OK
✓ Line count reduced as expected - OK

No issues encountered.
No deviations from plan.

Ready for review!
```

---

## For Code Reviewers

### Review Checklist

#### 1. Deliverables Check
- [ ] All promised files created
- [ ] All required files modified
- [ ] No extra/unexpected changes

#### 2. Code Quality
```bash
# Syntax
python3 -m py_compile [all modified files]

# Imports
grep "^import\|^from" [files] | head -20

# Docstrings
grep -A 3 "^class\|^def" [file] | grep '"""'
```

#### 3. Pattern Compliance
- [ ] Follows existing code style
- [ ] Proper error handling (try/except)
- [ ] Logging added where appropriate
- [ ] Type hints used
- [ ] Constants from Config class

#### 4. Integration
- [ ] No broken imports
- [ ] No circular dependencies
- [ ] Backward compatible where needed
- [ ] No functionality broken

#### 5. Testing
- [ ] All syntax tests pass
- [ ] Integration tests pass
- [ ] No new errors introduced

#### 6. Documentation
- [ ] Module docstrings present
- [ ] Class docstrings present
- [ ] Complex logic commented
- [ ] README updated if needed

### Review Commands

```bash
# Check syntax all Python files
find Broken_2.0 -name "*.py" -exec python3 -m py_compile {} \;

# Check line counts
wc -l Broken_2.0/calculator.py Broken_2.0/hardware/*.py

# Find all imports
grep -rn "^from hardware import" Broken_2.0/

# Check for common issues
grep -rn "TODO\|FIXME\|XXX" Broken_2.0/

# Verify no syntax errors
python3 -m compileall Broken_2.0/ 2>&1 | grep -i error
```

### Approval Criteria

✅ **Approve if:**
- All deliverables present
- All tests pass
- Code quality good
- Follows patterns
- Well documented
- No issues found

🔄 **Request changes if:**
- Missing deliverables
- Tests fail
- Poor code quality
- Doesn't follow patterns
- Lacks documentation
- Issues found

❌ **Reject if:**
- Major functionality broken
- Security issues
- Introduces bugs
- Doesn't match task spec

---

## Task Priority Matrix

### Start Here (Highest Priority)
1. **Task 1.1** - Hardware Layer ⭐⭐⭐
   - Foundation task
   - Detailed spec ready
   - No dependencies
   - Blocks 4 other tasks

2. **Task 1.2** - File System ⭐⭐⭐
   - Foundation task
   - No dependencies
   - Blocks 2 other tasks

3. **Task 1.3** - Math Engine ⭐⭐⭐
   - Foundation task
   - No dependencies
   - Blocks 2 other tasks

### Then Do (High Priority)
4. **Task 1.5** - App State ⭐⭐
   - Independent
   - Quick task

5. **Task 1.4** - UI Manager ⭐⭐
   - Depends on 1.1
   - Important for features

### Next (Medium Priority)
6-13. Category 2 tasks (Features)
14-17. Category 3 tasks (Integration)

### Finally (Lower Priority)
18-20. Category 4 & 5 tasks (Docs, Hardware)

---

## Parallel Execution Strategy

### Team of 5 Agents

**Week 1:**
- Agent 1: Task 1.1 (Hardware)
- Agent 2: Task 1.2 (File System)
- Agent 3: Task 1.3 (Math Engine)
- Agent 4: Task 1.5 (App State)
- Agent 5: Documentation review & setup

**Week 2:**
- Agent 1: Task 1.4 (UI Manager) - depends on 1.1
- Agent 2: Task 2.3 (Settings) - depends on 1.2
- Agent 3: Task 2.2 (Scientific) - depends on 1.3
- Agent 4: Task 2.4 (SD Card) - depends on 1.2
- Agent 5: Task 5.1 (Hardware Validation)

**Week 3-4:**
- Continue with Category 2 & 3 tasks
- Maintain dependency order
- Merge and test regularly

This parallel approach can complete the project in 3-4 weeks instead of 6-8!

---

## Common Questions

### Q: What if I find an issue with the task specification?
**A:** Document it and ask for clarification before proceeding.

### Q: Can I deviate from the implementation steps?
**A:** Minor deviations are OK if documented. Major changes need approval.

### Q: What if I discover a better approach?
**A:** Document your approach and reasoning. Discuss before implementing.

### Q: How strictly should I follow the line counts?
**A:** Line counts are estimates. Focus on clean code, not exact numbers.

### Q: What if tests fail?
**A:** Debug and fix. Don't mark task complete until all tests pass.

### Q: Can I work on multiple tasks?
**A:** Yes, but finish one before starting another. Check dependencies.

### Q: What about backwards compatibility?
**A:** Maintain it unless task specifically says to break it.

---

## Success Tips

✅ **Do:**
- Read all documentation first
- Follow existing patterns
- Test frequently
- Document changes
- Ask questions
- Report issues early

❌ **Don't:**
- Skip reading the docs
- Ignore test failures
- Deviate without documenting
- Leave TODOs in final code
- Rush through testing
- Assume anything works

---

## Resources

### Documentation
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Overview
- [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md) - All tasks
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md) - Coding guide
- [tasks/README.md](tasks/README.md) - Task index

### Task Files
- [tasks/TASK_1.1_Hardware_Layer.md](tasks/TASK_1.1_Hardware_Layer.md)
- [tasks/TASK_2.1_Games_Module.md](tasks/TASK_2.1_Games_Module.md)
- More to come...

### Repository
- [Main README](README.md) - Project overview
- `Broken_2.0/` - Source code
- `calculator_backup_working_*/` - Backup

---

**Ready to start? Pick a task and let's build something great! 🚀**
