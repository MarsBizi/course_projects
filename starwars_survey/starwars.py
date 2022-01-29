# %% 
import pandas as pd
import numpy as np
import altair as alt
import seaborn as sns
import altair_saver as save
from pandas.core.algorithms import value_counts
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import metrics


# %%
# Load data
url = "https://raw.githubusercontent.com/fivethirtyeight/data/master/star-wars-survey/StarWars.csv"
df = pd.read_csv(url, encoding="ISO-8859-1", header=None, skiprows=2)

df_names = (pd.read_csv(url, encoding="ISO-8859-1", nrows=1).melt())

#df_names


# ---------------

# Grand Question 1:
# Shorten the column names and clean them up for easier 
# use with pandas.

#columns = (pd.read_csv(url, encoding="ISO-8859-1", nrows=1))
#print(columns.head(1).to_markdown())
#%%
# replace values, strip space from beginning and end of string values
df_names =(df_names
   .replace('Unnamed: \d{1,2}', np.nan, regex=True)
   .replace('Response', "")
   .assign(
      clean_variable = lambda x: x.variable.str.strip()
         .replace(
            'Which of the following Star Wars films have you seen? Please select all that apply.','seen_any'),
      clean_value = lambda x: x.value.str.strip()
      )
   .fillna(method = 'ffill')
   .assign(
      column_name = lambda x: x.clean_variable.str.cat(x.clean_value, sep = "__") 
   )
)

#df_names
#%%
# replace variable columns for shorter values
variables_replace = {
    'Which of the following Star Wars films have you seen\\? Please select all that apply\\.':'seen',
    'Please rank the Star Wars films in order of preference with 1 being your favorite film in the franchise and 6 being your least favorite film.':'rank',
    'Please state whether you view the following characters favorably, unfavorably, or are unfamiliar with him/her.':'char_view',
    'Do you consider yourself to be a fan of the Star Trek franchise\\?':'star_trek_fan',
    'Do you consider yourself to be a fan of the Expanded Universe\\?\x8cæ':'expanded_fan',
    'Are you familiar with the Expanded Universe\\?':'know_expanded',
    'Have you seen any of the 6 films in the Star Wars franchise\\?':'seen_any',
    'Do you consider yourself to be a fan of the Star Wars film franchise\\?':'star_wars_fans',
    'Which character shot first\\?':'shot_first',
    'Unnamed: \d{1,2}':np.nan,
    ' ':'_',
}
# replace value columns for shorter values
values_replace = {
    'Response':'',
    'Star Wars: Episode ':'',
    ' ':'_'
}

#%%
# Prep column to use for header
df_cols_use = (df_names
    .assign(
        value_replace = lambda x:  x.value.str.strip().replace(values_replace, regex=True),
        variable_replace = lambda x: x.variable.str.strip().replace(variables_replace, regex=True)
    )
    .fillna(method = 'ffill')
    .fillna(value = "")
    .assign(column_names = lambda x: x.variable_replace.str.cat(x.value_replace, sep = "__").str.strip('__').str.lower()) # combines variable_replace + value_replace
    )
#df_cols_use

#%%
# replace with new column names
df.columns = df_cols_use.column_names.to_list()
df.columns = [*df.columns[:-1], 'region']
#print(df.head(0).to_markdown())



#%%
# ---------------------

# Grand Question 2:
# Filter the dataset to those that have seen at least one film.


seen_one = df.query('seen_any == "Yes"')
#print(seen_one.head(5).to_markdown())



#%% 
# ----------------------
# Grand Question 3:

# Please validate that the data provided on GitHub lines up with 
# the article by recreating 2 of their visuals and calculating 
# 2 summaries that they report in the article.


#%%
# prep data for shot first plot
shot_first = (seen_one.shot_first.value_counts()
                    .reset_index()
)
#shot_first

#%%
# define bar order
chart_order = ['Han', 'Greedo', "I don't understand this question"]
bars = (alt.Chart(shot_first)
            .transform_joinaggregate(
                total_resp = 'sum(shot_first)')
            .transform_calculate(
                percent='round(datum.shot_first / datum.total_resp * 100)')
            .mark_bar().encode(
                alt.X('percent:Q', title="", axis=None),
                alt.Y('index', title="", sort=chart_order))
            .properties(title={ "text":['Who Shot First?'], 
                                        "subtitle":['According to 935 respondents (in percentage)']}
                        )
)
text = (bars.mark_text(
                align='left',
                baseline='middle',
                dx=3)
            .encode(
                text='percent:Q')
)
plt_1 = (bars+text).configure_view(strokeWidth=0)
plt_1.save("plt_1.png")

#%%
# prep data for character favorability ratings plot
replace_val = {
    'Very favorably' : 'Favorable',
    'Somewhat favorably' : 'Favorable',
    'Neither favorably nor unfavorably (neutral)' : 'Neutral',
    'Somewhat unfavorably' : 'Unfavorable',
    'Very unfavorably' : 'Unfavorable',
    'Unfamiliar (N/A)' : 'Unfamilliar'
}

fav_char = (seen_one.iloc[:, 15:29].melt())
fav_char = (fav_char.assign(char_names = 
                        fav_char.variable.str.split('__', expand=True)
                        .rename(columns = {0: 'drop', 1:'char_name'})
                        .char_name
                        .str.replace('_', ' ')
                        .str.title()
                        )
                    .replace({'value':replace_val})
                    .rename(columns={'value':'rating'})
            )
            
#fav_char

#%%
rate_total = (fav_char.groupby(['char_names'])
                    .agg({'rating':'count'})
                    .rename(columns={'rating':'total_rating'})
                    .reset_index()
            )
#rate_total
#%%
fav_char_count = (fav_char.groupby(['char_names', 'rating'])
                    .agg({'rating':'count'})
                    .rename(columns={'rating':'count'})
                    .reset_index()
            )

#%%
char_perc = pd.merge(fav_char_count, rate_total, how='left', on='char_names')
#char_perc
#%%
char_perc['perc'] = round(char_perc['count'] / char_perc['total_rating'] * 100)
#char_perc

#%%
manual_order1 = char_perc.sort_values(['rating'], ascending=True)
manual_order1 = (manual_order1.iloc[0:14, :].sort_values('perc', ascending=False)
                .char_names
                .tolist())
#manual_order1

#%%
manual_order2 = ['Favorable', 'Neutral', 'Unfavorable', 'Unfamilliar']
manual_color = ['#77AA43', '#008FD5', '#FF2600', '#999999']

base = (alt.Chart(char_perc)
            .encode(
                x=alt.X('perc:Q', title="", axis=None),
                y=alt.Y('char_names', sort=manual_order1, title="")                
                )
            .properties(width=80)
)

bars = (base.mark_bar().encode(
            color=alt.Color('rating', legend=None, scale=alt.Scale(domain=manual_order2, range=manual_color))
))

text = (base.mark_text(
                align='left',
                baseline='middle',
                dx=3)
            .encode(
                text='perc:Q',)
)
plt_2 = (alt.layer(bars, text, data=char_perc)
    .facet(column=alt.Column('rating', sort=manual_order2, title=""))
    .properties(title={ "text":["'Star Wars' Character Favorability Ratings"], 
                                "subtitle":['By 935 respondents (in percentage)']}
                        )
    .configure_view(strokeWidth=0)
            )
plt_2.save('plt_2.png')

#%%
# Verify number of "watched atleast one" by gender
total_gender = (df.groupby('gender')
                    .agg({'seen_any':'count'})
                    .reset_index()
                    .rename(columns={'seen_any':'total'}))

seen_any_gender = (seen_one.groupby('gender')
                    .agg({'seen_any':'count'})
                    .reset_index())

summary1 = (pd.merge(seen_any_gender, total_gender)
                .assign(percentage = lambda x: x.seen_any / x.total))

print(summary1.to_markdown())


#%%
# Verify number of fans by gender
seen_one_gender = (seen_one.query('star_wars_fans == "Yes"')
                            .groupby('gender')
                            .agg({'star_wars_fans':'count'})
                            .reset_index())

seen_one_total = (seen_one.groupby('gender')
                            .agg({'star_wars_fans':'count'})
                            .reset_index()
                            .rename(columns={'star_wars_fans':'total'}))

summary = (pd.merge(seen_one_gender, seen_one_total)
            .assign(percentage = lambda x: x.star_wars_fans / x.total))

print(summary.to_markdown())


#%%
#df = df[df['household_income'].notna()]
# -------------------

# Grand Question 4:

## Create an additional column that converts the age ranges to 
## a number and drop the age range categorical column.

#%%
# convert age range to number
df = (df.assign(age_min = 
                    (df.age
                    .str.split("-", expand = True)
                    .rename(columns = {0: 'age_min', 1:"age_max"})
                    .age_min
                    .str.replace("> ", "")
                    .astype('float')
                    )
                )
        .drop(columns=['age'])
    )

#%%
df

#%%
## Create an additional column that converts the school groupings 
## to a number and drop the school categorical column.

# replacement values as dict
ed_years = {
    'Less than high school degree':'9',
    'High school degree':'12',
    'Some college or Associate degree':'14',
    'Bachelor degree':'16',
    'Graduate degree':'19'
}

# replace with new and drop old column
df = (df.assign(education_years = 
                    df.education.replace(ed_years).astype('float')
                )
        .drop(columns=['education'])
    )


# %%
## Create an additional column that converts the income ranges to a 
## number and drop the income range categorical column.

df = (df.assign(income = 
                    (df.household_income
                    .str.split(" - ", expand = True)
                    .rename(columns = {0: 'income_min', 1:"income_max"})
                    .income_min
                    .str.replace("$", "")
                    .str.replace(",", "")
                    .str.replace("+", "")
                    .astype('float')
                    )
                )
        .drop(columns=['household_income'])
    )

#%%
## Create your target (also known as label) column based on the new 
## income range column.


df = (df.assign(above50k = 
                    (df.income >= 50000).astype(int))
        .drop(columns=['income'])
    )

#%%
last_3 = df.iloc[:, -3:]

#%%
## One-hot encode all remaining categorical columns.

dummy_cols = df.iloc[:,np.r_[3:9, 15:30, 34]].columns.tolist()
print(dummy_cols)
dummy_cols_bin = df.iloc[:,np.r_[1:3, 30:34]].columns.to_list()
#dummy_cols_bin

# %%
dum1 = df.filter(dummy_cols)

dum1 = pd.get_dummies(dum1, dtype=np.int64)
#dum1
# %%
dum2 = df.filter(dummy_cols_bin)
dum2 = pd.get_dummies(dum2, drop_first=True, dtype=np.int64)
#dum2
# %%
encoded = pd.concat([dum1, dum2], axis=1)
encoded

starwars_ml_raw = pd.concat([encoded, last_3], axis=1)
starwars_ml_raw = starwars_ml_raw[starwars_ml_raw['education_years'].notna()]
starwars_ml_raw

sample_dat = starwars_ml_raw.iloc[:, np.r_[0, 6:12]]

#%%

# More preprocessing
# min-max scaling age_min and education_years
from sklearn.preprocessing import MinMaxScaler

minmax_scale = MinMaxScaler()
starwars_ml_raw['age_min'] = minmax_scale.fit_transform(starwars_ml_raw[['age_min']])
starwars_ml_raw['education_years'] = minmax_scale.fit_transform(starwars_ml_raw[['education_years']])

starwars_ml = starwars_ml_raw

#%%

# -----------------

# Grand Question 5:

# Build a machine learning model that predicts whether a person makes 
# more than $50k.


#%%
# split data
X_pred = starwars_ml.drop(['above50k'], axis=1)
y_pred = starwars_ml.above50k

X_train, X_test, y_train, y_test = train_test_split(
    X_pred, 
    y_pred, 
    test_size = .3, 
    random_state = 11)   

# %%
gb_model= GradientBoostingClassifier()

gb_model = gb_model.fit(X_train, y_train)

predict_p = gb_model.predict(X_test)
# %%
# print accuracy
gb_acc = print("Gradient Boosting Classifier Accuracy:",metrics.accuracy_score(y_test, predict_p))


# %%
gb_features = pd.DataFrame(
    {'f_names': X_train.columns,
    'f_values': gb_model.feature_importances_}).sort_values('f_values', ascending=False)

gb_features = gb_features.query('f_values>0.005')

rfc_plt = (alt.Chart(gb_features)
                .mark_bar()
                .encode(
                    x=alt.X('f_names', title='', sort='-y'),
                    y=alt.Y('f_values', title='Feature Importance')
                        )
                .properties(title={"text":['Feature importance for Random Forest model'],
                                "subtitle":['values above 0.01 from `dwellings_ml` dataset']}
                            )
            )
rfc_plt

# %%
cols = gb_features.f_names.tolist()

X_pred = starwars_ml.filter(cols)
y_pred = starwars_ml.above50k

X_train, X_test, y_train, y_test = train_test_split(
    X_pred, 
    y_pred, 
    test_size = .3, 
    random_state = 11)
# %%
#
gb_model= GradientBoostingClassifier(n_estimators=600, subsample=0.4, max_features=15, learning_rate=0.01, max_depth=5)

gb_model = gb_model.fit(X_train, y_train)

predict_p = gb_model.predict(X_test)

# %%
# print accuracy
gb_acc = print("Gradient Boosting Classifier Accuracy:",metrics.accuracy_score(y_test, predict_p))


# %%
gb_features = pd.DataFrame(
    {'f_names': X_train.columns,
    'f_values': gb_model.feature_importances_}).sort_values('f_values', ascending=False)

gb_features = gb_features.query('f_values>0.005')

rfc_plt = (alt.Chart(gb_features)
                .mark_bar()
                .encode(
                    x=alt.X('f_names', title='', sort='-y'),
                    y=alt.Y('f_values', title='Feature Importance')
                        )
                .properties(title={"text":['Feature importance for Random Forest model'],
                                "subtitle":['values above 0.01 from `dwellings_ml` dataset']}
                            )
            )
rfc_plt

#%%
X = starwars_ml.drop('above50k', axis=1)
y = starwars_ml['above50k']

# %%
from sklearn.feature_selection import SelectKBest, mutual_info_regression
#Select top 2 features based on mutual info regression
selector = SelectKBest(mutual_info_regression, k =6)
selector.fit(X, y)
X.columns[selector.get_support()]
# %%
X = (starwars_ml[['char_view__han_solo_Very favorably',
       'char_view__darth_vader_Very unfavorably',
       'char_view__lando_calrissian_Somewhat favorably',
       'char_view__padme_amidala_Neither favorably nor unfavorably (neutral)',
       'age_min', 'education_years']])
y = starwars_ml['above50k']
# %%
X_train, X_test, y_train, y_test = train_test_split(
    X, 
    y, 
    test_size = .2, 
    random_state = 11)
# %%
#n_estimators=600, subsample=0.4, max_features=15, learning_rate=0.01, max_depth=5
gb_model= GradientBoostingClassifier(n_estimators=600, learning_rate=0.001)

gb_model = gb_model.fit(X_train, y_train)

predict_p = gb_model.predict(X_test)
# %%
print("Gradient Boosting Classifier Accuracy:",metrics.accuracy_score(y_test, predict_p))
# %%

# %%
from sklearn.decomposition import PCA

pca = PCA(n_components=2).fit(X_train)
X_train = pca.transform(X_train)
X_test = pca.transform(X_test)
# %%
b_model= GradientBoostingClassifier(n_estimators=600, learning_rate=0.001)

gb_model = gb_model.fit(X_train, y_train)

predict_p = gb_model.predict(X_test)
# %%
print("Gradient Boosting Classifier Accuracy:",metrics.accuracy_score(y_test, predict_p))

# %%
from sklearn import preprocessing

std_scale = preprocessing.StandardScaler().fit(X_train)
X_train_std = std_scale.transform(X_train)
X_test_std = std_scale.transform(X_test)

#%%

b_model= GradientBoostingClassifier(n_estimators=600, learning_rate=0.001)

gb_model = gb_model.fit(X_train_std, y_train)

predict_p = gb_model.predict(X_test_std)
# %%
print("Gradient Boosting Classifier Accuracy:",metrics.accuracy_score(y_test, predict_p))

# %%
