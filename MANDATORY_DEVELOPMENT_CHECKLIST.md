# ⚠️ MANDATORY DEVELOPMENT CHECKLIST

**This checklist MUST be followed for EVERY code change, no exceptions.**

**Last Updated:** November 6, 2025  
**Maintained By:** Chava Palma (Founder & CEO)

---

## 🚨 CRITICAL RULE

**BEFORE writing ANY code that touches the database:**

1. **OPEN** `DATABASE_FIELD_STANDARDS.md`
2. **READ** the relevant collection's field definitions
3. **USE** the exact field names specified
4. **NEVER** guess or assume field names

---

## ✅ PRE-CODING CHECKLIST

Before writing any new code or modifying existing code:

- [ ] I have opened and read `DATABASE_FIELD_STANDARDS.md`
- [ ] I have identified which collections my code will touch
- [ ] I have noted the exact snake_case field names for MongoDB
- [ ] I have noted the exact camelCase field names for API/Frontend
- [ ] I understand which context I'm working in (Backend DB vs Frontend API)

---

## ✅ BACKEND DEVELOPMENT CHECKLIST

When writing Python code that queries MongoDB:

### MongoDB Queries

- [ ] All `.find()` queries use snake_case field names
- [ ] All `.find_one()` queries use snake_case field names
- [ ] All `.update()` queries use snake_case field names
- [ ] All `.insert()` queries use snake_case field names
- [ ] All `.aggregate()` pipelines use snake_case field names

### Examples

**❌ WRONG:**
```python
db.investments.find({'fundType': 'CORE'})  # camelCase in MongoDB
db.mt5_accounts.update_one({}, {'$set': {'fundType': 'BALANCE'}})
investment.get('principalAmount')  # If investment is from MongoDB
```

**✅ CORRECT:**
```python
db.investments.find({'fund_type': 'CORE'})  # snake_case in MongoDB
db.mt5_accounts.update_one({}, {'$set': {'fund_type': 'BALANCE'}})
investment.get('principal_amount')  # MongoDB uses snake_case
```

### API Responses

- [ ] All API responses are converted to camelCase before sending
- [ ] Field conversion function is used (snake_to_camel)
- [ ] _id is converted to id
- [ ] No snake_case fields leak to frontend

**❌ WRONG:**
```python
@app.get("/api/investments")
def get_investments():
    investments = db.investments.find().to_list()
    return investments  # Returns snake_case to frontend
```

**✅ CORRECT:**
```python
@app.get("/api/investments")
def get_investments():
    investments = db.investments.find().to_list()
    # Convert to camelCase
    return [convert_dict_keys(inv, to_camel=True) for inv in investments]
```

---

## ✅ FRONTEND DEVELOPMENT CHECKLIST

When writing JavaScript/React code:

### API Calls

- [ ] All data sent to API uses camelCase field names
- [ ] All data received from API is expected in camelCase
- [ ] No snake_case field names in frontend code

**❌ WRONG:**
```javascript
// Using snake_case in frontend
const investment = {
  fund_type: 'CORE',
  principal_amount: 10000
};
```

**✅ CORRECT:**
```javascript
// Using camelCase in frontend
const investment = {
  fundType: 'CORE',
  principalAmount: 10000
};
```

### Display Logic

- [ ] All field accesses use camelCase
- [ ] PropTypes/TypeScript interfaces use camelCase
- [ ] Component state uses camelCase

---

## ✅ POST-CODING CHECKLIST

After writing code:

- [ ] I have run the field standards audit: `python3 FIELD_STANDARDS_AUDIT.py`
- [ ] Audit shows 0 violations for my changes
- [ ] I have tested with real database data
- [ ] Backend returns camelCase to frontend
- [ ] Frontend displays data correctly
- [ ] No console errors related to field names

---

## ✅ NEW FIELD ADDITION CHECKLIST

If you need to add a NEW field not in DATABASE_FIELD_STANDARDS.md:

- [ ] Field name follows snake_case for database
- [ ] Field name follows camelCase for API
- [ ] Field is added to DATABASE_FIELD_STANDARDS.md in BOTH sections
- [ ] Example is provided showing snake_case and camelCase versions
- [ ] Field is documented with its purpose and data type
- [ ] All code using this field follows the standards
- [ ] Standards document is committed to GitHub

---

## ✅ CODE REVIEW CHECKLIST

Before merging or deploying code:

- [ ] Run `python3 FIELD_STANDARDS_AUDIT.py`
- [ ] Zero violations reported
- [ ] All MongoDB queries use snake_case
- [ ] All API responses use camelCase
- [ ] All frontend code uses camelCase
- [ ] DATABASE_FIELD_STANDARDS.md is up to date
- [ ] No hardcoded field names without checking standards first

---

## 🚨 COMMON VIOLATIONS TO AVOID

### Violation 1: Using camelCase in MongoDB Queries

```python
# ❌ WRONG
db.investments.find({'fundType': 'CORE'})

# ✅ CORRECT
db.investments.find({'fund_type': 'CORE'})
```

### Violation 2: Using snake_case in Frontend

```javascript
// ❌ WRONG
<div>{investment.fund_type}</div>

// ✅ CORRECT
<div>{investment.fundType}</div>
```

### Violation 3: Not Converting API Responses

```python
# ❌ WRONG
@app.get("/api/data")
def get_data():
    return db.collection.find_one()  # Returns snake_case

# ✅ CORRECT
@app.get("/api/data")
def get_data():
    data = db.collection.find_one()
    return convert_dict_keys(data, to_camel=True)  # Returns camelCase
```

### Violation 4: Mixing Cases in Same Context

```python
# ❌ WRONG
investment = {
    'fund_type': 'CORE',  # snake_case
    'principalAmount': 10000  # camelCase
}

# ✅ CORRECT - Choose ONE based on context
# For MongoDB:
investment = {
    'fund_type': 'CORE',
    'principal_amount': 10000
}

# For API/Frontend:
investment = {
    'fundType': 'CORE',
    'principalAmount': 10000
}
```

---

## 📊 ENFORCEMENT

**This checklist is MANDATORY. No exceptions.**

**Consequences of not following standards:**
1. Code breaks in production (like the cash flow bug)
2. Data inconsistency across platform
3. Wasted debugging time
4. User-facing errors
5. Loss of trust in platform

**How to ensure compliance:**
1. Run audit script before every commit
2. Check DATABASE_FIELD_STANDARDS.md for every field
3. Review all MongoDB queries for snake_case
4. Review all API code for camelCase
5. Test with real data before deploying

---

## 🎯 REMEMBER

**The DATABASE_FIELD_STANDARDS.md file is the SINGLE SOURCE OF TRUTH.**

- ✅ MongoDB = snake_case
- ✅ API/Frontend = camelCase
- ✅ Always convert between them
- ✅ Never guess field names
- ✅ Always check the standards document first

---

**This document must be followed 100% of the time.**

**Maintained by:** Chava Palma  
**Last Updated:** November 6, 2025  
**Next Review:** Before every code change
