- [hs2vec](#sec-1)
    - [Setup](#sec-1-0-1)
    - [Normalize the cost, attack, and health](#sec-1-0-2)
    - [Coerce the mechanics into binary features with one hot encoding](#sec-1-0-3)
    - [Binarize and encode the playerClass](#sec-1-0-4)
    - [Binarize and encode the rarity](#sec-1-0-5)
    - [Binarize and encode the play requirements](#sec-1-0-6)
    - [Binarize and encode the type](#sec-1-0-7)
    - [Finds and binarizes all the 'deal(s) x damage' cards, along with the heal cards](#sec-1-0-8)
    - [Join the dataframes together](#sec-1-0-9)
    - [Concatenate the vector lists](#sec-1-0-10)
    - [Pass into PCA to reduce the dimensions down to 50](#sec-1-0-11)
    - [Pass into TSNE](#sec-1-0-12)
    - [Create plotly graph](#sec-1-0-13)

# hs2vec<a id="orgheadline14"></a>

by Peixian Wang - 2016/8/3

*This is licensed under MIT, so do what you want with it, modify it, fork it, etc. If you use this code I'd appreciate an attribution back :>*

**MAKE SURE YOU'RE IN THE RIGHT VIRTUALENV**

### Setup<a id="orgheadline1"></a>

Import the supporting cast

```ipython
import pandas as pd
import numpy as np
```

```ipython
df = pd.read_json('../data/cards.json')
print(df.head(3))
print(df.columns)
```

      artist  attack  collectible  cost  durability dust entourage faction flavor  \
    0    NaN     0.0          NaN   0.0         NaN  NaN       NaN     NaN    NaN   
    1    NaN     NaN          NaN   2.0         NaN  NaN       NaN     NaN    NaN   
    2    NaN     1.0          NaN   1.0         NaN  NaN       NaN     NaN    NaN   
    
       health     ...     overload  \
    0     2.0     ...          NaN   
    1     NaN     ...          NaN   
    2     1.0     ...          NaN   
    
                                        playRequirements playerClass    race  \
    0                                                NaN      SHAMAN     NaN   
    1  {'REQ_MINION_OR_ENEMY_HERO': 0, 'REQ_STEADY_SH...      HUNTER     NaN   
    2                                                NaN     NEUTRAL  DRAGON   
    
      rarity         set spellDamage targetingArrowText  \
    0    NaN         TGT         NaN                NaN   
    1   FREE  HERO_SKINS         NaN                NaN   
    2    NaN         BRM         NaN                NaN   
    
                                                    text        type  
    0                             <b>Spell Damage +1</b>      MINION  
    1  <b>Hero Power</b>\nDeal $2 damage to the enemy...  HERO_POWER  
    2                                                NaN      MINION  
    
    [3 rows x 25 columns]
    Index(['artist', 'attack', 'collectible', 'cost', 'durability', 'dust',
           'entourage', 'faction', 'flavor', 'health', 'howToEarn',
           'howToEarnGolden', 'id', 'mechanics', 'name', 'overload',
           'playRequirements', 'playerClass', 'race', 'rarity', 'set',
           'spellDamage', 'targetingArrowText', 'text', 'type'],
          dtype='object')

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

             id    attack  cost    health
    3    OG_121  0.583333  0.28  0.466667
    6    OG_085  0.166667  0.16  0.266667
    10   AT_076  0.250000  0.16  0.266667
    15  CS2_124  0.250000  0.12  0.066667
    17  GVG_079  0.583333  0.32  0.466667

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

    ['ADJACENT_BUFF' 'AURA' 'BATTLECRY' 'CANT_ATTACK'
     'CANT_BE_TARGETED_BY_ABILITIES' 'CANT_BE_TARGETED_BY_HERO_POWERS' 'CHARGE'
     'CHOOSE_ONE' 'COMBO' 'DEATHRATTLE' 'DIVINE_SHIELD' 'ENRAGED' 'FORGETFUL'
     'FREEZE' 'INSPIRE' 'ImmuneToSpellpower' 'InvisibleDeathrattle' 'NONE'
     'OVERLOAD' 'POISONOUS' 'RITUAL' 'SECRET' 'SILENCE' 'SPELL_DAMAGE'
     'STEALTH' 'TAUNT' 'TOPDECK' 'WINDFURY']
             id        mechanics  \
    3    OG_121      [BATTLECRY]   
    6    OG_085           [NONE]   
    10   AT_076        [INSPIRE]   
    15  CS2_124         [CHARGE]   
    17  GVG_079  [DIVINE_SHIELD]   
    
                                      mechanics_binarized  \
    3   [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...   
    6   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...   
    10  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ...   
    15  [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, ...   
    17  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, ...   
    
                                         mechanics_sparse  
    3     (0, 54)\t1.0\n  (0, 52)\t1.0\n  (0, 50)\t1.0...  
    6     (0, 54)\t1.0\n  (0, 52)\t1.0\n  (0, 50)\t1.0...  
    10    (0, 54)\t1.0\n  (0, 52)\t1.0\n  (0, 50)\t1.0...  
    15    (0, 54)\t1.0\n  (0, 52)\t1.0\n  (0, 50)\t1.0...  
    17    (0, 54)\t1.0\n  (0, 52)\t1.0\n  (0, 50)\t1.0...

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

    ['DRUID' 'HUNTER' 'MAGE' 'NEUTRAL' 'PALADIN' 'PRIEST' 'ROGUE' 'SHAMAN'
     'WARLOCK' 'WARRIOR']
             id playerClass          player_class_binarized  \
    3    OG_121     WARLOCK  [0, 0, 0, 0, 0, 0, 0, 0, 1, 0]   
    6    OG_085        MAGE  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]   
    10   AT_076     PALADIN  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]   
    15  CS2_124     NEUTRAL  [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]   
    17  GVG_079     NEUTRAL  [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]   
    
                                      player_class_sparse  
    3     (0, 18)\t1.0\n  (0, 17)\t1.0\n  (0, 14)\t1.0...  
    6     (0, 18)\t1.0\n  (0, 17)\t1.0\n  (0, 14)\t1.0...  
    10    (0, 18)\t1.0\n  (0, 17)\t1.0\n  (0, 14)\t1.0...  
    15    (0, 18)\t1.0\n  (0, 17)\t1.0\n  (0, 14)\t1.0...  
    17    (0, 18)\t1.0\n  (0, 17)\t1.0\n  (0, 14)\t1.0...

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

    ['COMMON' 'EPIC' 'FREE' 'LEGENDARY' 'RARE']
             id     rarity rarity_binarized  \
    3    OG_121  LEGENDARY  [0, 0, 0, 1, 0]   
    6    OG_085       RARE  [0, 0, 0, 0, 1]   
    10   AT_076     COMMON  [1, 0, 0, 0, 0]   
    15  CS2_124       FREE  [0, 0, 1, 0, 0]   
    17  GVG_079     COMMON  [1, 0, 0, 0, 0]   
    
                                            rarity_sparse  
    3     (0, 8)\t1.0\n  (0, 7)\t1.0\n  (0, 4)\t1.0\n ...  
    6     (0, 8)\t1.0\n  (0, 7)\t1.0\n  (0, 4)\t1.0\n ...  
    10    (0, 8)\t1.0\n  (0, 7)\t1.0\n  (0, 4)\t1.0\n ...  
    15    (0, 8)\t1.0\n  (0, 7)\t1.0\n  (0, 4)\t1.0\n ...  
    17    (0, 8)\t1.0\n  (0, 7)\t1.0\n  (0, 4)\t1.0\n ...  
    <class 'scipy.sparse.csr.csr_matrix'>

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

    ['NONE' 'REQ_DAMAGED_TARGET_0' 'REQ_ENEMY_TARGET_0'
     'REQ_FRIENDLY_MINION_DIED_THIS_GAME_0' 'REQ_FRIENDLY_TARGET_0'
     'REQ_FROZEN_TARGET_0' 'REQ_HERO_TARGET_0' 'REQ_LEGENDARY_TARGET_0'
     'REQ_MINIMUM_ENEMY_MINIONS_1' 'REQ_MINIMUM_ENEMY_MINIONS_2'
     'REQ_MINIMUM_TOTAL_MINIONS_1' 'REQ_MINIMUM_TOTAL_MINIONS_2'
     'REQ_MINION_TARGET_0' 'REQ_MUST_TARGET_TAUNTER_0' 'REQ_NONSELF_TARGET_0'
     'REQ_NUM_MINION_SLOTS_1' 'REQ_TARGET_FOR_COMBO_0'
     'REQ_TARGET_IF_AVAILABLE_0' 'REQ_TARGET_IF_AVAILABLE_AND_DRAGON_IN_HAND_0'
     'REQ_TARGET_IF_AVAILABLE_AND_MINIMUM_FRIENDLY_MINIONS_4'
     'REQ_TARGET_MAX_ATTACK_2' 'REQ_TARGET_MAX_ATTACK_3'
     'REQ_TARGET_MIN_ATTACK_5' 'REQ_TARGET_MIN_ATTACK_7' 'REQ_TARGET_TO_PLAY_0'
     'REQ_TARGET_WITH_DEATHRATTLE_0' 'REQ_TARGET_WITH_RACE_14'
     'REQ_TARGET_WITH_RACE_15' 'REQ_TARGET_WITH_RACE_17'
     'REQ_TARGET_WITH_RACE_20' 'REQ_UNDAMAGED_TARGET_0' 'REQ_WEAPON_EQUIPPED_0']

### Binarize and encode the type<a id="orgheadline7"></a>

```ipython
df_type = df[['id', 'type']]
mlbin = LabelBinarizer()
binarized = mlbin.fit_transform(df_type['type'])
df_type['type_binarized'] = binarized.tolist()
print(mlbin.classes_)
```

    ['MINION' 'SPELL' 'WEAPON']

### Finds and binarizes all the 'deal(s) x damage' cards, along with the heal cards<a id="orgheadline8"></a>

All targeted damage cards are denoted with a $, healing is denoted with a #
The exceptions to this are random targets a (Eyedis Darkbane) and no targets (Darkiron Skulker)

```ipython
import re
df_damage = df[['id', 'text']]
damage_text = re.compile(r'.*eal(s)* \$*[0-9]* .amage', re.DOTALL)
health_text = re.compile(r'.*estore(s)*\s*\#*[0-9]\s*.ealth', re.DOTALL)
damage_binarized = []
for i, row in df_damage.iterrows():
    #create a binarized vector with keys [damage, health]
    val = [0, 0]
    if damage_text.match(str(row['text'])):
        val[0] = 1
    if health_text.match(str(row['text'])):
        val[1] = 1
    damage_binarized.append(val)
df_damage['damage_binarized'] = damage_binarized
print(df_damage.head(10))
```

             id                                               text  \
    3    OG_121  <b>Battlecry:</b> The next spell you cast this...   
    6    OG_085  After you cast a spell, <b>Freeze</b> a random...   
    10   AT_076            <b>Inspire:</b> Summon a random Murloc.   
    15  CS2_124                                      <b>Charge</b>   
    17  GVG_079                               <b>Divine Shield</b>   
    18  BRM_011  Deal $2 damage.\nUnlock your <b>Overloaded</b>...   
    19  CS2_122                 Your other minions have +1 Attack.   
    23  EX1_339  Copy 2 cards from your opponent's deck and put...   
    24  GVG_007  When you draw this, deal 2 damage to all chara...   
    25  GVG_086  Whenever you gain Armor, give this minion +1 A...   
    
       damage_binarized  
    3            [0, 0]  
    6            [0, 0]  
    10           [0, 0]  
    15           [0, 0]  
    17           [0, 0]  
    18           [1, 0]  
    19           [0, 0]  
    23           [0, 0]  
    24           [1, 0]  
    25           [0, 0]

### Join the dataframes together<a id="orgheadline9"></a>

```ipython
df_combined = df_n_stats.merge(df_mechanics, on='id')
df_combined = df_combined.merge(df_player_class, on='id')
df_combined = df_combined.merge(df_rarity, on='id')
df_combined = df_combined.merge(df_play_requirements, on='id')
df_combined = df_combined.merge(df_type, on='id')
df_combined = df_combined.merge(df_damage, on='id')
print(df_combined.head(5))
```

            id    attack  cost    health        mechanics  \
    0   OG_121  0.583333  0.28  0.466667      [BATTLECRY]   
    1   OG_085  0.166667  0.16  0.266667           [NONE]   
    2   AT_076  0.250000  0.16  0.266667        [INSPIRE]   
    3  CS2_124  0.250000  0.12  0.066667         [CHARGE]   
    4  GVG_079  0.583333  0.32  0.466667  [DIVINE_SHIELD]   
    
                                     mechanics_binarized  \
    0  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...   
    1  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...   
    2  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ...   
    3  [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, ...   
    4  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, ...   
    
                                        mechanics_sparse playerClass  \
    0    (0, 54)\t1.0\n  (0, 52)\t1.0\n  (0, 50)\t1.0...     WARLOCK   
    1    (0, 54)\t1.0\n  (0, 52)\t1.0\n  (0, 50)\t1.0...        MAGE   
    2    (0, 54)\t1.0\n  (0, 52)\t1.0\n  (0, 50)\t1.0...     PALADIN   
    3    (0, 54)\t1.0\n  (0, 52)\t1.0\n  (0, 50)\t1.0...     NEUTRAL   
    4    (0, 54)\t1.0\n  (0, 52)\t1.0\n  (0, 50)\t1.0...     NEUTRAL   
    
               player_class_binarized  \
    0  [0, 0, 0, 0, 0, 0, 0, 0, 1, 0]   
    1  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]   
    2  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]   
    3  [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]   
    4  [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]   
    
                                     player_class_sparse     rarity  \
    0    (0, 18)\t1.0\n  (0, 17)\t1.0\n  (0, 14)\t1.0...  LEGENDARY   
    1    (0, 18)\t1.0\n  (0, 17)\t1.0\n  (0, 14)\t1.0...       RARE   
    2    (0, 18)\t1.0\n  (0, 17)\t1.0\n  (0, 14)\t1.0...     COMMON   
    3    (0, 18)\t1.0\n  (0, 17)\t1.0\n  (0, 14)\t1.0...       FREE   
    4    (0, 18)\t1.0\n  (0, 17)\t1.0\n  (0, 14)\t1.0...     COMMON   
    
      rarity_binarized                                      rarity_sparse  \
    0  [0, 0, 0, 1, 0]    (0, 8)\t1.0\n  (0, 7)\t1.0\n  (0, 4)\t1.0\n ...   
    1  [0, 0, 0, 0, 1]    (0, 8)\t1.0\n  (0, 7)\t1.0\n  (0, 4)\t1.0\n ...   
    2  [1, 0, 0, 0, 0]    (0, 8)\t1.0\n  (0, 7)\t1.0\n  (0, 4)\t1.0\n ...   
    3  [0, 0, 1, 0, 0]    (0, 8)\t1.0\n  (0, 7)\t1.0\n  (0, 4)\t1.0\n ...   
    4  [1, 0, 0, 0, 0]    (0, 8)\t1.0\n  (0, 7)\t1.0\n  (0, 4)\t1.0\n ...   
    
      playRequirements                        play_requirements_binarized    type  \
    0           [NONE]  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...  MINION   
    1           [NONE]  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...  MINION   
    2           [NONE]  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...  MINION   
    3           [NONE]  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...  MINION   
    4           [NONE]  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...  MINION   
    
      type_binarized                                               text  \
    0      [1, 0, 0]  <b>Battlecry:</b> The next spell you cast this...   
    1      [1, 0, 0]  After you cast a spell, <b>Freeze</b> a random...   
    2      [1, 0, 0]            <b>Inspire:</b> Summon a random Murloc.   
    3      [1, 0, 0]                                      <b>Charge</b>   
    4      [1, 0, 0]                               <b>Divine Shield</b>   
    
      damage_binarized  
    0           [0, 0]  
    1           [0, 0]  
    2           [0, 0]  
    3           [0, 0]  
    4           [0, 0]

convert the sparse matricies into csc format

```ipython
transpose_to_csc = lambda x: x.tocsc()
df_combined[['mechanics_sparse', 'player_class_sparse', 'rarity_sparse']] = df_combined[['mechanics_sparse','player_class_sparse', 'rarity_sparse']].applymap(lambda x: x.tocsc())
print(df_combined.dtypes)
#df_sparse = df_combined[['mechanics_sparse', 'player_class_sparse', 'rarity_sparse']].apply(lambda x: x.tocsc(), axis=0)
#combined_spark_df = spark.createDataFrame(df_combined)
```

    id                              object
    attack                         float64
    cost                           float64
    health                         float64
    mechanics                       object
    mechanics_binarized             object
    mechanics_sparse                object
    playerClass                     object
    player_class_binarized          object
    player_class_sparse             object
    rarity                          object
    rarity_binarized                object
    rarity_sparse                   object
    playRequirements                object
    play_requirements_binarized     object
    type                            object
    type_binarized                  object
    text                            object
    damage_binarized                object
    dtype: object

### Concatenate the vector lists<a id="orgheadline10"></a>

```ipython
from sklearn.decomposition import PCA
from scipy.sparse import hstack
n_stats = ['attack', 'health']
header_list = list(df_combined.columns.values)
iter_headers = [header for header in header_list if 'binarized' in header]
df_combined['features'] = df_combined[n_stats].values.tolist()
for i, row in df_combined.iterrows():
    val = row['features']
    for header in iter_headers:
        val.extend(row[header])
    df_combined.set_value(i, 'features', val)
print(df_combined.head(5))
print(len(df_combined['features'][0]))
```

            id    attack  cost    health        mechanics  \
    0   OG_121  0.583333  0.28  0.466667      [BATTLECRY]   
    1   OG_085  0.166667  0.16  0.266667           [NONE]   
    2   AT_076  0.250000  0.16  0.266667        [INSPIRE]   
    3  CS2_124  0.250000  0.12  0.066667         [CHARGE]   
    4  GVG_079  0.583333  0.32  0.466667  [DIVINE_SHIELD]   
    
                                     mechanics_binarized  \
    0  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...   
    1  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...   
    2  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ...   
    3  [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, ...   
    4  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, ...   
    
                                        mechanics_sparse playerClass  \
    0    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (2, 0)\t1.0\n ...     WARLOCK   
    1    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (2, 0)\t1.0\n ...        MAGE   
    2    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (2, 0)\t1.0\n ...     PALADIN   
    3    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (2, 0)\t1.0\n ...     NEUTRAL   
    4    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (2, 0)\t1.0\n ...     NEUTRAL   
    
               player_class_binarized  \
    0  [0, 0, 0, 0, 0, 0, 0, 0, 1, 0]   
    1  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]   
    2  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]   
    3  [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]   
    4  [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]   
    
                                     player_class_sparse     rarity  \
    0    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (2, 0)\t1.0\n ...  LEGENDARY   
    1    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (2, 0)\t1.0\n ...       RARE   
    2    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (2, 0)\t1.0\n ...     COMMON   
    3    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (2, 0)\t1.0\n ...       FREE   
    4    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (2, 0)\t1.0\n ...     COMMON   
    
      rarity_binarized                                      rarity_sparse  \
    0  [0, 0, 0, 1, 0]    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (3, 0)\t1.0\n ...   
    1  [0, 0, 0, 0, 1]    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (3, 0)\t1.0\n ...   
    2  [1, 0, 0, 0, 0]    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (3, 0)\t1.0\n ...   
    3  [0, 0, 1, 0, 0]    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (3, 0)\t1.0\n ...   
    4  [1, 0, 0, 0, 0]    (0, 0)\t1.0\n  (1, 0)\t1.0\n  (3, 0)\t1.0\n ...   
    
      playRequirements                        play_requirements_binarized    type  \
    0           [NONE]  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...  MINION   
    1           [NONE]  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...  MINION   
    2           [NONE]  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...  MINION   
    3           [NONE]  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...  MINION   
    4           [NONE]  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...  MINION   
    
      type_binarized                                               text  \
    0      [1, 0, 0]  <b>Battlecry:</b> The next spell you cast this...   
    1      [1, 0, 0]  After you cast a spell, <b>Freeze</b> a random...   
    2      [1, 0, 0]            <b>Inspire:</b> Summon a random Murloc.   
    3      [1, 0, 0]                                      <b>Charge</b>   
    4      [1, 0, 0]                               <b>Divine Shield</b>   
    
      damage_binarized                                           features  
    0           [0, 0]  [0.5833333333333333, 0.4666666666666667, 0, 0,...  
    1           [0, 0]  [0.16666666666666666, 0.26666666666666666, 0, ...  
    2           [0, 0]  [0.25, 0.26666666666666666, 0, 0, 0, 0, 0, 0, ...  
    3           [0, 0]  [0.25, 0.06666666666666667, 0, 0, 0, 0, 0, 0, ...  
    4           [0, 0]  [0.5833333333333333, 0.4666666666666667, 0, 0,...  
    82

### Pass into PCA to reduce the dimensions down to 50<a id="orgheadline11"></a>

```ipython
from sklearn.decomposition import PCA
pca = PCA(n_components = 50)
pca_features = pca.fit_transform(df_combined['features'].tolist())
df_combined['pca_features'] = pca_features.tolist()
print(df_combined['pca_features'].head(5))
print(pca.explained_variance_ratio_)
```

    0    [-0.7546125898341142, 0.3109435899222342, -0.4...
    1    [-0.020847952649766004, 0.9224738688260612, 0....
    2    [-0.33925705957152824, -0.547709108625113, 0.3...
    3    [-0.6831570258323537, 0.13081263174728183, 0.1...
    4    [-0.8229260946759818, -0.6830626665540008, 0.3...
    Name: pca_features, dtype: object
    [ 0.22545168  0.09439072  0.08411502  0.06144576  0.04989462  0.03873717
      0.03684653  0.03323254  0.03002102  0.02111748  0.02097391  0.01995929
      0.01951327  0.01898548  0.01860501  0.01824986  0.01795614  0.01723633
      0.01509929  0.01479114  0.01316465  0.01135129  0.0097778   0.00799817
      0.0072036   0.0062829   0.00605377  0.00600344  0.00498473  0.00491853
      0.00455807  0.00421019  0.00393334  0.00380949  0.00369876  0.00353471
      0.00335253  0.00308618  0.00276883  0.00269349  0.00267812  0.00246453
      0.00232219  0.00181396  0.00159759  0.00136127  0.00122954  0.00113886
      0.00103312  0.00102281]

### Pass into TSNE<a id="orgheadline12"></a>

```ipython
from sklearn.manifold import TSNE
dimensions = 3
tnse_model = TSNE(n_components=dimensions, n_iter=10000000, metric="correlation", learning_rate=50, early_exaggeration=500.0, perplexity=40.0)
#tnse_model = TSNE(n_components = 3)
np.set_printoptions(suppress=True)
model = tnse_model.fit_transform(df_combined['pca_features'].tolist())
```

```ipython
df_plot = pd.DataFrame(model)
df_plot.columns = ['x', 'y', 'z']
df_plot['labels'] = list(map(lambda x: df[df['id'] == x]['name'].values[0], df_combined['id']))
df_plot['rarity'] = df_combined['rarity']
df_plot['cost'] = df_combined['cost']
df_plot['player_class'] = df_combined['playerClass']
df_plot['type'] = df_combined['type']
df_plot['card_info'] = list(map(lambda x: df[df['id']==x]['text'].values[0], df_combined['id']))
df_plot['card_set'] = list(map(lambda x: df[df['id'] == x]['set'].values[0], df_combined['id']))
print(df_plot.head(5))
```

              x         y         z                labels     rarity  cost  \
    0  2.342262 -0.101746 -1.961431              Cho'gall  LEGENDARY  0.28   
    1  2.780964 -1.692352  0.758270  Demented Frostcaller       RARE  0.16   
    2 -1.362544 -2.352792 -0.437803         Murloc Knight     COMMON  0.16   
    3 -0.175904 -1.200762 -3.346595             Wolfrider       FREE  0.12   
    4 -0.998853 -3.139931 -2.670621        Force-Tank MAX     COMMON  0.32   
    
      player_class    type                                          card_info  \
    0      WARLOCK  MINION  <b>Battlecry:</b> The next spell you cast this...   
    1         MAGE  MINION  After you cast a spell, <b>Freeze</b> a random...   
    2      PALADIN  MINION            <b>Inspire:</b> Summon a random Murloc.   
    3      NEUTRAL  MINION                                      <b>Charge</b>   
    4      NEUTRAL  MINION                               <b>Divine Shield</b>   
    
      card_set  
    0       OG  
    1       OG  
    2      TGT  
    3     CORE  
    4      GVG

Write out plot to a csv file

```ipython
df_plot.to_csv('../results/model.csv')
```

Write out the features array to a csv file

```ipython
df_combined.to_csv('../results/features.csv')
```

```ipython
print(df_plot.dtypes)
```

    x               float64
    y               float64
    z               float64
    labels           object
    rarity           object
    cost            float64
    player_class     object
    type             object
    card_info        object
    card_set         object
    dtype: object

### Create plotly graph<a id="orgheadline13"></a>

```ipython
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
def create_text(df):
    convert = lambda x: '{}:<br>{}'.format(x[0], x[1])
    return df.apply(convert, axis=1)

rarity_colors = {'LEGENDARY': '#F535A5', 'RARE': '#3993F9', 'EPIC': '#CC47D5', 'COMMON': '#F3F9F1', 'FREE': '#263238' }
class_colors = {'WARRIOR': '#8D0F01', 'SHAMAN': '#011784', 'ROGUE': '#4B4C47', 'PALADIN': '#A98E00', 'HUNTER': '#006E00', 'DRUID': '#703505', 'WARLOCK': '#7623AD', 'MAGE': '#0091AB', 'PRIEST': '#C7C19E', 'NEUTRAL': '#263238'} #colors from: https://www.reddit.com/r/hearthstone/comments/2d0x31/mtg_has_the_color_pie_here_is_a_hearthstone_color/
standard_sets = ('OG', 'TGT', 'CORE', 'BRM', 'LOE')
traces = []
clusters = []
df_plot = pd.read_csv('../results/model.csv')
category = df_plot['player_class']
for card_iter in category.unique():
    df_filtered = df_plot[(category == card_iter)]
    #df_filtered = df_filtered.query('card_set in {}'.format(standard_sets))
    trace = go.Scatter3d(
        type = "scatter3d",
        x = df_filtered['x'],
        y = df_filtered['y'],
        z = df_filtered['z'],
        mode = 'markers',
        name = card_iter,
        text = create_text(df_filtered[['labels', 'card_info']]),
        marker = dict(
            color = class_colors[card_iter]
        )
    )
    traces.append(trace)
    cluster = dict(
        alphahull = 3,
        name = card_iter,
        opacity = 0.05,
        type = "mesh3d",
        color = class_colors[card_iter],
        x = df_filtered['x'], y = df_filtered['y'], z = df_filtered['z']
    )
    #if card_iter != 'NEUTRAL': #don't bother with clusters for neutral
        #traces.append(cluster)
empty_axis = dict(zeroline=False, showaxeslabels=False, showticklabels=False, title='')
layout = dict(
    title = '3D Projection of All Wild Cards',
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=100
    ),
    scene = dict(
      xaxis = empty_axis,
      yaxis = empty_axis,
      zaxis = empty_axis
    ),
    legend = dict (
        orientation = 'h'
    ),
    paper_bgcolor='#f7f8fa',
    plot_bgcolor='#f7f8fa'
)
fig = go.Figure(data = traces, layout=layout)
py.plot(fig)
```

    'https://plot.ly/~sekki/95'
