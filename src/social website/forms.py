from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from stamps.models import UserProfil, Stamp, Collection, StampInCatalog, Transaction, Message
from django.core.exceptions import ValidationError
from stamps.multiselect import MultiSelectField
from datetime import datetime

class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'password' : forms.PasswordInput(render_value=False),
        }
        
class RegistrationForm(ModelForm):
    username        = forms.CharField(label=(u'User Name'))
    email           = forms.EmailField(label=(u'Email Address'))
    password        = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))
    password1       = forms.CharField(label=(u'Confirm Password'), widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = UserProfil
        fields = ['location', 'avatar']
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("That username is already taken. Please try something else.")
    
    def clean_password1(self):
        if 'password' in self.cleaned_data: 
            password = self.cleaned_data['password']
            password1 = self.cleaned_data['password1']
            if password != password1:
                raise forms.ValidationError("Passwords fields did not match, please fix this")
        return password

class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['message']
        widgets = {
            'message' : forms.Textarea(attrs={'rows':'5', 'cols':'80',})
        }

class SignupForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class EditForm(ModelForm):
    email           = forms.EmailField(label=(u'Email Address'))
    password        = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))
    class Meta:
        model = UserProfil
        fields = ['location', 'avatar']
        
class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['grade_receiver', 'review_receiver']
    def clean_grade_receiver(self):
        if int(self.cleaned_data['grade_receiver']) > 100:
            raise ValidationError('The grade should be between 0 and 100') 
        return self.cleaned_data['grade_receiver']
            
class CollectionForm(ModelForm):
    class Meta:
        model = Collection
        fields = ['unused_quantity', 'used_quantity']
        
    def clean(self):
        if int(self.cleaned_data['used_quantity']) == 0 and int(self.cleaned_data['unused_quantity']) == 0:
            raise ValidationError('You must own at least a copy of this stamp to add it to your collection') 
        return self.cleaned_data

CATALOG_CHOICES = (
    ('Michel','Michel'),
    ('Scott','Scott'),
    ('Stanley Gibbons','Stanley Gibbons'),
    ('Yvert et Tellier','Yvert et Tellier'),
    ('NO', 'None of the above'),
)

YEAR_CHOICES = [(u'', u'Select Year')]
YEAR_CHOICES.extend([(unicode(year), unicode(year)) for year in range(1840, datetime.now().year + 1)])


class StampInCatalogForm(ModelForm):
    class Meta:
        model = StampInCatalog
        fields = ['stampcat_id', 'catalog_name']
        widgets = {
            'catalog_name' : forms.Select(choices=CATALOG_CHOICES)
        }

class StampForm(ModelForm):
    class Meta:
        model = Stamp
        fields = ['name','series', 'issue_country', 'issue_year', 'face_value', 'perforation', 'paper_type', 'printing_method', 'color', 'watermark', 'picture']
        widgets = {
            'issue_year' : forms.Select(choices=YEAR_CHOICES)
        }
    def clean_issue_year(self):
        
        #reject data if not included between 1840 and current year
        if int((self.cleaned_data['issue_year']) < 1840 and self.cleaned_data['issue_year'] != 0000) or int(self.cleaned_data['issue_year']) > datetime.now().year:
            raise ValidationError('The year should be between 1840 and ' + str(datetime.now().year))
        return self.cleaned_data['issue_year']