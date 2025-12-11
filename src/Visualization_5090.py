import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import seaborn as sns
import os


# Helper functions
def parse_shipping(text):
    if pd.isna(text) or "Free" in str(text):
        return 0
    match = re.search(r"\$(\d+\.?\d*)", str(text))
    return float(match.group(1)) if match else 0


def load_and_prepare_data(csv_path):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found in visualization_5090.")
        return pd.DataFrame()

    df = pd.read_csv(csv_path)

    df["shipping_cost"] = df["shipping"].apply(parse_shipping)
    df["total_price"] = df["price"] + df["shipping_cost"]

    df["brand"] = df["brand"].fillna("Unknown").astype(str).str.strip().str.title()
    df["category"] = df["category"].fillna("Uncategorized").astype(str).str.strip()

    df = df.dropna(subset=["brand", "category", "total_price", "review_count"])
    df["review_count"] = df["review_count"].astype(int)

    return df


# Plot functions
def plot_category_average_price(df):
    if df.empty: return
    
    category_avg = (
        df.groupby("category")["total_price"]
          .mean()
          .sort_values(ascending=False)
          .reset_index()
    )

    try:
        colors = plt.colormaps.get_cmap("Set2").colors
    except AttributeError:
        colors = plt.get_cmap("Set2").colors

    plt.figure(figsize=(10, 5))
    plt.barh(
        category_avg["category"],
        category_avg["total_price"],
        color=colors[:len(category_avg)]
    )

    for i, v in enumerate(category_avg["total_price"]):
        plt.text(v + 10, i, f"${v:.2f}", va="center", fontweight="bold")

    plt.title("Average Price of RTX 5090", fontsize=16, fontweight="bold")
    plt.xlabel("Average Price ($)")
    plt.ylabel("GPU Category")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    output_path = "../data/images/gpu_category_avg_price.png"
    plt.savefig(output_path)
    print(f"Saved {output_path}")
    plt.close()


def plot_brand_by_category(df):
    if df.empty: return

    agg = (
        df.groupby(["category", "brand"])["total_price"]
          .mean()
          .reset_index()
    )

    if agg.empty: return

    categories = (
        agg.groupby("category")["total_price"]
           .mean()
           .sort_values()
           .index
    )

    brand_palette = {
        "Asus": "#92EBE5",
        "Msi": "#F3A17C",
        "Gigabyte": "#078DB5",
        "Zotac": "#C1C1D7",
    }

    n_cats = len(categories)
    if n_cats == 0: return
    
    fig, axes = plt.subplots(1, n_cats, figsize=(16, 5), sharey=True)
    
    if n_cats == 1:
        axes = [axes]

    for ax, cat in zip(axes, categories):
        sub = agg[agg["category"] == cat]

        sns.barplot(
            data=sub,
            x="brand",
            y="total_price",
            palette=brand_palette,
            errorbar=None,
            ax=ax,
        )

        ax.set_title(cat)
        ax.set_xlabel("Brand")
        ax.tick_params(axis="x", rotation=45)

    axes[0].set_ylabel("Average Total Price ($)")
    fig.suptitle(
        "RTX 5090 Price Comparison by Brand within Each Category",
        fontsize=16,
        fontweight="bold",
    )

    plt.tight_layout()
    output_path = "../data/images/gpu_category_bar_brand_consistent_color.png"
    plt.savefig(output_path, dpi=300)
    print(f"Saved {output_path}")
    plt.close()


def plot_sales_market_share(df):
    if df.empty: return

    sales = (
        df.groupby("brand")["review_count"]
          .sum()
          .sort_values(ascending=False)
    )

    if sales.sum() == 0:
        print(" ! No sales data (review counts) available for pie chart.")
        return

    try:
        colors = plt.colormaps.get_cmap("Blues")(np.linspace(0.4, 0.85, len(sales)))
    except AttributeError:
        colors = plt.get_cmap("Blues")(np.linspace(0.4, 0.85, len(sales)))

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        sales.values,
        labels=sales.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        pctdistance=0.75,
        wedgeprops=dict(width=0.35, edgecolor="white"),
    )

    ax.text(0, 0, "GPU Sales\nMarket Share", ha="center", va="center", fontsize=14, weight="bold")
    ax.set_title("Overall GPU Sales Distribution by Brand", pad=20)

    plt.tight_layout()
    output_path = "../data/images/gpu_sales_market_share.png"
    plt.savefig(output_path)
    print(f"Saved {output_path}")
    plt.close()


def plot_price_vs_sales_by_brand(df):
    if df.empty: return

    try:
        colors = plt.colormaps.get_cmap("Set2").colors
    except AttributeError:
        colors = plt.get_cmap("Set2").colors

    fig, ax = plt.subplots(figsize=(10, 5))

    unique_brands = df["brand"].unique()
    for i, brand in enumerate(unique_brands):
        sub = df[df["brand"] == brand].sort_values("total_price")
        if sub.empty: continue
        
        ax.plot(
            sub["total_price"],
            sub["review_count"],
            marker="o",
            linewidth=1.5,
            color=colors[i % len(colors)],
            label=brand,
        )

    ax.set_xlabel("Price")
    ax.set_ylabel("Sales")
    ax.set_title("Price vs. Sales by Brand", fontsize=16, fontweight="bold")
    ax.legend(title="Brand", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    output_path = "../data/images/gpu_price_vs_sales_by_brand.png"
    plt.savefig(output_path)
    print(f"Saved {output_path}")
    plt.close()


def plot_price_vs_sales_by_category(df):
    if df.empty: return

    try:
        colors = plt.colormaps.get_cmap("Set2").colors
    except AttributeError:
        colors = plt.get_cmap("Set2").colors

    category_order = (
        df.groupby("category")["total_price"]
          .mean()
          .sort_values()
          .index
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, cat in enumerate(category_order):
        sub = df[df["category"] == cat].sort_values("total_price")
        if len(sub) < 1:
            continue
        ax.plot(
            sub["total_price"],
            sub["review_count"],
            marker="o",
            linewidth=1.5,
            color=colors[i % len(colors)],
            label=cat,
        )

    ax.set_xlabel("Price")
    ax.set_ylabel("Sales")
    ax.set_title("Price vs. Sales by GPU Category", fontsize=16, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(title="Category", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    output_path = "../data/images/gpu_price_vs_sales_by_category.png"
    plt.savefig(output_path)
    print(f"Saved {output_path}")
    plt.close()


# Main Run Function
def run_visualization_5090():
    print(" --- Starting Advanced 5090 Visualization --- ")
    
    csv_path = "../data/processed/classified_5090.csv"
    
    df = load_and_prepare_data(csv_path)
    
    if not df.empty:
        plot_category_average_price(df)
        plot_brand_by_category(df)
        plot_sales_market_share(df)
        plot_price_vs_sales_by_brand(df)
        plot_price_vs_sales_by_category(df)
    else:
        print(" ! Dataframe is empty, skipping advanced visualization.")
        
    print(" === Advanced 5090 Visualization Completed === \n")

if __name__ == "__main__":
    run_visualization_5090()