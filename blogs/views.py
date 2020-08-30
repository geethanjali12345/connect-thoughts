from django.shortcuts import render,redirect,get_object_or_404,reverse
from django.views.generic import TemplateView,ListView,DetailView,CreateView,UpdateView,DeleteView,FormView
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.http import Http404
from django.forms import modelformset_factory
from taggit.models import Tag
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .mixins import FormUserNeededMixin
from .models import Posts,UserProfile, Comment, SubComment,Category
from .forms import UserRegistrationForm,AddBlogForm,UserProfileForm

# Create your views here.
def BlogsList(request,tag_slug=None):
	query=request.GET.get("q",None)
	common_tags = Posts.tags.most_common()[:8]
	posts=Posts.objects.all()
	paginator = Paginator(posts, 2)  # 3 posts in each page
	page = request.GET.get('page',1)
	categories=Category.objects.all()
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer deliver the first page
		posts = paginator.page(1)
	except EmptyPage:
		# If page is out of range deliver last page of results
		posts = paginator.page(paginator.num_pages)
	if query is not None:
		posts=Posts.objects.all()
		posts=posts.filter(
			Q(title__icontains=query) |
			Q(content__icontains=query) |
			Q(categories__slug__icontains=query) |
			Q(user__username__icontains=query)
		)
	return render(request,'blogslist.html',{'posts':posts,'common_tags':common_tags,'categories':categories})

def BlogDetail(request, pk):
    template_name = 'blog-detail.html'
    try:
    	post = get_object_or_404(Posts, id=pk)
    except:
    	raise Http404("Blog does not exist.")

    post.read+=1
    post.save()
    comments=post.comments.filter(post=post)
    is_liked= False
    if post.likes.filter(id=request.user.id).exists():
    	is_liked=True
    # category = post.categories.all()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Posts.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    if request.method == 'POST':
        comm = request.POST.get('comm')
        comm_id = request.POST.get('comm_id')
        if comm_id:
            SubComment(post=post,
                    user = request.user,
                    comm = comm,
                    comment = Comment.objects.get(id=int(comm_id))
                ).save()
        else:
            Comment(post=post, user=request.user, comm=comm).save()
    comments = []
    for c in Comment.objects.filter(post=post):
        comments.append([c, SubComment.objects.filter(comment=c)])
    params = {
		'comments':comments,
		'blog':post,
		'pop_post': Posts.objects.order_by('-read')[:6],
		"similar_posts":similar_posts,
		'is_liked':is_liked,
		# 'total_likes':post.total_likes()
		# 'category':category
		}

    return render(request, template_name, params)


class AddBlog(LoginRequiredMixin,CreateView):
    model=Posts
    form_class=AddBlogForm
    # fields=['title','content']
    template_name='addblog.html'
    success_url="/blogs"


def tagged(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    common_tags = Posts.tags.most_common()[:4]
    posts = Posts.objects.filter(tags=tag)
    context = {
        'tag':tag,
        'common_tags':common_tags,
        'posts':posts,
    }
    return render(request, 'blogslist.html', context)

def post_by_category(request, slug):
    category = Category.objects.get(slug=slug)
    posts = Posts.objects.filter(categories__slug=slug)
    context = {
        'category': category,
        'posts': posts
    }
    return render(request, 'categories.html', context)

def authorpostsview(request):
    myposts=Posts.objects.filter(user=request.user)
    print('post',myposts)
    return render(request,'myblogs.html',{'myposts':myposts})

class UpdateBlog(UpdateView):
	model=Posts
	form_class=AddBlogForm
	# fields=['title','content']
	template_name='updateblog.html'
	success_url="/blogs"

	@method_decorator(login_required(login_url="/login"))
	def dispatch(self, *args, **kwargs):
		return super(UpdateBlog, self).dispatch(*args, **kwargs)

class DeleteBlog(DeleteView):
	model=Posts
	template_name='deleteblog.html'
	success_url='/blogs'

	@method_decorator(login_required(login_url="/login"))
	def dispatch(self, *args, **kwargs):
		return super(DeleteBlog, self).dispatch(*args, **kwargs)

@login_required(login_url="/login")
def user_profile(request):
    """Display user profile information."""
    user = request.user
    return render(request, 'profile.html', {'user': user})

@login_required(login_url="/login")
def edit_user_profile(request):
    """Edit user profile information."""
    user = request.user
    # form1 = forms.UserUpdateForm(instance=user)
    form2 =UserProfileForm(instance=user.userprofile)
    if request.method == 'POST':
        # form1 = forms.UserUpdateForm(instance=user, data=request.POST)
        form2 = UserProfileForm(
            instance=user.userprofile,
            data=request.POST,
            files=request.FILES
        )
        if form2.is_valid():
            form2.save()
            # messages.success(request, "Your profile has been updated!")
            return redirect(reverse('profile'))
    # else:
    # 	form2= UserProfileForm()
    # 	return render(request,'addprofile.html',{'form':form2})
    return render(request, 'edit_profile.html',
        {'form': form2})

class AddProfile(LoginRequiredMixin,FormUserNeededMixin,CreateView):
	# model= Posts
	form_class=UserProfileForm
	template_name='addprofile.html'
	success_url='/profile'
	
class EditUserProfileView(FormView):
	model=UserProfile
	template_name='userprofile.html'
	form_class=UserProfileForm
	def get_object(self, *args, **kwargs):
		user = get_object_or_404(User, pk=self.kwargs['pk'])
		return user.userprofile
	def get_success_url(self, *args, **kwargs):
		return reverse("blogs")


def signup(request):
    # form = UserCreationForm()
    if request.method == 'POST': #if the form has been submitted
        form = UserRegistrationForm(request.POST) #form bound with post data
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request,'signup.html',{'form': form})

def signout(request):
    logout(request)
    return redirect('/blogs')

def like_post(request):
	post=get_object_or_404(Posts,id=request.POST.get('post_id'))
	is_liked= False
	if post.likes.filter(id=request.user.id).exists():
		post.likes.remove(request.user)
		is_liked= False
	else:
		post.likes.add(request.user)
		is_liked= True
	return redirect(post.get_absolute_url())