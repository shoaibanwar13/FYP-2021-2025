 
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('analysis.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('auth/',include('auth.urls')),
   
    
]
urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
