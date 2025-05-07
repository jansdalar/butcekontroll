
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Satınalma Bütçe Takip", layout="wide")

st.title("📊 Satınalma Bütçe Takip Uygulaması")

# --- Sidebar'da bütçe belirleme ---
st.sidebar.header("🎯 Yıllık Bütçeni Belirle")

default_budget = {
    "Kategori": ["Ambalaj", "Kimyasal", "Hammadde", "Etiket"],
    "Yıllık Bütçe": [300000, 500000, 800000, 100000]
}
budget_df = pd.DataFrame(default_budget)

uploaded_budget = st.sidebar.file_uploader("Excel ile bütçe yükle (opsiyonel)", type=["xlsx"])

if uploaded_budget:
    budget_df = pd.read_excel(uploaded_budget)

# --- Sipariş Girişi ---
st.subheader("🧾 Yeni Sipariş Girişi")

with st.form("siparis_formu"):
    kategori = st.selectbox("Kategori", budget_df["Kategori"].unique())
    tarih = st.date_input("Sipariş Tarihi", value=datetime.date.today())
    miktar = st.number_input("Miktar", min_value=1, value=100)
    birim_fiyat = st.number_input("Birim Fiyat (₺)", min_value=0.01, value=10.00)
    submitted = st.form_submit_button("Siparişi Kaydet")

# Siparişleri geçici olarak session state'te tut
if "orders" not in st.session_state:
    st.session_state["orders"] = pd.DataFrame(columns=["Tarih", "Kategori", "Miktar", "Birim Fiyat", "Tutar"])

if submitted:
    tutar = miktar * birim_fiyat
    new_order = pd.DataFrame([[tarih, kategori, miktar, birim_fiyat, tutar]],
                             columns=["Tarih", "Kategori", "Miktar", "Birim Fiyat", "Tutar"])
    st.session_state["orders"] = pd.concat([st.session_state["orders"], new_order], ignore_index=True)
    st.success(f"{kategori} için {tutar:,.2f} ₺ tutarında sipariş eklendi.")

# --- Sipariş Tablosu ---
st.subheader("📦 Siparişler")
st.dataframe(st.session_state["orders"], use_container_width=True)

# --- Özet Tablo ---
st.subheader("📌 Bütçe Özeti")

orders_grouped = st.session_state["orders"].groupby("Kategori")["Tutar"].sum().reset_index()
orders_grouped.columns = ["Kategori", "Harcanan"]

summary_df = pd.merge(budget_df, orders_grouped, on="Kategori", how="left").fillna(0)
summary_df["Kalan"] = summary_df["Yıllık Bütçe"] - summary_df["Harcanan"]
summary_df["Kullanım %"] = (summary_df["Harcanan"] / summary_df["Yıllık Bütçe"] * 100).round(2)

st.dataframe(summary_df, use_container_width=True)

# --- Grafik ---
st.subheader("📉 Bütçe Kullanım Grafiği")

import plotly.express as px
fig = px.bar(summary_df, x="Kategori", y="Kullanım %", color="Kullanım %",
             color_continuous_scale="RdYlGn_r", height=400, title="Kategori Bazlı Bütçe Kullanımı (%)")
st.plotly_chart(fig, use_container_width=True)
