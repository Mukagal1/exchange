from django import forms
from .models import Item, UserProfile

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'image', 'category']
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'image': 'Изображение',
            'category': 'Категория',
        }

class ExchangeRequestForm(forms.Form):
    from_item = forms.ModelChoiceField(queryset=Item.objects.none(), label="Выберите свою вещь")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['from_item'].queryset = Item.objects.filter(user=user)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image', 'city', 'country', 'latitude', 'longitude']