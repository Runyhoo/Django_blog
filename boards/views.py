from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse
from django.template import loader
from boards.models import Board,Topic, Post,TopicView
from .forms import NewTopicForm,PostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from django.views.generic import UpdateView,ListView
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

# Create your views here.

def home(request):
    boards = Board.objects.all()
    context = {
        'boards': boards,
    }

    template = loader.get_template('home.html')
    return HttpResponse(template.render(context,request))

def board_topics(request, pk):
    board = Board.objects.get(pk=pk)
    queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 20)

    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        # fallback to the first page
        topics = paginator.page(1)
    except EmptyPage:
        topics = paginator.page(paginator.num_pages)
    return render(request,'topics.html',{'board':board,'topics':topics})


@login_required(login_url='login')
def new_topics(request, pk):
    board = get_object_or_404(Board,pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk,topic_pk=topic.pk)  # TODO: redirect to the created topic page
    else:
            form = NewTopicForm()
    return render(request,'new_topic.html',{'board':board,
                                                                  'form':form})


def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.user.is_authenticated:
        # 只有认证用户才记录，且每个用户只记录一次
        _, created = TopicView.objects.get_or_create(
            user=request.user,
            topic=topic
        )
        if created:
            topic.views += 1
            topic.save()
    else:
        pass

    return render(request, 'topic_posts.html', {'topic': topic})

@login_required(login_url='login')
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()  # <- here
            topic.save()  # <- and here


            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)
    else:
                form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)


    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)




