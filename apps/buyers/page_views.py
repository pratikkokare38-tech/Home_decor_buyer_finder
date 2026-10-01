from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.core.constants import BUYER_CATEGORIES, US_STATES
from apps.buyers.models import SearchQuery, Buyer
from apps.core.models import ApiUsage
from django.conf import settings


@login_required
def search_page_view(request):
    hunter_used = ApiUsage.get_monthly_credits('hunter')
    hunter_remaining = max(0, settings.HUNTER_MONTHLY_BUDGET - hunter_used)

    recent_searches = SearchQuery.objects.filter(seller=request.user)[:5]

    context = {
        'categories': BUYER_CATEGORIES,
        'states': US_STATES,
        'hunter_remaining': hunter_remaining,
        'hunter_limit': settings.HUNTER_MONTHLY_BUDGET,
        'recent_searches': recent_searches,
    }
    return render(request, 'buyers/search.html', context)


@login_required
def results_page_view(request, search_id):
    search_query = get_object_or_404(SearchQuery, pk=search_id, seller=request.user)
    buyers = Buyer.objects.filter(search_query=search_query)

    context = {
        'search_query': search_query,
        'buyers': buyers,
        'total_found': search_query.total_found,
        'valid_emails_count': buyers.filter(email_status='valid').count(),
    }
    return render(request, 'buyers/results.html', context)
