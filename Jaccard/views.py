import nltk 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity


# Define the five texts as strings 
text1 = "The Black Lives Matter (BLM) movement is a social and political movement that advocates for the rights and equality of Black individuals. The movement began in 2013 after the acquittal of Trayvon Martin's killer and gained momentum in the wake of police killings of Black Americans such as Michael Brown, Tamir Rice, and Freddie Gray. BLM protests have taken place across the United States and around the world, calling for an end to systemic racism and police brutality, as well as for economic and political justice for Black people. The movement has also pushed for reforms in areas such as education, housing, and healthcare. In addition to protests and demonstrations, BLM activists have also used social media, art, and other forms of cultural expression to raise awareness about the movement's goals and message."
text2 = "The Black Lives Matter movement aims to promote the rights and equality of Black individuals by working to end systemic racism, police brutality and fighting for economic and political justice. It began in 2013 and gained momentum following the acquittal of Trayvon Martin's killer and the deaths of other Black Americans by police. Activists use various methods such as protests, social media, art and cultural expression to bring attention to the cause and also call for reforms in areas such as education, housing, and healthcare."
text3 = "The Black Lives Matter movement advocates for the rights and equality of Black people, with a focus on ending systemic racism, police brutality and fighting for economic and political justice. The movement gained traction in 2013, particularly following the acquittal of Trayvon Martin's killer and the deaths of other Black Americans at the hands of police. Activists use various strategies to raise awareness, such as demonstrations, social media, art and cultural expression, and call for reforms in areas like education, housing, and healthcare."
text4 = "The Black Lives Matter is a social movement that aims to bring attention to the issue of racial inequality and discrimination faced by Black people. It focuses on ending systemic racism, police brutality, and working towards economic and political justice for Black individuals. The movement gained significant attention in 2013, following the acquittal of Trayvon Martin's killer and the deaths of other Black Americans by police. Activists use various tactics, including protests, social media, art, and cultural expression, to raise awareness and push for reforms in areas such as education, housing, and healthcare."
text5 = "The Black Lives Matter movement is a campaign that works to highlight and address the issue of racial inequality and discrimination faced by Black individuals. The movement aims to end systemic racism, police brutality, and push for economic and political justice for Black people. The movement gained significant public attention in 2013, following the acquittal of Trayvon Martin's killer and the deaths of other Black Americans by police. Activists employ a variety of methods, such as demonstrations, social media, art and cultural expression to bring attention to the cause and push for changes in areas like education, housing and healthcare."


# Define a function to calculate the Jaccard similarity between two texts
def jaccard_similarity(text1, text2):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    words1 = [lemmatizer.lemmatize(w.lower()) for w in word_tokenize(text1) if not w.lower() in stop_words]
    words2 = [lemmatizer.lemmatize(w.lower()) for w in word_tokenize(text2) if not w.lower() in stop_words]
    intersection = set(words1).intersection(set(words2))
    union = set(words1).union(set(words2))
    return len(intersection) / len(union)


# Calculate the Jaccard similarity between each pair of texts
jaccard_scores = []
for i in range(1,6):
    for j in range(i+1, 6):
        jaccard_scores.append(jaccard_similarity(globals()[f"text{i}"], globals()[f"text{j}"]))


# Define a function to calculate the cosine similarity between two texts
def cosine_similarity(text1, text2):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    words1 = [lemmatizer.lemmatize(w.lower()) for w in word_tokenize(text1) if not w.lower() in stop_words]
    words2 = [lemmatizer.lemmatize(w.lower()) for w in word_tokenize(text2) if not w.lower() in stop_words]
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]


# Calculate the cosine similarity between each pair of texts
cosine_scores = []
for i in range(1, 6):
    for j in range(i+1, 6):
        cosine_scores.append(cosine_similarity(globals()[f"text{i}"], globals()[f"text{j}"]))


# Average the Jaccard and cosine similarity scores between each text
for i in range(1, 6):
    jaccard_sum = 0
    cosine_sum = 0
    count = 0
    for j in range(1, 6):
        if j != i:
            jaccard_sum += jaccard_scores[count]
            cosine_sum += cosine_scores[count]
            count += 1
    jaccard_avg = jaccard_sum / 4
    cosine_avg = cosine_sum / 4
    print(f"Text{i} - Jaccard similarity: {jaccard_avg:.3f}, Cosine similarity: {cosine_avg:.3f}")
