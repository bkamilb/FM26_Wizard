# utils/roles_database.py

FM26_ROLES = {
    # --- KALECİLER ---
    "Goalkeeper_IP": {
        "role_name": "Goalkeeper",
        "phase": "IP",
        "key_attributes": ["Handling", "Aerial Reach", "Command Of Area", "Communication", "Positioning", "Reflexes", "Agility", "Concentration"]
    },
    "Sweeper Keeper_OOP": {
        "role_name": "Sweeper Keeper",
        "phase": "OOP",
        "key_attributes": ["Handling", "Aerial Reach", "Command Of Area", "Communication", "Anticipation", "Decisions", "One On Ones", "Reflexes"]
    },
    
    # --- STOPERLER ---
    "Ball-Playing Centre-Back_IP": {
        "role_name": "Ball-Playing Centre-Back",
        "phase": "IP",
        "key_attributes": ["Heading", "Marking", "Passing", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach", "Expressive"]
    },
    "Stopping Centre-Back_OOP": {
        "role_name": "Stopping Centre-Back",
        "phase": "OOP",
        "key_attributes": ["Heading", "Marking", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach", "Bravery"]
    },
    
    # --- BEKLER ---
    "Inverted Full-Back_IP": {
        "role_name": "Inverted Full-Back",
        "phase": "IP",
        "key_attributes": ["Heading", "Marking", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach"]
    },
    "Complete Wing-Back_IP": {
        "role_name": "Complete Wing-Back",
        "phase": "IP",
        "key_attributes": ["Crossing", "Dribbling", "Passing", "Tackling", "Technique", "Work Rate", "Acceleration", "Stamina"]
    },

    # --- ORTA SAHALAR ---
    "Box-to-Box Playmaker_IP": {
        "role_name": "Box-to-Box Playmaker",
        "phase": "IP",
        "key_attributes": ["Off The Ball", "Passing", "Vision", "Decisions", "First Touch", "Technique", "Teamwork", "Work Rate"]
    },
    "Pressing CM_IP": {
        "role_name": "Pressing CM",
        "phase": "IP",
        "key_attributes": ["Tackling", "Anticipation", "Decisions", "Teamwork", "Work Rate", "Stamina", "Aggression"]
    },
    
    # --- KANATLAR ---
    "Inside Forward_IP": {
        "role_name": "Inside Forward",
        "phase": "IP",
        "key_attributes": ["Dribbling", "Off The Ball", "Anticipation", "First Touch", "Technique", "Acceleration", "Agility", "Composure"]
    },
    
    # --- FORVETLER ---
    "Poacher_IP": {
        "role_name": "Poacher",
        "phase": "IP",
        "key_attributes": ["Finishing", "Heading", "Off The Ball", "Anticipation", "Acceleration", "Composure", "Concentration"]
    },
    "Deep-Lying Forward_IP": {
        "role_name": "Deep-Lying Forward",
        "phase": "IP",
        "key_attributes": ["Finishing", "Off The Ball", "First Touch", "Technique", "Strength", "Composure"]
    }
}