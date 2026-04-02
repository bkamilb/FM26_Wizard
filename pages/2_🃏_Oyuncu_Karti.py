import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.roles_database import FM26_ROLES
from utils.calculations import get_best_roles_for_player

st.set_page_config(page_title="Oyuncu Kartı", page_icon="🃏", layout="wide")

st.title("🃏 Oyuncu Analiz Kartı")
st.markdown("Oyuncunuzun taktiksel DNA'sını, en uygun rollerini ve profil radarını buradan inceleyebilirsiniz.")

# 1. VERİ KONTROLÜ
if 'squad_data' not in st.session_state:
    st.warning("⚠️ Lütfen önce ana sayfadan (FM26 Tactical Wizard) kadro verisinin yüklendiğinden emin olun.")
    st.stop()

df = st.session_state['squad_data']

# 2. OYUNCU SEÇİMİ
player_list = df['Player'].sort_values().tolist()
selected_player = st.selectbox("🔍 Analiz Edilecek Oyuncuyu Seçin:", player_list)

if selected_player:
    # Oyuncunun verilerini çek
    player_row = df[df['Player'] == selected_player].iloc[0]
    position = player_row.get('Position', 'Bilinmiyor')
    age = player_row.get('Age', '-')
    
    st.divider()
    
    # 3. SAYFA TASARIMI (Sol: Radar, Sağ: Roller)
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader(f"👤 {selected_player}")
        st.caption(f"Mevki: {position} | Yaş: {age}")
        
        # --- RADAR GRAFİĞİ (SPIDER CHART) ---
        # Basit bir profil çıkarmak için temel özellikleri 5 ana dalda topluyoruz
        categories = ['Fiziksel', 'Zihinsel', 'Teknik', 'Hücum', 'Savunma']
        
        # Oyuncunun puanlarının ortalamasını alıyoruz
        fizik = player_row[['Pace', 'Acceleration', 'Stamina', 'Strength', 'Agility']].mean()
        zihin = player_row[['Anticipation', 'Decisions', 'Composure', 'Vision', 'Work Rate']].mean()
        teknik = player_row[['Passing', 'First Touch', 'Technique', 'Dribbling']].mean()
        hucum = player_row[['Finishing', 'Off The Ball', 'Crossing']].mean()
        savunma = player_row[['Tackling', 'Marking', 'Positioning']].mean()
        
        values = [fizik, zihin, teknik, hucum, savunma]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]], # Çizgiyi kapatmak için ilk değeri sona ekliyoruz
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(106, 13, 173, 0.4)',
            line=dict(color='#6a0dad', width=2)
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 20])),
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🎯 En Uygun Taktiksel Roller")
        st.markdown("Sistem, oyuncunun özelliklerini **113 Rol DNA'sı** ile eşleştirerek en yüksek potansiyele sahip olduğu rolleri listeledi.")
        
        # En iyi 5 rolü hesapla
        best_roles = get_best_roles_for_player(player_row, FM26_ROLES, top_n=5)
        
        if not best_roles:
            st.error("Rol veritabanında bir sorun oluştu veya oyuncu nitelikleri eksik.")
        else:
            for role_name, score in best_roles:
                # Puanı görselleştirmek için Progress Bar (İlerleme Çubuğu) kullanıyoruz
                st.markdown(f"**{role_name.replace('_', ' - ')}**")
                
                # Renk belirleme (90+ Elit, 80+ İyi, 70+ Ortalama)
                if score >= 85:
                    color = "success"  # Yeşil
                elif score >= 75:
                    color = "warning" # Sarı
                else:
                    color = "danger"   # Kırmızı
                    
                # Streamlit'in native progress bar'ı 0.0 ile 1.0 arası değer alır
                st.progress(score / 100)
                st.caption(f"Uyum Puanı: **%{score}**")

# Yukarıdaki kodlar aynı kalacak... (col1, col2 kısımları)
    
    st.divider()
    
    # 4. SCOUTLAB TARZI İSTATİSTİK KIYASLAMASI (PERCENTILE)
    st.subheader("📊 Per 90 İstatistik Kıyaslaması (Percentile Rank)")
    st.markdown("Oyuncunun maç başı istatistiklerinin **Mustermann** standartlarına göre ligin geri kalanıyla kıyaslanması.")
    
    from utils.benchmarks import MUSTERMANN_THRESHOLDS
    from utils.calculations import get_percentile_tier
    
    # Oyuncunun ana mevkisini bul (GK, DEF, MID, FWD)
    pos_str = str(position).upper()
    if "GK" in pos_str:
        pos_group = "GK"
    elif "D" in pos_str or "WB" in pos_str:
        pos_group = "DEF"
    elif "M" in pos_str or "AM" in pos_str:
        pos_group = "MID"
    elif "ST" in pos_str or "F" in pos_str:
        pos_group = "FWD"
    else:
        pos_group = "MID" # Varsayılan
        
    benchmarks = MUSTERMANN_THRESHOLDS.get(pos_group, {})
    
    if not benchmarks:
        st.info("Bu mevki için kıyaslama verisi bulunamadı.")
    else:
        # İstatistikleri yan yana şık kolonlar halinde gösterelim
        stat_cols = st.columns(len(benchmarks))
        
        for i, (metric_name, thresholds) in enumerate(benchmarks.items()):
            player_val = player_row.get(metric_name, 0)
            # Metrik 'Poss Lost' ise ters hesaplanır (Düşük = İyi)
            is_reverse = True if "Lost" in metric_name or "Conceded" in metric_name else False
            
            tier = get_percentile_tier(player_val, thresholds, reverse=is_reverse)
            
            # Renk ve ikon ataması
            if tier == "Elite":
                color_hex = "#00FF00" # Parlak Yeşil
                icon = "🔥"
            elif tier == "Good":
                color_hex = "#90EE90" # Açık Yeşil
                icon = "✅"
            elif tier == "Average":
                color_hex = "#FFD700" # Sarı
                icon = "⚠️"
            else:
                color_hex = "#FF4500" # Kırmızı
                icon = "❌"
                
            with stat_cols[i]:
                # Streamlit metric component ile şık gösterim
                st.metric(label=metric_name, value=player_val)
                st.markdown(f"<span style='color:{color_hex}; font-weight:bold;'>{icon} {tier}</span>", unsafe_allow_html=True)