from __future__ import unicode_literals

from django.db import models
import numpy as np




class Author(models.Model):
    name = models.CharField(max_length=128)
    def __str__(self):              # __unicode__ on Python 2
        return self.name

class Paper_cluster(models.Model):
    c_id = models.IntegerField()



class Paper(models.Model):
    name = models.CharField(max_length = 200)
    recid = models.IntegerField()
    abstract = models.CharField(max_length=2000)
    date = models.DateTimeField('date published',default="1900-01-01")
    author  = models.ManyToManyField(Author)
    cluster = models.ForeignKey(Paper_cluster, on_delete=models.CASCADE,default= 0)
    tfidf = models.CharField(max_length=5000,default = "")

    def vec_tfidf(self):
        return np.array(self.tfidf.split(','),dtype = np.float32)

    def average_rating(self):
        all_ratings = map(lambda x: x.rating, self.review_set.all())
        return np.mean(all_ratings)

    def __unicode__(self):
        return self.name


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    paper = models.ForeignKey(Paper)
    pub_date = models.DateTimeField('date published')
    user_name = models.CharField(max_length=100)
    comment = models.CharField(max_length=200)
    rating = models.IntegerField(choices=RATING_CHOICES)

