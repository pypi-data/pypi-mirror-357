import random
import pandas as pd
from .schemas import SCHEMAS
from .exceptions import SchemaNotFoundError, ColumnSelectionError

def generate(table: str, rows: int = 10, columns: int = 5) -> pd.DataFrame:
    table = table.lower()
    if table not in SCHEMAS:
        raise SchemaNotFoundError(f"Schema for table '{table}' not found.")

    schema = SCHEMAS[table]
    all_columns = schema["columns"]
    required = schema["required"]

    if columns < len(required):
        raise ColumnSelectionError(f"Minimum {len(required)} columns required for '{table}'.")

    optional = list(set(all_columns) - set(required))
    selected = required + random.sample(optional, min(columns - len(required), len(optional)))
    data = {col: _generate_data(col, rows) for col in selected}
    return pd.DataFrame(data)

def _generate_data(col: str, n: int):
    col = col.lower()

    if "id" in col or "roll" in col:
        return [random.randint(1000, 9999) for _ in range(n)]
    
    if "name" in col:
        return [random.choice(["Alice", "Bob", "Carol", "David", "Eve", "Tom", "Linda", "Max"]) for _ in range(n)]
    
    if "email" in col:
        return [f"user{i}@example.com" for i in range(n)]
    
    if "course" in col:
        return [random.choice(["BCA", "CSIT", "Engineering", "MBA", "BBA"]) for _ in range(n)]
    
    if "salary" in col:
        return [random.randint(30000, 120000) for _ in range(n)]
    
    if "dob" in col or "birth" in col:
        return [f"199{random.randint(0, 9)}-0{random.randint(1, 9)}-{random.randint(10, 28)}" for _ in range(n)]
    
    if "phone" in col:
        return [f"+977-98{random.randint(10000000, 99999999)}" for _ in range(n)]
    
    if "city" in col:
        return [random.choice(["Kathmandu", "Berlin", "Paris", "Tokyo", "Delhi"]) for _ in range(n)]
    
    if "country" in col:
        return [random.choice(["Nepal", "Germany", "France", "Japan", "India"]) for _ in range(n)]

    if "year" in col:
        return [random.choice(["1st", "2nd", "3rd", "4th"]) for _ in range(n)]
    
    if "address" in col or "location" in col:
        return [random.choice(["New Road", "Sukedhara", "Bhaktapur", "Thamel", "Lalitpur"]) for _ in range(n)]

    if "department" in col:
        return [random.choice(["HR", "Engineering", "Finance", "Marketing", "IT"]) for _ in range(n)]

    if "joining_date" in col:
        return [f"20{random.randint(10, 24)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}" for _ in range(n)]

    if "position" in col:
        return [random.choice(["Manager", "Developer", "Intern", "Analyst", "Designer"]) for _ in range(n)]

    if "manager" in col:
        return [random.choice(["Mr. A", "Mrs. B", "Dr. C", "Ms. D"]) for _ in range(n)]

    if "sport" in col:
        return [random.choice(["Football", "Cricket", "Tennis", "Basketball", "Volleyball"]) for _ in range(n)]

    if "team" in col:
        return [random.choice(["Team A", "Lakers", "Barcelona", "Man United", "Warriors"]) for _ in range(n)]

    if "position" in col and "player" in col:
        return [random.choice(["Goalkeeper", "Striker", "Defender", "Midfielder"]) for _ in range(n)]

    if "nationality" in col:
        return [random.choice(["Nepalese", "German", "French", "Japanese", "Indian"]) for _ in range(n)]

    if "matches" in col:
        return [random.randint(10, 500) for _ in range(n)]

    if "goals" in col:
        return [random.randint(0, 200) for _ in range(n)]

    if "rank" in col:
        return [random.randint(1, 100) for _ in range(n)]

    if "species" in col:
        return [random.choice(["Mammal", "Reptile", "Bird", "Amphibian", "Fish"]) for _ in range(n)]

    if "breed" in col:
        return [random.choice(["Labrador", "Persian", "Bengal", "Siberian", "Maine Coon"]) for _ in range(n)]

    if "color" in col:
        return [random.choice(["Black", "White", "Brown", "Spotted", "Golden"]) for _ in range(n)]

    if "habitat" in col:
        return [random.choice(["Forest", "Savannah", "Ocean", "Mountain", "River"]) for _ in range(n)]

    if "zoo" in col:
        return [random.choice(["Central Zoo", "Berlin Zoo", "Bronx Zoo", "London Zoo"]) for _ in range(n)]

    if "title" in col:
        return [random.choice(["Inception", "Titanic", "Avatar", "Interstellar", "Jaws"]) for _ in range(n)]

    if "genre" in col:
        return [random.choice(["Action", "Drama", "Comedy", "Thriller", "Sci-Fi"]) for _ in range(n)]

    if "release_year" in col:
        return [random.randint(1980, 2024) for _ in range(n)]

    if "director" in col:
        return [random.choice(["Nolan", "Spielberg", "Tarantino", "Scorsese", "Cameron"]) for _ in range(n)]

    if "duration" in col:
        return [random.randint(90, 180) for _ in range(n)]

    if "rating" in col:
        return [round(random.uniform(1.0, 10.0), 1) for _ in range(n)]

    if "language" in col:
        return [random.choice(["English", "Hindi", "Japanese", "German", "French"]) for _ in range(n)]

    if "budget" in col:
        return [random.randint(1_000_000, 300_000_000) for _ in range(n)]

    # Default fallback
    return [f"sample_{i}" for i in range(n)]
