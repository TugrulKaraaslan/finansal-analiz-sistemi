import streamlit as st
import pandas as pd

st.title("Rapor Görüntüleyici")

uploaded = st.file_uploader("Rapor Excel’i (.xlsx) seç", type="xlsx")
if uploaded:
    with st.spinner("Yükleniyor..."):
        xls = pd.ExcelFile(uploaded)
        tab1, tab2 = st.tabs(["Özet", "Hatalar"])
        with tab1:
            st.dataframe(pd.read_excel(xls, "Özet"))
        with tab2:
            hatalar = pd.read_excel(xls, "Hatalar")
            st.dataframe(
                hatalar.style.apply(
                    lambda s: [
                        "background-color:#faa" if v != "OK" else "" for v in s["durum"]
                    ],
                    axis=1,
                )
            )
