from django import forms

class commitform(forms.Form):
    #name = forms.CharField(max_length=30)
    #email = forms.EmailField(max_length=254)
    TextFile = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': '35',
                'cols': '150',
                #'placeholder': 'Write your name here'
            }
        )
    )
    #source = forms.CharField(       # A hidden input for internal use
    #    max_length=50,              # tell from which page the user sent the message
    #    widget=forms.HiddenInput()
    #)

    def clean(self):
        cleaned_data = super(commitform, self).clean()
    #    name = cleaned_data.get('name')
    #    email = cleaned_data.get('email')
        message = cleaned_data.get('TextFile')
    #     if not name and not email and not message:
    #        raise forms.ValidationError('You have to write something!')