from django import forms

from .models import City, State, Shop


# Kustomisasi Shop Admin Form
class ShopAdminForm(forms.ModelForm):

    class Meta:
        model = Shop
        fields = ('name', 'owner', 'email', 'phone', 'state', 'city', 'address', 'logo',)

    def __init__(self, *args, **kwargs):
        super(ShopAdminForm, self).__init__(*args, **kwargs)

        try:
            self.initial['state'] = kwargs['instance'].state.id
        except:
            pass

        state_list = [('', '---------')] + [(i.id, i.name) for i in State.objects.all()]

        try:
            self.initial['city'] = kwargs['instance'].city.id
            city_init_form = [(i.id, i.name) for i in City.objects.filter(
                state=kwargs['instance'].state
            )]
        except:
            city_init_form = [('', '---------')]

        self.fields['state'].widget = forms.Select(
            attrs={
                'id': 'id_state',
                'onchange': 'getCities(this.value)',
                'style': 'width:200px'
            },
            choices=state_list,
        )
        self.fields['city'].widget = forms.Select(
            attrs={
                'id': 'id_city',
                'style': 'width:200px'
            },
            choices=city_init_form
        )
