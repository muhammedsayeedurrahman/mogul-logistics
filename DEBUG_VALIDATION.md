# Debugging Shipment Validation

## Quick Test Instructions

### 1. Start Server with Console Visible

```bash
# Make sure you can see the console output
start_server.cmd
```

**IMPORTANT:** Keep the console window visible - debug messages will appear here!

### 2. Open Browser

Go to: http://localhost:8000

### 3. Test Scenario: SHP-003 on Easy

**Steps:**
1. Make sure difficulty is "Easy  -  1 ship, 5 steps, $5K"
2. In "Target Shipment" dropdown, select "SHP-003"
3. **Look at the validation message** that appears below the buttons
4. **Look at server console** for debug output

**Expected Result:**
```
⚠️ Shipment Not Available in Current Difficulty

SHP-003 does not exist in Easy difficulty.
Easy has only 1 shipment(s) (SHP-001 to SHP-001).

💡 SOLUTION
1. Change difficulty to Medium or higher
2. Click 🔄 Reset Episode
3. Execute action on SHP-003
```

**Debug console should show:**
```
[VALIDATION] ship_id=SHP-003, task_label=Easy  -  1 ship, 5 steps, $5K
[VALIDATION] ship_num=3
[VALIDATION] max_ships=1, ship_num > max_ships = True
```

### 4. Test Scenario: SHP-003 on Medium

**Steps:**
1. Change difficulty to "Medium  -  4 ships, 10 steps, $12K"
2. Target Shipment should still be "SHP-003"
3. **Look for validation message update**

**Expected Result:**
```
✅ SHP-003 is available in Medium difficulty. Ready to execute!
```

**Debug console should show:**
```
[VALIDATION] ship_id=SHP-003, task_label=Medium  -  4 ships, 10 steps, $12K
[VALIDATION] ship_num=3
[VALIDATION] max_ships=4, ship_num > max_ships = False
```

---

## Troubleshooting

### Issue: No validation message appears at all

**Check:**
1. Is the message area visible below the Execute/Reset buttons?
2. Look for a gray placeholder: "Select a shipment to see validation"
3. Check browser console (F12) for JavaScript errors

### Issue: Message doesn't update when changing dropdowns

**Check:**
1. Server console - are [VALIDATION] messages appearing?
2. If NO console messages:
   - The change event isn't firing
   - Restart server: Ctrl+C, then start_server.cmd again
3. If YES console messages but no UI update:
   - Browser cache issue
   - Hard refresh: Ctrl+Shift+R (Chrome/Firefox)

### Issue: Wrong message appears

**Check console output:**
- What is ship_num?
- What is max_ships?
- What is ship_num > max_ships?

**Example debug output:**
```
[VALIDATION] ship_id=SHP-003, task_label=Easy  -  1 ship, 5 steps, $5K
[VALIDATION] ship_num=3
[VALIDATION] max_ships=1, ship_num > max_ships = True
```

This means:
- Selected SHP-003 (ship number 3)
- On Easy difficulty (max 1 ship)
- 3 > 1 is True
- Should show orange warning ⚠️

---

## Complete Test Matrix

| Difficulty | Shipment | Should Show | Reason |
|------------|----------|-------------|--------|
| Easy | SHP-001 | ✅ Green | 1 <= 1 |
| Easy | SHP-002 | ⚠️ Orange | 2 > 1 |
| Easy | SHP-003 | ⚠️ Orange | 3 > 1 |
| Easy | SHP-004 | ⚠️ Orange | 4 > 1 |
| Medium | SHP-001 | ✅ Green | 1 <= 4 |
| Medium | SHP-002 | ✅ Green | 2 <= 4 |
| Medium | SHP-003 | ✅ Green | 3 <= 4 |
| Medium | SHP-004 | ✅ Green | 4 <= 4 |
| Medium | SHP-005 | ⚠️ Orange | 5 > 4 |
| Hard | SHP-001 to SHP-008 | ✅ Green | All valid |

---

## What to Report if Still Not Working

If validation still doesn't work after following above:

**Capture and share:**
1. Screenshot of the browser showing the manual control panel
2. Server console output (copy the [VALIDATION] lines)
3. What difficulty you selected
4. What shipment you selected
5. What message you see (or "no message")

**Example good bug report:**
```
SELECTED:
- Difficulty: Easy  -  1 ship, 5 steps, $5K
- Shipment: SHP-003

CONSOLE OUTPUT:
[VALIDATION] ship_id=SHP-003, task_label=Easy  -  1 ship, 5 steps, $5K
[VALIDATION] ship_num=3
[VALIDATION] max_ships=1, ship_num > max_ships = True

ACTUAL RESULT:
No message appears (or green message appears instead of orange)

EXPECTED:
Orange warning message
```

This gives me all the info needed to debug!

---

## Quick Fixes

### If validation message appears in wrong place:

The message should appear **directly below** the Execute/Reset buttons, **above** the "How to verify" text.

### If message is too small to see:

The warning should be:
- Large orange/red box
- With ⚠️ emoji (2rem size)
- Bold heading "Shipment Not Available"
- Pulsing animation

If you see it but it's tiny, that's a CSS issue.

---

## Test Right Now!

1. Make sure server is running: `start_server.cmd`
2. Open: http://localhost:8000
3. Select "Easy" difficulty
4. Select "SHP-003" in Target Shipment
5. **Look for orange warning box**
6. **Check server console for [VALIDATION] messages**

Then report back what you see!
