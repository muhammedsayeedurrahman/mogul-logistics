# Smart Shipment Validation - UX Enhancement

## What This Does

**Prevents judge confusion** by automatically validating that selected shipment exists in current difficulty and providing clear guidance.

---

## How It Works

### Scenario 1: Invalid Selection ❌
**User action:**
- Difficulty: **Easy** (1 shipment)
- Selected shipment: **SHP-003**

**System response:**
```
⚠️ Shipment Not Available in Current Difficulty

SHP-003 does not exist in Easy difficulty.
Easy has only 1 shipment(s) (SHP-001 to SHP-001).

💡 SOLUTION
1. Change difficulty to Medium or higher above
2. Click 🔄 Reset Episode
3. Then execute your action on SHP-003
```

**Visual:**
- Orange/red warning banner with pulse animation
- Clear problem statement
- Step-by-step solution

---

### Scenario 2: Valid Selection ✅
**User action:**
- Difficulty: **Medium** (4 shipments)
- Selected shipment: **SHP-003**

**System response:**
```
✅ SHP-003 is available in Medium difficulty. Ready to execute!
```

**Visual:**
- Green success banner
- Confirmation message
- No blocking

---

## Validation Logic

```python
Difficulty      → Max Shipments → Valid IDs
─────────────────────────────────────────
Easy            → 1             → SHP-001
Medium          → 4             → SHP-001 to SHP-004
Hard            → 8             → SHP-001 to SHP-008
```

**Auto-suggestion:**
- Select SHP-001 → Can use Easy
- Select SHP-002 to SHP-004 → Need Medium or higher
- Select SHP-005 to SHP-008 → Need Hard

---

## When Validation Triggers

1. **On page load** - Initial validation of defaults
2. **When shipment dropdown changes** - Real-time check
3. **When difficulty dropdown changes** - Re-validate selection

**Result:** Judges get **immediate feedback** before clicking "Execute"

---

## UX Benefits

### Before (Without Validation):
1. Judge selects Easy difficulty
2. Judge selects SHP-003 (doesn't exist)
3. Judge clicks "Execute"
4. **ERROR:** "Invalid target shipment SHP-003"
5. **Confusion:** Why doesn't it work?

### After (With Validation):
1. Judge selects Easy difficulty
2. Judge selects SHP-003
3. **IMMEDIATE WARNING** appears before clicking Execute
4. Warning says: "Change to Medium or higher"
5. Judge changes difficulty → Green checkmark
6. Judge clicks Execute → Success!

---

## Visual Design

### Warning Message (Invalid):
```
┌─────────────────────────────────────────┐
│ ⚠️  Shipment Not Available              │
│                                          │
│ SHP-003 does not exist in Easy.         │
│ Easy has only 1 shipment (SHP-001).     │
│                                          │
│ 💡 SOLUTION                             │
│ 1. Change difficulty to Medium          │
│ 2. Click Reset Episode                  │
│ 3. Execute action on SHP-003            │
└─────────────────────────────────────────┘
```
**Colors:** Orange/red gradient, pulsing border

### Success Message (Valid):
```
┌─────────────────────────────────────────┐
│ ✅ SHP-003 is available in Medium.      │
│    Ready to execute!                    │
└─────────────────────────────────────────┘
```
**Colors:** Green gradient

---

## Code Implementation

**File:** `server/gradio_custom.py`

**Key function:**
```python
def _validate_shipment_difficulty(ship_id, task_label):
    """Check if selected shipment exists in current difficulty."""
    ship_num = int(ship_id.split("-")[1])

    task_max_ships = {
        "Easy  -  1 ship, 5 steps, $5K": 1,
        "Medium  -  4 ships, 10 steps, $12K": 4,
        "Hard  -  8 ships, 15 steps, $15K": 8,
    }

    max_ships = task_max_ships.get(task_label, 1)

    if ship_num > max_ships:
        # Return warning message with suggestion
    else:
        # Return success message
```

**Wiring:**
```python
# Validate on shipment change
target_id.change(
    fn=_validate_shipment_difficulty,
    inputs=[target_id, task_selector],
    outputs=[validation_msg],
)

# Validate on difficulty change
task_selector.change(
    fn=_validate_shipment_difficulty,
    inputs=[target_id, task_selector],
    outputs=[validation_msg],
)

# Validate on page load
dashboard.load(
    fn=_validate_shipment_difficulty,
    inputs=[target_id, task_selector],
    outputs=[validation_msg],
)
```

---

## Impact on Judge Experience

### Before:
- ❌ Trial and error to find valid shipments
- ❌ Cryptic error messages after clicking Execute
- ❌ Confusion about difficulty vs shipment relationship

### After:
- ✅ **Immediate visual feedback** before attempting action
- ✅ **Clear guidance** on what to do
- ✅ **No errors** - prevented before execution
- ✅ **Self-explanatory** - judges understand the system instantly

---

## Testing Scenarios

1. **Load page (default Easy + SHP-001)**
   - Expected: ✅ Green success message

2. **Change to SHP-005 on Easy**
   - Expected: ⚠️ Warning with "Change to Hard"

3. **Change difficulty to Hard**
   - Expected: ✅ Green success message (SHP-005 now valid)

4. **Change to Medium**
   - Expected: ⚠️ Warning (SHP-005 invalid in Medium)

5. **Change to SHP-002**
   - Expected: ✅ Green success message (SHP-002 valid in Medium)

---

## Why This Matters for Winning

**Judge evaluation time: 5 minutes**

Every second wasted on confusion reduces score. This feature:
- Eliminates confusion instantly
- Shows **attention to UX detail**
- Demonstrates **production-ready thinking**
- Makes judges' job **easier** (they remember that!)

**Competitive advantage:**
- Most submissions have no validation
- This shows **professional polish**
- Judges think: "This team thinks about users"

---

## Summary

✅ Real-time validation
✅ Clear error messages
✅ Actionable solutions
✅ No trial and error
✅ Professional UX
✅ Judge-friendly

**Result:** Zero confusion, maximum clarity, winning impression.
