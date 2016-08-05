- [Maps Hearthstone cards to vectors for easy comparison](#sec-1)
    - [Demo - <https://peixian.github.io/hs2vec/>](#sec-1-0-1)
    - [What is this?](#sec-1-0-2)
    - [Data:](#sec-1-0-3)
    - [Code:](#sec-1-0-4)
  - [References:](#sec-1-1)
    - [[word2vec](https://radimrehurek.com/gensim/models/word2vec.html)](#sec-1-1-1)
    - [[web patterns](http://www.clips.ua.ac.be/pages/pattern-web)](#sec-1-1-2)
    - [[word2map](https://github.com/overlap-ai/words2map)](#sec-1-1-3)
    - [[mtgencode](https://github.com/billzorn/mtgencode)](#sec-1-1-4)
    - [[CardCrunch](https://github.com/PAK90/cardcrunch)](#sec-1-1-5)
    - [[pokemon-3d](https://github.com/minimaxir/pokemon-3d)](#sec-1-1-6)

# Maps Hearthstone cards to vectors for easy comparison<a id="orgheadline13"></a>

### Demo - <https://peixian.github.io/hs2vec/><a id="orgheadline1"></a>

### What is this?<a id="orgheadline2"></a>

Inspired by yhat's [word2vec](https://radimrehurek.com/gensim/models/word2vec.html) and minimaxir's [pokemon-3d](https://github.com/minimaxir/pokemon-3d) projects, I decided to see if it was possible to visualize all Hearthstone cards in 3d space. This is done in a few steps:

1.  Normalize all numerical values (cost, attack, health). Spells are assumed to have 0 health and 0 attack (this is probably horribly wrong, but the reasoning is left as an exercise to the reader).
2.  Binarize all the other data (mechanics, card class, rarity, play requirements, type).
3.  Dump everything into PCA and reduce it down to 50 dimensions (see <http://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html>)
4.  Use TNSE to condense into 3 dimensions and plot.

### Data:<a id="orgheadline3"></a>

There's two files in the results folder: features.csv and model.csv.

\`features.csv\` contains 877 rows, each row representing a different card: 

```:export
id                              hearthstone.json id
attack                          attack normalized to between [0,1]
cost                            mana cost normalized to [0,1]
health                          health normalized to [0,1]
mechanics                       string list of mechanics for the card
mechanics_binarized             binarized array of mechanics
mechanics_sparse                sparse array of mechanics
playerClass                     class the card belongs to
player_class_binarized          binarized array of player_classes
player_class_sparse             sparse array of player_classes
rarity                          rarity of the card
rarity_binarized                binarized array of rarities
rarity_sparse                   sparse array of the card
playRequirements                string list of play requirements
play_requirements_binarized     binarized list of play requirements
type                            type of card
type_binarized                  binarized list of types
text                            card text
damage_binarized                binarized array whether the card deals damage, restores health, or neither
features                        array concatenated from [attack, cost, health, mechanics_binarized, player_class_binarized, rarity_binarized, play_requirements_binarized, type_binarized, damage_binarized]
pca_features                    array of 50 dimensions, pca features
```

\`model.csv\` contains also 877 rows (each row is a card), but it's used to generate the 3d plot:

```:exports
x                TNSE generated x coordinate
y                TNSE generated y coordinate
z                TNSE generated z coordinate
labels           name of the card
rarity           rarity of the card
cost             cost of the card
player_class     class the card belongs to
type             type of the card
card_info        card text
card_set         card set
```

### Code:<a id="orgheadline5"></a>

All the code can be found in [hs<sub>pca.org</sub>](./notebook/hs_pca.md). 
This was made in org-babel, but github doesn't play as nice with org as it does with ipython notebooks, so there's a [hs<sub>pca.md</sub>](./notebooks/hs_pca.md) file for easier viewing online. 

1.  Requirements:

    If you want to run the org file you'll need scipi, numpy, pandas and scikit-learn. 

## References:<a id="orgheadline12"></a>

### [word2vec](https://radimrehurek.com/gensim/models/word2vec.html)<a id="orgheadline6"></a>

### [web patterns](http://www.clips.ua.ac.be/pages/pattern-web)<a id="orgheadline7"></a>

### [word2map](https://github.com/overlap-ai/words2map)<a id="orgheadline8"></a>

### [mtgencode](https://github.com/billzorn/mtgencode)<a id="orgheadline9"></a>

### [CardCrunch](https://github.com/PAK90/cardcrunch)<a id="orgheadline10"></a>

### [pokemon-3d](https://github.com/minimaxir/pokemon-3d)<a id="orgheadline11"></a>
