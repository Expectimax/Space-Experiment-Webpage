import json
from django.shortcuts import render, redirect
import random
import pandas as pd
from django.contrib import messages
from django.apps import apps
from django.contrib.auth.decorators import login_required
from .models import (Experiment, Image, AnswersFormalDelegate, AnswersSocialDelegate, AnswersPhenoDelegate,
                     AnswersIntuitiveDelegate, Visitors, Results, AnswersIntuitiveBase, AnswersPhenoBase,
                     AnswersSocialBase, AnswersFormalBase, FeedbackResultsFormal, FeedbackResultsSocial,
                     FeedbackResultsPheno, FeedbackResultsIntuitive, ExperimentSessionID, CompletionCode)


# this is the views file of the webpage. It defines the logic of what users can see when they enter the page or perform
# a certain action. First the views for each single page of the website is defined, later functions follow that are
# used to do calculations, messaging and so on
def home(request):
    # this is the "home" view, i.e. the page where users enter
    if not request.session.exists(request.session.session_key):
        request.session.create()
    session_id = request.session.session_key
    # here the user is randomly assigned to one treatment group when he clicks the first button
    if request.method == 'POST':
        random_group_int = random.randint(1, 5)
        if random_group_int == 1:
            experiment_group = 'base'
        elif random_group_int == 2:
            experiment_group = 'human_delegate'
        elif random_group_int == 3:
            experiment_group = 'feedback'
        elif random_group_int == 4:
            experiment_group = 'ai_delegate'
        else:
            experiment_group = 'delegation_counter'

        # if someone clicks the first button and a Visitor object with his session_id already exists, the user went
        # back to the home view. This triggers a message and the user get redirected to an open task
        if Visitors.objects.filter(session_id=session_id).exists():
            next_page = check_inputs_and_return_next_one(session_id, request)
            messages.warning(request, 'You already completed this task. You got redirected to an open task. '
                                      'Please proceed from there.', extra_tags='information_warning')
            return redirect(next_page)
        # otherwise a visitor object is created and the user gets redirected to the next open task
        else:
            Visitors.objects.create(session_id=session_id,
                                    experiment_group=experiment_group)
            next_page = check_inputs_and_return_next_one(session_id, request)
            return redirect(next_page)
    return render(request, 'myapp/home.html', )


def user_data_input(request):
    # this is the view for the first questionaire prior to the experiment
    if not request.session.exists(request.session.session_key):
        request.session.create()
    session_id = request.session.session_key
    # if a Visitor object with this session_id already exists, this visitor is used.
    if Visitors.objects.filter(session_id=session_id).exists():
        visitor = Visitors.objects.get(session_id=session_id)
    # otherwise the user skipped the home page. This triggers a messages and redirects him to the home page
    else:
        messages.warning(request, 'You tried to start the experiment somewhere in the middle. '
                                  'You got redirected to the first page. Please start from there.',
                         extra_tags='information_warning')
        return redirect('home')
    exp_group = visitor.experiment_group

    if request.method == 'POST':
        data = request.POST
        gender = data['Gender']
        country = data['inputCountry']
        age = data['inputAge']
        antibot = data['inputBOT']
        competency = data['Competency']

        # only those users who were allowed to delegate had to give their expectations, for all other users it was
        # set to 7
        if exp_group == 'human_delegate' or exp_group == 'feedback' or exp_group == 'delegation_counter':
            expectation = data['Expectations']
        else:
            expectation = 7

        # this logic makes sure that users answered all questions. If they didn't they received a message and had to
        # fill in the missing answers
        if gender == 'Gender:':
            gender = 'no_gender'
        if country == '':
            country = 'no_country'
        if age == '':
            age = -1
        if antibot == '':
            antibot = 6
        if competency == 'Please rate your prior knowledge:':
            competency = 'no_competency'
        if expectation == 'Please rate your expectations for the AI':
            expectation = 6

        if (country == 'no_country' or age == -1 or antibot == 6 or gender == 'no_gender' or
                competency == 'no_competency' or expectation == 6):
            messages.warning(request,
                             'You did not answer all the questions. Your answers from before were not saved, therefore please '
                             'answer all the questions again. Sorry for the inconvenience.',
                             extra_tags='information_error')
            return redirect('user_data_input')
        # if they did there answers were saved in the database
        else:
            if Visitors.objects.filter(session_id=session_id).exists():
                visitor = Visitors.objects.get(session_id=session_id)
                # check to prevent double submits
                if visitor.country == 'no_country_assigned' and visitor.age == 0 and visitor.gender == 'no_gender' and visitor.antibot == 0 and visitor.competency == "no_answer" and visitor.expectation == 0:
                    Visitors.objects.filter(session_id=session_id).update(gender=gender,
                                                                          country=country,
                                                                          age=age,
                                                                          competency=competency,
                                                                          antibot=antibot,
                                                                          expectation=expectation)
                    messages.success(request, 'You submitted your answers successfully.',
                                     extra_tags='information_success')
                    next_page = check_inputs_and_return_next_one(session_id, request)
                    return redirect(next_page)
                else:
                    # if a double submit was detected this triggerred a message and the user was redirected to
                    # an open task
                    next_page = check_inputs_and_return_next_one(session_id, request)
                    messages.warning(request, 'You already completed this task before. We will only collect your '
                                              'first answers! You got redirected to an open task. Please proceed from there.'
                                     , extra_tags='information_warning')
                    return redirect(next_page)
            else:
                next_page = check_inputs_and_return_next_one(session_id, request)
                return redirect(next_page)

    context = {'experiment_group': exp_group, }
    return render(request, 'myapp/user_data_input.html', context)


def gallery_euclidian(request):
    # this is the view for the formal task. Except of the images shown all four tasks look and work equivalently.
    experiments = Experiment.objects.all()
    if not request.session.exists(request.session.session_key):
        request.session.create()

    session_id = request.session.session_key
    # if a visitor already exists, use this object. Otherwise the user entered the experiment somewhere in the middle
    # and gets redirected to the home page.
    if Visitors.objects.filter(session_id=session_id).exists():
        visitor = Visitors.objects.get(session_id=session_id)
    else:
        messages.warning(request, 'You tried to start the experiment somewhere in the middle. '
                                  'You got redirected to the first page. Please start from there.',
                         extra_tags='information_warning')
        return redirect('home')

    # get treatment group of the visitor
    exp_group = visitor.experiment_group
    # get the possible answers if the visitor can delegate
    answers_formal_delegate = AnswersFormalDelegate.objects.filter(experiment='1')
    # get the possible answers if the user cannot delegate
    answers_formal_base = AnswersFormalBase.objects.filter(experiment='1')
    # get 12 randomly chosen images to from the formal image dataset to show to the user
    images_formal = fill_images_to_load(experiment='1', session_id=session_id)
    if ExperimentSessionID.objects.filter(session_id=session_id).exists():
        pass
    else:
        ExperimentSessionID.objects.create(session_id=session_id)
    set_image_attribute_seen(session_id, '1')

    # this is the logic for all treatment groups but the feedback group
    if exp_group != 'feedback':
        if request.method == 'POST':
            json_data_formal, check_all_toggled = get_results_from_radio(request)
            # if all images are classified
            if check_all_toggled:
                # if a visitor object exists
                if Visitors.objects.filter(session_id=session_id).exists():
                    # if a results object already exists
                    if Results.objects.filter(user_session_id=session_id).exists():
                        result = Results.objects.get(user_session_id=session_id)
                        # and if the formal images are still unanswered
                        if result.answers_formal == {}:
                            # update the results object with the answers given
                            Results.objects.filter(user_session_id=session_id).update(answers_formal=json_data_formal)
                            messages.warning(request, 'You successfully submitted your answers',
                                             extra_tags='information_success')
                            update_task_order(session_id, '1')
                            message_depending_on_number_of_delegates(json_data_formal, 3, 5,
                                                                     False, request, exp_group)
                            set_attribute_nr_delegated(json_data_formal, exp_group)
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                        # otherwise there is a double submit which is detected and prevented. This triggers a message
                        else:
                            messages.warning(request, 'You already completed this task before. We will only collect '
                                                      'your first try! You got redirected to the next open task',
                                             extra_tags='information_warning')
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                    # otherwise a new results object is created
                    else:
                        Results.objects.create(user_session_id=session_id, answers_formal=json_data_formal)
                        messages.success(request, 'You submitted your answers successfully',
                                         extra_tags='information_success')
                        Visitors.objects.filter(session_id=session_id).update(first_task='formal')
                        message_depending_on_number_of_delegates(json_data_formal, 3, 5,
                                                                 False, request, exp_group)
                        set_attribute_nr_delegated(json_data_formal, exp_group)
                        next_page = check_inputs_and_return_next_one(session_id, request)
                        return redirect(next_page)
                else:
                    # otherwise the user started in the middle and gets redirected to the beginning automatically
                    next_page = check_inputs_and_return_next_one(session_id, request)
                    return redirect(next_page)
            # otherwise the user has to answer the missing images
            else:
                messages.warning(request, 'You did not answer all the questions. Please choose an answer for '
                                          'every image. Your answers from before were not saved, therefore please '
                                          'answer all the questions again. Sorry for the inconvenience.',
                                 extra_tags='information_error')
                return redirect('gallery_euclidian')

    # this is the logic for the feedback treatment group. The logic itself is similar, but the user has to submit the
    # answer for one image after each image respectively. This triggers a reload which enables a message that gives
    # the user feedback
    elif exp_group == 'feedback':
        if request.method == 'POST':

            request_post_string = str(request.POST)
            if '.png_' in request_post_string:
                if Results.objects.filter(user_session_id=session_id).exists():
                    result = Results.objects.get(user_session_id=session_id)
                    if result.answers_formal == {}:
                        formal_feedback(session_id, request)
                        return redirect('gallery_euclidian')
                    else:
                        next_page = check_inputs_and_return_next_one(session_id, request)
                        messages.warning(request, 'You already completed this task before. We only collect the '
                                                  'first try. You got redirected to a task you have not finished yet.',
                                         extra_tags='information_warning')
                        return redirect(next_page)
                else:
                    formal_feedback(session_id, request)
                    return redirect('gallery_euclidian')

            else:
                if "feedback_final_submit_formal" in request.POST:
                    if Results.objects.filter(user_session_id=session_id).exists():
                        result = Results.objects.get(user_session_id=session_id)
                        if result.answers_formal == {}:
                            if check_all_tasks_answered_formal(session_id):
                                json_combined = combine_jsons(session_id, 'FeedbackResultsFormal', 'answers_formal')
                                Results.objects.filter(user_session_id=session_id).update(answers_formal=json_combined)
                                messages.warning(request, 'You submitted your answers successfully',
                                                 extra_tags='information_success')
                                update_task_order(session_id, '1')
                                message_depending_on_number_of_delegates(json_combined, 3, 5,
                                                                         True, request, exp_group)
                                set_attribute_nr_delegated_feedback(json_combined)
                                next_page = check_inputs_and_return_next_one(session_id, request)
                                return redirect(next_page)
                            else:
                                message_which_images_unanswered_formal(session_id, request)
                                messages.warning(request, 'You did not answer all the questions. Please answer all '
                                                          'of them to proceed', extra_tags='information_warning')
                                return redirect('gallery_euclidian')
                        else:
                            messages.warning(request, 'You already completed this task. We will only collect '
                                                      'your first answers!', extra_tags='information_warning')
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)

                    else:
                        if check_all_tasks_answered_formal(session_id):
                            json_combined = combine_jsons(session_id, 'FeedbackResultsFormal',
                                                          'answers_formal')
                            Results.objects.create(user_session_id=session_id, answers_formal=json_combined)
                            messages.warning(request, 'You submitted your answers successfully',
                                             extra_tags='information_success')
                            Visitors.objects.filter(session_id=session_id).update(first_task='formal')
                            message_depending_on_number_of_delegates(json_combined, 3, 5,
                                                                     True, request, exp_group)
                            set_attribute_nr_delegated_feedback(json_combined)
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                        else:
                            message_which_images_unanswered_formal(session_id, request)
                            messages.warning(request, 'You did not answer all questions. Please answer all of them '
                                                      'to proceed', extra_tags='information_warning')
                            return redirect('gallery_euclidian')
                else:
                    messages.warning(request, 'You tried to submit and empty form. Please choose an answer',
                                     extra_tags='information_error')
                    return redirect('gallery_euclidian')

    context = {'experiments': experiments,
               'images_formal': images_formal,
               'answers_formal_delegate': answers_formal_delegate,
               'answers_formal_base': answers_formal_base,
               'experiment_group': exp_group}

    return render(request, 'myapp/gallery_euclidian.html', context)


def gallery_social(request):
    # this is the view for the social space. It is equivalent to the formal view before, but it loads different images
    # and different answers
    experiments = Experiment.objects.all()
    if not request.session.exists(request.session.session_key):
        request.session.create()

    session_id = request.session.session_key
    if Visitors.objects.filter(session_id=session_id).exists():
        visitor = Visitors.objects.get(session_id=session_id)
    else:
        messages.warning(request, 'You tried to start the experiment somewhere in the middle. '
                                  'You got redirected to the first page. Please start from there.',
                         extra_tags='information_warning')
        return redirect('home')

    exp_group = visitor.experiment_group
    answers_social_delegate = AnswersSocialDelegate.objects.filter(experiment='2')
    answers_social_base = AnswersSocialBase.objects.filter(experiment='2')
    images_social = fill_images_to_load(experiment='2', session_id=session_id)
    if ExperimentSessionID.objects.filter(session_id=session_id).exists():
        pass
    else:
        ExperimentSessionID.objects.create(session_id=session_id)
    set_image_attribute_seen(session_id, '2')

    if exp_group != 'feedback':
        if request.method == 'POST':
            json_data_social, check_all_toggled = get_results_from_radio(request)

            if check_all_toggled:
                if Visitors.objects.filter(session_id=session_id).exists():
                    if Results.objects.filter(user_session_id=session_id).exists():
                        result = Results.objects.get(user_session_id=session_id)
                        if result.answers_social == {}:
                            Results.objects.filter(user_session_id=session_id).update(answers_social=json_data_social)
                            messages.warning(request, 'You successfully submitted your answers',
                                             extra_tags='information_success')
                            message_depending_on_number_of_delegates(json_data_social, 3, 5,
                                                                     False, request, exp_group)
                            update_task_order(session_id, '2')
                            set_attribute_nr_delegated(json_data_social, exp_group)
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                        else:
                            messages.warning(request, 'You already completed this task before. We will only collect '
                                                      'your first try! You got redirected to the next open task',
                                             extra_tags='information_warning')
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                    else:
                        Results.objects.create(user_session_id=session_id, answers_social=json_data_social)
                        messages.success(request, 'You submitted your answers successfully',
                                         extra_tags='information_success')
                        Visitors.objects.filter(session_id=session_id).update(first_task='social')
                        message_depending_on_number_of_delegates(json_data_social, 3, 5,
                                                                 False, request, exp_group)
                        set_attribute_nr_delegated(json_data_social, exp_group)
                        next_page = check_inputs_and_return_next_one(session_id, request)
                        return redirect(next_page)
                else:
                    next_page = check_inputs_and_return_next_one(session_id, request)
                    return redirect(next_page)
            else:
                messages.warning(request, 'You did not answer all the questions. Please choose an answer for '
                                          'every image. Your answers from before were not saved, therefore please '
                                          'answer all the questions again. Sorry for the inconvenience.',
                                 extra_tags='information_error')
                return redirect('gallery_social')

    elif exp_group == 'feedback':
        if request.method == 'POST':

            request_post_string = str(request.POST)
            if '.jpeg' in request_post_string:
                if Results.objects.filter(user_session_id=session_id).exists():
                    result = Results.objects.get(user_session_id=session_id)
                    if result.answers_social == {}:
                        social_feedback(session_id, request)
                        return redirect('gallery_social')
                    else:
                        next_page = check_inputs_and_return_next_one(session_id, request)
                        messages.warning(request, 'You already completed this task before. We only collect the '
                                                  'first try. You got redirected to a task you have not finished yet.',
                                         extra_tags='information_warning')
                        return redirect(next_page)
                else:
                    social_feedback(session_id, request)
                    return redirect('gallery_euclidian')

            else:
                if "feedback_final_submit_social" in request.POST:
                    if Results.objects.filter(user_session_id=session_id).exists():
                        result = Results.objects.get(user_session_id=session_id)
                        if result.answers_social == {}:
                            if check_all_tasks_answered_social(session_id):
                                json_combined = combine_jsons(session_id, 'FeedbackResultsSocial', 'answers_social')
                                Results.objects.filter(user_session_id=session_id).update(answers_social=json_combined)
                                messages.warning(request, 'You submitted your answers successfully',
                                                 extra_tags='information_success')
                                message_depending_on_number_of_delegates(json_combined, 3, 5,
                                                                         True, request, exp_group)
                                update_task_order(session_id, '2')
                                set_attribute_nr_delegated_feedback(json_combined)
                                next_page = check_inputs_and_return_next_one(session_id, request)
                                return redirect(next_page)
                            else:
                                message_which_images_unanswered_social(session_id, request)
                                messages.warning(request, 'You did not answer all the questions. Please answer all '
                                                          'of them to proceed', extra_tags='information_warning')
                                return redirect('gallery_social')
                        else:
                            messages.warning(request, 'You already completed this task. We will only collect '
                                                      'your first answers!', extra_tags='information_warning')
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)

                    else:
                        if check_all_tasks_answered_social(session_id):
                            json_combined = combine_jsons(session_id, 'FeedbackResultsSocial',
                                                          'answers_social')
                            Results.objects.create(user_session_id=session_id, answers_social=json_combined)
                            messages.warning(request, 'You submitted your answers successfully',
                                             extra_tags='information_success')
                            message_depending_on_number_of_delegates(json_combined, 3, 5,
                                                                     True, request, exp_group)
                            set_attribute_nr_delegated_feedback(json_combined)
                            Visitors.objects.filter(session_id=session_id).update(first_task='social')
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                        else:
                            message_which_images_unanswered_social(session_id, request)
                            messages.warning(request, 'You did not answer all questions. Please answer all of them '
                                                      'to proceed', extra_tags='information_warning')
                            return redirect('gallery_social')
                else:
                    messages.warning(request, 'You tried to submit and empty form. Please choose an answer',
                                     extra_tags='information_error')
                    return redirect('gallery_social')

    context = {'experiments': experiments,
               'images_social': images_social,
               'answers_social_delegate': answers_social_delegate,
               'answers_social_base': answers_social_base,
               'experiment_group': exp_group}

    return render(request, 'myapp/gallery_social.html', context)


def gallery_pheno(request):
    # this is the view for the phenomenological space. It is equivalent to the formal space, but it loads different
    # images and different answers
    experiments = Experiment.objects.all()
    if not request.session.exists(request.session.session_key):
        request.session.create()

    session_id = request.session.session_key
    if Visitors.objects.filter(session_id=session_id).exists():
        visitor = Visitors.objects.get(session_id=session_id)
    else:
        messages.warning(request, 'You tried to start the experiment somewhere in the middle. '
                                  'You got redirected to the first page. Please start from there.',
                         extra_tags='information_warning')
        return redirect('home')

    exp_group = visitor.experiment_group
    answers_pheno_delegate = AnswersPhenoDelegate.objects.filter(experiment='3')
    answers_pheno_base = AnswersPhenoBase.objects.filter(experiment='3')
    images_pheno = fill_images_to_load(experiment='3', session_id=session_id)
    if ExperimentSessionID.objects.filter(session_id=session_id).exists():
        pass
    else:
        ExperimentSessionID.objects.create(session_id=session_id)
    set_image_attribute_seen(session_id, '3')

    if exp_group != 'feedback':
        if request.method == 'POST':
            json_data_pheno, check_all_toggled = get_results_from_radio(request)

            if check_all_toggled:
                if Visitors.objects.filter(session_id=session_id).exists():
                    if Results.objects.filter(user_session_id=session_id).exists():
                        result = Results.objects.get(user_session_id=session_id)
                        if result.answers_pheno == {}:
                            Results.objects.filter(user_session_id=session_id).update(answers_pheno=json_data_pheno)
                            messages.warning(request, 'You successfully submitted your answers',
                                             extra_tags='information_success')
                            message_depending_on_number_of_delegates(json_data_pheno, 3, 5,
                                                                     False, request, exp_group)
                            update_task_order(session_id, '3')
                            set_attribute_nr_delegated(json_data_pheno, exp_group)
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                        else:
                            messages.warning(request, 'You already completed this task before. We will only collect '
                                                      'your first try! You got redirected to the next open task',
                                             extra_tags='information_warning')
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                    else:
                        Results.objects.create(user_session_id=session_id, answers_pheno=json_data_pheno)
                        messages.success(request, 'You submitted your answers successfully',
                                         extra_tags='information_success')
                        message_depending_on_number_of_delegates(json_data_pheno, 3, 5,
                                                                 False, request, exp_group)
                        Visitors.objects.filter(session_id=session_id).update(first_task='pheno')
                        set_attribute_nr_delegated(json_data_pheno, exp_group)
                        next_page = check_inputs_and_return_next_one(session_id, request)
                        return redirect(next_page)
                else:
                    next_page = check_inputs_and_return_next_one(session_id, request)
                    return redirect(next_page)
            else:
                messages.warning(request, 'You did not answer all the questions. Please choose an answer for '
                                          'every image. Your answers from before were not saved, therefore please '
                                          'answer all the questions again. Sorry for the inconvenience.',
                                 extra_tags='information_error')
                return redirect('gallery_pheno')

    elif exp_group == 'feedback':
        if request.method == 'POST':

            request_post_string = str(request.POST)
            if '.jpeg' in request_post_string:
                if Results.objects.filter(user_session_id=session_id).exists():
                    result = Results.objects.get(user_session_id=session_id)
                    if result.answers_pheno == {}:
                        pheno_feedback(session_id, request)
                        return redirect('gallery_pheno')
                    else:
                        next_page = check_inputs_and_return_next_one(session_id, request)
                        messages.warning(request, 'You already completed this task before. We only collect the '
                                                  'first try. You got redirected to a task you have not finished yet.',
                                         extra_tags='information_warning')
                        return redirect(next_page)
                else:
                    pheno_feedback(session_id, request)
                    return redirect('gallery_pheno')

            else:
                if "feedback_final_submit_pheno" in request.POST:
                    if Results.objects.filter(user_session_id=session_id).exists():
                        result = Results.objects.get(user_session_id=session_id)
                        if result.answers_pheno == {}:
                            if check_all_tasks_answered_pheno(session_id):
                                json_combined = combine_jsons(session_id, 'FeedbackResultsPheno', 'answers_pheno')
                                Results.objects.filter(user_session_id=session_id).update(answers_pheno=json_combined)
                                messages.warning(request, 'You submitted your answers successfully',
                                                 extra_tags='information_success')
                                message_depending_on_number_of_delegates(json_combined, 3, 5,
                                                                         True, request, exp_group)
                                update_task_order(session_id, '3')
                                set_attribute_nr_delegated_feedback(json_combined)
                                next_page = check_inputs_and_return_next_one(session_id, request)
                                return redirect(next_page)
                            else:
                                message_which_images_unanswered_pheno(session_id, request)
                                messages.warning(request, 'You did not answer all the questions. Please answer all '
                                                          'of them to proceed', extra_tags='information_warning')
                                return redirect('gallery_pheno')
                        else:
                            messages.warning(request, 'You already completed this task. We will only collect '
                                                      'your first answers!', extra_tags='information_warning')
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)

                    else:
                        if check_all_tasks_answered_pheno(session_id):
                            json_combined = combine_jsons(session_id, 'FeedbackResultsPheno',
                                                          'answers_pheno')
                            Results.objects.create(user_session_id=session_id, answers_pheno=json_combined)
                            messages.warning(request, 'You submitted your answers successfully',
                                             extra_tags='information_success')
                            message_depending_on_number_of_delegates(json_combined, 3, 5,
                                                                     True, request, exp_group)
                            Visitors.objects.filter(session_id=session_id).update(first_task='pheno')
                            set_attribute_nr_delegated_feedback(json_combined)
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                        else:
                            message_which_images_unanswered_pheno(session_id, request)
                            messages.warning(request, 'You did not answer all questions. Please answer all of them '
                                                      'to proceed', extra_tags='information_warning')
                            return redirect('gallery_pheno')
                else:
                    messages.warning(request, 'You tried to submit and empty form. Please choose an answer',
                                     extra_tags='information_error')
                    return redirect('gallery_pheno')

    context = {'experiments': experiments,
               'images_pheno': images_pheno,
               'answers_pheno_delegate': answers_pheno_delegate,
               'answers_pheno_base': answers_pheno_base,
               'experiment_group': exp_group}
    return render(request, 'myapp/gallery_pheno.html', context)


def gallery_intuitive(request):
    # this is the view for the intuitive space. It is equivalent to the formal space, but it loads different images.
    experiments = Experiment.objects.all()
    if not request.session.exists(request.session.session_key):
        request.session.create()

    session_id = request.session.session_key
    if Visitors.objects.filter(session_id=session_id).exists():
        visitor = Visitors.objects.get(session_id=session_id)
    else:
        messages.warning(request, 'You tried to start the experiment somewhere in the middle. '
                                  'You got redirected to the first page. Please start from there.',
                         extra_tags='information_warning')
        return redirect('home')

    exp_group = visitor.experiment_group
    answers_intuitive_delegate = AnswersIntuitiveDelegate.objects.filter(experiment='4')
    answers_intuitive_base = AnswersIntuitiveBase.objects.filter(experiment='4')
    images_intuitive = fill_images_to_load(experiment='4', session_id=session_id)
    if ExperimentSessionID.objects.filter(session_id=session_id).exists():
        pass
    else:
        ExperimentSessionID.objects.create(session_id=session_id)
    set_image_attribute_seen(session_id, '4')

    if exp_group != 'feedback':
        if request.method == 'POST':
            json_data_intuitive, check_all_toggled = get_results_from_radio(request)

            if check_all_toggled:
                if Visitors.objects.filter(session_id=session_id).exists():
                    if Results.objects.filter(user_session_id=session_id).exists():
                        result = Results.objects.get(user_session_id=session_id)
                        if result.answers_intuitive == {}:
                            Results.objects.filter(user_session_id=session_id).update(
                                answers_intuitive=json_data_intuitive)
                            messages.warning(request, 'You successfully submitted your answers',
                                             extra_tags='information_success')
                            message_depending_on_number_of_delegates(json_data_intuitive, 3, 5,
                                                                     False, request, exp_group)
                            update_task_order(session_id, '4')
                            set_attribute_nr_delegated(json_data_intuitive, exp_group)
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                        else:
                            messages.warning(request, 'You already completed this task before. We will only collect '
                                                      'your first try! You got redirected to the next open task',
                                             extra_tags='information_warning')
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                    else:
                        Results.objects.create(user_session_id=session_id, answers_intuitive=json_data_intuitive)
                        messages.success(request, 'You submitted your answers successfully',
                                         extra_tags='information_success')
                        message_depending_on_number_of_delegates(json_data_intuitive, 3, 5,
                                                                 False, request, exp_group)
                        Visitors.objects.filter(session_id=session_id).update(first_task='intuitive')
                        set_attribute_nr_delegated(json_data_intuitive, exp_group)
                        next_page = check_inputs_and_return_next_one(session_id, request)
                        return redirect(next_page)
                else:
                    next_page = check_inputs_and_return_next_one(session_id, request)
                    return redirect(next_page)
            else:
                messages.warning(request, 'You did not answer all the questions. Please choose an answer for '
                                          'every image. Your answers from before were not saved, therefore please '
                                          'answer all the questions again. Sorry for the inconvenience.',
                                 extra_tags='information_error')
                return redirect('gallery_intuitive')

    elif exp_group == 'feedback':
        if request.method == 'POST':

            request_post_string = str(request.POST)
            if '.jpeg' in request_post_string:
                if Results.objects.filter(user_session_id=session_id).exists():
                    result = Results.objects.get(user_session_id=session_id)
                    if result.answers_intuitive == {}:
                        intuitive_feedback(session_id, request)
                        return redirect('gallery_intuitive')
                    else:
                        next_page = check_inputs_and_return_next_one(session_id, request)
                        messages.warning(request, 'You already completed this task before. We only collect the '
                                                  'first try. You got redirected to a task you have not finished yet.',
                                         extra_tags='information_warning')
                        return redirect(next_page)
                else:
                    intuitive_feedback(session_id, request)
                    return redirect('gallery_intuitive')

            else:
                if "feedback_final_submit_intuitive" in request.POST:
                    if Results.objects.filter(user_session_id=session_id).exists():
                        result = Results.objects.get(user_session_id=session_id)
                        if result.answers_intuitive == {}:
                            if check_all_tasks_answered_intuitive(session_id):
                                json_combined = combine_jsons(session_id, 'FeedbackResultsIntuitive',
                                                              'answers_intuitive')
                                Results.objects.filter(user_session_id=session_id).update(
                                    answers_intuitive=json_combined)
                                messages.warning(request, 'You submitted your answers successfully',
                                                 extra_tags='information_success')
                                message_depending_on_number_of_delegates(json_combined, 3, 5,
                                                                         True, request, exp_group)
                                update_task_order(session_id, '4')
                                set_attribute_nr_delegated_feedback(json_combined)
                                next_page = check_inputs_and_return_next_one(session_id, request)
                                return redirect(next_page)
                            else:
                                message_which_images_unanswered_intuitive(session_id, request)
                                messages.warning(request, 'You did not answer all the questions. Please answer all '
                                                          'of them to proceed', extra_tags='information_warning')
                                return redirect('gallery_intuitive')
                        else:
                            messages.warning(request, 'You already completed this task. We will only collect '
                                                      'your first answers!', extra_tags='information_warning')
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)

                    else:
                        if check_all_tasks_answered_intuitive(session_id):
                            json_combined = combine_jsons(session_id, 'FeedbackResultsIntuitive',
                                                          'answers_intuitive')
                            Results.objects.create(user_session_id=session_id, answers_intuitive=json_combined)
                            messages.warning(request, 'You submitted your answers successfully',
                                             extra_tags='information_success')
                            message_depending_on_number_of_delegates(json_combined, 3, 5,
                                                                     True, request, exp_group)
                            Visitors.objects.filter(session_id=session_id).update(first_task='intuitive')
                            set_attribute_nr_delegated_feedback(json_combined)
                            next_page = check_inputs_and_return_next_one(session_id, request)
                            return redirect(next_page)
                        else:
                            message_which_images_unanswered_intuitive(session_id, request)
                            messages.warning(request, 'You did not answer all questions. Please answer all of them '
                                                      'to proceed', extra_tags='information_warning')
                            return redirect('gallery_intuitive')
                else:
                    messages.warning(request, 'You tried to submit and empty form. Please choose an answer',
                                     extra_tags='information_error')
                    return redirect('gallery_intuitive')

    context = {'experiments': experiments,
               'images_intuitive': images_intuitive,
               'answers_intuitive_delegate': answers_intuitive_delegate,
               'answers_intuitive_base': answers_intuitive_base,
               'experiment_group': exp_group
               }
    return render(request, 'myapp/gallery_intuitive.html', context)


def view_image(request, pk):
    # this is the view for when users wanted to enlarge an image by clicking the "View" button on the screen
    image = Image.objects.get(id=pk)
    exp = image.experiment
    print(exp)
    context = {'experiment': exp,
               'image': image}
    return render(request, 'myapp/view_image.html', context)


def add_image(request):
    # this is the view where admins can add new images to the database. This works with a single image, or a folder
    # containing multiple images
    if not request.user.is_authenticated:  # if the user is not authenticated
        messages.warning(request, 'You are not logged in!', extra_tags='information_warning')
        return redirect('home')  # redirect to login page
    else:
        experiments = Experiment.objects.all()

        if request.method == 'POST':

            data = request.POST
            images = request.FILES.getlist('images')
            name = images[0]

            if data['category'] != "none":
                experiment = Experiment.objects.get(id=data['category'])
            else:
                experiment = None
            for count, img in enumerate(images):
                name = images[count]
                Image.objects.create(experiment=experiment, image=img, name=name)

            return redirect('gallery_euclidian')

    context = {'experiments': experiments}
    return render(request, 'myapp/add_image.html', context)


def final_page(request):
    # this is the view for the final questionaire

    # create and display code for MTurk user to prove that they finished the experiment
    codes = CompletionCode.objects.filter(assigned=False)
    code = random.choice(codes)
    code_str = code.code
    CompletionCode.objects.filter(code=code).update(assigned=True)
    if not request.session.exists(request.session.session_key):
        request.session.create()
    session_id = request.session.session_key
    if Visitors.objects.filter(session_id=session_id).exists():
        visitor = Visitors.objects.get(session_id=session_id)

        exp_group = visitor.experiment_group

        if request.method == 'POST':
            data = request.POST
            formal_complexity = data['FormalComplexity']
            social_complexity = data['SocialComplexity']
            pheno_complexity = data['PhenoComplexity']
            intuitive_complexity = data['IntuitiveComplexity']

            # since only users who could delegate needed to give a perceived help answer, it was set to 7 for those who
            # could not delegate
            if exp_group == 'feedback' or exp_group == 'human_delegate' or exp_group == 'delegation_counter':
                perceived_help = data['PerceivedHelp']
            else:
                perceived_help = 7
            # this logic makes sure that all questions were answered. If not, users were redirected to the same page
            # to answer the missing questions.
            if formal_complexity == 'Please rate the complexity of the formal task (maps of postal code areas)':
                formal_complexity = 6
            if social_complexity == 'Please rate the complexity of the social task (rural vs. urban areas)':
                social_complexity = 6
            if pheno_complexity == 'Please rate the complexity of the phenomenological task (Find the correct city)':
                pheno_complexity = 6
            if intuitive_complexity == 'Please rate the complexity of the intuitive task (population density of StreetView images)':
                intuitive_complexity = 6
            if perceived_help == 'How helpful was the AI?':
                perceived_help = 6

            if (formal_complexity == 6 or social_complexity == 6 or pheno_complexity == 6 or pheno_complexity == 6 or
                    intuitive_complexity == 6 or perceived_help == 6):
                messages.warning(request,
                                 'You did not answer all the questions. Your answers from before were not saved, therefore please '
                                 'answer all the questions again. Sorry for the inconvenience.',
                                 extra_tags='information_error')
                return redirect('final_page')
            else:
                if Results.objects.filter(user_session_id=session_id).exists():
                    result = Results.objects.get(user_session_id=session_id)
                    if result.answers_social == {} or result.answers_pheno == {} or result.answers_intuitive == {} or result.answers_formal == {}:
                        messages.warning(request, 'You skipped parts of the experiment. We redirected you to the page '
                                                  'you skipped. Proceed from there!', extra_tags='information_warning')
                        chosen = check_inputs_and_return_next_one(session_id, request)
                        return redirect(chosen)
                    else:
                        visitor = Visitors.objects.get(session_id=session_id)

                        if visitor.complexity_formal == 0 and visitor.complexity_social == 0 and visitor.complexity_pheno == 0 and visitor.complexity_intuitive == 0 and visitor.perceived_help == 0:
                            Visitors.objects.filter(session_id=session_id).update(
                                complexity_formal=formal_complexity,
                                complexity_social=social_complexity,
                                complexity_pheno=pheno_complexity,
                                complexity_intuitive=intuitive_complexity,
                                perceived_help=perceived_help)

                            messages.success(request,
                                             'You submitted all your answers successfully. This is the end of the '
                                             'experiment. Thank you very much for your participation. You can '
                                             'close this window now!', extra_tags='information_success')
                            return redirect('home')
                        else:
                            chosen = check_inputs_and_return_next_one(session_id, request)
                            return redirect(chosen)
                else:
                    messages.warning(request, 'You skipped parts of the experiment. We redirected you to the task you '
                                              'skipped. Please proceed from there!', extra_tags='information_warning')
                    chosen = check_inputs_and_return_next_one(session_id, request)
                    return redirect(chosen)

    else:
        chosen = check_inputs_and_return_next_one(session_id, request)
        return redirect(chosen)

    context = {'experiment_group': exp_group,
               'survey_code': code_str, }
    return render(request, 'myapp/final_page.html', context)


def update_model_fields(request):
    # this is the view where admins can update model fields, i.e. the ai answer for an image. This works with an
    # Excel file
    if not request.user.is_authenticated:
        messages.warning(request, 'You are not logged in!', extra_tags='information_warning')
        return redirect('home')
    else:
        if request.method == 'POST':
            filename = request.FILES.get('excel')
            data = pd.read_excel(filename)
            for i in data.index:
                name = data.loc[i, 'Filename']
                ai_answer = data.loc[i, 'Predicted_Class']
                delegate = data.loc[i, 'Delegate']
                correct_answer = data.loc[i, 'Correct_Answer']
                ai_correct_prediction = data.loc[i, 'Correctly_Classified']

                Image.objects.filter(name=name).update(ai_answer=ai_answer,
                                                       correct_answer=correct_answer,
                                                       ai_delegate=delegate,
                                                       ai_predicted_correctly=ai_correct_prediction,
                                                       )

    return render(request, 'myapp/update_model_fields.html')


def add_completion_codes(request):
    # this is the view where admins can add new completion codes
    if not request.user.is_authenticated:
        messages.warning(request, 'You are not logged in!', extra_tags='information_warning')
        return redirect('home')
    else:
        if request.method == 'POST':
            filename = request.FILES.get('excel')
            data = pd.read_excel(filename)
            for i in data.index:
                code = data.loc[i, 'Code']
                CompletionCode.objects.create(code=code, assigned=False)

    return render(request, 'myapp/add_completion_codes.html')


''' this is the end of the view section, from now on you'll find functions used to do calculations'''


def get_results_from_radio(request):
    # this is a function which converts the answers given to a json string which can be saved in the database
    radio_on = list(request.POST)
    radio_on.pop(0)
    check_all_toggled = check_all_radios_toggled(radio_on)
    data_list = []
    for radio in radio_on:
        data = request.POST.get(radio)
        data_list.append(data)
    data_dict = {radio_on[i]: data_list[i] for i in range(len(radio_on))}
    json_data = json.dumps(data_dict, indent=4)
    return json_data, check_all_toggled


def check_all_radios_toggled(radio_data):
    # this simple function checks whether all radio buttons were toggled
    if len(radio_data) == 12:
        return True
    else:
        return False


def check_all_final_answers_completed(data):
    # this simple functions checks whether all final questions were answered
    data_str = str(data)
    if "Please rate the complexity of the" or 'How helpful was the AI' in data_str:
        return False
    else:
        return True


def get_feedback_results_from_image_radio(request):
    # this function converts the answers given for the feedback treatment group into a json string for each image
    data_dict = {}
    radio = list(request.POST)
    radio.pop(0)
    image_name_index = radio[0]
    answer = request.POST.get(image_name_index)
    index_str = str(int(image_name_index.split('_')[-1]))
    if len(index_str) == 1:
        image_name = image_name_index[:-2]
    else:
        image_name = image_name_index[:-3]
    index = int(index_str)
    data_dict[image_name] = answer
    json_data = json.dumps(data_dict, indent=4)
    return json_data, index, answer, image_name


def populate_feedback_answers(session_id, index, json_data, experiment, request):
    # this function uses the "submit_answers_for_index" function to check for any double submits for all four spaces
    if experiment == '1':
        if index == 0:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')
        elif index == 1:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')
        elif index == 2:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')
        elif index == 3:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')
        elif index == 4:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')
        elif index == 5:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')
        elif index == 6:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')
        elif index == 7:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')
        elif index == 8:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')
        elif index == 9:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')
        elif index == 10:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')
        else:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsFormal',
                                                    'answers_formal')

    elif experiment == '2':
        if index == 0:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')
        elif index == 1:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')
        elif index == 2:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')
        elif index == 3:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')
        elif index == 4:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')
        elif index == 5:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')
        elif index == 6:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')
        elif index == 7:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')
        elif index == 8:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')
        elif index == 9:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')
        elif index == 10:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')
        else:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsSocial',
                                                    'answers_social')

    elif experiment == '3':
        if index == 0:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsPheno',
                                                    'answers_pheno')
        elif index == 1:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsPheno',
                                                    'answers_pheno')
        elif index == 2:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsPheno',
                                                    'answers_pheno')
        elif index == 3:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsPheno',
                                                    'answers_pheno')
        elif index == 4:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsPheno',
                                                    'answers_pheno')
        elif index == 5:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsPheno',
                                                    'answers_pheno')
        elif index == 6:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsPheno',
                                                    'answers_pheno')
        elif index == 7:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsPheno',
                                                    'answers_pheno')
        elif index == 8:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsPheno',
                                                    'answers_pheno')
        elif index == 9:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsPheno',
                                                    'answers_pheno')
        else:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsPheno',
                                                    'answers_pheno')

    else:
        if index == 0:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
        elif index == 1:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
        elif index == 2:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
        elif index == 3:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
        elif index == 4:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
        elif index == 5:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
        elif index == 6:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
        elif index == 7:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
        elif index == 8:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
        elif index == 9:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
        elif index == 10:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
        else:
            double_submit = submit_answer_for_index(request, session_id, index, json_data, 'FeedbackResultsIntuitive',
                                                    'answers_intuitive')
    return double_submit


def submit_answer_for_index(request, session_id, index, json_data, model_name, field_prefix):
    # this function submits the answers for the feedback group and checks whether there are any double submits
    Model = apps.get_model('myapp', model_name)
    field_name = f'{field_prefix}{index + 1}'
    feedback_result_exists = Model.objects.filter(user_session_id=session_id).exists()

    if feedback_result_exists:
        feedback_result = Model.objects.get(user_session_id=session_id)
        if getattr(feedback_result, field_name) == {}:
            Model.objects.filter(user_session_id=session_id).update(**{field_name: json_data})
            message_string = f'You successfully submitted your answer for image {index + 1}'
            messages.warning(request, message_string, extra_tags='information_success')
            double_submit = False
        else:
            messages.warning(request,
                             'You already submitted an answer for this image. Please proceed with the next one.',
                             extra_tags='information_warning')
            double_submit = True
    else:
        Model.objects.create(user_session_id=session_id, **{field_name: json_data})
        print('new model created')
        message_string = f'You successfully submitted your answer for image {index + 1}'
        messages.warning(request, message_string, extra_tags='information_success')
        double_submit = False

    return double_submit


def combine_jsons(session_id, model_name, field_prefix):
    # this function combines the 12 json strings in the feedback group to a single json string which can be saved in
    # the database
    Model = apps.get_model('myapp', model_name)
    feedback_results = Model.objects.get(user_session_id=session_id)
    json_files = [getattr(feedback_results, f'{field_prefix}{i}') for i in range(1, 13)]

    python_objects = []
    for json_file in json_files:
        obj = json.loads(json_file)
        python_objects.append(obj)

    json_combined = json.dumps(python_objects, indent=4)
    return json_combined


def fill_images_to_load(experiment, session_id):
    # this function draws 12 random images out of the available images in each space depending on the treatment group.
    # It also makes sure that a user who comes back to a task that he has seen before sees the exact same images
    # as before
    visitor = Visitors.objects.get(session_id=session_id)
    exp_group = visitor.experiment_group

    if experiment == '1':
        if visitor.formal_images == {}:
            if exp_group == 'ai_delegate':
                images = list(Image.objects.filter(experiment=experiment).filter(ai_delegate=True))
                image_list_to_show = random.sample(images, 12)
                name_list = []
                for image in image_list_to_show:
                    name_list.append(image.name)
                image_json = json.dumps(name_list)
                Visitors.objects.filter(session_id=session_id).update(formal_images=image_json)
            else:
                images = list(Image.objects.filter(experiment=experiment))
                image_list_to_show = random.sample(images, 12)
                name_list = []
                for image in image_list_to_show:
                    name_list.append(image.name)
                image_json = json.dumps(name_list)
                Visitors.objects.filter(session_id=session_id).update(formal_images=image_json)

        else:
            name_json = visitor.formal_images
            name_list = json.loads(name_json)
            image_list_to_show = []
            for name in name_list:
                image = Image.objects.get(name=name)
                image_list_to_show.append(image)

    elif experiment == '2':
        if visitor.social_images == {}:
            if exp_group == 'ai_delegate':
                images = list(Image.objects.filter(experiment=experiment).filter(ai_delegate=True))
                image_list_to_show = random.sample(images, 12)
                name_list = []
                for image in image_list_to_show:
                    name_list.append(image.name)
                image_json = json.dumps(name_list)
                Visitors.objects.filter(session_id=session_id).update(social_images=image_json)
            else:
                images = list(Image.objects.filter(experiment=experiment))
                image_list_to_show = random.sample(images, 12)
                name_list = []
                for image in image_list_to_show:
                    name_list.append(image.name)
                image_json = json.dumps(name_list)
                Visitors.objects.filter(session_id=session_id).update(social_images=image_json)

        else:
            name_json = visitor.social_images
            name_list = json.loads(name_json)
            image_list_to_show = []
            for name in name_list:
                image = Image.objects.get(name=name)
                image_list_to_show.append(image)

    elif experiment == '3':
        if visitor.pheno_images == {}:
            if exp_group == 'ai_delegate':
                images = list(Image.objects.filter(experiment=experiment).filter(ai_delegate=True))
                image_list_to_show = random.sample(images, 12)
                name_list = []
                for image in image_list_to_show:
                    name_list.append(image.name)
                image_json = json.dumps(name_list)
                Visitors.objects.filter(session_id=session_id).update(pheno_images=image_json)
            else:
                images = list(Image.objects.filter(experiment=experiment))
                image_list_to_show = random.sample(images, 12)
                name_list = []
                for image in image_list_to_show:
                    name_list.append(image.name)
                image_json = json.dumps(name_list)
                Visitors.objects.filter(session_id=session_id).update(pheno_images=image_json)

        else:
            name_json = visitor.pheno_images
            name_list = json.loads(name_json)
            image_list_to_show = []
            for name in name_list:
                image = Image.objects.get(name=name)
                image_list_to_show.append(image)

    else:
        if visitor.intuitive_images == {}:
            if exp_group == 'ai_delegate':
                images = list(Image.objects.filter(experiment=experiment).filter(ai_delegate=True))
                image_list_to_show = random.sample(images, 12)
                name_list = []
                for image in image_list_to_show:
                    name_list.append(image.name)
                image_json = json.dumps(name_list)
                Visitors.objects.filter(session_id=session_id).update(intuitive_images=image_json)
            else:
                images = list(Image.objects.filter(experiment=experiment))
                image_list_to_show = random.sample(images, 12)
                name_list = []
                for image in image_list_to_show:
                    name_list.append(image.name)
                image_json = json.dumps(name_list)
                Visitors.objects.filter(session_id=session_id).update(intuitive_images=image_json)

        else:
            name_json = visitor.intuitive_images
            name_list = json.loads(name_json)
            image_list_to_show = []
            for name in name_list:
                image = Image.objects.get(name=name)
                image_list_to_show.append(image)

    return image_list_to_show


def check_all_tasks_answered_formal(session_id):
    # this function checks whether all images in the formal task are classified for the feedback group
    if FeedbackResultsFormal.objects.filter(user_session_id=session_id).exists():
        feedback_results = FeedbackResultsFormal.objects.get(user_session_id=session_id)
        if (feedback_results.answers_formal1 != {} and feedback_results.answers_formal2 != {}
                and feedback_results.answers_formal3 != {} and feedback_results.answers_formal4 != {}
                and feedback_results.answers_formal5 != {} and feedback_results.answers_formal6 != {}
                and feedback_results.answers_formal7 != {} and feedback_results.answers_formal8 != {}
                and feedback_results.answers_formal9 != {} and feedback_results.answers_formal10 != {}
                and feedback_results.answers_formal11 != {} and feedback_results.answers_formal12 != {}):
            all_answered = True
        else:
            all_answered = False
        return all_answered


def check_all_tasks_answered_social(session_id):
    # this function checks whether all images in the social task are classified for the feedback group
    if FeedbackResultsSocial.objects.filter(user_session_id=session_id).exists():
        feedback_results = FeedbackResultsSocial.objects.get(user_session_id=session_id)
        if (feedback_results.answers_social1 != {} and feedback_results.answers_social2 != {}
                and feedback_results.answers_social3 != {} and feedback_results.answers_social4 != {}
                and feedback_results.answers_social5 != {} and feedback_results.answers_social6 != {}
                and feedback_results.answers_social7 != {} and feedback_results.answers_social8 != {}
                and feedback_results.answers_social9 != {} and feedback_results.answers_social10 != {}
                and feedback_results.answers_social11 != {} and feedback_results.answers_social12 != {}):
            all_answered = True
        else:
            all_answered = False
        return all_answered


def check_all_tasks_answered_pheno(session_id):
    # this function checks whether all images in the phenomenological task are classified for the feedback group
    if FeedbackResultsPheno.objects.filter(user_session_id=session_id).exists():
        feedback_results = FeedbackResultsPheno.objects.get(user_session_id=session_id)
        if (feedback_results.answers_pheno1 != {} and feedback_results.answers_pheno2 != {}
                and feedback_results.answers_pheno3 != {} and feedback_results.answers_pheno4 != {}
                and feedback_results.answers_pheno5 != {} and feedback_results.answers_pheno6 != {}
                and feedback_results.answers_pheno7 != {} and feedback_results.answers_pheno8 != {}
                and feedback_results.answers_pheno9 != {} and feedback_results.answers_pheno10 != {}
                and feedback_results.answers_pheno11 != {} and feedback_results.answers_pheno12 != {}):
            all_answered = True
        else:
            all_answered = False
        return all_answered


def check_all_tasks_answered_intuitive(session_id):
    # this function checks whether all images in the intuitive task are classified for the feedback group
    if FeedbackResultsIntuitive.objects.filter(user_session_id=session_id).exists():
        feedback_results = FeedbackResultsIntuitive.objects.get(user_session_id=session_id)
        if (feedback_results.answers_intuitive1 != {} and feedback_results.answers_intuitive2 != {}
                and feedback_results.answers_intuitive3 != {} and feedback_results.answers_intuitive4 != {}
                and feedback_results.answers_intuitive5 != {} and feedback_results.answers_intuitive6 != {}
                and feedback_results.answers_intuitive7 != {} and feedback_results.answers_intuitive8 != {}
                and feedback_results.answers_intuitive9 != {} and feedback_results.answers_intuitive10 != {}
                and feedback_results.answers_intuitive11 != {} and feedback_results.answers_intuitive12 != {}):
            all_answered = True
        else:
            all_answered = False
        return all_answered


def message_which_images_unanswered_formal(session_id, request):
    # if there are images that are not classified yet for the feedback group in the formal task, then this function
    # triggers a message that tells users which images are missing still
    if FeedbackResultsFormal.objects.filter(user_session_id=session_id).exists():
        feedback_result = FeedbackResultsFormal.objects.get(user_session_id=session_id)
        feedback_results_list = [feedback_result.answers_formal1, feedback_result.answers_formal2,
                                 feedback_result.answers_formal3, feedback_result.answers_formal4,
                                 feedback_result.answers_formal5, feedback_result.answers_formal6,
                                 feedback_result.answers_formal7, feedback_result.answers_formal8,
                                 feedback_result.answers_formal9, feedback_result.answers_formal10,
                                 feedback_result.answers_formal11, feedback_result.answers_formal12]
        helper_list = [None if x == {} else 1 for x in feedback_results_list]
        indices = [i + 1 for i, v in enumerate(helper_list) if v is None]
        if indices:
            indices_str = str(indices)[1:-1]
            message_string = 'You are missing image number ' + indices_str + '!'
        else:
            message_string = 'All images have been answered!'
        messages.warning(request, message_string, extra_tags='information_warning')
    else:
        messages.warning(request, 'You are missing all images. Please choose an answer before you proceed',
                         extra_tags='information_warning')


def message_which_images_unanswered_social(session_id, request):
    # if there are images that are not classified yet for the feedback group in the social task, then this function
    # triggers a message that tells users which images are missing still
    if FeedbackResultsSocial.objects.filter(user_session_id=session_id).exists():
        feedback_result = FeedbackResultsSocial.objects.get(user_session_id=session_id)
        feedback_results_list = [feedback_result.answers_social1, feedback_result.answers_social2,
                                 feedback_result.answers_social3, feedback_result.answers_social4,
                                 feedback_result.answers_social5, feedback_result.answers_social6,
                                 feedback_result.answers_social7, feedback_result.answers_social8,
                                 feedback_result.answers_social9, feedback_result.answers_social10,
                                 feedback_result.answers_social11, feedback_result.answers_social12]
        helper_list = [None if x == {} else 1 for x in feedback_results_list]
        indices = [i + 1 for i, v in enumerate(helper_list) if v is None]
        if indices:
            indices_str = str(indices)[1:-1]
            message_string = 'You are missing image number ' + indices_str + '!'
        else:
            message_string = 'All images have been answered!'
        messages.warning(request, message_string, extra_tags='information_warning')
    else:
        messages.warning(request, 'You are missing all images. Please choose an answer before you proceed',
                         extra_tags='information_warning')


def message_which_images_unanswered_pheno(session_id, request):
    # if there are images that are not classified yet for the feedback group in the phenomenological task, then this
    # function triggers a message that tells users which images are missing still
    if FeedbackResultsPheno.objects.filter(user_session_id=session_id).exists():
        feedback_result = FeedbackResultsPheno.objects.get(user_session_id=session_id)
        feedback_results_list = [feedback_result.answers_pheno1, feedback_result.answers_pheno2,
                                 feedback_result.answers_pheno3, feedback_result.answers_pheno4,
                                 feedback_result.answers_pheno5, feedback_result.answers_pheno6,
                                 feedback_result.answers_pheno7, feedback_result.answers_pheno8,
                                 feedback_result.answers_pheno9, feedback_result.answers_pheno10,
                                 feedback_result.answers_pheno11, feedback_result.answers_pheno12]
        helper_list = [None if x == {} else 1 for x in feedback_results_list]
        indices = [i + 1 for i, v in enumerate(helper_list) if v is None]
        if len(indices) != 0:
            indices_str = str(indices)[1:-1]
            message_string = 'You are missing image number ' + indices_str + '!'
            messages.warning(request, message_string, extra_tags='information_warning')
        else:
            message_string = 'All images have been answered!'
            messages.warning(request, message_string, extra_tags='information_success')
    else:
        messages.warning(request, 'You are missing all images. Please choose an answer before you proceed',
                         extra_tags='information_warning')


def message_which_images_unanswered_intuitive(session_id, request):
    # if there are images that are not classified yet for the feedback group in the intuitive task, then this function
    # triggers a message that tells users which images are missing still
    if FeedbackResultsIntuitive.objects.filter(user_session_id=session_id).exists():
        feedback_result = FeedbackResultsIntuitive.objects.get(user_session_id=session_id)
        feedback_results_list = [feedback_result.answers_intuitive1, feedback_result.answers_intuitive2,
                                 feedback_result.answers_intuitive3, feedback_result.answers_intuitive4,
                                 feedback_result.answers_intuitive5, feedback_result.answers_intuitive6,
                                 feedback_result.answers_intuitive7, feedback_result.answers_intuitive8,
                                 feedback_result.answers_intuitive9, feedback_result.answers_intuitive10,
                                 feedback_result.answers_intuitive11, feedback_result.answers_intuitive12]
        helper_list = [None if x == {} else 1 for x in feedback_results_list]
        indices = [i + 1 for i, v in enumerate(helper_list) if v is None]
        if indices:
            indices_str = str(indices)[1:-1]
            message_string = 'You are missing image number ' + indices_str + '!'
        else:
            message_string = 'All images have been answered!'
        messages.warning(request, message_string, extra_tags='information_warning')
    else:
        messages.warning(request, 'You are missing all images. Please choose an answer before you proceed',
                         extra_tags='information_warning')


def show_feedback_messages(answer, correct_answer, ai_answer, request):
    # this function is used to give feedback to the participants in the feedback group only if they choose to delegate
    if answer != 'delegate':
        if answer == correct_answer:
            messages.warning(request, 'You answered this question correctly',
                             extra_tags='feedback_info')
        else:
            message_string = ('You answered this question incorrectly. The correct answer was: '
                              + correct_answer)
            messages.warning(request, message_string, extra_tags='feedback_info')
    else:
        if ai_answer == correct_answer:
            messages.warning(request, 'You delegated this image to the AI. '
                                      'The AI answered correctly', extra_tags='feedback_info')
        else:
            messages.warning(request, 'You delegated this image to the AI. The AI did answer'
                                      ' the question incorrectly', extra_tags='feedback_info')


def check_finished_inputs_and_return_random_next_one(session_id, request):
    # this function checks which tasks the participant has already finished. It then randomly chooses a next one
    if Results.objects.filter(user_session_id=session_id).exists():
        results = Results.objects.get(user_session_id=session_id)
        # it first checks which of the 4 spatial tasks are open still
        all_possible_ones = ['gallery_social', 'gallery_pheno', 'gallery_intuitive', 'gallery_euclidian']
        result_list = [results.answers_social, results.answers_pheno, results.answers_intuitive, results.answers_formal]
        results_helper = [0 if x == {} else 1 for x in result_list]
        open_indices = [i for i, v in enumerate(results_helper) if v == 0]

        if not open_indices:
            # if none of them are open, it checks whether the final page is answered already
            if check_if_final_page_answered(session_id):
                # if it is, the experiment is finished and the user tried to answer some of the task again. This is
                # prevented, it triggers a message and it redirects the user to the home page
                chosen = 'home'
                messages.warning(request, 'You have finished all the tasks. We only collect the answers for the '
                                          'first try. Thank you again for your participation.',
                                 extra_tags='information_warning')
            else:
                # if it isn't the user get redirected to the final page
                chosen = 'final_page'

        else:
            # if there are still open tasks, one random one out of the open ones is chosen and returned
            possible_ones = []
            for i in open_indices:
                possible_ones.append(all_possible_ones[i])
            chosen = random.choice(possible_ones)

    else:
        possible_ones = ['gallery_euclidian', 'gallery_social', 'gallery_pheno', 'gallery_intuitive']
        chosen = random.choice(possible_ones)
    return chosen


def check_inputs_and_return_next_one(session_id, request):
    # this function uses the above function and checks whether the user already answered the first questionaire
    # and the home page
    if Visitors.objects.filter(session_id=session_id).exists():
        visitor = Visitors.objects.get(session_id=session_id)
        if visitor.gender == 'no_gender' and visitor.age == 0 and visitor.country == 'no_country_assigned' and visitor.competency == 'no_answer' and visitor.antibot == 0:
            chosen = 'user_data_input'
        else:
            chosen = check_finished_inputs_and_return_random_next_one(session_id, request)

    else:
        chosen = 'home'
        messages.warning(request, 'You tried to start the experiment somewhere in the middle. '
                                  'You got redirected to the first page. Please start from there.',
                         extra_tags='information_warning')
    return chosen


def check_if_final_page_answered(session_id):
    # this function simply checks whether the final page is answered already
    visitor = Visitors.objects.get(session_id=session_id)
    if visitor.complexity_formal == 0 and visitor.complexity_social == 0 and visitor.complexity_pheno == 0 and visitor.complexity_intuitive == 0:
        return False
    else:
        return True


def formal_feedback(session_id, request):
    # this function is used to include the details of the feedback message for the feedback group in the formal task
    json_data, index, answer, image_name = get_feedback_results_from_image_radio(request)
    double_submit = populate_feedback_answers(session_id, index - 1, json_data, '1', request, )
    only_one_image_toggled = check_if_single_imaged_toggled(json_data)
    image = Image.objects.get(name=image_name)
    correct_answer = image.correct_answer

    if not double_submit:
        if answer == 'high population density':
            answer_short = 'High'
        elif answer == 'low population density':
            answer_short = 'Low'
        elif answer == 'medium population density':
            answer_short = 'Middle'
        else:
            answer_short = 'delegate'

        ai_answer = image.ai_answer
        show_feedback_messages(answer_short, correct_answer, ai_answer, request)


def social_feedback(session_id, request):
    # this function is used to include the details of the feedback message for the feedback group in the social task
    json_data, index, answer, image_name = get_feedback_results_from_image_radio(request)
    double_submit = populate_feedback_answers(session_id, index - 1, json_data, '2', request)
    image = Image.objects.get(name=image_name)
    correct_answer = image.correct_answer

    if not double_submit:
        if answer == 'rural, small town':
            answer_short = 'Rural'
        elif answer == 'urban city':
            answer_short = 'Urban'
        else:
            answer_short = 'delegate'

        ai_answer = image.ai_answer
        show_feedback_messages(answer_short, correct_answer, ai_answer, request)


def pheno_feedback(session_id, request):
    # this function is used to include the details of the feedback message for the feedback group in the
    # phenomenological task
    json_data, index, answer, image_name = get_feedback_results_from_image_radio(request)
    double_submit = populate_feedback_answers(session_id, index - 1, json_data, '3', request)
    image = Image.objects.get(name=image_name)
    correct_answer = image.correct_answer

    if not double_submit:
        if answer == 'Berlin':
            answer_short = 'Berlin'
        elif answer == 'Los Angeles':
            answer_short = 'Los Angeles'
        elif answer == 'Paris':
            answer_short = 'Paris'
        elif answer == 'New York':
            answer_short = 'New York'
        else:
            answer_short = 'delegate'

        ai_answer = image.ai_answer
        show_feedback_messages(answer_short, correct_answer, ai_answer, request)


def intuitive_feedback(session_id, request):
    # this function is used to include the details of the feedback message for the feedback group in the intuitive task
    json_data, index, answer, image_name = get_feedback_results_from_image_radio(request)
    double_submit = populate_feedback_answers(session_id, index - 1, json_data, '4', request, )
    image = Image.objects.get(name=image_name)
    correct_answer = image.correct_answer

    if not double_submit:
        if answer == 'high population density':
            answer_short = 'High'
        elif answer == 'low population density':
            answer_short = 'Low'
        elif answer == 'medium population density':
            answer_short = 'Middle'
        else:
            answer_short = 'delegate'

        ai_answer = image.ai_answer
        show_feedback_messages(answer_short, correct_answer, ai_answer, request)


def check_number_of_completed_tasks(session_id):
    # this function simply checks how many tasks a user has completed already
    result = Results.objects.get(user_session_id=session_id)
    result_list = [result.answers_pheno, result.answers_social, result.answers_intuitive, result.answers_formal]
    completed_list = [0 if x == {} else 1 for x in result_list]
    completed_indices = [i for i, v in enumerate(completed_list) if v == 1]
    return len(completed_indices)


def update_task_order(session_id, experiment):
    # this function sets the "first task", "second task", "third task", and "fourth task" field for the visitor
    completed = check_number_of_completed_tasks(session_id)
    if experiment == '1':
        if completed == 2:
            Visitors.objects.filter(session_id=session_id).update(second_task='formal')
        elif completed == 3:
            Visitors.objects.filter(session_id=session_id).update(third_task='formal')
        elif completed == 4:
            Visitors.objects.filter(session_id=session_id).update(fourth_task='formal')

    elif experiment == '2':
        if completed == 2:
            Visitors.objects.filter(session_id=session_id).update(second_task='social')
        elif completed == 3:
            Visitors.objects.filter(session_id=session_id).update(third_task='social')
        elif completed == 4:
            Visitors.objects.filter(session_id=session_id).update(fourth_task='social')

    elif experiment == '3':
        if completed == 2:
            Visitors.objects.filter(session_id=session_id).update(second_task='pheno')
        elif completed == 3:
            Visitors.objects.filter(session_id=session_id).update(third_task='pheno')
        elif completed == 4:
            Visitors.objects.filter(session_id=session_id).update(fourth_task='pheno')

    else:
        if completed == 2:
            Visitors.objects.filter(session_id=session_id).update(second_task='intuitive')
        elif completed == 3:
            Visitors.objects.filter(session_id=session_id).update(third_task='intuitive')
        elif completed == 4:
            Visitors.objects.filter(session_id=session_id).update(fourth_task='intuitive')


def count_delegates(data_json):
    # this function counts how often a user (excluding the feedback group) has delegated an image for each space
    # (self-fulfilling prophecy)
    data_dict = json.loads(data_json)
    print('data_dict_non_feedback', data_dict)
    data_str = str(data_dict)[1:-1]
    print('data_str_non_feedback', data_str)
    string_list = data_str.split(',')
    print('string_list_non_feedback', string_list)
    answer_list = []
    for string in string_list:
        print(string)
        answer = string.split(':')[1][2:-1]
        answer_list.append(answer)
    nr_delegates = answer_list.count('delegate to the AI')
    return nr_delegates


def count_delegates_feedback(data_json):
    # this function counts how often a user in the feedback group has delegated an image for each space
    # (self-fulfilling prophecy)
    data_dict = json.loads(data_json)
    print(data_dict)
    data_str = str(data_dict)[2:-1]
    print(data_str)
    string_list = data_str.split(',')
    print(string_list)
    answer_list = []
    for string in string_list:
        print(string)
        answer = string.split(':')[1][2:-2]
        answer_list.append(answer)
    nr_delegates = answer_list.count('delegate to the AI')
    return nr_delegates


def message_depending_on_number_of_delegates(data_json, lower_bound, upper_bound, feedback, request, exp_group):
    # this function provides the self-fulfilling prophecy messages to the user if they delegate less than the lower
    # bound or more than the upper bound
    if exp_group == 'feedback' or exp_group == 'human_delegate' or exp_group == 'delegation_counter':
        if not feedback:
            nr_delegates = count_delegates(data_json)
        else:
            nr_delegates = count_delegates_feedback(data_json)
        if nr_delegates < lower_bound:
            messages.warning(request, 'You only delegated very few tasks to the AI in the last experiment. An AI '
                                      'system learns and improves if it sees large amounts of data. Since you only delegated'
                                      ' very few tasks, the AI did not improve significantly during the last experiment. '
                                      'Therefore, in the next experiment, it is less capable compared to users who delegated'
                                      ' more. Keep this in mind when you decide whether you want to delegate a task or not'
                                      ' in the next experiment.', extra_tags='feedback_error')
        elif nr_delegates > upper_bound:
            messages.warning(request, 'You delegated a lot of tasks to the AI in the last experiment. An AI system '
                                      'learns and improves if'
                                      ' it sees large amounts of data. Since you delegated a lot of tasks, the AI did '
                                      'improve significantly during the last experiment. Therefore, in the next experiment,'
                                      ' it will show better results compared to a user who delegated less. Keep this in'
                                      ' mind when you decide whether you want to delegate a task or not in the next '
                                      'experiment.', extra_tags='feedback_success')


def set_image_attribute_seen(session_id, experiment):
    # this function saves how often one specific image was seen by a user in the image model
    if check_first_load(session_id, experiment):
        visitor = Visitors.objects.get(session_id=session_id)
        if experiment == '1':
            image_json = visitor.formal_images
        elif experiment == '2':
            image_json = visitor.social_images
        elif experiment == '3':
            image_json = visitor.pheno_images
        else:
            image_json = visitor.intuitive_images

        image_list = json.loads(image_json)

        for image_name in image_list:
            image = Image.objects.get(name=image_name)
            nr_seen = image.nr_seen + 1
            Image.objects.filter(name=image_name).update(nr_seen=nr_seen)

        if experiment == '1':
            ExperimentSessionID.objects.filter(session_id=session_id).update(formal_session=True)
        if experiment == '2':
            ExperimentSessionID.objects.filter(session_id=session_id).update(social_session=True)
        if experiment == '3':
            ExperimentSessionID.objects.filter(session_id=session_id).update(pheno_session=True)
        if experiment == '4':
            ExperimentSessionID.objects.filter(session_id=session_id).update(intuitive_session=True)

    else:
        pass


def check_first_load(session_id, experiment):
    # this function checks whether a user has loaded a new task for the first time or not
    session = ExperimentSessionID.objects.get(session_id=session_id)
    if experiment == '1':
        if not session.formal_session:
            first_load = True
        else:
            first_load = False
    elif experiment == '2':
        if not session.social_session:
            first_load = True
        else:
            first_load = False
    elif experiment == '3':
        if not session.pheno_session:
            first_load = True
        else:
            first_load = False
    else:
        if not session.intuitive_session:
            first_load = True
        else:
            first_load = False
    return first_load


def set_attribute_nr_delegated(json_data, exp_group):
    # this function increases the "nr_delegated" field of the image model by 1 whenever the user
    # (excluding feedback group) decides to delegate an image
    if exp_group == 'human_delegate' or exp_group == 'delegation_counter':
        data_dict = json.loads(json_data)
        for image_name, answer in data_dict.items():
            if answer == 'delegate to the AI':
                image = Image.objects.get(name=image_name)
                nr_delegated = image.nr_delegated + 1
                Image.objects.filter(name=image_name).update(nr_delegated=nr_delegated)
    else:
        pass


def set_attribute_nr_delegated_feedback(json_data):
    # this function increases the "nr_delegated" field of the image model by 1 whenever the user
    # in the feedback group decides to delegate an image
    data_dict = json.loads(json_data)
    single_dict = {image_name: answer for dictionary in data_dict for image_name, answer in dictionary.items()}
    for image_name, answer in single_dict.items():
        if answer == 'delegate to the AI':
            print(image_name)
            image = Image.objects.get(name=image_name)
            nr_delegated = image.nr_delegated + 1
            Image.objects.filter(name=image_name).update(nr_delegated=nr_delegated)


def check_if_single_imaged_toggled(json_data):
    # this function checks that users in the feedback group haven't toggled multiple images when they submit an answer
    # for a single image
    data_dict = json.loads(json_data)
    nr_answers = len(data_dict)
    print(data_dict)
    print(nr_answers)
    return True
