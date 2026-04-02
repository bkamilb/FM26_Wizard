import streamlit as st
import pandas as pd
from utils.roles_database import FM26_ROLES
from utils.calculations import calculate_role_suitability

st.set_page_config(page_title="Taktik Tahtası", page_icon="♟️", layout="wide")

st.title("♟️ Taktik Tahtası & İlk 11 Otomasyonu")
st.markdown("Bir formasyon seçin ve sistem, oyuncularınızın 'Rol Uyum Puanlarını' (RSS) hesaplayarak sahaya en kusursuz 11'i sürsün.")

# 1. VERİ KONTROLÜ
if 'squad_data' not in st.session_state:
    st.warning("⚠️ Lütfen önce ana sayfadan kadro verisinin yüklendiğinden emin olun.")
    st.stop()

df = st.session_state['squad_data']

# 2. FORMASYON ŞABLONLARI (Kendi rollerimize göre)
# Not: Veritabanımıza (roles_database) eklediğimiz rolleri kullanıyoruz.
FORMATIONS = {
    "4-3-3 Modern Hücum": {
        "GK": "Goalkeeper_IP",
        "DR": "Inverted Full-Back_IP",
        "DCR": "Ball-Playing Centre-Back_IP",
        "DCL": "Ball-Playing Centre-Back_IP",
        "DL": "Complete Wing-Back_IP",
        "DM": "Pressing CM_IP",           # Merkezde sigorta
        "MCR": "Box-to-Box Playmaker_IP",
        "MCL": "Box-to-Box Playmaker_IP",
        "AMR": "Inside Forward_IP",
        "AML": "Inside Forward_IP",
        "ST": "Deep-Lying Forward_IP"
    },
    "4-4-2 Çift Forvet Klasik": {
        "GK": "Goalkeeper_IP",
        "DR": "Inverted Full-Back_IP",
        "DCR": "Ball-Playing Centre-Back_IP",
        "DCL": "Stopping Centre-Back_OOP",
        "DL": "Inverted Full-Back_IP",
        "MR": "Inside Forward_IP",
        "MCR": "Pressing CM_IP",
        "MCL": "Box-to-Box Playmaker_IP",
        "ML": "Inside Forward_IP",
        "STR": "Deep-Lying Forward_IP",
        "STL": "Poacher_IP"
    }
}

st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Taktik Seçimi")
    selected_formation_name = st.selectbox("Formasyon Şablonu Seçiniz:", list(FORMATIONS.keys()))
    
    if st.button("İlk 11'i Kur 🚀", type="primary"):
        st.session_state['build_xi'] = True

with col2:
    if st.session_state.get('build_xi', False):
        st.subheader(f"✨ En İyi 11: {selected_formation_name}")
        
        formation_roles = FORMATIONS[selected_formation_name]
        best_xi = []
        used_players = set() # Bir oyuncunun iki farklı mevkide oynamasını engellemek için
        
        # Her pozisyon için en iyi oyuncuyu bul
        for pos, role_key in formation_roles.items():
            candidates = []
            
            for index, row in df.iterrows():
                player_name = row['Player']
                
                # Eğer oyuncu zaten başka bir mevkiye seçildiyse atla
                if player_name in used_players:
                    continue
                    
                score = calculate_role_suitability(row, role_key, FM26_ROLES)
                candidates.append((player_name, score))
            
            # Bu rol için en yüksek puanlı oyuncuyu bul
            if candidates:
                candidates.sort(key=lambda x: x[1], reverse=True)
                top_player, top_score = candidates[0]
                
                best_xi.append({
                    "Pozisyon": pos,
                    "Taktiksel Rol": role_key.replace('_', ' '),
                    "Seçilen Oyuncu": top_player,
                    "Rol Uyumu": top_score
                })
                
                used_players.add(top_player)
        
        # Sonuçları DataFrame'e çevir ve göster
        xi_df = pd.DataFrame(best_xi)
        
        # Takımın genel uyum ortalamasını hesapla
        team_avg_score = xi_df['Rol Uyumu'].mean()
        
        st.metric("Takım Genel Uyum Puanı (Kimya)", f"%{team_avg_score:.1f}")
        
        # Şık bir tablo çiz
        st.dataframe(
            xi_df.style.map(
                lambda x: 'background-color: #004d00; color: white' if x >= 85 else 
                          'background-color: #808000; color: white' if x >= 75 else 
                          'background-color: #800000; color: white',
                subset=['Rol Uyumu']
            ),
            use_container_width=True
        )
        
        st.caption("Not: Koyu Yeşil (%85+) Elit uyumu, Sarı (%75+) İyi uyumu, Bordo (%75 Altı) Zayıf uyumu temsil eder.")