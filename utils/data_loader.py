import pandas as pd
import streamlit as st

@st.cache_data
def load_squad_data(file_path):
    """
    FM26'dan export edilen noktalı virgül (;) ayrımına sahip CSV dosyasını okur,
    yüzde (%) işaretlerini ve virgüllü ondalıkları temizleyerek sayısal formata çevirir.
    """
    try:
        # Veriyi oku
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        
        # İçinde '%' geçen sütunları (Örn: Pas %, Hdr %) temizle ve sayıya çevir
        percent_cols = [col for col in df.columns if '%' in col]
        for col in percent_cols:
            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        # Eğer export'ta ondalık sayılar virgülle (,) geldiyse noktaya (.) çevir
        df = df.replace(',', '.', regex=True)
        
        # Sayısal olması gereken tüm sütunları güvenli bir şekilde float/int'e çevir
        cols_to_exclude = ['Player', 'Position']
        numeric_cols = [col for col in df.columns if col not in cols_to_exclude]
        
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        return df
    
    except Exception as e:
        st.error(f"Veri yüklenirken kritik bir hata oluştu: {e}")
        return pd.DataFrame()