from django.shortcuts import redirect
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .services.enedis_client import EnedisClient
from .models import LinkyPoint, AccessRequest
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import render
from .models import LinkyPoint, EnergyConsumption
import json

def client_login(request):
    """
    Login page for individuals.
    """
    return render(request, 'client_login.html')

def client_signup(request):
    """
    Signup page for individuals.
    """
    return render(request, 'client_signup.html')

def landing(request):
    """
    Public landing page for Linky Monitor.
    """
    return render(request, 'landing.html')

def pro_landing(request):
    """
    Public landing page for professionals (login).
    """
    return render(request, 'pro_landing.html')

def client_dashboard(request):
    """
    Main dashboard for the client (Mon Espace).
    Shows consumption stats and charts.
    """
    user = request.user
    linky = None
    has_subscription = False # Default to False: Restricted access

    if user.is_authenticated:
        linky = LinkyPoint.objects.filter(user=user).first()
        # Mock Subscription Logic: In production, check Stripe/User capabilities
        # For Demo: Assume Jean Dupont (or sandbox PRM) has valid subscription
        if linky and linky.prm_id == "11453290002823":
             has_subscription = True
    
    # Defaults
    context = {
        'linky': linky,
        'is_sandbox': linky.prm_id == "11453290002823" if linky else False, 
        'has_subscription': has_subscription,
        'yesterday_conso': 0,
        'trend': 0,
        'monthly_estimate_eur': 0,
        'kwh_price': 0.22,
        'daily_conso_30d': [],
        'monthly_conso': [0]*12,
        'yearly_conso_3y': {},
    }

    if linky:
        # TEMP: Mock contract data for demo/sandbox
        if not linky.subscription_type:
            linky.subscription_type = "HPHC (Heures Pleines / Heures Creuses)"
            linky.subscribed_power = "9 kVA"
            linky.last_index = 12453.2
        
        context['subscriber_name'] = f"{user.first_name} {user.last_name}" if user.is_authenticated else "Jean DUPONT"
        context['prm_display'] = linky.prm_id if linky else "11453290002823"
        # 1. Yesterday Consumption
        yesterday = timezone.now().date() - timedelta(days=1)
        # Sandbox fix: use latest available date if yesterday is empty
        latest = EnergyConsumption.objects.filter(linky_point=linky).order_by('-timestamp').first()
        if latest:
            yesterday_data = EnergyConsumption.objects.filter(linky_point=linky, timestamp__date=latest.timestamp.date()).first()
            context['yesterday_conso'] = yesterday_data.value_kwh if yesterday_data else 0
            
            # Trend (vs same day last week)
            last_week = latest.timestamp.date() - timedelta(days=7)
            last_week_data = EnergyConsumption.objects.filter(linky_point=linky, timestamp__date=last_week).first()
            if last_week_data and last_week_data.value_kwh > 0:
                context['trend'] = round(((yesterday_data.value_kwh - last_week_data.value_kwh) / last_week_data.value_kwh) * 100)

        # 2. Monthly Estimate (current month total)
        current_month = latest.timestamp.month if latest else timezone.now().month
        month_total = EnergyConsumption.objects.filter(
            linky_point=linky, 
            timestamp__month=current_month,
            data_type='DAILY'
        ).aggregate(Sum('value_kwh'))['value_kwh__sum'] or 0
        context['monthly_estimate_eur'] = month_total * context['kwh_price']

        # 3. Charts Data
        # 30 Days
        conso_30d = EnergyConsumption.objects.filter(
            linky_point=linky,
            data_type='DAILY'
        ).order_by('-timestamp')[:30]
        context['daily_conso_30d'] = [{'date': e.timestamp.strftime('%d/%m'), 'val': float(e.value_kwh)} for e in reversed(conso_30d)]

        # 12 Months (Rolling)
        monthly_conso_labels = []
        monthly_conso_values = []
        
        if latest:
            end_date = latest.timestamp.date()
            start_date = (end_date.replace(day=1) - timedelta(days=365)).replace(day=1) # Approx 1 year ago
            
            conso_12m = EnergyConsumption.objects.filter(
                linky_point=linky, 
                timestamp__gte=start_date,
                timestamp__lte=end_date,
                data_type='DAILY'
            ).annotate(
                month=ExtractMonth('timestamp'), 
                year=ExtractYear('timestamp')
            ).values('year', 'month').annotate(total=Sum('value_kwh')).order_by('year', 'month')

            # Build continuous list of last 12 months (even if empty in DB)
            curr = start_date
            # Map DB results for fast lookup: "2025-2" -> 123.4
            db_map = {f"{e['year']}-{e['month']}": e['total'] for e in conso_12m}
            
            # French Month Names
            months_fr = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]

            for _ in range(12):
                 # Move to next month logic if needed, but simpler to just iterate
                 key = f"{curr.year}-{curr.month}"
                 val = db_map.get(key, 0)
                 monthly_conso_labels.append(f"{months_fr[curr.month-1]} {str(curr.year)[-2:]}")
                 monthly_conso_values.append(round(val))
                 
                 # Increment month
                 curr = (curr.replace(day=1) + timedelta(days=32)).replace(day=1)
                 if curr > end_date.replace(day=1) + timedelta(days=10): break

            context['monthly_conso'] = monthly_conso_values
            context['monthly_conso_labels'] = monthly_conso_labels

        # 3 Years
        conso_3y = EnergyConsumption.objects.filter(
            linky_point=linky, 
            data_type='DAILY'
        ).values('timestamp__year').annotate(total=Sum('value_kwh')).order_by('timestamp__year')
        for e in conso_3y:
            context['yearly_conso_3y'][str(e['timestamp__year'])] = round(e['total'])
        
        context['has_3y_data'] = len(context['yearly_conso_3y']) >= 3

        # NEW: Totals and HPHC Estimates
        context['total_30d'] = sum(d['val'] for d in context['daily_conso_30d'])
        context['total_12m'] = sum(context['monthly_conso'])
        
        # Estimate HPHC (60/40) as we only have DAILY data
        context['hp_30d'] = context['total_30d'] * 0.6
        context['hc_30d'] = context['total_30d'] * 0.4
        context['hp_12m'] = context['total_12m'] * 0.6
        context['hc_12m'] = context['total_12m'] * 0.4

    # Serialize for JS
    context['daily_conso_30d_json'] = json.dumps(context['daily_conso_30d'])
    context['monthly_conso_json'] = json.dumps(context['monthly_conso'])
    context['monthly_conso_labels_json'] = json.dumps(context.get('monthly_conso_labels', []))
    context['yearly_conso_3y_json'] = json.dumps(context['yearly_conso_3y'])

    return render(request, 'dashboard/client.html', context)

class StartEnedisAuthView(APIView):
    permission_classes = [AllowAny]  # Permettre aux utilisateurs non connectés

    def get(self, request):
        client = EnedisClient()
        # Si l'utilisateur est connecté, on utilise son ID, sinon on génère un état temporaire
        if request.user.is_authenticated:
            state = f"user_{request.user.id}"
        else:
            # Pour les utilisateurs anonymes, on génère un état unique
            import uuid
            state = f"anonymous_{uuid.uuid4().hex[:16]}"
        
        url = client.get_authorization_url(state=state)
        return Response({"auth_url": url})

class EnedisCallbackView(APIView):
    permission_classes = [AllowAny] # Callback comes from Enedis, user might lose session if cross-domain, but usually browser cookie handles it.

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')
        
        if error:
            # User likely declined or something went wrong on Enedis side
            return redirect('/dashboard/client/?status=error&msg=Autorisation refusée ou annulée')

        if not code:
            return redirect('/dashboard/client/?status=error&msg=Code de validation manquant')


        # Basic state validation
        # In PROD: Validate state properly to prevent CSRF and identifying the user
        
        client = EnedisClient()
        try:
            tokens = client.exchange_code(code)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        # Create or Update LinkyPoint
        # Note: We need to know WHICH user this belongs to.
        # If state contains user_id, extract it.
        user = None
        if state and state.startswith("user_"):
            try:
                user_id = int(state.split("_")[1])
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
            except:
                pass
        
        if not user and request.user.is_authenticated:
            user = request.user
            logger.info(f"Using authenticated user {user.id} from session.")
            
        if not user:
             logger.error("Could not identify user for Enedis callback.")
             return redirect('/dashboard/client/?status=error&msg=Utilisateur non identifié (session expirée)')


        usage_point_id = tokens.get("usage_point_id") # Check Enedis response format
        if not usage_point_id:
             # Fallback if Enedis doesn't return PRM in token response, usually it does or needs a separate call
             usage_point_id = "UNKNOWN_PRM" 
             logger.warning("Enedis token response did not contain 'usage_point_id'.")

        LinkyPoint.objects.update_or_create(
            user=user,
            defaults={
                "prm_id": usage_point_id,
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "token_expires_at": timezone.now() + timedelta(seconds=int(tokens.get("expires_in", 3600)))
            }
        )
        logger.info(f"LinkyPoint for user {user.id} (PRM: {usage_point_id}) updated/created successfully.")

        # Finalize
        logger.info(f"Successfully processed Enedis callback for PRM {usage_point_id}")
        
        return render(request, 'energy/auth_success.html', {
            "prm_id": usage_point_id,
            "status": "success"
        })


class CreateAccessRequestView(APIView):
    permission_classes = [IsAuthenticated] # Must be an installer (User)

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        # Logic: Create a request
        access_req = AccessRequest.objects.create(
            installer=request.user,
            client_email=email
        )

        # In a real app, send Email here with the magic link
        # magic_link = f"{settings.FRONTEND_URL}/authorize-installer?token={access_req.unique_token}"
        
        return Response({
            "status": "created", 
            "token": str(access_req.unique_token),
            "message": "Invite generated. Send this token or link to client."
        })

def demo_login(request):
    """
    Force login as Jean DUPONT (Demo User)
    """
    from django.contrib.auth import login, get_user_model
    User = get_user_model()
    
    # Get or Create Jean
    user, created = User.objects.get_or_create(username="jean.dupont@example.com", defaults={
        "first_name": "Jean",
        "last_name": "DUPONT",
        "email": "jean.dupont@example.com"
    })
    
    # Ensure Linky Point Exists for Sandbox
    # Fix IntegrityError: Clean up any existing LinkyPoint for this user OR this PRM
    # LinkyPoint.objects.filter(prm_id="11453290002823").delete()
    # LinkyPoint.objects.filter(user=user).delete()
    
    LinkyPoint.objects.get_or_create(
        user=user,
        prm_id="11453290002823",
        defaults={
            "subscription_type": "HPHC",
            "subscribed_power": "9 kVA",
            "last_index": 12453.2
        }
    )
    
    login(request, user)
    return redirect('dashboard-client')

class SyncSandboxDataView(APIView):
    """
    Triggers a manual fetch of Sandbox data for the authenticated user.
    Uses Client Credentials flow as per Sandbox documentation.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 1. Get or Create Sandbox LinkyPoint for this user
        prm_id = "11453290002823" # Active Charge PRM (Sandbox)
        
        # Handle OneToOne constraint: If user has a Linky, use it, even if PRM differs (update it for demo)
        linky, created = LinkyPoint.objects.get_or_create(user=request.user, defaults={'prm_id': prm_id})
        
        if not created and linky.prm_id != prm_id:
             linky.prm_id = prm_id
             linky.save()

        # 2. Authenticate
        client = EnedisClient()
        if not client.is_sandbox:
             return Response({"error": "Server not in Sandbox mode"}, status=400)
             
        try:
            tokens = client.get_token()
            access_token = tokens.get("access_token")
            # Update token in DB
            linky.access_token = access_token
            # Safe default for expiry
            expires_in = int(tokens.get("expires_in", 3600))
            linky.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
            linky.save()
        except Exception as e:
            return Response({"error": f"Auth failed with Enedis: {str(e)}"}, status=500)

        # 3. Fetch Data (last 30 days for chart)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        try:
            data = client.fetch_load_curve(access_token, prm_id, start_date, end_date)
            
            # 4. Store Data
            if "error" in data:
                 return Response({"error": f"API Error: {data}"}, status=400)

            reading = data.get('meter_reading', {})
            points = reading.get('interval_reading', [])
            
            count = 0
            for pt in points:
                # Value is in Watts (Half-hourly average power)
                val_watts = float(pt['value'])
                # Convert to kWh for 30min slot: (Watts * 0.5h) / 1000
                val_kwh = (val_watts * 0.5) / 1000.0
                
                dt = timezone.datetime.strptime(pt['date'], "%Y-%m-%d %H:%M:%S")
                dt = timezone.make_aware(dt)
                
                EnergyConsumption.objects.update_or_create(
                    linky_point=linky,
                    timestamp=dt,
                    data_type='LOAD_CURVE',
                    defaults={'value_kwh': val_kwh}
                )
                count += 1
                
            return Response({
                "status": "success", 
                "imported_points": count, 
                "prm": prm_id,
                "data_points": points
            })
            
        except Exception as e:
            return Response({"error": f"Fetch failed: {str(e)}"}, status=500)

def enedis_consent_view(request):
    """
    Vue dynamique pour la page de consentement Enedis.
    Prépare l'URL d'autorisation officielle.
    """
    from django.urls import reverse
    client = EnedisClient()
    # Génération de l'URL officielle (utilisera le client_id du .env)
    try:
        # On passe un state qui pourrait être utile plus tard, ou récupéré du PRM en query param
        prm = request.GET.get('prm', 'unknown')
        auth_url = client.get_authorization_url(state=f"prm_{prm}")
    except Exception as e:
        auth_url = "#"

    # Pour le test immédiat/simulation
    sim_success_url = reverse('simulation_enedis_success')

    return render(request, 'simulation/enedis_consent.html', {
        'enedis_auth_url': auth_url,
        'sim_success_url': sim_success_url
    })
