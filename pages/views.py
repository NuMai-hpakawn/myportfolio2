from django.shortcuts import render

def about(request):
    return render(request,"pages/about.html")

def contact(request):
    if request.method == 'POST':
        # Handle form submission
        # You can add email sending logic here
        from django.contrib import messages
        messages.success(request, 'Thank you for your message! I will get back to you within 24 hours.')
        return render(request, "pages/contact.html")
    return render(request, "pages/contact.html")

def portfolio(request):
    return render(request,"pages/portfolio.html")

def activities(request):
    return render(request,"pages/activities.html")

