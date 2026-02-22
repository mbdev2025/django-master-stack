from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.audit.models import AuditSession
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import SolarSimulation, DocumentAnalysis
from .services.pdf_parser import AdobePDFParser
from apps.energy.models import EnergyConsumption, LinkyPoint
from django.db.models import Sum
from django.db.models.functions import ExtractMonth

@login_required
def solar_analysis(request):
    session, _ = AuditSession.objects.get_or_create(user=request.user)
    sim, created = SolarSimulation.objects.get_or_create(audit=session)
    
    # Defaults
    lat = request.session.get('last_sim_lat', 48.85)
    lon = request.session.get('last_sim_lon', 2.35)
    
    if request.method == "POST":
        address = request.POST.get('address')
        sim.kwp = float(request.POST.get('kwp', 3.0))
        sim.orientation = float(request.POST.get('orientation', 0))
        sim.tilt = float(request.POST.get('tilt', 35))
        sim.save()
        
        if address:
            from apps.scrapers.services.geocoding import get_lat_lon_from_address
            session.address = address
            session.save()
            glat, glon = get_lat_lon_from_address(address)
            if glat and glon:
                lat, lon = glat, glon
        
        sim.run_pvgis_simulation(lat, lon)
        request.session['last_sim_lat'] = lat
        request.session['last_sim_lon'] = lon
        return redirect('analysis_solar')

    # --- REAL DATA INTEGRATION ---
    linky = LinkyPoint.objects.filter(user=request.user).first()
    monthly_conso = [0]*12
    yearly_conso_3y = {} # {year: total}
    daily_conso_30d = [] # list of {date: val}
    
    if linky:
        # Last 3 years
        three_years_ago = timezone.now() - timedelta(days=3*365)
        conso_3y = EnergyConsumption.objects.filter(
            linky_point=linky, 
            timestamp__gte=three_years_ago,
            data_type='DAILY'
        ).values('timestamp__year').annotate(total=Sum('value_kwh')).order_by('timestamp__year')
        for e in conso_3y:
            yearly_conso_3y[str(e['timestamp__year'])] = round(e['total'])

        # Last 12 months (latest available year in sandbox)
        latest_data = EnergyConsumption.objects.filter(linky_point=linky).order_by('-timestamp').first()
        if latest_data:
            target_year = latest_data.timestamp.year
            conso_12m = EnergyConsumption.objects.filter(
                linky_point=linky, 
                timestamp__year=target_year,
                data_type='DAILY'
            ).annotate(month=ExtractMonth('timestamp')).values('month').annotate(total=Sum('value_kwh')).order_by('month')
            
            for entry in conso_12m:
                monthly_conso[entry['month']-1] = round(entry['total'])

        # Last 30 days of data
        conso_30d = EnergyConsumption.objects.filter(
            linky_point=linky,
            data_type='DAILY'
        ).order_by('-timestamp')[:30]
        daily_conso_30d = [{'date': e.timestamp.strftime('%d/%m'), 'val': e.value_kwh} for e in reversed(conso_30d)]

    monthly_prod = [0]*12
    if sim.hourly_production:
        for hour, val in enumerate(sim.hourly_production):
            month = int(hour / 730)
            if month < 12:
                monthly_prod[month] += (val / 1000.0)
        monthly_prod = [round(x) for x in monthly_prod]

    sim.calculate_kpis()

    context = {
        'session': session,
        'sim': sim,
        'lat': lat,
        'lon': lon,
        'monthly_prod': monthly_prod,
        'monthly_conso': monthly_conso,
        'yearly_conso_3y': yearly_conso_3y,
        'daily_conso_30d': daily_conso_30d,
        'is_sandbox': getattr(settings, 'ENEDIS_API_BASE_URL', '').find('sandbox') != -1 or not linky
    }
    return render(request, 'analysis/solar.html', context)

@login_required
def upload_document(request):
    """View to handle PDF upload (Invoice or Quote)."""
    if request.method == 'POST' and request.FILES.get('document'):
        session, _ = AuditSession.objects.get_or_create(user=request.user)
        doc_type = request.POST.get('doc_type', 'INVOICE')
        file = request.FILES['document']
        
        doc = DocumentAnalysis.objects.create(
            audit=session,
            document_type=doc_type,
            file=file,
            status='PENDING'
        )
        
        try:
            doc.status = 'PROCESSING'
            doc.save()
            parser = AdobePDFParser()
            try:
                file_path = doc.file.path 
            except NotImplementedError:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    for chunk in file.chunks(): tmp.write(chunk)
                    file_path = tmp.name

            raw_json = parser.extract_pdf_content(file_path)
            doc.raw_json_result = raw_json
            
            if doc_type == 'INVOICE':
                doc.extracted_data = parser.parse_invoice_data(raw_json)
            elif doc_type == 'QUOTE':
                doc.extracted_data = parser.parse_quote_data(raw_json)
                
            doc.status = 'COMPLETED'
            doc.save()
        except Exception as e:
            doc.status = 'FAILED'
            doc.error_message = str(e)
            doc.save()
        return redirect('analysis_solar')
    return render(request, 'analysis/upload_modal.html')

@login_required
def list_documents(request):
    session = get_object_or_404(AuditSession, user=request.user)
    docs = DocumentAnalysis.objects.filter(audit=session).order_by('-created_at')
    data = [{
        'id': d.id,
        'type': d.get_document_type_display(),
        'status': d.status,
        'filename': d.file.name.split('/')[-1],
        'data': d.extracted_data
    } for d in docs]
    return JsonResponse({'documents': data})
