from .models import AuditSession, Equipment, ApplianceCategory, ProjectQuote, QuoteLineItem, CostCategory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

@login_required
def quote_editor(request):
    """Vue pour éditer le devis financier"""
    session, _ = AuditSession.objects.get_or_create(user=request.user, defaults={'name': f"Audit {request.user.username}"})
    
    # Get or Create Quote
    quote, created = ProjectQuote.objects.get_or_create(audit=session)
    
    items = quote.items.all().order_by('category')
    
    context = {
        'quote': quote,
        'items': items,
        'categories': CostCategory.choices,
        'total_ht': quote.total_ht(),
        'total_ttc': quote.total_ttc()
    }
    return render(request, 'audit/quote.html', context)

@login_required
def add_quote_line(request):
    if request.method == "POST":
        session = AuditSession.objects.get(user=request.user)
        quote, _ = ProjectQuote.objects.get_or_create(audit=session)
        
        desc = request.POST.get('description')
        cat = request.POST.get('category')
        qty = float(request.POST.get('quantity', 1))
        price = float(request.POST.get('price', 0))
        
        QuoteLineItem.objects.create(
            quote=quote,
            category=cat,
            description=desc,
            quantity=qty,
            unit_price_ht=price
        )
    return redirect('audit_quote_editor')

@login_required
def delete_quote_line(request, item_id):
    # Ensure user owns the quote
    item = get_object_or_404(QuoteLineItem, id=item_id, quote__audit__user=request.user)
    item.delete()
    return redirect('audit_quote_editor')

@login_required
def audit_dashboard(request):
    """Vue principale de l'audit : Liste des pièces et appareils"""
    # Recup ou Création auto d'une session
    session, created = AuditSession.objects.get_or_create(
        user=request.user, 
        defaults={'name': f"Audit {request.user.username}"}
    )
    
    equipments = session.equipments.all().order_by('category')
    
    # Calculs Totaux
    total_conso_theorique = sum(e.yearly_consumption() for e in equipments)
    
    # CATALOGUE RAPIDE (Pour démo)
    # A terme, ce catalogue pourrait venir d'une API externe ou d'un scrapper
    catalog = [
        {'name': 'Frigo Récent (A+)', 'power': 150, 'cat': 'kitchen', 'h_winter': 24, 'h_summer': 24},
        {'name': 'Frigo Américain (Vieux)', 'power': 400, 'cat': 'kitchen', 'h_winter': 24, 'h_summer': 24},
        {'name': 'Lave-Linge (Cycle Eco)', 'power': 2000, 'cat': 'living', 'h_winter': 1, 'h_summer': 1},
        {'name': 'Sèche-Linge', 'power': 2500, 'cat': 'living', 'h_winter': 1.5, 'h_summer': 0},
        {'name': 'TV LED 55"', 'power': 100, 'cat': 'living', 'h_winter': 4, 'h_summer': 2},
        {'name': 'Box Internet', 'power': 15, 'cat': 'living', 'h_winter': 24, 'h_summer': 24},
        {'name': 'Pompe à Chaleur (Air/Eau)', 'power': 3000, 'cat': 'heating', 'h_winter': 5, 'h_summer': 0},
        {'name': 'Climatisation (Split)', 'power': 1500, 'cat': 'heating', 'h_winter': 0, 'h_summer': 4},
        {'name': 'Ballon ECS (Cumulus 200L)', 'power': 2200, 'cat': 'water', 'h_winter': 3, 'h_summer': 3},
        {'name': 'Pompe Piscine (1CV)', 'power': 750, 'cat': 'outdoor', 'h_winter': 2, 'h_summer': 10},
    ]

    context = {
        'session': session,
        'equipments': equipments,
        'total_conso': total_conso_theorique,
        'catalog': catalog,
        'categories': ApplianceCategory.choices
    }
    return render(request, 'audit/dashboard.html', context)

@login_required
def add_equipment(request):
    if request.method == "POST":
        session = AuditSession.objects.get(user=request.user)
        name = request.POST.get('name')
        power = int(request.POST.get('power', 0))
        cat = request.POST.get('category', 'other')
        h_win = float(request.POST.get('h_winter', 0))
        h_sum = float(request.POST.get('h_summer', 0))
        
        Equipment.objects.create(
            audit=session,
            name=name,
            power_watts=power,
            category=cat,
            hours_per_day_winter=h_win,
            hours_per_day_summer=h_sum
        )
    return redirect('audit_dashboard')

@login_required
def delete_equipment(request, eq_id):
    eq = get_object_or_404(Equipment, id=eq_id, audit__user=request.user)
    eq.delete()
    return redirect('audit_dashboard')

@login_required
def roi_report(request):
    """Vue du rapport de rentabilité (ROI)"""
    session, _ = AuditSession.objects.get_or_create(user=request.user)
    quote, _ = ProjectQuote.objects.get_or_create(audit=session)
    
    investment_cost = float(quote.total_ttc())
    initial_savings = float(session.yearly_savings_estimated)
    inflation_rate = float(session.electricity_inflation) / 100
    
    # Projection sur 20 ans
    years = []
    cumulative_savings = []
    current_savings_cumulated = 0
    current_annual_savings = initial_savings
    
    break_even_year = None
    
    for year in range(0, 21): # 0 à 20 ans (0 = départ)
        years.append(year)
        
        if year == 0:
             cumulative_savings.append(0)
             current_savings_cumulated = 0
        else:
            # L'économie augmente chaque année car le prix de l'électricité augmente
            if year > 1:
                current_annual_savings = current_annual_savings * (1 + inflation_rate)
                
            current_savings_cumulated += current_annual_savings
            cumulative_savings.append(round(current_savings_cumulated, 2))
        
        # Test Rentabilité
        if break_even_year is None and current_savings_cumulated >= investment_cost:
            break_even_year = year
    
    # Chart Data adjustments for Year 0
    chart_investment = [investment_cost] * 21 # 0 to 20

    context = {
        'session': session,
        'quote': quote,
        'investment': investment_cost,
        'break_even_year': break_even_year,
        'total_savings_20y': cumulative_savings[-1],
        'net_gain_20y': cumulative_savings[-1] - investment_cost,
        
        # Chart Data
        'chart_labels': years,
        'chart_data': cumulative_savings,
        'chart_investment': chart_investment
    }
    return render(request, 'audit/roi.html', context)

@login_required
def update_assumptions(request):
    if request.method == "POST":
        session = AuditSession.objects.get(user=request.user)
        session.yearly_savings_estimated = request.POST.get('savings', 1200)
        session.electricity_inflation = request.POST.get('inflation', 5)
        session.save()
    return redirect('audit_roi_report')
