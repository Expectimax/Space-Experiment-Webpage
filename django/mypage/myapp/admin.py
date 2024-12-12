from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
# this file is used to register all models for the admin page
# Register your models here.
from .models import (Experiment, Image, AnswersFormalDelegate, AnswersPhenoDelegate, AnswersIntuitiveDelegate,
                     AnswersSocialDelegate, Visitors, Results, AnswersSocialBase, AnswersFormalBase, AnswersPhenoBase,
                     AnswersIntuitiveBase, FeedbackResultsFormal, FeedbackResultsIntuitive, FeedbackResultsPheno,
                     FeedbackResultsSocial, ExperimentSessionID, CompletionCode)


class ResultResource(resources.ModelResource):
    class Meta:
        model = Results


class VisitorsResource(resources.ModelResource):
    class Meta:
        model = Visitors


class ResultAdmin(ImportExportModelAdmin):
    resource_classes = [ResultResource]


class VisitorsAdmin(ImportExportModelAdmin):
    resource_classes = [VisitorsResource]


admin.site.register(Experiment)
admin.site.register(Image)
admin.site.register(Visitors, VisitorsAdmin)
admin.site.register(Results, ResultAdmin)
admin.site.register(AnswersFormalDelegate)
admin.site.register(AnswersPhenoDelegate)
admin.site.register(AnswersIntuitiveDelegate)
admin.site.register(AnswersSocialDelegate)
admin.site.register(AnswersSocialBase)
admin.site.register(AnswersFormalBase)
admin.site.register(AnswersPhenoBase)
admin.site.register(AnswersIntuitiveBase)
admin.site.register(FeedbackResultsFormal)
admin.site.register(FeedbackResultsIntuitive)
admin.site.register(FeedbackResultsPheno)
admin.site.register(FeedbackResultsSocial)
admin.site.register(ExperimentSessionID)
admin.site.register(CompletionCode)


