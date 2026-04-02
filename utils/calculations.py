# utils/calculations.py
import pandas as pd

def calculate_role_suitability(player_row, role_key, roles_db):
    """
    Bir oyuncunun (player_row), belirli bir role (role_key) ne kadar uygun olduğunu 100 üzerinden hesaplar.
    """
    if role_key not in roles_db:
        return 0.0
        
    attributes = roles_db[role_key]["key_attributes"]
    total_score = 0
    valid_attributes_count = 0
    
    for attr in attributes:
        # Oyuncunun CSV'sinde bu nitelik var mı kontrol et
        if attr in player_row.index:
            try:
                # 20 üzerinden olan değeri al
                val = float(player_row[attr])
                total_score += val
                valid_attributes_count += 1
            except ValueError:
                continue
            
    if valid_attributes_count == 0:
        return 0.0
        
    # Maksimum alınabilecek puan (Geçerli nitelik sayısı * 20)
    max_possible_score = valid_attributes_count * 20
    
    # 100 üzerinden yüzdeye çevir
    suitability_percentage = (total_score / max_possible_score) * 100
    return round(suitability_percentage, 1)

def get_best_roles_for_player(player_row, roles_db, top_n=3):
    """
    Oyuncunun tüm kayıtlı roller içinden en yüksek puan aldığı ilk 'top_n' rolü döndürür.
    """
    scores = {}
    for role_key in roles_db.keys():
        score = calculate_role_suitability(player_row, role_key, roles_db)
        scores[role_key] = score
        
    # Puanlara göre büyükten küçüğe sırala (Örn: [("Poacher_IP", 85.4), ("Inside Forward_IP", 82.1)])
    sorted_roles = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_roles[:top_n]

def get_percentile_tier(value, thresholds, reverse=False):
    """
    Oyuncunun değerini (value) 4 dilimli eşik (thresholds) ile kıyaslar.
    Döndürdüğü değerler: "Poor", "Average", "Good", "Elite"
    """
    try:
        val = float(value)
    except:
        return "N/A"

    if reverse:
        # Ters metrikler (Örn: Top Kaybı). Düşük olan daha iyidir.
        if val <= thresholds[3]: return "Elite"
        elif val <= thresholds[2]: return "Good"
        elif val <= thresholds[1]: return "Average"
        else: return "Poor"
    else:
        # Normal metrikler. Yüksek olan daha iyidir.
        if val >= thresholds[3]: return "Elite"
        elif val >= thresholds[2]: return "Good"
        elif val >= thresholds[1]: return "Average"
        else: return "Poor"