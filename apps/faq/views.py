# -*- coding: utf-8 -*-
import datetime, settings
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView,FormView,DetailView, ListView

from forms import QuestionForm
from models import Question
from apps.siteblocks.models import Settings
from django.core.mail.message import EmailMessage


class QuestionListView(ListView):
    model = Question
    template_name = 'faq/faq.html'
    context_object_name = 'questions'
    queryset = model.objects.published()

questions_list = QuestionListView.as_view()

#class QuestionByCategoryView(DetailView):
#    model = QuestionCategory
#    template_name = 'faq/faq_by_category.html'
#    context_object_name = 'questionCategory'
#
#    def get_context_data(self, **kwargs):
#        context = super(QuestionByCategoryView, self).get_context_data(**kwargs)
#        if context['questionCategory'].is_published == False:
#            context['questionCategory'] = False
#        return context
#
#questions_by_category = QuestionByCategoryView.as_view()

class QuestionFormView(FormView):
    form_class = QuestionForm
    template_name = 'faq/faq_form.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionFormView,self).get_context_data()
        context['faq_form'] = self.form_class
        return context

question_form = QuestionFormView.as_view()

@csrf_exempt
def SaveQuestionForm(request):
    if request.is_ajax():
        data = request.POST.copy()
        faq_form = QuestionForm(data)
        if faq_form.is_valid():
            saved_object = faq_form.save()
            subject = u'ЧитаМаг - Новый вопрос.'
            subject = u''.join(subject.splitlines())
            message = render_to_string(
                'faq/admin_message_template.html',
                    {
                    'saved_object': saved_object,
                }
            )
            try:
                emailto = Settings.objects.get(name='workemail').value
            except Settings.DoesNotExist:
                emailto = False

            if emailto:
                msg = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [emailto])
                msg.content_subtype = "html"
                msg.send()

            return HttpResponse('success')
        else:
            faq_form_html = render_to_string(
                'faq/faq_form.html',
                    {'faq_form': faq_form}
            )
            return HttpResponse(faq_form_html)
    else:
        return HttpResponseBadRequest()