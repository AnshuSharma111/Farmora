## 13. Geolocation Utilities
**Location:** `tools/geo_utils.py`

**Description:**
Provides utilities for working with geographical coordinates, including reverse geocoding and finding nearby markets. Features offline fallback when API is unavailable.

### 13.1 get_state_district
**Signature:**
```python
def get_state_district(lat: float, lon: float) -> Tuple[str, Optional[str]]
```

**Parameters:**
- `lat` (float): Latitude coordinate
- `lon` (float): Longitude coordinate

**Returns:**
- `Tuple[str, Optional[str]]`: A tuple containing (state_name, district_name) where district_name may be None if not found

**Raises:**
- `RuntimeError`: If the API request fails or no state is found

**Example Usage:**
```python
from tools.geo_utils import get_state_district

state, district = get_state_district(30.7463, 76.6469)
# Returns: ("Punjab", "Mohali")
```

### 13.2 get_nearest_markets
**Signature:**
```python
def get_nearest_markets(state: str, district: str, commodity: str) -> List[str]
```

**Parameters:**
- `state` (str): State name
- `district` (str): District name
- `commodity` (str): Commodity name

**Returns:**
- `List[str]`: List of market names in the district

**Example Usage:**
```python
from tools.geo_utils import get_nearest_markets

markets = get_nearest_markets("Punjab", "Mohali", "rice")
# Returns: ["Sri Har Gobindpur", "Kharar", "Mohali"]
```

### 13.3 normalize_district_name
**Signature:**
```python
def normalize_district_name(district: str) -> str
```

**Parameters:**
- `district` (str): District name to normalize

**Returns:**
- `str`: Normalized district name with common suffixes removed and standard naming applied

**Example Usage:**
```python
from tools.geo_utils import normalize_district_name

clean_name = normalize_district_name("Kharar Tahsil")
# Returns: "Mohali"

clean_name = normalize_district_name("SAS Nagar")
# Returns: "Mohali"
```
