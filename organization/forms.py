from django import forms
from jalali_date_new.fields import JalaliDateField, JalaliDateTimeField
from jalali_date_new.widgets import AdminJalaliDateWidget, AdminJalaliTimeWidget,\
									AdminJalaliDateTimeWidget
from .models import VacationRequest, ProblemReport


VACATION_STATUS = [
    ("تمام موارد", "تمام موارد"),
    ("بررسی نشده", "بررسی نشده"),
    ("تایید جانشین", "تایید جانشین"),
    ("رد جانشین", "رد جانشین"),
    ("موافقت شده", "موافقت شده"),
    ("رد شده", "رد شده")
]

VACATION_BOSS_STATUS = [
    ("تایید جانشین", "تایید جانشین"),
    ("موافقت شده", "موافقت شده"),
    ("رد شده", "رد شده")
]

VACATION_ALTER_STATUS = [
    ("بررسی نشده", "بررسی نشده"),
    ("تایید جانشین", "تایید جانشین"),
    ("رد جانشین", "رد جانشین")
]

PROBLEM_STATUS = [
    ("تمام موارد", "تمام موارد"),
    (True, "موثر بوده"),
    (False, "موثر نبوده")
]


class VacationRequestForm(forms.ModelForm):

    class Meta:
        model = VacationRequest
        fields = ('type', 'alternative', 'start_date', 'end_date', 'duration', 'description')
        widgets = {
            'alternative': forms.Select(attrs={
                'class': "formTextBox",
                'id': "alternative",
                'placeholder': "جایگزین",
            }),
            'duration': forms.NumberInput(attrs={
                'class': "formTextBox",
                'id': "duration",
                'placeholder': "مدت",
            }),
            'type': forms.Select(attrs={
                'class': "formTextBox",
                'id': "type",
                'placeholder': "نوع مرخصی",
            }),
            'description': forms.Textarea(attrs={
                'class': "formTextBox",
                'id': "description",
                'placeholder': "توضیحات",
            })
        }

    def __init__(self, *args, **kwargs):
        super(VacationRequestForm, self).__init__(*args, **kwargs)
        self.fields['start_date'] = JalaliDateTimeField(label="تاریخ شروع",
                                                        widget=AdminJalaliDateTimeWidget)
        self.fields['start_date'].widget.attrs.update({'class': 'formTextBox'})
        self.fields['start_date'].widget.attrs.update({'placeholder': 'تاریخ و ساعت شروع'})

        self.fields['end_date'] = JalaliDateTimeField(label="تاریخ پایان",
                                                      widget=AdminJalaliDateTimeWidget)
        self.fields['end_date'].widget.attrs.update({'class': 'formTextBox'})
        self.fields['end_date'].widget.attrs.update({'placeholder': 'تاریخ و ساعت پایان'})


class VacationRequestBossReviewForm(forms.ModelForm):

    class Meta:
        model = VacationRequest
        fields = ('status',)
        widgets = {
            'status': forms.Select(attrs={
                'class': "formTextBox",
                'id': "status",
            }),
        }

    def __init__(self, *args, **kwargs):
        super(VacationRequestBossReviewForm, self).__init__(*args, **kwargs)
        self.fields['status'].choices = VACATION_BOSS_STATUS


class VacationRequestAlterReviewForm(forms.ModelForm):

    class Meta:
        model = VacationRequest
        fields = ('status',)
        widgets = {
            'status': forms.Select(attrs={
                'class': "formTextBox",
                'id': "status",
            }),
        }

    def __init__(self, *args, **kwargs):
        super(VacationRequestAlterReviewForm, self).__init__(*args, **kwargs)
        self.fields['status'].choices = VACATION_ALTER_STATUS


class ProblemReportForm(forms.ModelForm):

    class Meta:
        model = ProblemReport
        fields = ('type', 'corrective_actions', 'prevention_actions', 'description', 'effective')
        widgets = {
            'type': forms.TextInput(attrs={
                'class': "formTextBox",
                'id': "type",
                'maxlength': "150",
                'placeholder': "نوع خطا",
                'required': "true"
            }),
            'description': forms.Textarea(attrs={
                'class': "formTextBox",
                'id': "description",
                'placeholder': "توضیحات",
                'maxlength': "250"
            }),
            'corrective_actions': forms.Textarea(attrs={
                'class': "formTextBox",
                'id': "corrective_actions",
                'placeholder': "اقدامات اصلاحی",
                'maxlength': "250"
            }),
            'prevention_actions': forms.Textarea(attrs={
                'class': "formTextBox",
                'id': "description",
                'placeholder': "اقدامات پیشگیری",
                'maxlength': "250"
            }),
            'effective': forms.CheckboxInput(attrs={
                'class': "formTextBox",
                'id': "effective",
                'label': "مؤثر بوده/نبوده"
            })
        }


class SearchForm(forms.Form):

    start_date = JalaliDateTimeField(label="تاریخ شروع",
                                     widget=AdminJalaliDateWidget)
    start_date.widget.attrs.update({'class': 'formTextBox'})
    start_date.widget.attrs.update({'placeholder': 'تاریخ شروع'})

    end_date = JalaliDateTimeField(label="تاریخ پایان",
                                   widget=AdminJalaliDateWidget)
    end_date.widget.attrs.update({'class': 'formTextBox'})
    end_date.widget.attrs.update({'placeholder': 'تاریخ پایان'})

    status = forms.CharField(widget=forms.Select(attrs={
        'class': "formTextBox",
        'id': "status",
    }, choices=VACATION_STATUS), label="وضعیت")


class ProblemSearchForm(forms.Form):

    start_date = JalaliDateTimeField(label="تاریخ شروع",
                                     widget=AdminJalaliDateWidget)
    start_date.widget.attrs.update({'class': 'formTextBox'})
    start_date.widget.attrs.update({'placeholder': 'تاریخ شروع'})

    end_date = JalaliDateTimeField(label="تاریخ پایان",
                                   widget=AdminJalaliDateWidget)
    end_date.widget.attrs.update({'class': 'formTextBox'})
    end_date.widget.attrs.update({'placeholder': 'تاریخ پایان'})

    status = forms.CharField(widget=forms.Select(attrs={
        'class': "formTextBox",
        'id': "status",
    }, choices=PROBLEM_STATUS), label="موثر بوده/نبوده")