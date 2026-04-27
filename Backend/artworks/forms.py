from django import forms
from .models import Order, CustomOrder, Artwork

class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['title', 'description', 'image', 'category', 'price', 'is_available']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'placeholder': 'Artwork Title'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'placeholder': 'Story behind the pattern...', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all'}),
            'price': forms.NumberInput(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'placeholder': 'Price in INR'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'w-5 h-5 accent-black'}),
        }

class ArtworkOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'email', 'phone', 'address', 'quantity']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Shipping Address', 'rows': 3}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded', 'min': 1}),
        }

class CustomOrderForm(forms.ModelForm):
    class Meta:
        model = CustomOrder
        fields = ['name', 'email', 'phone', 'art_type', 'size', 'detail_level', 'color_preference', 'description', 'reference_image', 'deadline']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'placeholder': 'Phone Number'}),
            'art_type': forms.Select(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all'}),
            'size': forms.Select(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'id': 'id_size'}),
            'detail_level': forms.Select(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'id': 'id_detail_level'}),
            'color_preference': forms.TextInput(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'placeholder': 'e.g., Black & White, Colorful'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'placeholder': 'Describe your vision... (Optional)', 'rows': 4}),
            'reference_image': forms.FileInput(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'accept': 'image/*'}),
            'deadline': forms.DateInput(attrs={'class': 'w-full p-3 border border-gray-100 rounded-none focus:border-black outline-none transition-all', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
class UPIPaymentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['transaction_id', 'payment_screenshot']
        widgets = {
            'transaction_id': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Enter 12-digit Transaction ID', 'required': 'true'}),
            'payment_screenshot': forms.FileInput(attrs={'class': 'w-full p-2 border rounded', 'accept': 'image/*'}),
        }
