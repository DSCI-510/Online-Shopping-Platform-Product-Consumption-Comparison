import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import warnings
warnings.filterwarnings('ignore')

def parse_shipping(text):
    if pd.isna(text) or 'Free' in str(text):
        return 0
    match = re.search(r'(\d+\.\d+)', str(text))
    return float(match.group(1)) if match else 0

def run_visualization():
    print(" --- Starting SSD Visualization --- ")
    
    input_file = '../data/processed/cleaned_2t_ssd.csv'
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Cannot proceed with visualization.")
        return

    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    sns.set_style("whitegrid")
    
    df = pd.read_csv(input_file)
    
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce')
    
    df['shipping_cost'] = df['shipping'].apply(parse_shipping)
    df['total_price'] = df['price'] + df['shipping_cost']
    

    brand_avg_price = df.groupby('brand')['total_price'].mean().sort_values(ascending=False).reset_index()
    if not brand_avg_price.empty:
        plt.figure(figsize=(12, 8))
        barplot = sns.barplot(x='total_price', y='brand', data=brand_avg_price, palette='viridis')
        plt.title('Average Price of 2TB SSDs by Brand (Incl. Shipping)', fontsize=16)
        plt.xlabel('Average Price ($)', fontsize=12)
        plt.ylabel('Brand', fontsize=12)
        for i, v in enumerate(brand_avg_price['total_price']):
            barplot.text(v + 1, i, f"${v:.1f}", color='black', va='center', fontweight='bold')
        plt.tight_layout()
        output_path = "../data/images/ssd_brand_avg_price.png"
        plt.savefig(output_path)
        print(f"Saved {output_path}")
        plt.close()

    if 'brand' in df.columns and 'review_count' in df.columns:
        top_brands_sales = df.groupby('brand')['review_count'].sum().sort_values(ascending=True).tail(15)
        if not top_brands_sales.empty:
            plt.figure(figsize=(12, 8))
            bars = plt.barh(range(len(top_brands_sales)), top_brands_sales.values,
                            color=plt.cm.coolwarm(np.linspace(0.2, 0.8, len(top_brands_sales))))
            plt.title('Top 15 Brands by Sales Proxy (Review Count)', fontsize=16, fontweight='bold')
            plt.xlabel('Total Reviews', fontsize=12)
            plt.ylabel('Brand', fontsize=12)
            plt.yticks(range(len(top_brands_sales)), top_brands_sales.index)
            for i, (bar, value) in enumerate(zip(bars, top_brands_sales.values)):
                plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2,
                         f'{int(value):,}', ha='left', va='center', fontsize=10, fontweight='bold')
            plt.tight_layout()
            output_path = "../data/images/ssd_top_brands_sales.png"
            plt.savefig(output_path)
            print(f"Saved {output_path}")
            plt.close()

    if 'total_price' in df.columns:
        plt.figure(figsize=(10, 6))
        price_clean = df['price'].dropna()
        sns.histplot(price_clean, bins=30, kde=True, color='skyblue')
        plt.title('2TB SSD Price Distribution', fontsize=16, fontweight='bold')
        plt.xlabel('Total Price ($)', fontsize=12)
        plt.ylabel('Count(Frequency)', fontsize=12)
        plt.axvline(price_clean.mean(), color='red', linestyle='dashed', linewidth=2, label=f'mean price: ${price_clean.mean():.2f}')
        plt.grid(True, alpha=0.6)
        plt.tight_layout()
        output_path = "../data/images/ssd_price_distribution.png"
        plt.savefig(output_path)
        print(f"Saved {output_path}")
        plt.close()

    if 'review_count' in df.columns:
        # brand sales distribution pie chart
        plt.figure(figsize=(10, 8))
        brand_sales = df.groupby('brand')['review_count'].sum().fillna(0)
        brand_sales = brand_sales.sort_values(ascending=False)

        # top 10 brands, others combined
        top_n = 5
        top_brands_sales = brand_sales.head(top_n)
        other_sales = brand_sales[top_n:].sum()

        if other_sales > 0:
            sales_data = pd.concat([top_brands_sales, pd.Series({'Others': other_sales})])
        else:
            sales_data = top_brands_sales

        labels = sales_data.index
        sizes = sales_data.values
        colors = plt.cm.tab20c(np.arange(len(labels)))

        wedges, texts, autotexts = plt.pie(sizes, 
                                            labels=labels,
                                            autopct='%1.1f%%',
                                            startangle=90,
                                            colors=colors,
                                            textprops={'fontsize': 8},
                                            pctdistance=0.75)

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        plt.title(f'Top {top_n} brand distribution', fontsize=20, fontweight='bold')
        plt.tight_layout()

        output_path = "../data/images/ssd_brand_sales_distribution.png"
        plt.savefig(output_path)
        print(f"Saved {output_path}")
        plt.close()

    print(" === SSD Visualization Completed === \n")

if __name__ == "__main__":
    run_visualization()