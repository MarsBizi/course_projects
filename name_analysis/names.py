# %%
# Import libraries
import pandas as pd 
import numpy as np 
import altair as alt
#import altair_saver as save
import tabulate

# %%
# Load in data
url = "https://raw.githubusercontent.com/byuidatascience/data4names/master/data-raw/names_year/names_year.csv"

df = pd.read_csv(url)


# %%
rand_samp = df.sample(5)
print(rand_samp.to_markdown())

# %%

# If you talked to someone named Brittany on the phone, 
# what is your guess of their age? What ages would you not guess?

britt = df.query("name == 'Brittany'")
britt.sort_values('Total').tail(14)

# %%
# Plot line chart for Brittany 
britt_plt = alt.Chart(britt).encode(
    x=alt.X("year", title="Year of birth", axis=alt.Axis(format='.0f')),
    y=alt.Y("Total", title="Number of birth names")
).mark_line(interpolate='monotone').properties(title="Guessing the age of a 'Brittany'")

britt_plt.save("britt.png")


sorted = britt.sort_values("Total", ascending=False).head(10)
sorted

britt_plt

# %%

# Mary, Martha, Peter, and Paul are all Christian names. From 1920 - 2000, 
# compare the name usage of each of the four names.

# Filter names, and year range
mmpp = (df.query("name == 'Mary' | name == 'Martha' | name == 'Peter' | name == 'Paul'")
    .query("year >= 1920 & year <= 2000"))


# %%
# plot line graph with names and occurences
mmpp_plt = alt.Chart(mmpp).encode(
    x=alt.X("year", axis=alt.Axis(format='.0f'), title="Year of Birth"),
    y=alt.Y("Total", title="Number of birth names"),
    color=alt.Color("name", legend=alt.Legend(title=""))
).mark_line(
    interpolate='monotone'
)

mmpp_plt

# %%
# calculate average 
mmpp_avg = (mmpp.groupby('name')
                .Total.mean()
                .reset_index()
                .rename(columns = {'Total' : 'avg'}))

avg_plt = alt.Chart(mmpp_avg).mark_rule(strokeDash=[5, 3]).encode(
    y='avg',
    color='name'
)

# add average line for each name as layer
avg_plt = alt.layer(avg_plt + mmpp_plt).properties(
    title={
        "text":["Usage of Martha, Mary, Peter, and Paul between 1920-2000"], 
        "subtitle":['Trend and Average'],
      "subtitleColor": "gray"
        }
)

avg_plt.save('mmpp.png')

# %%

## How does your name at your birth year compare to its use historically?

# My name doesn't exist in the data, a name will be randomly selected to analyse
rand_name = df.sample(random_state=12)
rand_name
name = df.query("name == 'Amos'")

name.tail(30)
# %%
# Plot line graph for 'Amos'
total_plt= alt.Chart(name).encode(
    x="year",
    y="Total"
).mark_line(interpolate='monotone')

# %%
sorted = name.sort_values("Total")
low = sorted.head(1)
high = sorted.tail(1)
tbl = pd.concat([high, low]).filter(['name', 'year', 'Total'])

print(tbl.to_markdown())
# %%
# add year to plot
year96 = name.query("year == 1996")

year96_plt = alt.Chart(year96).encode(
    x=alt.X("year", axis=alt.Axis(format='.0f'), title="Year of Birth"),
    y=alt.Y("Total", title="Number of birth names")
).mark_circle(color="orange", size=45, opacity=0.6)

year_line_plt = alt.Chart(year96).encode(
    x="year",
    y="Total"
).mark_rule(color="orange", strokeDash=[10, 10])

text = alt.Chart({'values':[{'x': 2002, 'y': 58}]}).mark_text(
    text='1996', color="orange", size=14
).encode(
    x='x:Q', y='y:Q'
)

fig = (alt.layer(total_plt + year96_plt + year_line_plt + text)
    .properties(title='The name "Amos" historically vs. 1996'))

fig.save("birth_year.png")
fig


# %%

# Think of a unique name from a famous movie. 
# Plot that name and see how increases line up with 
# the movie release.

# filter name 'Willy'
willy = df.query("name == 'Willy'")

# Plot line graph
willy_plt = (alt.Chart(willy).mark_line(color="#6f6f6f", interpolate='monotone')
    .encode(
        x=alt.X("year", axis=alt.Axis(title="Year of Birth", format='.0f')),
        y=alt.Y("Total", axis=alt.Axis(title="Number of birth names"))))

#line = alt.Chart(pd.DataFrame({'x': [1971]})).mark_rule().encode(x='x')

# willy_line_plt = (alt.Chart(pd.DataFrame({'x': [1971]}))
#     .encode(
#         x="x")
#     .mark_rule(color="#f58a42", strokeDash=[10, 10]))

# add layers to highlight timeframe
rect1 = pd.DataFrame({
    'x1': [1971],
    'x2': [2020]
})

shade1 = alt.Chart(rect1).mark_rect(
    opacity=0.15,
    color="#3f0063"
).encode(
    x='x1',
    x2='x2',
    y=alt.value(0),  # 0 pixels from top
    y2=alt.value(300)  # 300 pixels from top
)

rect2 = pd.DataFrame({
    'x1': [2005],
    'x2': [2020]
})

shade2 = alt.Chart(rect2).mark_rect(
    opacity=0.15,
    color="#3f0063"
).encode(
    x='x1',
    x2='x2',
    y=alt.value(0),  # 0 pixels from top
    y2=alt.value(300)  # 300 pixels from top
)

# text = alt.Chart({'values':[{'x': 1985, 'y': 58}]}).mark_text(
#     text='"Willy Wonka \nand \nThe Chocolate Factory" \n was released', 
#     size=9,
#     lineBreak="\n",
#     color="#54006e", 
#     align="center"
# ).encode(
#     x='x:Q', y='y:Q'
# )

# Final plot
movie_plt = (alt.layer(willy_plt + shade1 + shade2)
                .properties(
                    title={
                        "text":['"Charlie and the Chocolate Factory"'], 
                        "color" : "#6b00a8",
                        "subtitle":["Popularity of the name - Willy", "Since its release in 1971 and 2005"],
                        "subtitleColor": "gray"
                        }))

movie_plt.save('movie_plt.png')
movie_plt

