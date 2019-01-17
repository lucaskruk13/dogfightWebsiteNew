from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import login as auth_login
from .forms import SignUpForm, ProfileForm
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, DetailView
from .models import Profile, Scores
from django.conf import  settings




@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):

    model = Profile

    template_name = 'accounts/my_account.html'
    form_class = ProfileForm
    success_url = reverse_lazy('feed')


    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        profile = self.request.user.profile

        if profile.initial: # to change from initial run after the handicap has been updated
            profile.initial = False

        profile.save()
        return super().form_valid(form)

    # def get_success_url(self, **kwargs):
    #     if kwargs != None:
    #         return reverse_lazy('profile', kwargs = {'user_pk': self.request.user.id})


class ProfileView(DetailView):

    model = Profile
    template_name = 'accounts/profile.html'
    pk_url_kwarg = "user_pk"


    def get_object(self, queryset=None):
        return get_object_or_404(Profile, pk=self.kwargs.get('user_pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get additional Context

        context['scores'] = Scores.objects.filter(user=self.kwargs.get('user_pk')).order_by('created_at').reverse()
        context['profile_image_path'] = settings.MEDIA_URL

        return context



# @method_decorator(login_required, name='dispatch')
# class UserUpdateView(UpdateView):
#     model = User
#     fields = ('first_name', 'last_name', 'email',)
#     template_name = 'accounts/my_account.html'
#     success_url = reverse_lazy('my_account')
#
#     def get_object(self, queryset=None):
#         return self.request.user

# Create your views here.
def signup(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('my_account')
    else:
        form = SignUpForm()
    return render(request, 'accounts/auth/signup.html', {'form': form})

