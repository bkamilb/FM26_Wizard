import streamlit as st
import pandas as pd
from utils.data_loader import load_squad_data

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="FM26 Tactical Wizard",
    page_icon="🧙‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # --- BAŞLIK VE KARŞILAMA ---
    st.title("🧙‍♂️ FM26 Tactical Wizard")
    st.markdown("""
    **Hoş Geldiniz!** Bu platform; FM26 takımınızın gizli potansiyelini ortaya çıkarmak, 
    113 farklı taktiksel rol ile oyuncu analizi yapmak ve Scoutlab tarzı görselleştirmeler 
    sunmak için sıfırdan inşa edilmiştir.
    """)
    st.info("👈 Analize başlamak için sol menüden bir sayfa seçin.")
    st.divider()

    # --- ARAYÜZDEN DOSYA YÜKLEME ---
    st.subheader("📁 Kadro Verisini Yükle")
    
    # Kullanıcıdan CSV dosyası alıyoruz
    uploaded_file = st.file_uploader("FM26'dan export ettiğiniz kadro dosyasını (CSV) buraya sürükleyin veya seçin:", type=["csv"])
    
    if uploaded_file is not None:
        with st.spinner("Kadro verileri analiz motoruna yükleniyor..."):
            # Pandas, direkt yüklenen dosyayı da okuyabilir, path yazmamıza gerek yok!
            df = load_squad_data(uploaded_file)
            
        if not df.empty:
            # Veriyi diğer sayfalarda kullanabilmek için Session State'e kaydediyoruz
            st.session_state['squad_data'] = df
            st.success(f"✅ Kadro başarıyla yüklendi! Toplam Oyuncu Sayısı: {len(df)}")
            
            # Önizleme
            with st.expander("Kadro Verisini İncele (İlk 5 Oyuncu)"):
                st.dataframe(df.head(), use_container_width=True)
        else:
            st.error("⚠️ Hata: Dosya formatı uygun değil veya içerik boş.")
    else:
        # Eğer henüz dosya yüklenmediyse kullanıcıyı uyar
        st.warning("Uygulamayı kullanmaya başlamak için lütfen yukarıdan CSV dosyanızı yükleyin.")

if __name__ == "__main__":
    main()