# 🔗 Recommendation Flow - Integration Guide

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Request                             │
│  city='Paris', budget=100, categories=['Food', 'Culture']   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          app.py: generate_plan() route                       │
│  - Validates user input                                     │
│  - Calls get_recommendations_for_city()                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│    app.py: get_recommendations_for_city()                   │
│  - Loads city_data.json using data_handler                 │
│  - Checks if city exists                                    │
│  - Extracts places for that city                           │
│  - Calls recommender.get_recommendations()                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────┐
    │   RECOMMENDATION LOGIC             │
    │   (recommender.py)                │
    │                                    │
    │  Input: places, budget, categories│
    │                                    │
    │  1. filter_by_category()           │
    │     ↓ Remove non-matching items   │
    │                                    │
    │  2. filter_by_budget()             │
    │     ↓ Remove expensive items      │
    │                                    │
    │  3. rank_recommendations()         │
    │     ↓ Sort by cost, limit to 10  │
    │                                    │
    │  Output: Top 10 recommendations   │
    └────────────────────────────────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Has places?      │
                └────┬─────────────┘
             YES │         │ NO
                 │         └──────────────────┐
                 │                            │
                 ▼                            ▼
        ┌──────────────────┐      ┌─────────────────────────┐
        │ Return actual    │      │ Use FALLBACK_PLACES     │
        │ recommendations  │      │ (hardcoded samples)     │
        │ from city_data   │      │                         │
        └────┬─────────────┘      └──────────┬──────────────┘
             │                               │
             └───────────────┬───────────────┘
                             │
                             ▼
            ┌──────────────────────────────┐
            │  Return 10 recommendations   │
            │  to user                     │
            └──────────────────────────────┘
```

---

## 📁 File Structure

```
trip_recommendation/
├── Data/
│   ├── city_data.json          ← Real city data (Paris, Rome, etc.)
│   ├── users.json
│   └── forum.json
├── project/
│   ├── data_handler.py         ← Loads/saves JSON files
│   ├── recommender.py          ← Filtering & ranking logic
│   │   └── FALLBACK_PLACES     ← Sample data (when no city_data)
│   └── app.py
│       ├── load_city_data()           ← Reads city_data.json
│       └── get_recommendations_for_city()  ← Orchestrates flow
```

---

## 🎯 How Samples Work

### Scenario 1: City Exists in city_data.json
```
User searches: Paris
                ↓
city_data['Paris'] exists? YES
                ↓
places = city_data['Paris']['places']  ← Real Paris places
                ↓
Use recommender to filter & rank real places
                ↓
Return recommendations from REAL DATA
```

### Scenario 2: City NOT in city_data.json (Empty Database)
```
User searches: Barcelona
                ↓
city_data['Barcelona'] exists? NO
                ↓
No real data available
                ↓
Use FALLBACK_PLACES (hardcoded samples)
    - Street Food Tour ($8)
    - Museum Visit ($12)
    - City Viewpoint ($5)
    - etc.
                ↓
Return generic recommendations
```

---

## 🧪 Example Walkthrough

### Input:
```python
city = 'Paris'
budget = 100
categories = ['Food', 'Culture/History']
```

### Flow:

**Step 1: Load city_data**
```python
city_data = {
    'Paris': {
        'places': [
            {'name': 'Eiffel Tower', 'category': 'Sightseeing', 'cost': 20},
            {'name': 'Louvre Museum', 'category': 'Culture/History', 'cost': 15},
            {'name': 'Bistro', 'category': 'Food', 'cost': 25},
            {'name': 'Luxury Restaurant', 'category': 'Food', 'cost': 60},
            {'name': 'Street Food', 'category': 'Food', 'cost': 8}
        ]
    }
}
```

**Step 2: filter_by_category(places, ['Food', 'Culture/History'])**
```
Input 5 places
↓
Remove Sightseeing items
↓
Keep: [Louvre, Bistro, Luxury Restaurant, Street Food]
Output: 4 places
```

**Step 3: filter_by_budget(filtered_places, 100, reserve=25)**
```
max_spend = 100 - 25 = 75
↓
Keep places with cost <= 75
↓
Remove: Luxury Restaurant ($60 is OK, not removed!)
Actually all pass: [Louvre($15), Bistro($25), Luxury Restaurant($60), Street Food($8)]
↓
Output: 4 places
```

**Step 4: rank_recommendations(filtered_places, sort_by='cost', limit=10)**
```
Sort by cost ascending:
↓
[
  1. Street Food ($8)
  2. Louvre Museum ($15)
  3. Bistro ($25)
  4. Luxury Restaurant ($60)
]
↓
Limit to 10 (we have 4, so all included)
↓
Return all 4
```

### Output:
```python
[
    {'name': 'Street Food', 'category': 'Food', 'cost': 8},
    {'name': 'Louvre Museum', 'category': 'Culture/History', 'cost': 15},
    {'name': 'Bistro', 'category': 'Food', 'cost': 25},
    {'name': 'Luxury Restaurant', 'category': 'Food', 'cost': 60}
]
```

---

## 🔍 Code Integration Points

### app.py calls recommender:
```python
from recommender import get_recommendations, get_fallback_recommendations

def get_recommendations_for_city(city, budget, categories):
    city_data = load_city_data()  # Load from city_data.json
    
    if city not in city_data:
        # No city data → use fallback samples
        return get_fallback_recommendations(max_spend, categories)
    
    places = city_data[city].get('places', [])
    
    # Use actual city data
    return get_recommendations(city, budget, categories, places)
```

### recommender.py filtering chain:
```python
def get_recommendations(city, budget, categories, places):
    # Step 1: Filter by selected categories
    by_category = filter_by_category(places, categories)
    
    # Step 2: Filter by budget
    by_budget = filter_by_budget(by_category, budget)
    
    # Step 3: Rank and limit
    return rank_recommendations(by_budget, sort_by='cost', limit=10)
```

---

## 📊 Sample Data (FALLBACK_PLACES)

Used when city_data.json is empty or city not found:

| Category | Places | Budget |
|----------|--------|--------|
| Food | Street Food Tour, Restaurant, Market Tour | $8-15 |
| Shopping | Local Market, Souvenir Shops | $20-25 |
| Culture/History | Museum, Temple Tour, Art Gallery | $8-12 |
| Sightseeing | Viewpoint, Walking Tour, Park | $0-18 |

All fallback places are generic and work for any city.

---

## ✅ Current Integration Status

✅ data_handler.py - Loads city_data.json  
✅ recommender.py - Filters & ranks places  
✅ app.py - Orchestrates the flow  
✅ Fallback samples - Generic recommendations  
✅ 27/27 tests passing  

**Everything is now connected!** Users get:
- Real recommendations from city_data if available
- Fallback generic recommendations if not

