# app.py
import streamlit as st
from scraper import scrape_jumia
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

st.title("🛍️ Jumia Product Recommender")

url = st.text_input("Paste any Jumia category/search URL:")

if st.button("Scrape & Recommend"):
    if url:
        with st.spinner("Scraping Jumia... please wait ⏳"):
            df = scrape_jumia(url, max_pages=5)

        if df.empty:
            st.error("No products found. Please check the link.")
        else:
            st.success(f"Found {len(df)} products!")


             # ✅ Round price & rating to 2 decimals
            # if "Price (NGN)" in df.columns:
                # df["Price (NGN)"] = df["Price (NGN)"].apply(lambda x: f"{x:,.0f}")
            # if "Rating" in df.columns:
                # df["Rating"] = df["Rating"].round(1)

            # Show all products
            st.subheader("📋 All Products Scraped")
            st.dataframe(df)

            # Drop products with missing values
            df = df.dropna(subset=["Price (NGN)", "Rating"])

            if df.empty:
                st.warning("No products with both price and rating available.")
            else:
                #  we want to sort using valuescore of the product 
                # If some prices are strings with commas, remove commas first
                df['Price_numeric'] = df['Price (NGN)'].apply(lambda x: float(str(x).replace(',', '')))

                # then you can calculate for value score
                df['ValueScore'] = df['Rating'] / df['Price_numeric']

                # now sort using value score
                df_sorted = df.sort_values(by='ValueScore', ascending=False)

                # Top 10 recommendations
                top10 = df_sorted.head(10).reset_index(drop=True)

                top10["Rating"] = top10["Rating"].apply(lambda x: f"{x:.1f}") #this shows rating as one decimal 5.0 4.5 instead of 5.000 4.5000
                top10["Price (NGN)"] = top10["Price_numeric"].apply(lambda x: f"{x:,.0f}")


                st.subheader("🏆 Top 10 Best Value-for-Money Products")
                st.dataframe(top10[["Product Name", "Price (NGN)", "Rating"]], width=900)

                # Download option
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", csv, "jumia_products.csv", "text/csv")
