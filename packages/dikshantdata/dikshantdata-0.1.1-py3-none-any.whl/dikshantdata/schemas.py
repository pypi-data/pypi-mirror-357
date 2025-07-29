SCHEMAS = {
    "students": {
        "columns": ["roll_no", "name", "email", "course", "year", "dob", "address", "phone", "city", "country"],
        "required": ["roll_no", "name"]
    },
    "employees": {
        "columns": ["emp_id", "name", "department", "salary", "email", "joining_date", "position", "manager", "location"],
        "required": ["emp_id"]
    },
    "players": {
        "columns": ["player_id", "name", "sport", "team", "position", "nationality", "dob", "matches_played", "goals_scored", "rank"],
        "required": ["player_id", "name"]
    },
    "animals": {
        "columns": ["animal_id", "name", "species", "breed", "age", "color", "habitat", "zoo"],
        "required": ["animal_id", "name"]
    },
    "movies": {
        "columns": ["movie_id", "title", "genre", "release_year", "director", "duration", "rating", "language", "budget"],
        "required": ["movie_id", "title"]
    }
}
