from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.buyers.models import Buyer
from apps.campaigns.models import Campaign, EmailTemplate, EmailLog, Unsubscribe
from apps.accounts.models import SellerProfile


@login_required
def compose_page_view(request):
    buyer_ids_str = request.GET.get('buyers', '')
    buyer_ids = [int(i) for i in buyer_ids_str.split(',') if i.isdigit()]
    
    buyers = Buyer.objects.filter(id__in=buyer_ids, seller=request.user) if buyer_ids else Buyer.objects.filter(seller=request.user, email_status='valid')[:10]
    profile, _ = SellerProfile.objects.get_or_create(user=request.user)

    templates = EmailTemplate.objects.filter(seller=request.user)

    context = {
        'buyers': buyers,
        'buyer_ids_str': ','.join(str(b.id) for b in buyers),
        'profile': profile,
        'templates': templates,
    }
    return render(request, 'campaigns/compose.html', context)


@login_required
def confirm_page_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id, seller=request.user)
    logs = EmailLog.objects.filter(campaign=campaign)

    context = {
        'campaign': campaign,
        'logs': logs,
    }
    return render(request, 'campaigns/confirm.html', context)


@login_required
def history_page_view(request):
    campaigns = Campaign.objects.filter(seller=request.user)
    recent_logs = EmailLog.objects.filter(campaign__seller=request.user)[:50]

    context = {
        'campaigns': campaigns,
        'logs': recent_logs,
    }
    return render(request, 'campaigns/history.html', context)


def unsubscribe_page_view(request):
    email = request.GET.get('email', '').strip().lower()
    success = False
    if email:
        Unsubscribe.objects.get_or_create(email=email, defaults={'reason': 'User clicked email unsubscribe link'})
        success = True

    return render(request, 'campaigns/unsubscribe.html', {'email': email, 'success': success})
