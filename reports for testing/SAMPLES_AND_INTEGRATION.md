# 📊 Samples & Integration Summary

## What Are the Samples?

The **samples** are **hardcoded fallback recommendations** stored in `recommender.py` as `FALLBACK_PLACES`. They're generic places that can be suggested for ANY city when real city data isn't available.

### Sample Places by Category:

#### 🍽️ Food (3 items)
- Street Food Tour - **$8** (1.5 hours)
- Local Restaurant - **$15** (1.5 hours)
- Food Market Tour - **$12** (2 hours)

#### 🛍️ Shopping (2 items)
- Local Market - **$20** (2 hours)
- Souvenir Shops - **$25** (1.5 hours)

#### 🏛️ Culture/History (3 items)
- Museum Visit - **$12** (2 hours)
- Ancient Temple Tour - **$8** (1.5 hours)
- Art Gallery - **$10** (1.5 hours)

#### 🌍 Sightseeing (3 items)
- City Viewpoint - **$5** (1 hour)
- City Walking Tour - **$18** (2 hours)
- Nature Park Visit - **$0** FREE! (2 hours)

---

## How It's Connected to city_data

### The Integration Flow:

```
User Input (city, budget, categories)
        ↓
    app.py
        ↓
get_recommendations_for_city()
        ├─ Loads city_data.json via data_handler
        ├─ Checks if city exists
        ├─ Gets places from city_data[city]['places']
        │
        ├─ IF city has data:
        │   └─ Call recommender.get_recommendations(city, budget, categories, places)
        │       ├─ filter_by_category() → Remove non-matching
        │       ├─ filter_by_budget()   → Remove too expensive
        │       └─ rank_recommendations() → Sort & limit to 10
        │
        └─ IF city has NO data:
            └─ Call recommender.get_fallback_recommendations(max_spend, categories)
                └─ Use hardcoded FALLBACK_PLACES samples
```

### Three Scenarios:

**Scenario 1: City exists with data**
```
Paris has 50 places in city_data.json
  ↓
Filter by selected categories (e.g., Food, Culture)
  ↓
Filter by budget ($100 - $25 reserve = $75 max)
  ↓
Sort by cost, return top 10
  ↓
User gets REAL Paris recommendations ✅
```

**Scenario 2: City exists but NO places**
```
Barcelona is in city_data.json
  but places = []
  ↓
Use FALLBACK_PLACES samples
  ↓
User gets generic recommendations ✅
```

**Scenario 3: City not in city_data.json**
```
User searches: Unknown City
  City not found in city_data.json
  ↓
Use FALLBACK_PLACES samples
  ↓
User gets generic recommendations ✅
```

---

## Example: Real Integration

### city_data.json structure:
```json
{
  "Paris": {
    "name": "Paris",
    "places": [
      {"name": "Eiffel Tower", "category": "Sightseeing", "cost": 20},
      {"name": "Louvre", "category": "Culture/History", "cost": 15},
      {"name": "Street Food", "category": "Food", "cost": 8},
      ...
    ],
    "categories": ["Food", "Culture/History", "Sightseeing"]
  }
}
```

### Code Flow:
```python
# User searches Paris
recommendations = get_recommendations_for_city(
    city='Paris',
    budget=100,
    categories=['Food']
)

# Inside get_recommendations_for_city():
city_data = load_city_data()  # Loads city_data.json
places = city_data['Paris']['places']  # Gets Paris places

# Call recommender with REAL data
result = get_recommendations(
    city='Paris',
    budget=100,
    categories=['Food'],
    places=places  # ← REAL data from city_data.json!
)

# recommender.py filters:
# 1. filter_by_category() → Keep only Food
# 2. filter_by_budget()   → Keep cost <= 75 (100-25)
# 3. rank_recommendations() → Sort by cost, return top 10

# Returns real Paris food recommendations
```

---

## Key Points

✅ **Samples** = Generic fallback data (FALLBACK_PLACES)  
✅ **Real Data** = Comes from city_data.json  
✅ **Filtering** = Same logic works for both real & fallback data  
✅ **Seamless** = User doesn't know if using real data or fallback  

### Data Priority:
1. **First choice**: Real places from city_data.json
2. **Fallback**: Generic samples from FALLBACK_PLACES
3. **Result**: User always gets recommendations

---

## Files Involved

| File | Role | Type |
|------|------|------|
| city_data.json | Real city data | Data file |
| data_handler.py | Loads JSON files | Utility module |
| recommender.py | Filters & ranks | Logic module |
| app.py | Orchestrates flow | Web app |
| FALLBACK_PLACES | Generic samples | Data constant |

---

## Testing

✅ **27 tests passing** (test_recommender.py)
- Filtering by budget
- Filtering by category
- Ranking recommendations
- Fallback samples
- Integration workflow

All edge cases covered:
- Empty data
- Invalid inputs
- Multiple categories
- Budget constraints
- Limit enforcement

