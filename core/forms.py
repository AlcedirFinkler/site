from django import forms
from django.core.mail.message import EmailMessage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Tenant, PlanoAssinatura

class ContatoForm(forms.Form):
    nome = forms.CharField(
        label='Nome', 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail', 
        max_length=100,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    assunto = forms.CharField(
        label='Assunto', 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mensagem = forms.CharField(
        label='Mensagem', 
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    def send_mail(self):
        nome = self.cleaned_data['nome']
        email = self.cleaned_data['email']
        assunto = self.cleaned_data['assunto']
        mensagem = self.cleaned_data['mensagem']

        conteudo = f'Nome: {nome}\nE-mail: {email}\nAssunto: {assunto}\nMensagem: {mensagem}'

        mail = EmailMessage(
            subject=assunto,
            body=conteudo,
            from_email='contato@manutec.com.br',
            to=['contato@manutec.com.br',],
            headers={'Reply-To': email}
        )
        mail.send()

class CadastroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        max_length=100, 
        required=True, 
        help_text='Informe um e-mail válido',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=100, 
        required=True, 
        help_text='Informe seu nome',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100, 
        required=True, 
        help_text='Informe seu sobrenome',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

class CadastroTenantForm(forms.ModelForm):
    plano = forms.ModelChoiceField(
        queryset=PlanoAssinatura.objects.filter(ativo=True),
        widget=forms.RadioSelect(),
        empty_label=None
    )
    cpf_cnpj = forms.CharField(
        label='CPF/CNPJ',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 12345678901 ou 12345678000199'})
    )
    
    class Meta:
        model = Tenant
        fields = ['slug', 'email', 'empresa', 'telefone', 'plano', 'cpf_cnpj']
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: minhaempresa'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: contato@minhaempresa.com.br'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da sua empresa'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: (11) 99999-9999'}),
        }
        help_texts = {
            'slug': 'Este será o subdomínio do seu tenant (ex: minhaempresa.weconn.com.br)',
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if Tenant.objects.filter(slug=slug).exists():
            raise forms.ValidationError("Este subdomínio já está em uso. Por favor, escolha outro.")
        return slug
        
    def save(self, commit=True):
        tenant = super().save(commit=False)
        tenant.nome = self.cleaned_data['slug']  # Define o nome igual ao slug
        
        if commit:
            tenant.save()
        return tenant