import openai
import pandas as pd
import numpy as np

# Load the dataset from the specified location
df = pd.read_excel(r"file_path_here")

# Select the necessary columns
columns_to_select = [
    "Query Id", "Query Name", "Date", "Title", "Snippet", "Full Text", "Url", "Domain", 
    "Sentiment", "Page Type", "Thread Entry Type", "MODEL", "Category Details", 
    "Brand-Pushed", "Language", "Country Code", "Continent Code", "Continent", 
    "Country", "City Code", "Account Type", "Added", "Assignment", "Author", 
    "product", "other_brands", "cross_product", "cross_category", "gift", "celebrity", 
    "wedding_couple", "event", "possible_categories", "keywords", "total_topics"
]

# Create a subset of the dataframe
df_subset = df[columns_to_select]

# Define binary classification columns
binary_columns = [
    "product", "other_brands", "cross_product", "cross_category", 
    "gift", "celebrity", "wedding_couple", "event"
]

# Replace NaN values with 0 and convert binary columns to integer type
df[binary_columns] = df[binary_columns].fillna(0).astype(int)

# Create a subset after processing binary columns
df_subset = df[columns_to_select]

# Set up OpenAI GPT API (ensure you have your OpenAI API key)
openai.api_key = 'your_api_key'

df = df_subset  

# Function to summarize content for each topic category
def generate_summary_for_topic(topic_column, df):
    # Filter rows where the topic column is marked as 1
    topic_rows = df[df[topic_column] == 1]
    
    # Concatenate the 'Full Text' column content for the selected topic
    text_to_summarize = "\n".join(topic_rows['Full Text'].fillna('').values)
    
    # Request a summary from GPT in Korean with 5-6 key points per topic
    print(f"Processing topic '{topic_column}'...")
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"""
                Summarize the following content under the topic '{topic_column}' into 5-6 key points.
                Each point should be concise and formatted with bullet points (•) instead of numbers.
                Ensure to include the essential details using the 5W1H method (Who, What, Where, When, Why, How).
                Avoid redundant or unnecessary information.

                **Example Summary:**

                Summary for 'celebrity':
                • Loewe's Puzzle Bag, launched in 2015, has become an iconic item for the brand.
                • Wang Yibo, a Loewe global ambassador, introduced the 2025 SS collection.
                • Shin Min-a attended Loewe's 2025 S/S collection show in Paris, showcasing a unique style.
                • Seungkwan from SEVENTEEN completed his look with a Loewe 2024 white anagram sweater and denim pants.
                • The Loewe Puzzle Bag is a luxurious item known for its practicality and design.

                Use a similar format to summarize the content below with 5-6 key points:

                {text_to_summarize}
                """
            }
        ],
        max_tokens=200,  # Limit summary length
        temperature=0.7
    )

    return response['choices'][0]['message']['content'].strip()

# List of binary columns representing topic categories
binary_columns = [
    "product", "other_brands", "cross_product", "cross_category", 
    "gift", "celebrity", "wedding_couple", "event"
]

# Generate summaries for each topic category
summaries = {}
for i, column in enumerate(binary_columns, 1):
    print(f"Processing topic {i} of {len(binary_columns)}: {column}...")
    summaries[column] = generate_summary_for_topic(column, df)

# Convert summaries to a pandas DataFrame
summary_df = pd.DataFrame(list(summaries.items()), columns=["Topic", "Summary"])

# Save the summaries to an Excel file
summary_df.to_excel(r"file_path_here", index=False)

print("Summaries have been saved to 'final_summary.xlsx'.")
