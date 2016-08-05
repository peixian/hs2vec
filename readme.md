- [Maps Hearthstone cards to vectors for easy comparison](#sec-1)
- [Installation:](#sec-2)
  - [References:](#sec-2-1)
    - [[word2vec](https://radimrehurek.com/gensim/models/word2vec.html)](#sec-2-1-1)
    - [[web patterns](http://www.clips.ua.ac.be/pages/pattern-web)](#sec-2-1-2)
    - [[word2map](https://github.com/overlap-ai/words2map)](#sec-2-1-3)
    - [[mtgencode](https://github.com/billzorn/mtgencode)](#sec-2-1-4)
    - [[CardCrunch](https://github.com/PAK90/cardcrunch)](#sec-2-1-5)

# Maps Hearthstone cards to vectors for easy comparison<a id="orgheadline1"></a>

# Installation:<a id="orgheadline8"></a>

If you have the usual tools of the trade for ml (pandas, numpy, etc), this'll be easy. Otherwise strap in.

1.  Install [anaconda](https://www.continuum.io/downloads) and create a new virtualenv in python3 with pandas and numpy.
2.  Run the following script:

```sh
mkdir hearthstone_data
cd hearthstone_data
git clone https://github.com/peixian/Yet-Another-Hearthstone-Analyzer
mv Yet-Another-Hearthstone-Analyzer yaha
git clone https://github.com/peixian/hs2vec
cd hs2vec
mkdir test_data
```

1.  Install the requirements with:

```sh
pip install -r requirements.txt
```

1.  Open emacs, switch to the virtualenv you just made in emacs, and you *should* be able to run the org-babel file. Feel free to open a github issue if it doesn't work.

## References:<a id="orgheadline7"></a>

### [word2vec](https://radimrehurek.com/gensim/models/word2vec.html)<a id="orgheadline2"></a>

### [web patterns](http://www.clips.ua.ac.be/pages/pattern-web)<a id="orgheadline3"></a>

### [word2map](https://github.com/overlap-ai/words2map)<a id="orgheadline4"></a>

### [mtgencode](https://github.com/billzorn/mtgencode)<a id="orgheadline5"></a>

### [CardCrunch](https://github.com/PAK90/cardcrunch)<a id="orgheadline6"></a>
