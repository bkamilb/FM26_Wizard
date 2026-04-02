import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
from utils.roles_database import FM26_ROLES
from utils.calculations import get_best_roles_for_player, get_percentile_tier

# ==========================================
# SAYFA AYARLARI VE CSS
# ==========================================
st.set_page_config(page_title="Takım Analizi", page_icon="📊", layout="wide")

# X-Düzlemi Hizalaması ve Kart Tasarımı İçin CSS
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    
    /* Analiz Kartları Tasarımı */
    .analysis-card {
        background-color: #1a1e29;
        border: 1px solid #2d3342;
        border-radius: 12px;
        padding: 22px;
        height: 100%;
        display: flex;
        flex-direction: column;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        margin-bottom: 20px;
    }
    
    /* Nitelik kutusuna sabit yükseklik vererek istatistikleri aynı X hizasına çekeriz */
    .attr-container {
        min-height: 400px; 
        flex-grow: 1;
    }
    
    /* Hizalama: İstatistikleri kartın en altına, aynı X hizasına iter */
    .stats-section-wrapper {
        margin-top: auto;
        padding-top: 20px;
        border-top: 1px solid #2d3436;
        margin-bottom: 5px;
    }
    
    .stats-header-text {
        color: #636e72;
        font-size: 0.75rem;
        font-weight: bold;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 15px;
    }

    /* Grid Yapısı */
    .card-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 25px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Tam Kadro Analizi ve Röntgen")
st.markdown("Kadroya genel bir bakış atın, oyuncu detaylarını inceleyin ve takımın kalite dağılımını analiz edin.")

if 'squad_data' not in st.session_state:
    st.warning("⚠️ Lütfen önce ana sayfadan kadro verisinin yüklendiğinden emin olun.")
    st.stop()

df = st.session_state['squad_data']

# ==========================================
# MUSTERMANN & GENEL EŞİKLER
# ==========================================
GENERIC_THRESHOLDS = {
    "Int/90": [0.5, 1.0, 1.5, 2.0], "Poss Won/90": [3.0, 5.0, 7.0, 9.0],
    "Tck A": [0.5, 1.0, 1.5, 2.0], "Tck R": [50.0, 60.0, 70.0, 80.0],
    "Blk/90": [0.1, 0.3, 0.5, 0.8], "Clr/90": [0.5, 1.0, 2.0, 3.0],
    "Hdr %": [40.0, 50.0, 60.0, 70.0], "Aer A/90": [1.0, 2.0, 3.0, 5.0],
    "Goals per 90 minutes": [0.05, 0.15, 0.30, 0.50], "xG/90": [0.1, 0.2, 0.3, 0.4],
    "Shot/90": [0.5, 1.0, 2.0, 3.0], "Drb/90": [0.5, 1.5, 2.5, 4.0],
    "Asts/90": [0.05, 0.10, 0.15, 0.20], "xA/90": [0.05, 0.10, 0.15, 0.20],
    "Ps A/90": [20.0, 30.0, 45.0, 60.0], "Pas %": [75.0, 80.0, 85.0, 90.0],
    "KP/90": [0.5, 1.0, 1.5, 2.0], "OP-KP/90": [0.3, 0.7, 1.2, 1.7],
    "Pr passes/90": [1.0, 2.5, 4.0, 6.0], "Dist/90": [10.0, 11.0, 11.5, 12.0],
    "Pres A/90": [10.0, 15.0, 20.0, 25.0], "Pres C/90": [2.0, 4.0, 6.0, 8.0]
}

MUSTERMANN_THRESHOLDS = {
    "GK": {
        "Poss Won/90": [7.25, 7.62, 8.17, 8.53], "Ps A/90": [21.58, 23.26, 24.38, 26.06],
        "Pr passes/90": [0.37, 0.58, 0.74, 0.98], "Poss Lost/90": [8.21, 6.04, 3.67, 2.35]
    },
    "DEF": {
        "Poss Won/90": [8.33, 9.09, 9.77, 10.54], "Hdr %": [52.4, 60.8, 65.6, 70.7],
        "Aer A/90": [3.15, 3.82, 4.57, 5.35], "Tck R": [72.4, 74.7, 76.7, 79.0],
        "Int/90": [2.38, 2.65, 2.88, 3.12]
    },
    "MID": {
        "Ps A/90": [24.46, 32.74, 41.52, 53.69], "Pas %": [77.5, 82.5, 85.9, 88.6],
        "Pr passes/90": [2.86, 3.99, 5.16, 6.55], "Poss Won/90": [5.12, 6.45, 7.60, 8.90]
    },
    "FWD": {
        "Goals per 90 minutes": [0.15, 0.28, 0.42, 0.58], "xG/90": [0.18, 0.29, 0.40, 0.55],
        "Shot/90": [1.50, 2.10, 2.80, 3.60], "Drb/90": [1.20, 2.50, 4.00, 5.80]
    }
}

# ==========================================
# GÜNCEL OYUNCU GRUPLARI
# ==========================================
OUTFIELD_GROUPS = [
    {
        "name": "⚽ Hücum ve Bitiricilik",
        "attrs": ["Finishing", "Long Shots", "Composure", "Off The Ball", "Anticipation", "Technique", "First Touch", "Heading"],
        "stats": ["Goals per 90 minutes", "xG/90", "Shot/90"]
    },
    {
        "name": "🧠 Yaratıcılık ve Oyun Kurulumu",
        "attrs": ["Passing", "Vision", "Decisions", "Team Work", "Dribbling", "Flair", "Technique", "First Touch", "Crossing"],
        "stats": ["Ps A/90", "Pas %", "KP/90", "Pr passes/90", "Asts/90", "xA/90", "Drb/90"]
    },
    {
        "name": "🛡️ Savunma ve Çalışkanlık",
        "attrs": ["Tackling", "Marking", "Positioning", "Anticipation", "Concentration", "Team Work", "Work Rate", "Aggression", "Bravery"],
        "stats": ["Poss Won/90", "Int/90", "Tck R", "Blk/90", "Clr/90", "Pres A/90"]
    },
    {
        "name": "🏃‍♂️ Fiziksel Kapasite ve Atletizm",
        "attrs": ["Pace", "Acceleration", "Agility", "Balance", "Stamina", "Work Rate", "Strength"],
        "stats": ["Dist/90", "Aer A/90", "Hdr %"]
    }
]

GK_GROUPS = [
    {
        "name": "🧤 Kaleci Refleks ve Kurtarış",
        "attrs": ["Handling", "Reflexes", "One On Ones", "Aerial Reach", "Agility", "Concentration"],
        "stats": ["Poss Won/90"]
    },
    {
        "name": "🧠 Kaleci Alan Savunması",
        "attrs": ["Command Of Area", "Communication", "Positioning", "Anticipation", "Rushing Out (Tendency)", "Decisions"],
        "stats": []
    },
    {
        "name": "👟 Kaleci Dağıtım (Pas)",
        "attrs": ["Kicking", "Throwing", "Passing", "Vision", "First Touch", "Composure"],
        "stats": ["Ps A/90", "Pr passes/90", "Poss Lost/90"]
    },
    {
        "name": "🏃‍♂️ Kaleci Atletizm",
        "attrs": ["Pace", "Acceleration", "Jumping Reach", "Strength", "Balance"],
        "stats": []
    }
]

# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================
def get_pos_group(pos_str):
    p = str(pos_str).upper()
    if "GK" in p: return "GK"
    elif any(x in p for x in ["D ", "D(", "WB", "D/WB"]): return "DEF"
    elif any(x in p for x in ["M ", "M(", "AM"]): return "MID"
    else: return "FWD"

def get_thresholds_for_stat(pos_group, stat_name):
    if pos_group in MUSTERMANN_THRESHOLDS and stat_name in MUSTERMANN_THRESHOLDS[pos_group]:
        return MUSTERMANN_THRESHOLDS[pos_group][stat_name]
    if stat_name in GENERIC_THRESHOLDS: return GENERIC_THRESHOLDS[stat_name]
    return [0.1, 0.2, 0.3, 0.4]

def get_percentile_value(value, thresholds, reverse=False):
    try: 
        val = float(value)
        if pd.isna(val): val = 0.0 
    except: return 0
    t = thresholds
    if len(t) < 4 or t[3] == t[0]: return 50 
    
    if not reverse:
        if val <= t[0]: return 5
        elif val >= t[3]: return 95
        else: return 5 + (val - t[0]) * (90) / (t[3] - t[0])
    else:
        if val >= t[0]: return 5
        elif val <= t[3]: return 95
        else: return 5 + (t[0] - val) * (90) / (t[0] - t[3])

def get_attr_val(row, attr_name):
    if attr_name in row: return row[attr_name]
    clean = attr_name.replace(" ", "").lower()
    for col in row.index:
        if col.replace(" ", "").lower() == clean:
            return row[col]
    return 0

# ==========================================
# GÖRSEL RENDERERLAR
# ==========================================
def render_attribute_bar(name, value):
    try: val = int(value)
    except: val = 0
    perc = (val / 20) * 100
    color = "#1DD1A1" if val >= 15 else "#FECA57" if val >= 11 else "#FF6B6B"
    track = "rgba(29, 209, 161, 0.2)" if val >= 15 else "rgba(254, 202, 87, 0.2)" if val >= 11 else "rgba(255, 107, 107, 0.2)"
    
    return f"""
    <div style='margin-bottom: 8px;'>
        <div style='display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 3px;'>
            <span style='color: #b2bec3; font-weight: 500;'>{name}</span>
            <span style='font-weight: 700; color: #fff;'>{val}</span>
        </div>
        <div style='width: 100%; background-color: {track}; height: 6px; border-radius: 4px;'>
            <div style='width: {perc}%; background-color: {color}; height: 100%; border-radius: 4px;'></div>
        </div>
    </div>
    """

def render_scoutlab_stat_bar(metric_name, value, thresholds, perc):
    color = "#1DD1A1" if perc >= 75 else "#10AC84" if perc >= 50 else "#FECA57" if perc >= 25 else "#FF6B6B"
    track = "rgba(29, 209, 161, 0.15)" if perc >= 75 else "rgba(16, 172, 132, 0.15)" if perc >= 50 else "rgba(254, 202, 87, 0.15)" if perc >= 25 else "rgba(255, 107, 107, 0.15)"
    display_val = f"{float(value):.2f}"
    
    return f"""
    <div style='margin-bottom: 12px;'>
        <div style='display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px;'>
            <span style='color: #dfe6e9; font-size: 0.85rem;'>{metric_name}</span>
            <div style='text-align: right;'>
                <span style='font-size: 1.1rem; font-weight: bold; color: #fff;'>{display_val}</span>
                <span style='font-size: 0.75rem; color: {color}; font-weight: bold;'>%{int(perc)}</span>
            </div>
        </div>
        <div style='width: 100%; background-color: {track}; height: 8px; border-radius: 4px; position: relative;'>
            <div style='width: {perc}%; background-color: {color}; height: 100%; border-radius: 4px;'></div>
        </div>
    </div>
    """

# ==========================================
# POP-UP (DIALOG) FONKSİYONU
# ==========================================
@st.dialog("👤 Gelişmiş Oyuncu Analizi", width="large")
def show_player_popup(player_name):
    player_row = df[df['Player'] == player_name].iloc[0]
    position = str(player_row.get('Position', 'Bilinmiyor'))
    pos_group = get_pos_group(position)
    
    # Dinamik Mevki Kıyaslaması
    roles_regex = r"(GK|D|WB|M|AM|ST)"
    target_roles = set(re.findall(roles_regex, position))
    
    def matches_target(pos_str):
        if not isinstance(pos_str, str): return False
        player_roles = set(re.findall(roles_regex, pos_str))
        return not target_roles.isdisjoint(player_roles)

    same_pos_df = df[df['Position'].apply(matches_target)].copy()

    best_roles = get_best_roles_for_player(player_row, FM26_ROLES, top_n=1)
    score = int(best_roles[0][1]) if best_roles else 0
    t_color = "#1DD1A1" if score >= 85 else "#10AC84" if score >= 75 else "#FECA57" if score >= 65 else "#FF6B6B"
    t_text = "ROTASYON" if 65 <= score < 75 else "YETERLİ" if 75 <= score < 85 else "ELİT" if score >= 85 else "YETERSİZ"

    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1e272e 0%, #000000 100%); padding: 20px 30px; border-radius: 12px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; border-left: 8px solid {t_color};'>
        <div style='display: flex; align-items: center; gap: 20px;'>
            <div style='width: 60px; height: 60px; border-radius: 50%; background: #2d3436; display: flex; justify-content: center; align-items: center; font-size: 2rem;'>👤</div>
            <div>
                <h1 style='margin:0; color: #fff; font-size: 2.2rem; letter-spacing: -0.5px;'>{player_name}</h1>
                <div style='margin-top: 5px; display: flex; gap: 12px; align-items: center;'>
                    <span style='background-color: {t_color}; color: black; padding: 2px 10px; border-radius: 20px; font-weight: bold; font-size: 0.8rem;'>{position}</span>
                    <span style='color: #b2bec3; font-size: 0.9rem;'>Yaş: {player_row.get('Age', '-')}</span>
                </div>
            </div>
        </div>
        <div style='text-align: right;'>
            <div style='color: {t_color}; font-weight: bold; font-size: 1.2rem;'>{t_text}</div>
            <div style='color: #636e72; font-size: 0.7rem;'>Uyum Skoru</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📑 Profil ve İstatistikler", "📊 Grafik & Matris Merkezi"])
    
    with tab1:
        groups = GK_GROUPS if pos_group == "GK" else OUTFIELD_GROUPS
        for row_idx in range(0, 4, 2):
            cols = st.columns(2)
            for col_idx in range(2):
                with cols[col_idx]:
                    grp = groups[row_idx + col_idx]
                    card_html = f"""
                    <div class='analysis-card'>
                        <div style='padding: 15px 20px; border-bottom: 1px solid #2d3342;'>
                            <h4 style='margin: 0; color: #74b9ff; font-size: 1.15rem; font-weight: 600;'>{grp["name"]}</h4>
                        </div>
                        <div style='padding: 20px; flex-grow: 1; display: flex; flex-direction: column;'>
                            <div class='attr-container'>
                                <div style='margin-bottom: 15px;'><span style='color:#636e72; font-size: 0.75rem; font-weight:bold; letter-spacing: 1px; text-transform: uppercase;'>1-20 Nitelikleri</span></div>
                    """
                    valid_attrs = []
                    for attr in grp["attrs"]:
                        val = get_attr_val(player_row, attr)
                        try:
                            v = int(val)
                            valid_attrs.append(v)
                            card_html += render_attribute_bar(attr, v)
                        except: pass
                    
                    avg_attr = np.mean(valid_attrs) if valid_attrs else 0
                    card_html += f"<div style='text-align: right; font-size: 0.8rem; color: #b2bec3; margin-top: 8px;'>Ortalama: <strong style='color:#fff;'>{avg_attr:.1f}</strong></div></div>"
                    
                    if grp["stats"]:
                        card_html += "<div class='stats-section-wrapper'><div class='stats-header-text'>Performans (Başarı Sıralı)</div>"
                        stat_results = []
                        for stat in grp["stats"]:
                            if stat in df.columns:
                                val = player_row.get(stat, 0)
                                thresholds = get_thresholds_for_stat(pos_group, stat)
                                is_rev = True if any(x in stat for x in ["Lost", "Conceded"]) else False
                                perc = get_percentile_value(val, thresholds, is_rev)
                                stat_results.append({'name': stat, 'val': val, 'perc': perc, 't': thresholds})
                        stat_results.sort(key=lambda x: x['perc'], reverse=True)
                        for s in stat_results:
                            card_html += render_scoutlab_stat_bar(s['name'], s['val'], s['t'], s['perc'])
                        card_html += "</div>"
                    card_html += "</div></div>"
                    st.markdown(card_html, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🕸️ Gelişmiş Grafik ve Matris Merkezi")
        
        # Grafik Helper
        def draw_scatter_matrix(x_col, y_col, title, color_hex="#1DD1A1"):
            if x_col in same_pos_df.columns and y_col in same_pos_df.columns:
                m_df = same_pos_df.dropna(subset=[x_col, y_col]).copy()
                m_df['Durum'] = m_df['Player'].apply(lambda x: "Seçili Oyuncu" if x == player_name else "Diğer Mevkidaşlar")
                fig = px.scatter(m_df, x=x_col, y=y_col, hover_name="Player", color="Durum",
                                 color_discrete_map={"Seçili Oyuncu": color_hex, "Diğer Mevkidaşlar": "#4b5563"},
                                 title=title, template="plotly_dark")
                fig.update_traces(marker=dict(size=14, line=dict(width=1.5, color='#111827')))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#dfe6e9'),
                                  legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, title=""))
                return fig
            return None

        # --- RADAR VE BİRİNCİL MATRİS ---
        r_col, m_col = st.columns(2)
        with r_col:
            st.markdown(f"##### 🎯 Yetenek Radarı ({player_name} vs {position})")
            cats = ['Fiziksel', 'Zihinsel', 'Teknik', 'Hücum', 'Savunma']
            p_vals = [
                player_row[['Pace', 'Acceleration', 'Stamina', 'Strength']].mean(),
                player_row[['Anticipation', 'Decisions', 'Composure', 'Vision']].mean(),
                player_row[['Passing', 'First Touch', 'Technique']].mean(),
                player_row[['Finishing', 'Off The Ball']].mean(),
                player_row[['Tackling', 'Marking', 'Positioning']].mean()
            ]
            t_vals = [
                same_pos_df[['Pace', 'Acceleration', 'Stamina', 'Strength']].mean().mean(),
                same_pos_df[['Anticipation', 'Decisions', 'Composure', 'Vision']].mean().mean(),
                same_pos_df[['Passing', 'First Touch', 'Technique']].mean().mean(),
                same_pos_df[['Finishing', 'Off The Ball']].mean().mean(),
                same_pos_df[['Tackling', 'Marking', 'Positioning']].mean().mean()
            ]
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=p_vals + [p_vals[0]], theta=cats + [cats[0]], fill='toself', fillcolor='rgba(29, 209, 161, 0.3)', line=dict(color='#1DD1A1', width=2.5), name=player_name))
            fig.add_trace(go.Scatterpolar(r=t_vals + [t_vals[0]], theta=cats + [cats[0]], fill='none', line=dict(color='#636e72', width=2, dash='dash'), name='Mevki Ort.'))
            fig.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=True, range=[0, 20], gridcolor='#333')), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True, margin=dict(l=50, r=50, t=30, b=30))
            st.plotly_chart(fig, use_container_width=True, theme=None)
        
        with m_col:
            # 1. Matris: Mevkiye Göre Birincil Performans
            if pos_group == "FWD": x1, y1, t1 = "xG/90", "Goals per 90 minutes", "Bitiricilik Verimliliği"
            elif pos_group == "DEF": x1, y1, t1 = "Poss Won/90", "Int/90", "Savunma Aktifliği"
            elif pos_group == "MID": x1, y1, t1 = "Ps A/90", "Pas %", "Pas Dağıtımı ve Güven"
            else: x1, y1, t1 = "Ps A/90", "Pas %", "Genel Katkı"
            fig1 = draw_scatter_matrix(x1, y1, t1)
            if fig1: st.plotly_chart(fig1, use_container_width=True, theme=None)

        st.divider()

        # --- İKİNCİL VE ÜÇÜNCÜL MATRİSLER ---
        m_col2, m_col3 = st.columns(2)
        with m_col2:
            # 2. Matris: Yaratıcılık / Tehdit
            if pos_group == "FWD": x2, y2, t2 = "Shot/90", "Drb/90", "Hücum Tehdidi"
            elif pos_group == "MID": x2, y2, t2 = "Pr passes/90", "KP/90", "Yaratıcılık Matrisi"
            elif pos_group == "DEF": x2, y2, t2 = "Aer A/90", "Hdr %", "Hava Topu Hakimiyeti"
            else: x2, y2, t2 = "Pr passes/90", "KP/90", "Oyun Kurulumu"
            fig2 = draw_scatter_matrix(x2, y2, t2, "#FECA57")
            if fig2: st.plotly_chart(fig2, use_container_width=True, theme=None)
            
        with m_col3:
            # 3. Matris: Genel Etki / Defansif Verimlilik
            if pos_group == "FWD": x3, y3, t3 = "xG/90", "Asts/90", "Skor Katkısı"
            elif pos_group == "MID": x3, y3, t3 = "Poss Won/90", "Int/90", "Defansif Orta Saha Katkısı"
            elif pos_group == "DEF": x3, y3, t3 = "Tck A", "Tck R", "Müdahale Kalitesi"
            else: x3, y3, t3 = "Poss Won/90", "Int/90", "Defansif Katkı"
            fig3 = draw_scatter_matrix(x3, y3, t3, "#74b9ff")
            if fig3: st.plotly_chart(fig3, use_container_width=True, theme=None)

        st.divider()

        # --- PERFORMANS DAĞILIMI (PERCENTILE ÖZETİ) ---
        st.markdown("##### 📈 Mustermann Metrik Özeti (Percentile)")
        m_stats = MUSTERMANN_THRESHOLDS.get(pos_group, GENERIC_THRESHOLDS).keys()
        perc_data = []
        for s in m_stats:
            if s in df.columns:
                val = player_row.get(s, 0)
                thr = get_thresholds_for_stat(pos_group, s)
                rev = True if any(x in s for x in ["Lost", "Conceded"]) else False
                p = get_percentile_value(val, thr, rev)
                perc_data.append({"Metrik": s, "Percentile": p})
        
        if perc_data:
            perc_df = pd.DataFrame(perc_data).sort_values("Percentile", ascending=True)
            fig_bar = px.bar(perc_df, x="Percentile", y="Metrik", orientation='h',
                             color="Percentile", color_continuous_scale="Viridis",
                             range_x=[0, 100], template="plotly_dark")
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  coloraxis_showscale=False, height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True, theme=None)

# ==========================================
# ANA SAYFA: TABLO VE SEÇİM
# ==========================================
st.subheader("📋 Takım Kadrosu ve Seçim")
st.info("Aşağıdaki tablodan bir satıra tıklayarak oyuncuyu seçin, ardından Profillendir butonuna basın.")

base_cols = ['Player', 'Position', 'Age', 'Minutes', 'Average Rating']
display_cols = [c for c in base_cols if c in df.columns]

# Seçim ve Aksiyon Alanı
c_table, c_action = st.columns([4, 1])

with c_table:
    # Dinamik yükseklik
    table_height = (len(df) + 1) * 35 + 3
    selection_event = st.dataframe(
        df[display_cols],
        use_container_width=True,
        hide_index=True,
        height=table_height,
        selection_mode="single-row",
        on_select="rerun"
    )

with c_action:
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    selected_rows = selection_event.selection.rows
    
    if selected_rows:
        target_name = df.iloc[selected_rows[0]]['Player']
        st.success(f"Seçili: **{target_name}**")
        if st.button("Profillendir ↗️", type="primary", use_container_width=True):
            show_player_popup(target_name)
    else:
        st.warning("Lütfen tablodan bir oyuncu seçin.")

st.divider()

# ==========================================
# KADRO RÖNTGENİ
# ==========================================
st.subheader("🚨 Kadro Röntgeni")
squad_health = []
for index, row in df.iterrows():
    best_roles = get_best_roles_for_player(row, FM26_ROLES, top_n=1)
    score = best_roles[0][1] if best_roles else 0
    if score >= 85: tier = "🔥 Elit"
    elif score >= 75: tier = "✅ Yeterli"
    elif score >= 65: tier = "⚠️ Rotasyon"
    else: tier = "❌ Yetersiz"
    squad_health.append({
        "Oyuncu": row['Player'], "Grup": get_pos_group(row.get('Position', '')),
        "Max Uyum": score, "Sınıf": tier
    })
health_df = pd.DataFrame(squad_health)
tier_counts = health_df['Sınıf'].value_counts()

c1, c2, c3, c4 = st.columns(4)
c1.metric("🔥 Elit", tier_counts.get("🔥 Elit", 0))
c2.metric("✅ Yeterli", tier_counts.get("✅ Yeterli", 0))
c3.metric("⚠️ Rotasyon", tier_counts.get("⚠️ Rotasyon", 0))
c4.metric("❌ Yetersiz", tier_counts.get("❌ Yetersiz", 0))

g1, g2 = st.columns([1.5, 1])
with g1:
    fig = px.histogram(health_df, x="Grup", color="Sınıf", barmode="group",
                       color_discrete_map={"🔥 Elit": "#1DD1A1", "✅ Yeterli": "#10AC84", "⚠️ Rotasyon": "#FECA57", "❌ Yetersiz": "#FF6B6B"},
                       template="plotly_dark")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True, theme=None)
with g2:
    st.dataframe(health_df.sort_values("Max Uyum", ascending=False), use_container_width=True, hide_index=True, height=400)