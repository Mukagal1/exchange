from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'image']
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'image': 'Изображение'
        }

class ExchangeRequestForm(forms.Form):
    from_item = forms.ModelChoiceField(queryset=Item.objects.none(), label="Выберите свою вещь")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['from_item'].queryset = Item.objects.filter(user=user)