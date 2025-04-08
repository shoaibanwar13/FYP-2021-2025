
from django.db.models import ExpressionWrapper, F 
from django.db import models
from django.contrib.auth.models import User
from .utlis import generate_ref_code
from django.utils import timezone
from datetime import timedelta
from cloudinary_storage.storage import RawMediaCloudinaryStorage
#each model represented by class and each model has no of class variables 
class User_Result(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='User_Result',blank=True)
    user_text=models.CharField(null=True,max_length=2000)
    positive=models.DecimalField(max_digits=20,decimal_places=20)
    negative=models.DecimalField(max_digits=20,decimal_places=20)
    result=models.CharField(null=True,max_length=30)

    class Meta:
        verbose_name_plural='User Result'
    def __str__(self):
        return f"{self.user.username}-{self.result}"
class Plans(models.Model):
    name=models.CharField(null=True,max_length=100)
    plan_description=models.TextField()
    plan_pricing=models.DecimalField(max_digits=10,decimal_places=2)
    discount=models.CharField(max_length=10)
    benefit1=models.CharField(max_length=20)
    benefit2=models.CharField(max_length=20)
    duration=models.IntegerField(null=True)
    plan_image=models.ImageField(upload_to="plan_images/",null=True)
    created_at=models.DateTimeField(default=timezone.now)
    class Meta:
        verbose_name_plural='Plans'
    def __str__(self):
        return self.name 
class Plan_purchase(models.Model): 
    status ={
        ('Active','Active') ,
        ('Inactive','Inactive'),
        ('Expired','Expired')
    }
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='PlanBuy')
    plan_name=models.CharField(max_length=50)
    plan_price=models.DecimalField(max_digits=10,decimal_places=2)
    paid=models.BooleanField(default=False)
    plan_expired=models.IntegerField(default=32)
    created_at=models.DateTimeField(default=timezone.now)
    status= models.CharField(max_length=50,default="Active" ,choices=status)
    def save(self,*args,**kwargs):
        if self.paid and not self.plan_expired:
            self.expired_date=self.created_at+timedelta(days=self.plan_expired)
        super().save(*args,**kwargs)
    @property 
    def expiration_date(self):
        if self.paid:
            return self.created_at+timedelta(days=self.plan_expired)
        else:
            None
    class Meta:
        verbose_name_plural='Purchase Plans'
    def __str__(self):
        return self.plan_name
# class Profile(models.Model):
#     user=models.OneToOneField(User, on_delete=models.CASCADE)
#     user_image=models.ImageField(upload_to="profile_images/",null=True,default="media/user.jpg")
#     cover_image=models.ImageField(upload_to="profile_images/",null=True,default="media/user.jpg")
#     phone_number=models.CharField(max_length=15)
#     user_bio=models.TextField()
#     def __str__(self):
#         return self.user.username
class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    user_image=models.ImageField(upload_to="profile_images/",null=True,default="media/user.jpg")
    cover_image=models.ImageField(upload_to="profile_images/",null=True,default="media/user.jpg")
    phone_number=models.CharField(max_length=15)
    user_bio=models.TextField()
    code=models.CharField(max_length=5,blank=True)
    recommended_by=models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name="ref_by")
    profession=models.CharField(max_length=200,null=True)
    bio=models.TextField(null=True)
    profilepic=models.ImageField(upload_to='profilepic/', null=True,default="https://res.cloudinary.com/dm9eqnawe/image/upload/v1/media/profilepic/avatar_wtgsf3")
    created=models.DateTimeField(default=timezone.now)
    phone=models.CharField(max_length=200,null=True)
    address=models.CharField(max_length=200,null=True)
    city=models.CharField(max_length=200,null=True)
    state=models.CharField(max_length=200,null=True)
    country=models.CharField(max_length=200,null=True)
    facebook = models.URLField(blank=True, null=True)   
    skype= models.URLField(blank=True, null=True)   
    twitter = models.URLField(blank=True, null=True)   
    linkedin = models.URLField(blank=True, null=True)
    #method to sshow username with referal name
    def __str__(self) :

        return  f"{self.user.username}-{self.code}"
    #function to get get recommended profile
    def get_recommended_profile(self):
        query=Profile.objects.all()
        my_recs=[]
        for profile in query:
            if profile.recommended_by==self.user:
                my_recs.append(profile)
        return my_recs
    #save refferal code 
    def save(self, *args, **kwargs):
        if self.code=="":
            code=generate_ref_code()
            self.code=code
        super().save(*args, **kwargs)
 
    def __str__(self):
         return self.user.username
class Analysis(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='User_Analysis_report')
    unique_tags = models.FileField(upload_to='analysis_files/')
    signi_and_rel=models.FileField(upload_to='analysis_files/',null=True)
    unique_posts=models.FileField(upload_to='analysis_files/',null=True)
    total_recomendation=models.FileField(upload_to='analysis_files/',null=True)
    extracted_post=models.FileField(upload_to='analysis_files/',null=True)
    LDA_Topic=models.FileField(upload_to='analysis_files/',null=True)
    papularity_of_topics=models.FileField(upload_to='analysis_files/',null=True)
    difficulty_of_topics=models.FileField(upload_to='analysis_files/',null=True)
    trends_of_topics=models.FileField(upload_to='analysis_files/',null=True)
    question_analysis_with_percentages=models.FileField(upload_to='analysis_files/',null=True)
    coherence_score=models.DecimalField(max_digits=30,default=0,decimal_places=15)
    perplexity=models.DecimalField(max_digits=30,default=0,decimal_places=15)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)





    


