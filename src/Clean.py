import pandas as pd
import os

def run_cleaning(path: str):
    
    data_dir = path
    input_dir = os.path.join(data_dir, 'raw')
    output_dir = os.path.join(data_dir, 'processed')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(" --- Clean GPU data --- ")
    
    # 5090 Data (p8)
    gpu_file = "Raw_newegg_5090_results_p8.csv"
    gpu_path = os.path.join(input_dir, gpu_file)
    if os.path.exists(gpu_path):
        df = pd.read_csv(gpu_path)
        filtered = df[df["title"].str.contains("Graphics Card", case=False, na=False)]
        filtered = filtered.dropna()
        filtered.to_csv(os.path.join(output_dir,"cleaned_5090.csv"), index=False)
        

        print(f"Saved cleaned_5090.csv (from {output_dir})")
    else:
        print(f"Warning: {gpu_file} not found.")

    print(" --- Clean 2T SSD --- ")
    
    # 2T SSD Data (p2)
    ssd_file = "Raw_newegg_2tb_ssd_results_p2.csv"
    ssd_path = os.path.join(input_dir, ssd_file)
    if os.path.exists(ssd_path):
        df = pd.read_csv(ssd_path)
        df.to_csv(os.path.join(output_dir, "cleaned_2t_ssd.csv"), index=False)
        print(f"Saved cleaned_2t_ssd.csv (from {ssd_path})")
    else:
        print(f"Warning: {ssd_path} not found.")

#if __name__ == "__main__":
#    run_cleaning()