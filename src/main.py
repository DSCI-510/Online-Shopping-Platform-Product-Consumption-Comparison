import os
import sys
import Fetch
import Clean
import Classify_gpu
import Visualization_5090
import Visualization_ssd
import Analysis

def ensure_working_directory(expected_dir):
    current_dir = os.getcwd()
    expected_path = os.path.abspath(expected_dir)
    
    if current_dir != expected_path:
        print(f"current dir: {current_dir}")
        print(f"expected dir: {expected_path}")
        print("switching...")
        
        try:
            os.chdir(expected_path)
            print(f"switched to: {os.getcwd()}")
        except Exception as e:
            print(f"fail to switch to the directory: {e}")
            print("please manually swithc: cd", expected_dir)
            sys.exit(1)
    
    return True

def main():

    print("=== Step 1: Fetching Data ===")
    # 5090 (8 pages)
    #Fetch.run_fetch("5090", "../data/raw","newegg_5090_results", 8)
    # 2tb ssd (2 pages)
    #Fetch.run_fetch("2tb ssd", "../data/raw", "newegg_2tb_ssd_results", 2)

    print("\n=== Step 2: Cleaning Data ===")
    Clean.run_cleaning("../data")

    print("\n=== Step 3: Classifying GPU Data ===")
    Classify_gpu.run_classification()

    print("\n=== Step 4: Analyzing GPU Data ===")
    Analysis.run_analysis()

    print("\n=== Step 4: Visualization ===")
    Visualization_5090.run_visualization_5090()
    Visualization_ssd.run_visualization()
    
    print("\n=== All tasks completed. Check 'processed' and 'images' folder. ===")

if __name__ == "__main__":
    ensure_working_directory(os.path.join(os.path.dirname(__file__), "..", "src"))
    main()