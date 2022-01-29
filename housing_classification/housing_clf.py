#%%
# the full imports
import pandas as pd 
import numpy as np
import seaborn as sns
import altair as alt
import altair_saver as save
#%%
# the from imports
from altair.vegalite.v4.schema.channels import Color
from matplotlib.pyplot import xlim, xticks
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import metrics
from toolz.itertoolz import groupby

# %%
# load datasets
dwellings_denver = pd.read_csv("https://github.com/byuidatascience/data4dwellings/raw/master/data-raw/dwellings_denver/dwellings_denver.csv")
dwellings_ml = pd.read_csv("https://github.com/byuidatascience/data4dwellings/raw/master/data-raw/dwellings_ml/dwellings_ml.csv")
dwellings_neighborhoods_ml = pd.read_csv("https://github.com/byuidatascience/data4dwellings/raw/master/data-raw/dwellings_neighborhoods_ml/dwellings_neighborhoods_ml.csv")   

alt.data_transformers.enable('json')
# %%
# Create 2-3 charts that evaluate potential relationships 
# between the home variables and before1980.

#%%
# plot distribution of stories using sns
stories_plt = sns.displot(dwellings_ml, x='stories', kind='kde', hue='before1980', fill=True)
stories_plt.set(xlabel='Number of floors', xticks=np.arange(1,4,1), )._legend.set_title('Before 1980?')
for t, l in zip(stories_plt._legend.texts, ['No', 'Yes']): t.set_text(l)

#%%
# plot total units
tounits = dwellings_denver.query('stories>0')
tounits = (alt.Chart(tounits)
                .mark_circle()
                .encode(
                    x=alt.X('yrbuilt',
                            scale=alt.Scale(zero=False), 
                            title='Year Built', 
                            axis=alt.Axis(format='.0f')
                            ),
                    y=alt.Y('totunits', 
                            title='Total units'),
                    color=alt.condition('datum.yrbuilt>1980', 
                                        alt.ColorValue('blue'), 
                                        alt.ColorValue('orange')
                                        )
                        )
                .properties(title={ "text":['Total dwelling units in the building']})
            )

tounits.save("tounits.png")

#%%
# count unique values of condition column
cond_vals = print(dwellings_denver
                    .reset_index()
                    .groupby('condition')['index']
                    .nunique()
                    .to_markdown())

cond_summary = dwellings_denver.condition.value_counts(normalize=True).reset_index()
# print(cond_summary.assign(
#     condition = lambda x: x.condition * 100).round(2).to_markdown())
#%% 
# plot condition column
cond = (dwellings_denver
            .query('(yrbuilt>0) and (condition in ["AVG","Good","VGood","Excel"])')
            .dropna(subset=['condition'])
        )

cond_plt = (alt.Chart(cond)
            .mark_boxplot(size=15, extent=1)
            .encode(
                x=alt.X('yrbuilt',
                        scale=alt.Scale(zero=False), 
                        title='Year Built', 
                        axis=alt.Axis(format='.0f'),
                        ),
                y=alt.Y('condition', title='Condition'),
                color=alt.Color('condition', title='')
            ).properties(title={"text":['Condition of buildings by year built'],
                                "subtitle":['as of 2013']}))
cond_plt.save('cond_plt.png')
# %%
# Can you build a classification model (before or after 1980) 
# that has at least 90% accuracy for the state of Colorado to 
# use (explain your model choice and which models you tried)?

# %%
# prep data using all features
X_pred = dwellings_ml.drop(['yrbuilt', 'before1980'], axis=1)
y_pred = dwellings_ml.before1980
# %%
X_train, X_test, y_train, y_test = train_test_split(
    X_pred, 
    y_pred, 
    test_size = .34, 
    random_state = 76)   

# %%
# Gradient Boosting Classifier
from sklearn import tree

gb_model= GradientBoostingClassifier()

gb_model = gb_model.fit(X_train, y_train)

predict_p = gb_model.predict(X_test)
# %%
# print accuracy
gb_acc = print("Gradient Boosting Classifier Accuracy:",metrics.accuracy_score(y_test, predict_p))

# %%
# df_features = pd.DataFrame(
#     {'f_names': X_train.columns,
#     'f_values': gb_model.feature_importances_}).sort_values('f_values', ascending=False)

# df_features
 
# %%
# Random Forest Classifier
from sklearn.ensemble import RandomForestClassifier

rf_model = RandomForestClassifier()

rf_model = rf_model.fit(X_train, y_train)

predict_p = rf_model.predict(X_test)
# %%
rfc = print("Random Forest Classifier Accuracy:",metrics.accuracy_score(y_test, predict_p))

# %%
# AdaBoost Classifier
from sklearn.ensemble import AdaBoostClassifier

ada_model = AdaBoostClassifier()

ada_model = ada_model.fit(X_train, y_train)

predict_p = ada_model.predict(X_test)
# %%
ada = print("AdaBoost Classifier Accuracy:",metrics.accuracy_score(y_test, predict_p))

# %%
df_features = pd.DataFrame(
    {'f_names': X_train.columns,
    'f_values': ada_model.feature_importances_}).sort_values('f_values', ascending=False)

df_features

# %%
# Will you justify your classification model by detailing 
# the most important features in your model (a chart and 
# a description are a must)?

# %%


rf_features = pd.DataFrame(
    {'f_names': X_train.columns,
    'f_values': rf_model.feature_importances_}).sort_values('f_values', ascending=False)

rf_features = rf_features.query('f_values>0.01')
#df_features
rfc_plt = (alt.Chart(rf_features)
                .mark_bar()
                .encode(
                    x=alt.X('f_names', title='', sort='-y'),
                    y=alt.Y('f_values', title='Feature Importance')
                        )
                .properties(title={"text":['Feature importance for Random Forest model'],
                                "subtitle":['values above 0.01 from `dwellings_ml` dataset']}
                            )
            )

rfc_plt.save('rfc_plt.png')

# %%
# Can you describe the quality of your classification model 
# using 2-3 evaluation metrics?
# You need to explain how to interpret each evaluation metric 
# when you provide the value.

# extract column names from rf_features
features = rf_features.f_names.tolist()

# %%
X_pred = dwellings_ml[features]
y_pred = dwellings_ml.before1980
# %%
X_train, X_test, y_train, y_test = train_test_split(
    X_pred, 
    y_pred, 
    test_size = .34, 
    random_state = 76)   
# %%
rf1_model = RandomForestClassifier()

rf1_model = rf1_model.fit(X_train, y_train)

predict_p = rf1_model.predict(X_test)
# %%
rfc = print("Random Forest Classifier Accuracy:",metrics.accuracy_score(y_test, predict_p))
# %%
print(metrics.confusion_matrix(y_test, predict_p))
metrics.plot_confusion_matrix(rf1_model, X_test, y_test)
# %%
clf_report = metrics.classification_report(y_test, predict_p, output_dict=True)

# %%
print(pd.DataFrame(clf_report).transpose().to_markdown())
