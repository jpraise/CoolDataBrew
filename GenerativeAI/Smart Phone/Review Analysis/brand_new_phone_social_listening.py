import pandas as pd
import json
import time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

# Function to validate comparison data consistency
def validate_comparison(data):
    mentioned = data.get("Mentioned", "NA")
    features = data.get("Features compared", "NA")
    # Validation and correction conditions
    if mentioned is False:
        features = "NA"
    elif mentioned is True and (not features or features == "NA"):
        return False
    return True

# Function to analyze reviews using OpenAI's API
def summarize_reviews(reviews_list: list[str], api_key: str):
    client = OpenAI(api_key=api_key)
    
    system_role = """
    You are a product review analysis expert, and your job is to review marketing articles. Note that these articles are scraped from websites and as such may contain information 
    unrelated to articles such as "Home", "Menu", "Go to Content" etc. Identify these elements and ignore them when evaluating the actual articles. Your responsibilities are as follows:
    
    1. Provide a summary for each review:
       - **Customer satisfaction**: Highlight what customers are happy about.
       - **Areas for improvement**: Describe what customers suggest needs to be improved.
       - **Key findings for the review**: Include unexpected insights or notable feedback specific to the review.
       
    2. Identify whether the review contains comparisons to the following brands and specify the characteristics being compared:
       - **Comparison to Xiaomi**: Indicate if the review mentions comparisons to Xiaomi phones. If yes, describe the characteristics compared (e.g., price, camera quality, performance). If no, provide 'NA'.
       - **Comparison to Huawei**: Indicate if the review mentions comparisons to Huawei phones. If yes, describe the characteristics compared (e.g., software, AI capabilities, camera, security). If no, provide 'NA'.
       - **Comparison to Oppo**: Indicate if the review mentions comparisons to Oppo phones. If yes, describe the characteristics compared (e.g., battery life, fast charging, design). If no, provide 'NA'.
       - **Comparison to Chinese brand**: Indicate if the review mentions comparisons to other Chinese phone brands (excluding Xiaomi, Huawei, and Oppo). If yes, describe the characteristics compared (e.g., overall performance, affordability, market positioning). If no, provide 'NA'.
       - **Comparison to Google**: Indicate if the review mentions comparisons to Google phones. If yes, describe the characteristics compared (e.g., software experience, AI capabilities, camera). If no, provide 'NA'.
       - **Comparison to Apple**: Indicate if the review mentions comparisons to Apple phones. If yes, describe the characteristics compared (e.g., design, ecosystem, performance). If no, provide 'NA'.
    
    Present the analysis results in JSON format with the following structure. Ensure all fields are included and responses with undefined categories will be considered invalid.
    Always respond in English regardless of the language used in the review or prompt.

    ### JSON format Example:
    ```json
    {
        "Customer satisfaction": "Customers appreciated the AI-based personalization features and camera quality.",
        "Areas for improvement": "There were concerns about battery life and device durability.",
        "Key findings for the review": "The review highlighted standout AI capabilities and strong chipset performance.",
        "Comparison to Xiaomi": {
            "Mentioned": true,
            "Features compared": "Price, performance"
        },
        "Comparison to Huawei": {
            "Mentioned": false,
            "Features compared": "NA"
        },
        "Comparison to Oppo": {
            "Mentioned": false,
            "Features compared": "NA"
        },
        "Comparison to Chinese brand": {
            "Mentioned": true,
            "Features compared": "Build quality, affordability"
        },
        "Comparison to Google": {
            "Mentioned": false,
            "Features compared": "NA"
        },
        "Comparison to Apple": {
            "Mentioned": true,
            "Features compared": "Design, ecosystem"
        }
    }
    """

    all_data = []
    start_time = time.time()
    
    for idx, review in enumerate(reviews_list):
        user_prompt = f"Analyze the following Galaxy S25 product review:\n'{review}'"
        success = False  # Flag to indicate successful processing
        
        while not success:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    temperature=0.4,
                    messages=[
                        {"role": "system", "content": system_role},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                
                response_content = response.choices[0].message.content
                start_idx = response_content.find("{")
                end_idx = response_content.rfind("}")
                json_string = response_content[start_idx:end_idx + 1]
                
                parsed_json = json.loads(json_string)
                
                # Validate comparison data for each brand
                xiaomi_valid = validate_comparison(parsed_json.get("Comparison to Xiaomi", {}))
                huawei_valid = validate_comparison(parsed_json.get("Comparison to Huawei", {}))
                oppo_valid = validate_comparison(parsed_json.get("Comparison to Oppo", {}))
                chinese_valid = validate_comparison(parsed_json.get("Comparison to Chinese brand", {}))
                google_valid = validate_comparison(parsed_json.get("Comparison to Google", {}))
                apple_valid = validate_comparison(parsed_json.get("Comparison to Apple", {}))
    
                # Retry if validation fails
                if not (xiaomi_valid and huawei_valid and oppo_valid and chinese_valid and google_valid and apple_valid):
                    print(f"Inconsistent comparison data at index {idx}. Retrying...")
                    continue
                
                # Append validated data into the list
                all_data.append({
                    "customer_satisfaction": parsed_json.get("Customer satisfaction", "NA"),
                    "areas_for_improvement": parsed_json.get("Areas for improvement", "NA"),
                    "key_findings": parsed_json.get("Key findings for the review", "NA"),
                    "xiaomi_mentioned": parsed_json.get("Comparison to Xiaomi", {}).get("Mentioned", "NA"),
                    "xiaomi_features": parsed_json.get("Comparison to Xiaomi", {}).get("Features compared", "NA"),
                    "huawei_mentioned": parsed_json.get("Comparison to Huawei", {}).get("Mentioned", "NA"),
                    "huawei_features": parsed_json.get("Comparison to Huawei", {}).get("Features compared", "NA"),
                    "oppo_mentioned": parsed_json.get("Comparison to Oppo", {}).get("Mentioned", "NA"),
                    "oppo_features": parsed_json.get("Comparison to Oppo", {}).get("Features compared", "NA"),
                    "chinese_brand_mentioned": parsed_json.get("Comparison to Chinese brand", {}).get("Mentioned", "NA"),
                    "chinese_brand_features": parsed_json.get("Comparison to Chinese brand", {}).get("Features compared", "NA"),
                    "google_mentioned": parsed_json.get("Comparison to Google", {}).get("Mentioned", "NA"),
                    "google_features": parsed_json.get("Comparison to Google", {}).get("Features compared", "NA"),
                    "apple_mentioned": parsed_json.get("Comparison to Apple", {}).get("Mentioned", "NA"),
                    "apple_features": parsed_json.get("Comparison to Apple", {}).get("Features compared", "NA")
                })
                
                success = True
                time.sleep(5)  # Delay to avoid rate limits
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error at index {idx}: {e}")
                continue
            except KeyError as e:
                print(f"Missing key in response at index {idx}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error at index {idx}: {e}")
                continue

                time.sleep(2)  # Wait before retrying
                
    end_time = time.time()
    print(f"Processed {len(all_data)} reviews successfully.")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    
    return pd.DataFrame(all_data)

# Read the Excel file into a DataFrame and filter relevant reviews
df = pd.read_excel(
    r"file_path_here",
    sheet_name="Sheet1"
)
df = df[df['relevant_yn'] == 1].reset_index(drop=True)

# Extract reviews from the 'final_text' column
reviews = df['final_text'].tolist()

# Split the reviews into three parts for concurrent processing
n = len(reviews)
third = n // 3
review_list1 = reviews[:third]
review_list2 = reviews[third:2 * third]
review_list3 = reviews[2 * third:]

my_openai_api_key = "your_api_key"

# Process reviews concurrently using ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=3) as executor:
    future1 = executor.submit(summarize_reviews, review_list1, my_openai_api_key)
    future2 = executor.submit(summarize_reviews, review_list2, my_openai_api_key)
    future3 = executor.submit(summarize_reviews, review_list3, my_openai_api_key)

# Merge results and save to Excel
df1 = future1.result()
df2 = future2.result()
df3 = future3.result()

result_df = pd.concat([df1, df2, df3], ignore_index=True)
result_df.to_excel(r"file_path_here", index=False)
