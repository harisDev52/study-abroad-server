import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier

# Load the data
data = pd.read_csv('programs.csv')

# Separate features and target
X = data.drop(['id', 'university'], axis=1)  # Features (excluding 'id' and 'university')
Y = data[['university']]  # Target

# Define the preprocessing steps for numerical and categorical features
numeric_features = ['duration', 'fees', 'cgpa', 'ielts']
numeric_transformer = StandardScaler()

categorical_features = ['domain', 'independent_scholarship', 'university_scholarship']
categorical_transformer = OneHotEncoder(handle_unknown='ignore')

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])

# Instantiate the KNeighborsClassifier
model_knn = KNeighborsClassifier(n_neighbors=5)

# Define the pipeline
pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('knn', model_knn)])

# Fit the pipeline on training data only
pipeline.fit(X, Y)

# Get user input for domain
user_domain = input("Enter your domain: ").strip().title()  # Capitalize the first letter of each word

# Prepare user input for prediction
user_data = pd.DataFrame([[user_domain, 0, 0, 0, 0, 0, 0]], columns=['domain', 'duration', 'fees', 'cgpa', 'ielts', 'independent_scholarship', 'university_scholarship'])

# Find the index of the row with the matching domain
index = data[data['domain'] == user_domain].index

if not index.empty:
    # Retrieve the full row of data corresponding to the domain
    user_data = data.loc[index]
    # Replace 0 with 'No' and 1 with 'Yes' for 'independat_scholarship' and 'university_scholorship' columns
    user_data['independent_scholarship'] = user_data['independent_scholarship'].apply(lambda x: 'No' if x == 0 else 'Yes')
    user_data['university_scholarship'] = user_data['university_scholarship'].apply(lambda x: 'No' if x == 0 else 'Yes')
    print("Recommended Universities for domain '{}'".format(user_domain))
    print(user_data)
else:
    print("No matching data found for domain '{}'".format(user_domain))
