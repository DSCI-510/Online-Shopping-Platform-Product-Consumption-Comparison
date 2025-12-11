import pandas as pd
import numpy as np
import seaborn as sns
import os
from scipy import stats
import sys

class Tee:
    def __init__(self, *files):
        self.files = files
    
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    
    def flush(self):
        for f in self.files:
            f.flush()

def save_analysis_to_file(gpu_analysis_func, ssd_analysis_func):
    output_dir = '../data/processed'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, 'analysis_results.txt')
 
    original_stdout = sys.stdout
    
    with open(output_file, 'w', encoding='utf-8') as f:
        tee = Tee(original_stdout, f)
        sys.stdout = tee
        
        try:
            gpu_results = gpu_analysis_func()
            ssd_results = ssd_analysis_func()
            
            print("\n" + "=" * 60)
            print("ANALYSIS COMPLETE")
            print("=" * 60)
            print(f"Analysis results saved to: {output_file}")
            
        finally:
            sys.stdout = original_stdout
    
    print(f"\nResults also saved to: {output_file}")
    return gpu_results, ssd_results

def analyze_gpu_data():
    print("=" * 60)
    print("GPU MARKET ANALYSIS")
    print("=" * 60)
    
    # Load classified GPU data
    input_file = '../data/processed/classified_5090.csv'
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return None
    
    df = pd.read_csv(input_file)
    
    # Basic descriptive statistics
    print("\n   1. BASIC DESCRIPTIVE STATISTICS:")
    print("-" * 40)
    print(f"Total Products Analyzed: {len(df)}")
    print(f"Unique Brands: {df['brand'].nunique()}")
    print(f"Brands: {', '.join(sorted(df['brand'].unique()))}")
    
    price_stats = df['price'].describe()
    print(f"\nPrice Statistics:")
    print(f"  Mean Price: ${price_stats['mean']:.2f}")
    print(f"  Median Price: ${price_stats['50%']:.2f}")
    print(f"  Minimum Price: ${price_stats['min']:.2f}")
    print(f"  Maximum Price: ${price_stats['max']:.2f}")
    print(f"  Price Range: ${price_stats['max'] - price_stats['min']:.2f}")
    print(f"  Standard Deviation: ${price_stats['std']:.2f}")
    
    # Category-based analysis
    print("\n   2. CATEGORY-WISE ANALYSIS:")
    print("-" * 40)
    
    categories = ['Water Cooled Flagship', 'Air Cooled Flagship', 'Game-enhanced', 'Basic', 'Uncategorized']
    category_stats = {}
    
    for category in categories:
        if category in df['category'].unique():
            cat_df = df[df['category'] == category]
            stats_dict = {
                'count': len(cat_df),
                'mean_price': cat_df['price'].mean(),
                'median_price': cat_df['price'].median(),
                'min_price': cat_df['price'].min(),
                'max_price': cat_df['price'].max(),
                'price_std': cat_df['price'].std(),
                'brands': cat_df['brand'].nunique(),
                'avg_title_length': cat_df['title'].str.len().mean()
            }
            category_stats[category] = stats_dict
            
            print(f"\n{category}:")
            print(f"  Products: {stats_dict['count']}")
            print(f"  Average Price: ${stats_dict['mean_price']:.2f}")
            print(f"  Price Range: ${stats_dict['min_price']:.2f} - ${stats_dict['max_price']:.2f}")
            print(f"  Unique Brands: {stats_dict['brands']}")
    
    # Brand analysis
    print("\n   3. BRAND ANALYSIS:")
    print("-" * 40)
    
    brand_stats = df.groupby('brand').agg({
        'price': ['count', 'mean', 'median', 'min', 'max', 'std'],
        'title': 'count'
    }).round(2)
    
    brand_stats.columns = ['Count', 'Mean_Price', 'Median_Price', 'Min_Price', 'Max_Price', 'Price_Std', 'Title_Count']
    brand_stats = brand_stats.sort_values('Count', ascending=False)
    
    print("\nTop 5 Brands by Product Count:")
    print(brand_stats.head())
    
    # Price segmentation
    print("\n   4. PRICE SEGMENTATION:")
    print("-" * 40)
    
    # Define price tiers
    price_tiers = {
        'Budget (<$1000)': df[df['price'] < 1000],
        'Mid-range ($1000-$1500)': df[(df['price'] >= 1000) & (df['price'] < 1500)],
        'High-end ($1500-$2000)': df[(df['price'] >= 1500) & (df['price'] < 2000)],
        'Premium (≥$2000)': df[df['price'] >= 2000]
    }
    
    for tier_name, tier_df in price_tiers.items():
        if len(tier_df) > 0:
            print(f"{tier_name}: {len(tier_df)} products (${tier_df['price'].min():.2f}-${tier_df['price'].max():.2f})")
    
    # Statistical tests
    print("\n   5. STATISTICAL TESTS:")
    print("-" * 40)
    
    # Test if there are significant price differences between categories
    category_groups = []
    for category in ['Water Cooled Flagship', 'Air Cooled Flagship', 'Game-enhanced', 'Basic']:
        if category in df['category'].unique():
            category_groups.append(df[df['category'] == category]['price'])
    
    if len(category_groups) >= 2:
        # One-way ANOVA test
        f_stat, p_value = stats.f_oneway(*category_groups)
        print(f"ANOVA Test for Price Differences Between Categories:")
        print(f"  F-statistic: {f_stat:.4f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < 0.05:
            print("  Result: Significant price differences exist between categories (p < 0.05)")
        else:
            print("  Result: No significant price differences between categories")
    
    # Key insights
    print("\n   7. KEY INSIGHTS:")
    print("-" * 40)
    
    # Most expensive brand
    most_expensive_brand = brand_stats.loc[brand_stats['Mean_Price'].idxmax()]
    print(f"• Most expensive brand on average: {most_expensive_brand.name} (${most_expensive_brand['Mean_Price']:.2f})")
    
    # Most popular brand
    most_popular_brand = brand_stats.iloc[0]
    print(f"• Most popular brand by product count: {most_popular_brand.name} ({int(most_popular_brand['Count'])} products)")
    
    # Price premium analysis
    premium_categories = ['Water Cooled Flagship', 'Air Cooled Flagship']
    premium_df = df[df['category'].isin(premium_categories)]
    standard_df = df[df['category'].isin(['Game-enhanced', 'Basic'])]
    
    if len(premium_df) > 0 and len(standard_df) > 0:
        premium_avg = premium_df['price'].mean()
        standard_avg = standard_df['price'].mean()
        premium_pct = ((premium_avg - standard_avg) / standard_avg) * 100
        
        print(f"• Premium categories cost {premium_pct:.1f}% more than standard categories")
        print(f"  (${premium_avg:.2f} vs ${standard_avg:.2f})")
    
    return df, category_stats, brand_stats

def analyze_ssd_data():
    print("\n" + "=" * 60)
    print("SSD MARKET ANALYSIS (2TB)")
    print("=" * 60)
    
    input_file = '../data/processed/cleaned_2t_ssd.csv'
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return None
    
    df = pd.read_csv(input_file)
    
    # Basic statistics
    print(f"\nTotal 2TB SSDs Analyzed: {len(df)}")
    
    if 'price' in df.columns:
        price_stats = df['price'].describe()
        print(f"\nSSD Price Statistics:")
        print(f"  Mean: ${price_stats['mean']:.2f}")
        print(f"  Median: ${price_stats['50%']:.2f}")
        print(f"  Range: ${price_stats['min']:.2f} - ${price_stats['max']:.2f}")
        print(f"  Standard Deviation: ${price_stats['std']:.2f}")
        
        # Price distribution analysis
        price_q1 = df['price'].quantile(0.25)
        price_q3 = df['price'].quantile(0.75)
        price_iqr = price_q3 - price_q1
        print(f"  IQR (Middle 50%): ${price_q1:.2f} - ${price_q3:.2f}")
        
        # Identify outliers using IQR method
        lower_bound = price_q1 - 1.5 * price_iqr
        upper_bound = price_q3 + 1.5 * price_iqr
        outliers = df[(df['price'] < lower_bound) | (df['price'] > upper_bound)]
        print(f"  Potential Price Outliers: {len(outliers)} products")
    
    if 'brand' in df.columns:
        print(f"\nSSD Brands Available: {df['brand'].nunique()}")
        brand_counts = df['brand'].value_counts()
        print(f"\nTop 5 Brands by Product Count:")
        for brand, count in brand_counts.head().items():
            print(f"  {brand}: {count} products")

    if 'price' in df.columns and 'brand' in df.columns:
        brand_price_stats = df.groupby('brand')['price'].agg(['mean', 'median', 'count']).round(2)
        brand_price_stats = brand_price_stats.sort_values('count', ascending=False)
        
        print(f"\nBrand Price Analysis:")
        print(brand_price_stats.head(10))
    
    return df

def run_analysis():
    print(" --- Starting analysis --- ")
    return save_analysis_to_file(analyze_gpu_data, analyze_ssd_data)

#if __name__ == "__main__":
#    run_analysis()