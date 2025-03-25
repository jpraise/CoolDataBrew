import time
import json
import pandas as pd
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load the Excel file
file_path = r"file_path_here"
raw = pd.read_excel(file_path, sheet_name='Sheet1', 
                    usecols=['Query Id', 'Query Name', 'Date', 'Title', 'Snippet', 'Full Text', 'Url', 'Domain', 
                            'Sentiment', 'Page Type', 'Thread Entry Type', 'Brand_1', 'Brand_2', 'Category Details', 'BP', 
                             'Country Code', 'Account Type', 'Author'])

# Filter data where 'Brand_1' is not null
raw2 = raw[raw.Brand_1.notnull()].reset_index(drop=True)

# OpenAI API settings
my_openai_api_key = "your_api_key"
client = OpenAI(api_key=my_openai_api_key)

# List of brands to analyze
brands = ["LOEWE", "Bottega Veneta", "Celine", "Miu Miu"]

# OpenAI system prompt configuration
system_prompt = """
    You are a product reviewer, analyzing social media content to determine whether it contains specific topics.
    Using the JSON format provided below, return 51 fields: 
    - 47 binary fields (1 if the topic is present, 0 if not).
    - 1 field for possible categories.
    - 1 field for keywords.
    - 1 field indicating if the content is irrelevant (garbage).
    - 1 field explaining why the content was marked as irrelevant.

    ### JSON format Example:
    ```json
        {
            "logo": 1,
            "Logo-embellished/focused": 1,
            "Subtle/discreet logo/logoless": 0,
            "Featuring an anagram": 1,
            "logo_Others": 0,
            "material": 0,
            "Calfskin leather": 0,
            "Lambskin leather": 0,
            "Canvas": 0,
            "shape": 0,
            "color": 0,
            "Black": 0,
            "size": 1,
            "storage capacity": 0,
            "format": 1,
            "Tote/top handle bags": 0,
            "Crossbody bags": 0,
            "Shoulder bags": 1,
            "Bucket bags": 0,
            "Pouches/clutches": 0,
            "coordinated outfit": 1,
            "For casual looks": 0,
            "possible_categories": "Limited Edition, Seasonal Collection, Pricing",
            "keywords": "Black, Leather, Accessory",
            "garbage_yn": 0,
            "classification_reason": "NA"
        }
    ```
"""

# Dictionary to store final results
brand_results = {}

# Function to process brand data
def process_brand(brand):
    print(f"Processing brand: {brand}")
    brand_data = raw2[raw2['Brand_1'].str.contains(brand, na=False)].reset_index(drop=True)
    text_data = brand_data['Full Text']
    reviews = text_data.to_list()
    results = []

    for idx, review in enumerate(reviews):
        user_prompt = f"Analyze the following social media content:\n'{review}'"
        success = False  

        while not success:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )

                response_content = response.choices[0].message.content
                start_idx = response_content.find("{")
                end_idx = response_content.rfind("}")
                json_string = response_content[start_idx:end_idx + 1]

                parsed_json = json.loads(json_string)
                parsed_json["index"] = idx

                results.append(parsed_json)
                success = True
                print(f"{brand} - {idx} succeed")

            except Exception as e:
                print(f"Error at index {idx} for {brand}. Retrying...")
                print(f"Error: {str(e)}")
                time.sleep(1)

    df = pd.DataFrame(results)

    # Extract topics for each entry
    categories = [
        "logo", "material", "shape", "color", "size", "storage capacity", 
        "format", "coordinated outfit"
    ]
    df['Topic'] = df.apply(lambda row: ', '.join([cat for cat in categories if row.get(cat, 0) == 1]), axis=1)
    brand_df = pd.concat([brand_data, df], axis=1)
    
    return brand, brand_df

# Measure execution time
start_time = time.time()

# Use ThreadPoolExecutor for parallel processing
with ThreadPoolExecutor(max_workers=4) as executor:
    future_to_brand = {executor.submit(process_brand, brand): brand for brand in brands}
    
    for future in as_completed(future_to_brand):
        brand = future_to_brand[future]
        try:
            brand_name, brand_df = future.result()
            brand_results[brand_name] = brand_df
        except Exception as exc:
            print(f'{brand} generated an exception: {exc}')

# Save results to Excel
output_path = r"file_path_here"
with pd.ExcelWriter(output_path) as writer:
    for brand, df in brand_results.items():
        df.to_excel(writer, index=False, sheet_name=brand)

print(f"Results saved to {output_path}")
