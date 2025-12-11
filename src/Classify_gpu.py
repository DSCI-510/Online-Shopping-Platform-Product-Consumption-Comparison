import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def classify_gpu_logic(title):
    if not isinstance(title, str):
        return 'Uncategorized'
        
    title = title.upper()
    
    water_cooling_keywords = [
        'LIQUID', 'AIO', 'ARCTICSTORM', 'WATER', 'AORUS AI BOX',
        'WATERFORCE'
    ]
    if 'GIGABYTE' in title and (' W-' in title or ' WB-' in title or 'WATERFORCE' in title):
        return 'Water Cooled Flagship'
    elif any(keyword in title for keyword in water_cooling_keywords):
        return 'Water Cooled Flagship'
    

    flagship_air_keywords = [
        'SUPRIM', 'ROG ASTRAL', 'AMP EXTREME', 'AORUS X', 'AORUS ST',
        'AORUS MASTER', 'AORUS ELITE', 'XTREME'
    ]
    if any(keyword in title for keyword in flagship_air_keywords):
        return 'Air Cooled Flagship'
    
    game_enhanced = [
        'GAMING TRIO', 'TUF GAMING', 'VANGUARD', 'AORUS M', 'GAMING OC',
        'AORUS', 'GAMING'
    ]
    if any(keyword in title for keyword in game_enhanced):
        return 'Game-enhanced'
    
    basic_model = ['VENTUS', 'WINDFORCE', 'SOLID']
    if any(keyword in title for keyword in basic_model):
        return 'Basic'
    
    return 'Uncategorized'

def run_classification():
    print(" --- Classify GPU --- ")
    
    input_file = '../data/processed/cleaned_5090.csv'
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    df = pd.read_csv(input_file)
    
    df['category'] = df['title'].apply(classify_gpu_logic)
    
    output_file = '../data/processed/classified_5090.csv'
    df.to_csv(output_file, index=False)
    print(f"Saved classified data to {output_file}")
    
    print("Classification Statistics:")
    print(df['category'].value_counts())
    print("\n")
    
    categories = df['category'].unique()
    order = ['Water Cooled Flagship', 'Air Cooled Flagship', 'Game-enhanced', 'Basic', 'Uncategorized']
    sorted_categories = [c for c in order if c in categories]
    
    for category in sorted_categories:
        print(f"=== {category} ===")
        category_df = df[df['category'] == category][['title', 'brand', 'price']]
        category_df = category_df.sort_values(by='price', ascending=False)
        for _, row in category_df.iterrows():
            title_text = str(row['title'])[:60].ljust(60)
            print(f"- {str(row['brand']):8s}: {title_text}... | ${row['price']:.2f}")
        
        if not category_df.empty:
            print(f"Total: {len(category_df)} products, Avg Price: ${category_df['price'].mean():.2f}\n")
    
    if not df.empty:
        plt.figure(figsize=(12, 8))
    
        category_counts = df['category'].value_counts().reindex(order).dropna()
    
        if not category_counts.empty:
            bar_width = 0.5
            
            colors = plt.cm.Set3(np.arange(len(category_counts)) / len(category_counts))
            
            bars = plt.bar(category_counts.index, category_counts.values, 
                        width=bar_width, color=colors, 
                        linewidth=1.2, alpha=0.85)
            
            plt.title('GPU Category Distribution', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('GPU Category', fontsize=12, fontweight='bold')
            plt.ylabel('Count', fontsize=12, fontweight='bold')
            plt.xticks(rotation=45, ha='right', fontsize=11)
            plt.yticks(fontsize=11)
            
            for bar, value in zip(bars, category_counts.values):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, height + max(category_counts.values)*0.01,
                        f'{value}', ha='center', va='bottom', 
                        fontsize=10, fontweight='bold')
            
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
            
            plt.tight_layout()
            
            if not os.path.exists("../data/images"):
                os.makedirs("../data/images")
            plt.savefig('../data/images/gpu_category_distribution_basic.png')
            plt.close()

#if __name__ == "__main__":
#    run_classification()