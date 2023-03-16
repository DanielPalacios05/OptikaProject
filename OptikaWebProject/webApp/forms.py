from django import forms
from django.forms import formset_factory

class PersonForm(forms.Form):
    name = forms.CharField(label="Nombre:",widget=forms.TextInput(attrs={"class":"form_control"}))

class FileForm(forms.Form):

    image = forms.FileField(required=True,label="Imagen:",widget=forms.ClearableFileInput(attrs={
            "class":"form-control pictureInput",
            "autocomplete":"off"}
    )
    )

FileFormset = formset_factory(FileForm,extra=1)