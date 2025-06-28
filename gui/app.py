import pandas as pd
import streamlit as st

st.title("Rapor Görüntüleyici")

uploaded = st.file_uploader("Rapor Excel’i (.xlsx) seç", type="xlsx")
if uploaded:
    with st.spinner("Yükleniyor..."):
        xls = pd.ExcelFile(uploaded)
        tab1, tab2 = st.tabs(["Özet", "Hatalar"])
        with tab1:
            df_ozet = pd.read_excel(xls, "Özet")
            if df_ozet.empty:
                warn = (
                    "Filtreniz hiçbir sonuç döndürmedi. Koşulları gevşetmeyi deneyin."
                )
                st.warning(warn)
                print(warn)
            else:
                st.dataframe(df_ozet)
        with tab2:
            hatalar = pd.read_excel(xls, "Hatalar")
            if hatalar.empty:
                st.write("Hata verisi bulunamadı")
            else:
                st.dataframe(
                    hatalar.style.apply(
                        lambda s: [
                            "background-color:#faa" if v != "OK" else ""
                            for v in s["durum"]
                        ],
                        axis=1,
                    )
                )
