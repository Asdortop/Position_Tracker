# Full Code Review - Issues Found
**Date:** Current
**Status:** Issues need to be fixed

## Issues Found

### 🔴 CRITICAL Issue #1: Missing Column in TaxLot Model
**File:** `app/repositories/crud_operations.py`  
**Lines:** 43-56  
**Problem:** The `get_capital_gains_report` method references `TaxLot.gains_type` which doesn't exist in the model  
**Impact:** Will cause runtime error if this method is ever called  
**Fix Needed:** Either remove the method (if not used) or add a computed property

### 🟡 WARNING Issue #2: Broken Import in Price Service
**File:** `app/services/price_service.py`  
**Line:** 46  
**Problem:** Tries to import non-existent function `update_security_price`  
**Impact:** Will cause error if this service is used  
**Fix Needed:** Update to use `upsert_price` from crud_ops

### 🟡 WARNING Issue #3: Price Service Not Used
**File:** `app/services/price_service.py`  
**Status:** This file appears to be unused/legacy code  
**Impact:** Dead code that can cause confusion  
**Fix Needed:** Either implement it properly or remove it

Let me fix these issues...
