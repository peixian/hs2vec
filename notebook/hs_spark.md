- [Hey! If you're reading this on Github, you should download this file instead. Github doesn't display org-babel files very well.](#sec-1)
    - [Setup](#sec-1-0-1)
    - [Normalize the cost, attack, and health](#sec-1-0-2)
    - [Coerce the mechanics into binary features with one hot encoding](#sec-1-0-3)
    - [Binarize and encode the playerClass](#sec-1-0-4)
    - [Binarize and encode the rarity](#sec-1-0-5)
    - [Binarize and encode the play requirements](#sec-1-0-6)
    - [Join the dataframes together](#sec-1-0-7)
    - [Pass into TSNE](#sec-1-0-8)
    - [Create plotly graph](#sec-1-0-9)

# Hey! If you're reading this on Github, you should download this file instead. Github doesn't display org-babel files very well.<a id="orgheadline10"></a>

by Peixian Wang - 2016/8/3

*This is licensed under MIT, so do what you want with it, modify it, fork it, etc. If you use this code I'd apprechiate an attribution back :>*

**MAKE SURE YOU'RE IN THE RIGHT VIRTUALENV**

### Setup<a id="orgheadline1"></a>

Import the supporting cast

```ipython
import collectobot
import yaha_analyzer
import pandas as pd
import numpy as np
```

```ipython
df = pd.read_json('../data/cards.json')
print(df.head(3))
print(df.columns)
```

Filter out all the weird generated cards:

```ipython
df = df[df['collectible'] == 1.0]
df = df[pd.notnull(df['cost'])]
```

### Normalize the cost, attack, and health<a id="orgheadline2"></a>

```ipython
from sklearn import preprocessing

df[['attack', 'health']] = df[['attack', 'health']].fillna(0) #Fill the spells with 0 attack and 0 health to normalize (there's probably a better way of doing this)

min_max_scaler = preprocessing.MinMaxScaler()
norm = lambda x: min_max_scaler.fit_transform(x)
df_n_stats = df[['id', 'attack', 'cost', 'health']]
df_n_stats[['attack', 'cost', 'health']] = df_n_stats[['attack', 'cost', 'health']].apply(norm)
print(df_n_stats.head(5))
```

### Coerce the mechanics into binary features with one hot encoding<a id="orgheadline3"></a>

```ipython
df_mechanics = df[['id','mechanics', 'overload', 'spellDamage']] #weirdly overload isn't a listed mechanic, check bug: https://github.com/HearthSim/HearthstoneJSON/issues/35
for i, row in df_mechanics.iterrows():
    val = row['mechanics']
    overload = row['overload']
    spell_damage = row['spellDamage']
    #hey look kids let's violate DRY today!
    if pd.notnull(overload):
        if isinstance(val, list) and 'OVERLOAD' not in val:
            val.append('OVERLOAD')
        elif not isinstance(val, list):
            val = ['OVERLOAD']
    if pd.notnull(spell_damage):
        if isinstance(val, list) and 'SPELL_DAMAGE' not in val:
            val.append('SPELL_DAMAGE')
        elif not isinstance(val, list):
            val = ['SPELL_DAMAGE']
    if not isinstance(val, list) and pd.isnull(overload) and pd.isnull(spell_damage):
        val = ['NONE']
    df_mechanics.set_value(i, 'mechanics', val)
df_mechanics.drop('overload', axis=1, inplace=True)
df_mechanics.drop('spellDamage', axis=1, inplace=True)
import sklearn
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import OneHotEncoder
mlbin = MultiLabelBinarizer()
binarized = mlbin.fit_transform(df_mechanics['mechanics']) #transform into a matrix of integers
enc = sklearn.preprocessing.OneHotEncoder() #binarize and encode
encoded = enc.fit_transform(binarized)

df_mechanics['mechanics_binarized'] = binarized.tolist()
df_mechanics['mechanics_sparse'] = encoded
print(mlbin.classes_)
print(df_mechanics.head(5))
#print(df_mechanics.dtypes) #[id, mechanics, mechanics_binarized, sparse] -> [string, list, list, scipi csr]
```

### Binarize and encode the playerClass<a id="orgheadline4"></a>

```ipython
df_player_class = df[['id', 'playerClass']]
df_player_class['playerClass'].fillna('Neutral', inplace=True)

from sklearn.preprocessing import LabelBinarizer
mlbin = LabelBinarizer()
binarized = mlbin.fit_transform(df_player_class['playerClass'])
enc = sklearn.preprocessing.OneHotEncoder()
encoded = enc.fit_transform(binarized)

df_player_class['player_class_binarized'] = binarized.tolist()
df_player_class['player_class_sparse'] = encoded
print(mlbin.classes_)
print(df_player_class.head(5))
```

### Binarize and encode the rarity<a id="orgheadline5"></a>

```ipython
df_rarity = df[['id', 'rarity']]
mlbin = LabelBinarizer()
binarized = mlbin.fit_transform(df_rarity['rarity'])
enc = sklearn.preprocessing.OneHotEncoder()
encoded = enc.fit_transform(binarized)

df_rarity['rarity_binarized'] = binarized.tolist()
df_rarity['rarity_sparse'] = encoded
print(mlbin.classes_)
print(df_rarity.head(5))
print(type(df_rarity['rarity_sparse'][3]))
```

### Binarize and encode the play requirements<a id="orgheadline6"></a>

Condense each dictionary into a list of strings with "{key}<sub>val</sub>"

```ipython
df_play_requirements = df[['id', 'playRequirements']]
#df_play_requirements['playRequirements'].fillna(0, inplace=True)
l_1 = df_play_requirements[pd.notnull(df['playRequirements'])]['playRequirements'].map(lambda x: ["{}_{}".format(k, v) for k,v in x.items()])
l_2  = df_play_requirements[pd.isnull(df['playRequirements'])]['playRequirements'].map(lambda x: ['NONE'])
df_play_requirements['playRequirements'] = l_1.combine_first(l_2)
#df_play_requirements[pd.isnull(df['playRequirements'])]['playRequirements'] = ['NONE']*null_length
#print(df_play_requirements)
#print(pd.concat([l_1, l_2], axis=1))
mlbin = MultiLabelBinarizer()
binarized = mlbin.fit_transform(df_play_requirements['playRequirements'])
df_play_requirements['play_requirements_binarized'] = binarized.tolist()
print(mlbin.classes_)
```

### Join the dataframes together<a id="orgheadline7"></a>

```ipython
df_combined = df_n_stats.merge(df_mechanics, on='id')
df_combined = df_combined.merge(df_player_class, on='id')
df_combined = df_combined.merge(df_rarity, on='id')
df_combined = df_combined.merge(df_play_requirements, on='id')
print(df_combined.head(5))
```

convert the sparse matricies into csc format

```ipython
transpose_to_csc = lambda x: x.tocsc()
df_combined[['mechanics_sparse', 'player_class_sparse', 'rarity_sparse']] = df_combined[['mechanics_sparse','player_class_sparse', 'rarity_sparse']].applymap(lambda x: x.tocsc())
print(df_combined.dtypes)
#df_sparse = df_combined[['mechanics_sparse', 'player_class_sparse', 'rarity_sparse']].apply(lambda x: x.tocsc(), axis=0)
#combined_spark_df = spark.createDataFrame(df_combined)
```

### Pass into TSNE<a id="orgheadline8"></a>

```ipython
from sklearn.decomposition import PCA
from scipy.sparse import hstack
df_combined['features'] = df_combined[['attack', 'cost', 'health']].values.tolist()
for i, row in df_combined.iterrows():
    val = row['features']
    val.extend(row['mechanics_binarized'])
    val.extend(row['player_class_binarized'])
    val.extend(row['rarity_binarized'])
    val.extend(row['play_requirements_binarized'])
    df_combined.set_value(i, 'features', val)
print(df_combined.head(5))
print(len(df_combined['features'][0]))
```

```ipython
from sklearn.manifold import TSNE
#tnse_model = TSNE(n_components=dimensions, n_iter=10000000, metric="correlation", learning_rate=50, early_exaggeration=500.0, perplexity=40.0)
tnse_model = TSNE(n_components = 3)
np.set_printoptions(suppress=True)
model = tnse_model.fit_transform(df_combined['features'].tolist())
```

```ipython
df_plot = pd.DataFrame(model)
df_plot.columns = ['x', 'y', 'z']
df_plot['labels'] = list(map(lambda x: df[df['id'] == x]['name'].values[0], df_combined['id']))
df_plot['rarity'] = list(map(lambda x: df[df['id'] == x]['rarity'].values[0], df_combined['id']))
df_plot['cost'] = list(map(lambda x: df[df['id'] == x]['cost'].values[0], df_combined['id']))
df_plot['player_class'] = df_combined['playerClass']
print(df_plot.head(5))
```

Write to csv

```ipython
df_plot.to_csv('../results/model.tsv', sep='\t')
```

### Create plotly graph<a id="orgheadline9"></a>

```ipython
import plotly.plotly as py
import plotly.graph_objs as go

rarity_colors = {'LEGENDARY': '#F535A5', 'RARE': '#3993F9', 'EPIC': '#CC47D5', 'COMMON': '#F3F9F1', 'FREE': '#263238' }
class_colors = {'WARRIOR': '#8D0F01',
                'SHAMAN': '#011784',
                'ROGUE': '#4B4C47',
                'PALADIN': '#A98E00',
                'HUNTER': '#006E00',
                'DRUID': '#703505',
                'WARLOCK': '#7623AD',
                'MAGE': '#0091AB',
                'PRIEST': '#C7C19E', 
                'NEUTRAL': '#263238'} #colors from: https://www.reddit.com/r/hearthstone/comments/2d0x31/mtg_has_the_color_pie_here_is_a_hearthstone_color/
traces = []
clusters = []
category = df_plot['player_class']
for card_iter in category.unique():
    df_filtered = df_plot[category == card_iter]
    trace = go.Scatter3d(
        type = "scatter3d",
        x = df_filtered['x'],
        y = df_filtered['y'],
        z = df_filtered['z'],
        mode = 'markers',
        name = card_iter,
        text = df_filtered['labels'],
        marker = dict(
            color = class_colors[card_iter]
        )
    )
    traces.append(trace)
    cluster = dict(
        alphahull = 3,
        name = card_iter,
        opacity = 0.1,
        type = "mesh3d",
        color = class_colors[card_iter],
        x = df_filtered['x'], y = df_filtered['y'], z = df_filtered['z']
    )
    if card_iter != 'NEUTRAL': #don't bother with clusters for neutral
        traces.append(cluster)
empty_axis = dict(zeroline=False, showaxeslabels=False, showticklabels=False, title='')
layout = go.Layout(
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0
    ),
    scene = dict(
      xaxis = empty_axis,
      yaxis = empty_axis,
      zaxis = empty_axis
  ),
  paper_bgcolor='#f7f8fa',
  plot_bgcolor='#f7f8fa'
)
#print(clusters[:2])
fig = go.Figure(data = traces, layout=layout)
py.plot(fig)
```

    'https://plot.ly/~sekki/45'
