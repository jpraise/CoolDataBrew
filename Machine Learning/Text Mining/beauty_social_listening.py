import re
import pandas as pd
from konlpy.tag import Kkma
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import time

def remove_emojis(data):
    """Remove emojis and special characters"""
    emoj = re.compile(
        "["
        u"\U00002700-\U000027BF"  # Dingbats
        u"\U0001F600-\U0001F64F"  # Emoticons
        u"\U00002600-\U000026FF"  # Miscellaneous Symbols
        u"\U0001F300-\U0001F5FF"  # Miscellaneous Symbols And Pictographs
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        u"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
        "]",
        re.UNICODE
    )
    return re.sub(emoj, '', data)

def clean_text(text):
    """Clean text: Remove broken characters and extract only valid characters"""
    if isinstance(text, str):
        byte_string = text.encode('utf-8', errors='ignore')
    else:
        byte_string = text

    # Define hashtag pattern
    hashtag_pattern = re.compile(r'#[\w가-힣]+')
    hashtags = hashtag_pattern.findall(text)

    # Extract valid Korean, English, and numeric characters
    cleaned_text = ''
    i = 0
    while i < len(byte_string):
        if 0xEA <= byte_string[i] <= 0xED:  # Korean character range
            if i + 2 < len(byte_string):
                cleaned_text += byte_string[i:i+3].decode('utf-8', errors='ignore')
                i += 3
            else:
                i += 1
        elif 0x41 <= byte_string[i] <= 0x5A or 0x61 <= byte_string[i] <= 0x7A or 0x30 <= byte_string[i] <= 0x39:  # English letters, numbers
            cleaned_text += chr(byte_string[i])
            i += 1
        else:
            i += 1

    # Add hashtags back
    cleaned_text += ' ' + ' '.join(hashtags)

    return ' '.join(cleaned_text.split())

# Define inclusion and exclusion word lists
preserve_words = [
    '추웠다', '재밌다', '체험했다', '만족했다', '놀랐다', '개선됐다', '편리했다', '공감했다', 
    '참여했다', '발견했다', '변화했다', '추천했다', '글로스', '글로우', '센슈얼', '블러쉬'
]

excluded_words = [
    "에는", "마다", "에서", "처럼", "으로", "에요", "예요", "이고", "그리고", "하지만", 
    "그러나", "또한", "하며", "하고", "이런", "이렇게", "이제", "하다", "있다", "되어", 
    "합니다", "했어요", "한다", "있죠", "같은", "싶은", "더욱", "그냥"
]

def preserve_specific_words(text, words_to_preserve):
    """Temporarily replace specific words to preserve them"""
    for idx, word in enumerate(words_to_preserve):
        text = re.sub(word, f"PRESERVED_WORD_{idx}", text, flags=re.IGNORECASE)
    return text

def restore_preserved_words(text, words_to_preserve):
    """Restore temporarily replaced words back to original"""
    for idx, word in enumerate(words_to_preserve):
        text = text.replace(f"PRESERVED_WORD_{idx}", word)
    return text

def get_results(kr_data: pd.Series | list[str], excluded_words: list[str], preserve_words: list[str]) -> dict:
    data_dict = {
        "comment_id": [],
        "word_fragment": [],
        "word_type": [],
        "word_count": []
    }
    kkma = Kkma()
    hashtag_pattern = re.compile(r'#[\w가-힣]+')

    for index, sentence in enumerate(kr_data):
        cleaned_sentence = clean_text(sentence)
        if not cleaned_sentence:
            continue

        preserved_sentence = preserve_specific_words(cleaned_sentence, preserve_words)
        
        # Extract hashtags
        hashtags = hashtag_pattern.findall(cleaned_sentence)
        
        try:
            sentence_array = kkma.pos(preserved_sentence)
            for word, pos in sentence_array:
                word = restore_preserved_words(word, preserve_words)
                if word not in excluded_words:
                    data_dict["comment_id"].append(f"COMMENT_{str(index + 1).zfill(6)}")
                    data_dict["word_fragment"].append(word)
                    data_dict["word_type"].append(pos)
                    data_dict["word_count"].append(1)

            # Add hashtags
            for hashtag in hashtags:
                data_dict["comment_id"].append(f"COMMENT_{str(index + 1).zfill(6)}")
                data_dict["word_fragment"].append(hashtag)
                data_dict["word_type"].append('HASHTAG')
                data_dict["word_count"].append(1)

            # Add words from preserve_words
            for word in preserve_words:
                if word in cleaned_sentence:
                    data_dict["comment_id"].append(f"COMMENT_{str(index + 1).zfill(6)}")
                    data_dict["word_fragment"].append(word)
                    data_dict["word_type"].append('PRESERVED')
                    data_dict["word_count"].append(1)

        except Exception as e:
            print(f"Error in processing sentence: {cleaned_sentence[:50]}... -> {e}")
            words = re.findall(r'\w+', cleaned_sentence)
            for word in words:
                word = restore_preserved_words(word, preserve_words)
                if word not in excluded_words:
                    data_dict["comment_id"].append(f"COMMENT_{str(index + 1).zfill(6)}")
                    data_dict["word_fragment"].append(word)
                    data_dict["word_type"].append('UNKNOWN')
                    data_dict["word_count"].append(1)

    return data_dict

def return_dataframes(text_arrays: list[list[str]], excluded_words: list[str], preserve_words: list[str]):
    def get_text_dataframes():
        results_list = []
        for text_list in text_arrays:
            results_list.append(get_results(text_list, excluded_words, preserve_words))
        return results_list

    def form_frequency_tables(results_array: list[dict]):
        dataframes_list = []
        for dictionary in results_array:
            data = pd.DataFrame(dictionary)
            temp = data[["word_fragment", "word_count"]].groupby("word_fragment", as_index=False).sum()
            data = pd.merge(temp, data.drop_duplicates(subset=["word_fragment"])[["word_fragment", "word_type"]], on="word_fragment", how="left")
            data.loc[(data["word_type"].isin(["NNG", "NNM", "NNP", "PRESERVED", "HASHTAG"])) & (data["word_fragment"].str.len() != 1), "usefulness_flag"] = 1
            dataframes_list.append(data.fillna(0).sort_values(by="word_count", ascending=False))
        return dataframes_list

    results_list = get_text_dataframes()
    frequency_tables = form_frequency_tables(results_list)
    return frequency_tables

# Data processing and filtering
if __name__ == "__main__":
    start_time = time.time()  # Record start time

    df = pd.read_excel(r"file_path_here", engine='openpyxl')
    df = df.dropna(subset=["MENTION"])  # Remove NULL values

    # Generate COMMENT_ID
    df["comment_id"] = [f"COMMENT_{str(i + 1).zfill(6)}" for i in range(len(df))]

    # Perform morphological analysis and create DataFrame
    table_list = return_dataframes([list(df["MENTION"])], excluded_words, preserve_words)

    # Apply filtering
    filtered_table = table_list[0]

    # Save results
    filtered_table.to_excel("frequency_241219_kkma_hashtag.xlsx", index=False)

    end_time = time.time()  # Record end time
    execution_time = end_time - start_time  # Calculate execution time
    print(f"Execution time: {execution_time:.2f} seconds")
