from django.shortcuts import get_object_or_404, render

from sklearn.neighbors import NearestNeighbors
from django.contrib.auth.decorators import login_required
from .models import Review, Paper,Paper_cluster,Author
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .forms import ReviewForm
import datetime
import numpy as np
from collections import defaultdict



def find_similar_article(paper,num = 10):
    target = paper.vec_tfidf().reshape(1,-1)
    paper_list = paper.cluster.paper_set.exclude(recid = paper.recid)
    recid_list = np.array(map(lambda x:x.recid,paper_list))
    features = np.array(map(lambda x:x.vec_tfidf(),paper_list))

    NN_model = NearestNeighbors(n_neighbors=10, algorithm='brute', metric='cosine')
    NN_model.fit(features)

    try: num = int(num)
    except ValueError:
        num = 50

    score, similar_intem_index = NN_model.kneighbors(target, n_neighbors=num)
    recid_reults = recid_list[similar_intem_index[0]]
    qs = Paper.objects.filter(recid__in = recid_reults)

    qs_sorted = list()
    for id in recid_reults:
        qs_sorted.append(qs.get(recid=id))
    return qs_sorted, 1-score[0]


def review_list(request):
    latest_review_list = Review.objects.order_by('-pub_date')[:9]
    context = {'latest_review_list':latest_review_list}
    return render(request, 'reviews/review_list.html', context)


def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'reviews/review_detail.html', {'review': review})

def check_form(request,subset = None):
    if "orderby" in request.POST:
        selected_value = request.POST["orderby"]
        if not subset:
            if selected_value == "Newest to Oldest":
                paper_list = Paper.objects.order_by('-date')
            elif selected_value == "Avg Rating: High to Low":
                paper_list = sorted(Paper.objects.all(),key = lambda x: 0 if np.isnan(x.average_rating())  else -x.average_rating())
            elif selected_value =='Num Rating: High to Low':
                paper_list = sorted(Paper.objects.all(),key = lambda x: -x.review_set.count())
            else:
                paper_list = Paper.objects.all()
        else:
            if selected_value == "Newest to Oldest":
                paper_list = subset.order_by('-date')
            elif selected_value == "Avg Rating: High to Low":
                paper_list = sorted(subset.all(),key = lambda x: 0 if np.isnan(x.average_rating())  else -x.average_rating())
            elif selected_value =='Num Rating: High to Low':
                paper_list = sorted(subset.all(),key = lambda x: -x.review_set.count())
            else:
                paper_list = subset.all()

        if 'number' in request.POST:
            show = request.POST['number']
            if show not in ["all",'Default'] :
                context = {'paper_list':paper_list[:int(show)], "rank": selected_value,'show':show}
            elif show == "Default":
                context = {'paper_list':paper_list[:50], "rank": selected_value,'show':"Default(50)"}
            else:
                context = {'paper_list':paper_list, "rank": selected_value,'show':show}

    else:
        if not subset:
            paper_list = Paper.objects.all()[:50]
            context = {'paper_list':paper_list}
        else:
            return {'paper_list':subset}
    return context



def paper_list(request):

    context = check_form(request)
    return render(request, 'reviews/paper_list.html', context)


def paper_detail(request, paper_recid):
    paper = get_object_or_404(Paper, recid=paper_recid)
    form = ReviewForm()
    return render(request, 'reviews/paper_detail.html', {'paper': paper, 'form': form})

@login_required
def add_review(request, paper_recid):
    paper = get_object_or_404(Paper, recid=paper_recid)
    form = ReviewForm(request.POST)
    if form.is_valid():
        rating = form.cleaned_data['rating']
        comment = form.cleaned_data['comment']
        user_name = request.user.username
        review = Review()
        review.paper = paper
        review.user_name = user_name
        review.rating = rating
        review.comment = comment
        review.pub_date = datetime.datetime.now()
        review.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:paper_detail', args=(paper.recid,)))

    return render(request, 'reviews/paper_detail.html', {'paper': paper, 'form': form})

@login_required
def user_review_list(request, username=None):
    if not username:
        username = request.user.username
    latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
    context = {'latest_review_list':latest_review_list, 'username':username}
    return render(request, 'reviews/user_review_list.html', context)

def user_recommendation_list(request):
    # get this user reviews
    user_reviews = Review.objects.filter(user_name=request.user.username).prefetch_related('paper')
    # from the reviews, get a set of wine IDs
    user_reviews_paper_ids = map(lambda x: x.paper.recid, user_reviews)
    # then get a wine list excluding the previous IDs
    if not user_reviews_paper_ids:
        paper_list = []
    else:
        ratings = np.array(map(lambda x:x.rating,user_reviews),dtype = float)
        ratings /= np.sum(ratings)
    sim = defaultdict(int)
    for i,j in enumerate(user_reviews):
        papers,score = find_similar_article(j.paper,num = 10)
        index = np.array(map(lambda x:x.recid,papers))
        score = ratings[i] * score
        for n in range(10):
            sim[index[n]] += score[n]
    out = np.array(sim.items(),dtype = object)
    out_sorted = np.array(sorted(out,key =lambda x:x[1])[::-1])

    context = check_form(request)
    if "show" in context.keys():
        try: show = int(context['show'])
        except ValueError:
            show = 50
    else:
        show = 10

    if out.shape[0] < show:
        recids = out_sorted[:,0]
    else:
        recids = out_sorted[:show,0]

    paper_list = []
    for i in recids:
        paper_list.append(Paper.objects.get(recid = i))

    return render(
        request,
        'reviews/user_recommendation_list.html',
        {'username': request.user.username,'paper_list': paper_list}
    )

def show_similar_paper(request,paper_recid):
    paper= get_object_or_404(Paper, recid=paper_recid)
    #paper_list = paper.cluster.paper_set.exclude(recid = paper.recid)
    paper_list = find_similar_article(paper,"50")[0]
    context = check_form(request,paper_list)
    context["paper_list"] = paper_list
    context['paper'] = paper
    if "show" in context.keys():
        context["paper_list"] =  find_similar_article(paper,context['show'])[0]

    return render(request, 'reviews/similar_paper.html', context)



def search(request):

    if "search_box" in request.GET:
        search_box = request.GET["search_box"]
        content = {}
        if 'search_by' in request.GET:
            if request.GET["search_by"]== "Text":
                content['paper_list'] = Paper.objects.filter(name__contains=search_box).all()
            elif request.GET['search_by'] == "Author":
                authors = Author.objects.filter(name__contains = search_box ).all()
                papers = map(lambda x:x.paper_set.all(),authors)
                paper_list = papers[0]
                for i in papers[1:]:
                    paper_list = paper_list|i
                content['paper_list'] = paper_list
            else:
                content['paper_list'] = Paper.objects.filter(name__contains=search_box).all()

            content['search_by'] = request.GET["search_by"]

        else:
            content['paper_list'] = Paper.objects.filter(name__contains=search_box).all()
        content['search_box'] = request.GET["search_box"]

    else:
        content = {'paper_list':Paper.objects.all()}

    #content = check_form(request,content)
    #content['paper_list'] = check_form(request)['paper_list']


    temp = check_form(request,content['paper_list'])

    if temp['paper_list']:
        if 'search_by' in content:
            content['paper_list'] = temp['paper_list']


        #     temp['search_by'] = content['search_by']
        # content = temp


    print(content.keys())

    return render(request, 'reviews/paper_list.html', content)