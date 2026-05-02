from django import forms
from django.contrib.auth.models import User
from .models import Profile



class UserRegistrationForm(forms.ModelForm):
    # Ism va Familiya (Profile uchun)
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ismingiz'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Familiyangiz'
    }))
    
    # Email (Login sifatida ishlatiladi)
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Email (Login uchun)'
    }))

    # Avatar (Ixtiyoriy rasm)
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control'
    }))

    # Parollar
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Parol yarating'
    }))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Parolni qayta kiriting'
    }))

    class Meta:
        model = User
        # User modelida bizga faqat email va password kerak (username o'rniga email ketadi)
        fields = ['email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Email tizimda bor-yo'qligini tekshiramiz (Username sifatida ham emailni saqlaymiz)
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Bu email bilan allaqachon ro'yxatdan o'tilgan.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Parollar bir-biriga mos kelmadi!")
        return cleaned_data

    def save(self, commit=True):
        # 1. Userni yaratamiz
        user = super().save(commit=False)
        # Emailni username-ga o'zlashtiramiz, chunki Django auth username-ni talab qiladi
        user.username = self.cleaned_data['email'] 
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data["password"])
        
        if commit:
            user.save()
            # 2. Profile-ni yaratamiz (Ism, Familiya va Avatar bilan)
            Profile.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                avatar=self.cleaned_data.get('avatar')
            )
        return user