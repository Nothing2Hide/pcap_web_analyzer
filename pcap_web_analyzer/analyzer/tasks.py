from __future__ import absolute_import, unicode_literals
from django.conf import settings
from celery import shared_task
from pcapanalysis import Pcap
from pymisp import PyMISP, PyMISPError
from .models import Analysis, AnalysisStatus, AnalysisResult, Alert
import subprocess


@shared_task
def add(x, y):
    return x + y


@shared_task
def pcap_analysis(analysis_id):
    """
    Analyze the pcap file, first extract the IOCs then check in the MISP server
    """
    analysis = Analysis.objects.get(pk=analysis_id)
    print('analyzing : %s' % analysis_id)
    try:
        # Fix ME: log issues PyMISPError here
        server = PyMISP(settings.MISP_SERVER, settings.MISP_KEY, True, 'json')
        pc = Pcap(settings.TEMP_FOLDER + '/' + analysis_id + '.pcap')
        malicious = False
        results = []
        pc.extract_indicators()
        analysis.status = AnalysisStatus.SEARCH
        analysis.save()
        for ind in pc.indicators:
            print(ind)
            events = server.search(values = [ind['value']])
            if len(events['response']) > 0:
                malicious = True
                for event in events['response']:
                    results.append({
                        'indicator': ind['value'],
                        'event': event['Event']['info'],
                        'event_id': event['Event']['id']
                    })
    except PyMISPError:
        # TODO: create log here
        analysis.status = AnalysisStatus.ERROR
        analysis.result = AnalysisResult.ERROR
        analysis.save()
    else:
        for alert in results:
            a = Alert()
            a.analysis = analysis
            a.indicator = alert['indicator']
            a.event_id = int(alert['event_id'])
            a.event_name = alert['event']
            a.save()
        if malicious:
            analysis.result = AnalysisResult.MALICIOUS
        else:
            analysis.result = AnalysisResult.NOTHING
        analysis.status = AnalysisStatus.DONE
        analysis.save()
    # Securely delete the pcap file
    subprocess.check_call([
        'shred',
        '-zu',
        settings.TEMP_FOLDER + '/' + analysis_id + '.pcap']
    )

    # TODO: delete the pcap file securely
