from django.db import models
from enum import Enum


class AnalysisStatus(Enum):
    UPLOAD = "Upload in progress"
    INDICATOR = "Extraction of indicator"
    SEARCH = "Research of indicators in the database"
    ERROR = "Error"
    DONE = "Done"


class AnalysisResult(Enum):
    NOTHING = "Nothing malicious found"
    MALICIOUS = "Malicious indicators found"
    ERROR = "Error during analysis"


class Analysis(models.Model):
    analysis_id = models.CharField(max_length=64, primary_key=True)
    created = models.DateTimeField('date created')
    status = models.CharField(
            max_length=10,
            choices=[(tag, tag.value) for tag in AnalysisStatus]
    )
    result = models.CharField(
        max_length=10,
        choices=[(tag, tag.value) for tag in AnalysisResult]
    )
    ip = models.CharField(max_length=255)


class Alert(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    indicator = models.CharField(max_length=256)
    event_id = models.IntegerField()
    event_name = models.CharField(max_length=256)
