import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import GridSearchCV
from nltk.corpus import stopwords
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image
import matplotlib.dates as mdates
import random

# Download NLTK data
nltk.download('stopwords')
nltk.download('punkt')

np.random.seed(42)
random.seed(42)

# Load data (Replace with actual dataset)
df = english_data  # Replace with actual data file

# Text preprocessing function
def preprocess_text(text):
    try:
        text = re.sub(r'[^a-zA-Z\s]', '', str(text).lower())
        stop_words = set(stopwords.words('english'))
        tokens = text.split()  # Simple tokenization
        return ' '.join([word for word in tokens if word not in stop_words])
    except Exception as e:
        print(f"Error processing text: {e}")
        return ""

df['processed_text'] = df['Title'] + ' ' + df['Message']
df['processed_text'] = df['processed_text'].apply(preprocess_text)

# Topic modeling
vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
doc_term_matrix = vectorizer.fit_transform(df['processed_text'])

# GridSearch for LDA
param_grid = {'n_components': [2, 3, 4, 5, 6], 'learning_decay': [0.5, 0.7, 0.9]}
lda = LatentDirichletAllocation(random_state=42)
grid_search = GridSearchCV(lda, param_grid=param_grid, cv=5)
grid_search.fit(doc_term_matrix)

best_lda_model = grid_search.best_estimator_

# Set color scheme
colors = plt.cm.get_cmap('tab10', best_lda_model.n_components)  # Use 'tab10' colormap

lda_output = best_lda_model.transform(doc_term_matrix)
df['main_topic'] = lda_output.argmax(axis=1)

# Extract top keywords for each topic
feature_names = vectorizer.get_feature_names_out()
topic_keywords = []
for topic_idx, topic in enumerate(best_lda_model.components_):
    top_keywords = [feature_names[i] for i in topic.argsort()[:-11:-1]]  # Top 10 keywords
    topic_keywords.append(', '.join(top_keywords))

topic_keyword_df = pd.DataFrame({
    'Topic': range(best_lda_model.n_components),
    'Keywords': topic_keywords
})

# Similarity measurement and network graph generation
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df['processed_text'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

G = nx.Graph()
for i in range(len(df)):
    for j in range(i + 1, len(df)):
        if cosine_sim[i][j] > 0.7:
            G.add_edge(i, j, weight=cosine_sim[i][j])

# Cross-domain Spread calculation function
def calculate_cross_domain_spread(df):
    return df.groupby('main_topic')['Domain'].nunique()

cross_domain_spread = calculate_cross_domain_spread(df)

# Chart 1: Topic Spread Over Time
plt.figure(figsize=(15, 8))
topic_spread = df.groupby(['CreatedTime', 'main_topic']).size().unstack(fill_value=0).cumsum()
topic_totals = topic_spread.iloc[-1]
total_documents = topic_totals.sum()

# Plot line chart
for topic in range(best_lda_model.n_components):
    plt.plot(topic_spread.index, topic_spread[topic], 
             label=f'Topic {topic} ({topic_totals[topic]} docs, {topic_totals[topic]/total_documents:.1%}, CDS: {cross_domain_spread[topic]})',
             color=colors(topic))

# Set title and labels
plt.title('Topic Spread Over Time', fontsize=14)
plt.xlabel('Time', fontsize=12)
plt.ylabel('Cumulative Number of Articles', fontsize=12)

# Adjust legend position to prevent overlapping
plt.legend(title='Topics (Total docs, % of corpus, Cross-domain Spread)',
           bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

# Format x-axis
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=6))
plt.xlim(topic_spread.index.min(), topic_spread.index.max())
plt.gcf().autofmt_xdate()

plt.tight_layout()
plt.savefig('topic_spread.png', dpi=300)
plt.show()

# Chart 2: Topic Distribution Across Top 20 Domains
top_20_domains = df['Domain'].value_counts().nlargest(20)
domain_topic_dist = df[df['Domain'].isin(top_20_domains.index)].groupby('Domain')['main_topic'].value_counts(normalize=True).unstack(fill_value=0)
domain_topic_dist = domain_topic_dist.loc[top_20_domains.index]

plt.figure(figsize=(20, 15))
ax = domain_topic_dist.plot(kind='barh', stacked=True, color=[colors(i) for i in range(domain_topic_dist.shape[1])], width=0.9)

plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.title('Topic Distribution Across Top 20 Domains', fontsize=12)
plt.xlabel('Proportion (%)', fontsize=7)
plt.ylabel('Domain', fontsize=7)

# Add data labels
domain_labels = [f"{domain} ({count} articles)" for domain, count in top_20_domains.items()]
ax.set_yticklabels(domain_labels[::-1])

plt.tight_layout()
plt.savefig('topic_distribution.png', dpi=300)
plt.show()

# Chart 3: Top 20 Influential Domains
domain_influence = pd.DataFrame({
    'Domain': [df['Domain'].iloc[n] for n in G.nodes()],
    'Degree': [G.degree(n) for n in G.nodes()]
})
domain_influence = domain_influence.groupby('Domain')['Degree'].sum().sort_values(ascending=False).nlargest(20)

plt.figure(figsize=(15, 8))
ax = domain_influence.plot(kind='bar')
plt.title("Top 20 Influential Domains", fontsize=16)
plt.xlabel("Domain", fontsize=12)
plt.ylabel("Total Degree in Network", fontsize=12)

# Add data labels
for i in ax.patches:
    ax.annotate(f'{i.get_height()}', 
                (i.get_x() + i.get_width() / 2., i.get_height()), 
                ha='center', va='bottom')

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('Top_20_Influential_Domains.png')
plt.show()

# Extract initial articles for each topic
first_spread_articles = pd.DataFrame()
top_influential_domains = domain_influence.index.tolist()

for domain in top_influential_domains:
    domain_articles = df[df['Domain'] == domain]
    
    if not domain_articles.empty:
        for topic in df['main_topic'].unique():
            topic_articles = domain_articles[domain_articles['main_topic'] == topic]
            if not topic_articles.empty:
                earliest_article = topic_articles.loc[topic_articles['CreatedTime'].idxmin()]
                
                if 'InfluenceMetric' in topic_articles.columns:
                    highest_influence_article = topic_articles.loc[topic_articles['InfluenceMetric'].idxmax()]
                    selected_article = highest_influence_article if earliest_article['InfluenceMetric'] < highest_influence_article['InfluenceMetric'] else earliest_article
                else:
                    selected_article = earliest_article
                
                first_spread_articles = pd.concat([first_spread_articles, selected_article.to_frame().T])

# Save results to Excel
with pd.ExcelWriter(r'file_path_here', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Raw Data', index=False)
    topic_spread.to_excel(writer, sheet_name='Topic Spread')
    domain_topic_dist.to_excel(writer, sheet_name='Domain Topic Distribution')
    domain_influence.to_excel(writer, sheet_name='Influential Domains')
    topic_keyword_df.to_excel(writer, sheet_name='Topic Keywords', index=False)
    first_spread_articles.to_excel(writer, sheet_name='First Spread Articles by Topic', index=False)

    workbook = writer.book
    for image_file in ['topic_spread.png', 'topic_distribution.png', 'Top_20_Influential_Domains.png']:
        worksheet = workbook.create_sheet(title=image_file[:-4])
        img = Image(image_file)
        worksheet.add_image(img, 'A1')

print("Analysis complete. Results saved in 'fin_article_analysis.xlsx'")
