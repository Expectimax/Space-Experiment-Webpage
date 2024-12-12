from django.db import models

# this file defines the different models in the database with all respective fields


class Experiment(models.Model):
    # Experiment model (formal, social, pheno, intuitive)
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name


class Image(models.Model):
    # Image model (belongs to which experiment, image itself, image name, ai answer ...)
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(null=False, blank=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    ai_answer = models.CharField(max_length=12, null=False, blank=False, default='no_answer')
    ai_predicted_correctly = models.BooleanField(null=False, blank=False, default='False')
    ai_delegate = models.BooleanField(null=False, blank=False, default='False')
    correct_answer = models.CharField(max_length=12, null=False, blank=False, default='no_answer')
    nr_seen = models.IntegerField(null=False, blank=False, default=0)
    nr_delegated = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return str(self.name)


class Visitors(models.Model):
    # Visitor model (ID, which experiment group, gender, age, country ...)
    session_id = models.CharField(max_length=40, null=False, blank=False, default='no_session_id')
    experiment_group = models.CharField(max_length=20, null=False, blank=False, default='no_group_assigned')
    gender = models.CharField(max_length=20, null=False, blank=False, default='no_gender')
    age = models.IntegerField(null=False, blank=False, default=0)
    country = models.CharField(max_length=20, null=False, blank=False, default='no_country_assigned')
    competency = models.CharField(max_length=10, null=False, blank=False, default='no_answer')
    expectation = models.IntegerField(null=False, blank=False, default=0)
    antibot = models.IntegerField(null=False, blank=False, default=0)
    perceived_help = models.IntegerField(null=False, blank=False, default=0)
    complexity_formal = models.IntegerField(null=False, blank=False, default=0)
    complexity_social = models.IntegerField(null=False, blank=False, default=0)
    complexity_pheno = models.IntegerField(null=False, blank=False, default=0)
    complexity_intuitive = models.IntegerField(null=False, blank=False, default=0)
    formal_images = models.JSONField(null=False, blank=True, default=dict)
    social_images = models.JSONField(null=False, blank=True, default=dict)
    pheno_images = models.JSONField(null=False, blank=True, default=dict)
    intuitive_images = models.JSONField(null=False, blank=True, default=dict)
    first_task = models.CharField(max_length=15, null=False, blank=False, default='no_first_task')
    second_task = models.CharField(max_length=15, null=False, blank=False, default='no_second_task')
    third_task = models.CharField(max_length=15, null=False, blank=False, default='no_third_task')
    fourth_task = models.CharField(max_length=15, null=False, blank=False, default='no_fourth_task')


class Results(models.Model):
    # Results model (ID, answers for each task)
    user_session_id = models.CharField(max_length=2000, null=False, blank=False, default='no_session_id')
    answers_formal = models.JSONField(null=False, default=dict)
    answers_social = models.JSONField(null=False, default=dict)
    answers_pheno = models.JSONField(null=False, default=dict)
    answers_intuitive = models.JSONField(null=False, default=dict)


class FeedbackResultsFormal(models.Model):
    # helper Model to cache the feedback answers until all answers are given for the formal space
    user_session_id = models.CharField(max_length=2000, null=False, blank=False, default='no_session_id')
    answers_formal1 = models.JSONField(null=False, default=dict)
    answers_formal2 = models.JSONField(null=False, default=dict)
    answers_formal3 = models.JSONField(null=False, default=dict)
    answers_formal4 = models.JSONField(null=False, default=dict)
    answers_formal5 = models.JSONField(null=False, default=dict)
    answers_formal6 = models.JSONField(null=False, default=dict)
    answers_formal7 = models.JSONField(null=False, default=dict)
    answers_formal8 = models.JSONField(null=False, default=dict)
    answers_formal9 = models.JSONField(null=False, default=dict)
    answers_formal10 = models.JSONField(null=False, default=dict)
    answers_formal11 = models.JSONField(null=False, default=dict)
    answers_formal12 = models.JSONField(null=False, default=dict)


class FeedbackResultsSocial(models.Model):
    # helper Model to cache the feedback answers until all answers are given for the social space
    user_session_id = models.CharField(max_length=2000, null=False, blank=False, default='no_session_id')
    answers_social1 = models.JSONField(null=False, default=dict)
    answers_social2 = models.JSONField(null=False, default=dict)
    answers_social3 = models.JSONField(null=False, default=dict)
    answers_social4 = models.JSONField(null=False, default=dict)
    answers_social5 = models.JSONField(null=False, default=dict)
    answers_social6 = models.JSONField(null=False, default=dict)
    answers_social7 = models.JSONField(null=False, default=dict)
    answers_social8 = models.JSONField(null=False, default=dict)
    answers_social9 = models.JSONField(null=False, default=dict)
    answers_social10 = models.JSONField(null=False, default=dict)
    answers_social11 = models.JSONField(null=False, default=dict)
    answers_social12 = models.JSONField(null=False, default=dict)


class FeedbackResultsPheno(models.Model):
    # helper Model to cache the feedback answers until all answers are given for the phenomenological space
    user_session_id = models.CharField(max_length=2000, null=False, blank=False, default='no_session_id')
    answers_pheno1 = models.JSONField(null=False, default=dict)
    answers_pheno2 = models.JSONField(null=False, default=dict)
    answers_pheno3 = models.JSONField(null=False, default=dict)
    answers_pheno4 = models.JSONField(null=False, default=dict)
    answers_pheno5 = models.JSONField(null=False, default=dict)
    answers_pheno6 = models.JSONField(null=False, default=dict)
    answers_pheno7 = models.JSONField(null=False, default=dict)
    answers_pheno8 = models.JSONField(null=False, default=dict)
    answers_pheno9 = models.JSONField(null=False, default=dict)
    answers_pheno10 = models.JSONField(null=False, default=dict)
    answers_pheno11 = models.JSONField(null=False, default=dict)
    answers_pheno12 = models.JSONField(null=False, default=dict)


class FeedbackResultsIntuitive(models.Model):
    # helper Model to cache the feedback answers until all answers are given for the intuitive space
    user_session_id = models.CharField(max_length=2000, null=False, blank=False, default='no_session_id')
    answers_intuitive1 = models.JSONField(null=False, default=dict)
    answers_intuitive2 = models.JSONField(null=False, default=dict)
    answers_intuitive3 = models.JSONField(null=False, default=dict)
    answers_intuitive4 = models.JSONField(null=False, default=dict)
    answers_intuitive5 = models.JSONField(null=False, default=dict)
    answers_intuitive6 = models.JSONField(null=False, default=dict)
    answers_intuitive7 = models.JSONField(null=False, default=dict)
    answers_intuitive8 = models.JSONField(null=False, default=dict)
    answers_intuitive9 = models.JSONField(null=False, default=dict)
    answers_intuitive10 = models.JSONField(null=False, default=dict)
    answers_intuitive11 = models.JSONField(null=False, default=dict)
    answers_intuitive12 = models.JSONField(null=False, default=dict)


class ExperimentSessionID(models.Model):
    # helper model to cache if users have loaded a task for the first time or not
    session_id = models.CharField(max_length=2000, null=False, blank=False, default='no_session_id')
    formal_session = models.BooleanField(default=False)
    social_session = models.BooleanField(default=False)
    pheno_session = models.BooleanField(default=False)
    intuitive_session = models.BooleanField(default=False)

# defines the formal answers for the groups who are allowed to delegate
FORMAL_CHOICES_DELEGATE = (
    ("high population density", "high"),
    ("medium population density", "medium"),
    ("low population density", "low"),
    ("delegate to the AI", "AI")
)
# defines the social answers for the groups who are allowed to delegate
SOCIAL_CHOICES_DELEGATE = (
    ("urban city", "urban"),
    ("rural / small town", "rural"),
    ("delegate to the AI", "AI"),
)
# defines the pheno answers for the groups who are allowed to delegate
PHENO_CHOICES_DELEGATE = (
    ("Berlin", "Berlin"),
    ("Los Angeles", "Los Angeles"),
    ("New York", "New York"),
    ("Paris", "Paris"),
    ("delegate to the AI", "AI")
)
# defines the intuitive answers for the groups who are allowed to delegate
INTUITIVE_CHOICES_DELEGATE = (
    ("high population density", "high"),
    ("medium population density", "medium"),
    ("low population density", "low"),
    ("delegate to the AI", "AI")
)
# defines the formal answers for the groups who are not allowed to delegate
FORMAL_CHOICES_BASE = (
    ("high population density", "high"),
    ("medium population density", "medium"),
    ("low population density", "low"),
)
# defines the social answers for the groups who are not allowed to delegate
SOCIAL_CHOICES_BASE = (
    ("urban city", "urban"),
    ("rural / small town", "rural"),
)
# defines the pheno answers for the groups who are not allowed to delegate
PHENO_CHOICES_BASE = (
    ("Berlin", "Berlin"),
    ("Los Angeles", "Los Angeles"),
    ("New York", "New York"),
    ("Paris", "Paris"),
)
# defines the intuitive answers for the groups who are not allowed to delegate
INTUITIVE_CHOICES_BASE = (
    ("high population density", "high"),
    ("medium population density", "medium"),
    ("low population density", "low"),
)


class AnswersFormalDelegate(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=30, null=False, blank=False, choices=FORMAL_CHOICES_DELEGATE)


class AnswersFormalBase(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=30, null=False, blank=False, choices=FORMAL_CHOICES_BASE)


class AnswersSocialDelegate(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=30, null=False, blank=False, choices=SOCIAL_CHOICES_DELEGATE)


class AnswersSocialBase(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=30, null=False, blank=False, choices=SOCIAL_CHOICES_BASE)


class AnswersPhenoDelegate(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=30, null=False, blank=False, choices=PHENO_CHOICES_DELEGATE)


class AnswersPhenoBase(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=30, null=False, blank=False, choices=PHENO_CHOICES_BASE)


class AnswersIntuitiveDelegate(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=30, null=False, blank=False, choices=INTUITIVE_CHOICES_DELEGATE)


class AnswersIntuitiveBase(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=30, null=False, blank=False, choices=INTUITIVE_CHOICES_BASE)


class CompletionCode(models.Model):
    # Model for the completion codes for MTurk workers
    code = models.CharField(max_length=30, null=False, blank=False, primary_key=True)
    assigned = models.BooleanField(default=False)
