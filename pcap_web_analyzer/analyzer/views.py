from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime
import string
import random
from .forms import UploadFileForm
from .models import Analysis, AnalysisStatus, AnalysisResult, Alert
from .tasks import pcap_analysis

def analysis_new(request):
    # FIXME: protect this page a bit , too many objects created all over the place
    # Create a random id
    new_uid = ''.join([random.choice(string.ascii_lowercase + string.digits) for _ in range(64)])
    # Create a new Analysis
    new_analysis = Analysis()
    new_analysis.analysis_id = new_uid
    # FIXME: datetime is without timezone here
    new_analysis.created = datetime.now()
    new_analysis.status = AnalysisStatus.UPLOAD
    new_analysis.save()
    # TODO: save the IP address ?
    # Return the id
    return JsonResponse({'id': new_uid})

@csrf_exempt
def analysis_upload(request, analysis_id):
    """
    /analysis/UID/upload
    Method to upload the pcap file
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            analysis = get_object_or_404(Analysis, pk=analysis_id)
            with open(settings.TEMP_FOLDER + '/' + analysis.analysis_id + '.pcap', 'wb+') as destination:
                 for chunk in request.FILES['file'].chunks():
                     destination.write(chunk)
            analysis.status = AnalysisStatus.INDICATOR
            analysis.save()
            # Launch the background Celery task
            pcap_analysis.delay(analysis.analysis_id)
            return JsonResponse({'result': 'ok'})
        else:
            return JsonResponse({'result': 'failed'})
    else:
        return JsonResponse({'result': 'failed'})

def analysis_show(request, analysis_id):
    """
    /analysis/UID
    Returns information on the analysis
    """
    analysis = get_object_or_404(Analysis, pk=analysis_id)
    alerts = Alert.objects.filter(analysis=analysis)
    res = {
        'id': analysis.analysis_id,
        'created': analysis.created,
        'status': analysis.status,
        'result': analysis.result,
        'alerts': [{'indicator': a.indicator, 'event': a.event_name} for a in alerts]
    }
    return JsonResponse(res)

    pass
