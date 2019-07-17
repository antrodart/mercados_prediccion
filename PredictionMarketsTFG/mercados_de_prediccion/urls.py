from django.urls import path
from . import views

urlpatterns = [
	#  Static pages
    path('', views.HomePageView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
	path('contact/', views.ContactView.as_view(), name='contact'),

	#  Users
	path('user/', views.display_profile_view, name='display_profile'),
	path('user/cancel-deletion', views.cancel_deletion_user_view, name='cancel_deletion_user'),

	#  Categories
	path('categories/', views.list_categories_view, name='categories'),
	path('category/create/', views.create_category_view, name='create_category'),
	path('category/edit/', views.edit_category_view, name='edit_category'),

	#  Communities
	path('communities/all/', views.list_all_communities_view, name='list_all_communities'),
	path('communities/created/', views.list_created_communities_view, name='list_created_communities'),
	path('community/create/', views.create_community_view, name='create_community'),
	path('community/edit/', views.edit_community_view, name='edit_community'),
	path('community/', views.display_community_view, name='display_community'),
	path('community/request-join/', views.request_to_join_community, name='request_to_join_community'),
	path('community/accept/', views.accept_user_to_community_view, name='accept_user_to_community'),
	path('community/members/', views.list_members_community_view, name='list_members_community'),

	#  Markets
	path('market/create/', views.create_market_view, name='create_market'),
	path('market/edit/', views.edit_market_view, name='edit_market'),
	path('market/', views.display_market_view, name='display_market'),
	path('markets/', views.list_markets_view, name='markets'),
	path('judge-markets/', views.list_judge_public_markets, {'created': False}, name='judge_public_markets'),
	path('judge-markets/created/', views.list_judge_public_markets, {'created': True}, name='judge_public_markets'),
	path('judge-markets/judge/<int:market_id>/<slug:slug>', views.judge_market, name='judge_market'),

	#  Assets
	path('asset/buy/', views.buy_asset_view, name='buy_asset'),

	#  AJAX calls
	path('ajax/related_markets/', views.ajax_related_markets, name='related_markets'),
	path('ajax/chart/', views.ajax_charts, name='ajax_charts'),

	#  Bets
	path('bets/<int:user_id>', views.past_bets, name='past_bets'),

]