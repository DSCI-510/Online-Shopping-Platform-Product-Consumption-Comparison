This section documents the core functions used in the project codebase, detailing their purpose, input parameters, and return types. *No manually input needed*

**Module: `Fetch.py` (Data Collection)**

* `get_headers() -> Dict[str, str]`
    * **Description**: Generates a dictionary of HTTP headers with a randomized User-Agent. This is used to mimic a real browser request and avoid anti-scraping mechanisms.
    * **Returns**: A dictionary containing `User-Agent` and `Accept-Language` headers.

* `fetch_html(url: str) -> Optional[str]`
    * **Description**: Sends a GET request to the specified URL using the generated headers. It handles request exceptions and ensures the response status is valid.
    * **Parameters**: `url` (str) - The target URL to scrape.
    * **Returns**: The raw HTML content string if successful, otherwise `None`.

* `parse_search_page(html: str, keyword: str) -> Tuple[List[Dict], Optional[int]]`
    * **Description**: Parses the raw HTML of a search result page using BeautifulSoup. It extracts product details (title, price, shipping, brand, rating, reviews) and detects pagination limits.
    * **Parameters**:
        * `html` (str): Raw HTML content.
        * `keyword` (str): The search term used (for context).
    * **Returns**: A tuple containing a list of product dictionaries and the maximum page number detected.

* `run_fetch(keyword: str, output_path: str, output_base: str, page_limit: int) -> None`
    * **Description**: The high-level controller function for the scraping process. It constructs the search URL, iterates through pages, and saves the collected data to a CSV file.
    * **Parameters**:
        * `keyword` (str): Search term (e.g., "5090").
        * `output_path` (str): Directory to save raw data.
        * `output_base` (str): Base filename for the CSV.
        * `page_limit` (int): Maximum number of pages to scrape.

**Module: `Clean.py` (Data Cleaning)**

* `run_cleaning(path: str) -> None`
    * **Description**: Executes the data cleaning pipeline. It loads raw CSVs, removes rows with missing values, filters for relevant keywords (e.g., ensuring "Graphics Card" is in the title), and saves the clean data to the `processed` directory.
    * **Parameters**: `path` (str) - The root data directory containing `raw` and `processed` subfolders.

**Module: `Classify_gpu.py` (Data Classification)**

* `classify_gpu_logic(title: str) -> str`
    * **Description**: Applies hierarchical keyword matching to categorize a GPU based on its product title.
    * **Parameters**: `title` (str) - The product title.
    * **Returns**: A string category: 'Water Cooled Flagship', 'Air Cooled Flagship', 'Game-enhanced', 'Basic', or 'Uncategorized'.

* `run_classification() -> None`
    * **Description**: Loads the cleaned GPU dataset, applies `classify_gpu_logic` to create a new `category` column, and saves the enhanced dataset for analysis.

**Module: `Analysis.py` (Statistical Analysis)**

* `analyze_gpu_market() -> Dict[str, Any]`
    * **Description**: Performs descriptive statistics on the GPU dataset, including price mean, median, standard deviation, and performs an ANOVA test to check for price differences between categories.
    * **Returns**: A dictionary containing calculated statistical metrics.

* `analyze_ssd_market() -> Dict[str, Any]`
    * **Description**: Analyzes the SSD dataset, calculating price distribution statistics, identifying outliers using the IQR method, and ranking brands by market share.
    * **Returns**: A dictionary containing SSD market metrics.

**Module: `Visualization_*.py` (Plotting)**

* `parse_shipping(text: Any) -> float`
    * **Description**: A helper function to extract numerical shipping costs from string fields (e.g., converts "+ $9.99 shipping" to `9.99`).
    * **Parameters**: `text` (Any) - The raw shipping text.
    * **Returns**: Float value of the shipping cost (0.0 if free).

* `run_visualization_5090() -> None`
    * **Description**: Generates and saves visualizations for the GPU market, including "Price vs. Sales" scatter plots and "Category Price" bar charts.

* `run_visualization_ssd() -> None`
    * **Description**: Generates and saves visualizations for the SSD market, including "Brand Market Share" pie charts and "Price Distribution" bar charts.