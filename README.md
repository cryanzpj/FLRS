# FLRS: a Django Template for Recommendation Websites 

A physics literature recommendation website based on data from [INSPIRE-HEP](http://inspirehep.net/). Only The abstract was used to train the model. The baseline model is tf-idf + clustering + cosine similarity. The code can be used as a starting template for recommendation based websites.

![scalar](./image/shot.png)

## Usage
To run on a local server: 
```
python manage.py runserver
```
And access the website at http://127.0.0.1:8000/reviews/paper

To use database commands: 
```
python manage.py dbshell
```
To load your own data, modify the load.py 



Prerequisites
-------------
- Python 2.7
- [NLTK](http://www.nltk.org/)
- [Sklearn](http://scikit-learn.org/stable/)
- [Gensim](https://radimrehurek.com/gensim/)
- [Django](https://www.djangoproject.com/)
