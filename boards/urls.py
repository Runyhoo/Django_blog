from django.urls import path
from  .import views
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.home,name='home'),
    path('signup/', accounts_views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'),name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('boards/<int:pk>/', views.board_topics, name='board_topics'),
    path('boards/<int:pk>/new/', views.new_topics, name='new_topics'),
    path('boards/<int:pk>/topics/<int:topic_pk>/', views.topic_posts, name='topic_posts'),
    path('boards/<int:pk>/topics/<int:topic_pk>/reply/', views.reply_topic, name='reply_topic'),
    path('boards/<int:pk>/topics/<int:topic_pk>/post/<int:post_pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('settings/account/',accounts_views.UserUpdateView.as_view(), name='my_account')

]