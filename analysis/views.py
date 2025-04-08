from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
import requests
from .models import User_Result,Plans,Plan_purchase
from django.http import JsonResponse
from django.contrib.auth import  logout
import stripe
import json
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from apscheduler.schedulers.background import BackgroundScheduler
from django.contrib import messages
from  .models import Profile
from django.utils import timezone
import pandas as pd
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from django.http import JsonResponse
from .models import Analysis
# # send email to expire  plan user
# def send_mail(email,user,plan_name):
#     email_subject2 = "Plan Expire Date Is Approaching "
#     message2 = render_to_string('expire_plan.html', {
#                 'user':user,
#                 'plan_name':plan_name
                 
#         })
#     email_message2 = EmailMessage(email_subject2, message2, settings.EMAIL_HOST_USER, [email])
#     email_message2.send()
# # Function to start a scheduler for sending emails
# def start_scheduler(email,user,plan_name):
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(send_mail, 'interval',hours=0,minutes=0,seconds=0,args=[email,user,plan_name])  # Change as needed
#     scheduler.start()
# #Function to Detect expire plan to  email when plan expire to start schedular
# def sendemail():
     
#     plans = Plan_purchase.objects.filter(paid=True)
#     for plan in plans:
#         expiredate=plan.expiration_date
#         days_until_expiration = (expiredate - timezone.now()).days
#         print(days_until_expiration)
#         if 0 < days_until_expiration <= 1:
#             user=plan.user
#             email=plan.user.email
#             plan_name=plan.plan_name
#             plan.delete()
#             start_scheduler(email,user,plan_name)
#calling sending mail function


 #API URL 
API_URL = "https://api-inference.huggingface.co/models/Remicm/sentiment-analysis-model-for-socialmedia"

headers = {"Authorization": "Bearer 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"} #Authentication Token of your account
#query func send req to API 
def query(payload):
    #this fun use for sending request to api and get response mean result
	response = requests.post(API_URL, headers=headers, json=payload)
     #data return 
	return response.json()  
def contactus(request):
     user_data=User_Result.objects.filter(user=request.user)
     return render(request,'contact.html',{'user_data':user_data})
def index(request):
    
    plan=Plans.objects.all()
    print(plan)
    return render(request,'index2.html',{'plan':plan})
   
def aboutus(request):
    return render(request, 'about.html')

# @login_required
def sentimental_analysis(request):
    try:
        free_trial=User_Result.objects.filter(user=request.user).count()
        print(free_trial)
        user=request.user 
        plan_check=Plan_purchase.objects.filter(user=request.user)

        if free_trial==2 and not plan_check:
           messages.warning(request,"Free trial Limit reached please purchase a plan now")
           return redirect ('limit_reached')
         
    except:
         pass 
    
    
    
    if request.method=='POST': #check if request is GET
        input_text=request.POST.get('text','') #store input_text from form 
        output=query({"inputs":input_text})#call query function to get results
        print(output)
        #check instance if it contain data
        if isinstance(output, list) and output:
            #store output from zero index
            sentiment_predictions = output[0]
             #collect result 
            predict={prediction['label']:prediction['score']for prediction in sentiment_predictions}
            #covert 2D arry Result into jason format
            sentiment_data_json = json.dumps(predict)
            print(sentiment_data_json)
            sentiment_data_dict = json.loads(sentiment_data_json)
            negative_score = sentiment_data_dict["LABEL_0"]
            positive_score=sentiment_data_dict["LABEL_1"]
            print(negative_score,positive_score)

            # comparing condition in result variable
            if positive_score > negative_score:
                result = 'positive'
            else:
               result = 'negative'
            
               # store data in db 
            data=User_Result(user=request.user,user_text=input_text,positive=positive_score,negative=negative_score, result=result)
            data.save()  
           
            
        
            context={ 
                'positive_score':positive_score,
                'negative_score':negative_score,
                 
                'result':result,
                'input_text':input_text,
                'sentiment_scores':sentiment_data_json
            

        
             }
            
       
      
            return render(request,'result.html',context)
         
        
    return render(request,'fileupload.html')
# @login_required
def user_history(request):
      # get all results of user from database 
        user_data=User_Result.objects.filter(user=request.user)
        return render(request,'history.html',{'user_data':user_data})
# @login_required
def plan_detail(request,id):
     plan_detail=get_object_or_404(Plans,id=id) 
     print(plan_detail)
     pub_key = settings.STRIPE_PUBLIC_KEY
     check=Plan_purchase.objects.filter(user=request.user).exists()
     return render(request,'plan_detail.html',{'plan_detail':plan_detail,'pub_key':pub_key,'check':check})

def pricing(request):
    plan=Plans.objects.all()
    if request.htmx:
        return render(request,'components/pricing.html',{'plan':plan})
    else:
        return render(request,'pricing.html',{'plan':plan})
        
def chat_form(request):
    return render(request,'chatform.html')

def start_order(request):
    # Extract data from request body
    data = json.loads(request.body)
    # get plan name and paid amount
    name = data.get('name', '')
    raw_paid_amount = data.get('paid_amount', '0.00')
    
    # Convert paid_amount to Decimal
    paid_amount = Decimal(raw_paid_amount)
    
    # Multiply by 100 and format the result
    result = int(paid_amount * Decimal('100.00'))
    
    items = []
    price = result
    
    # Construct line items for Stripe checkout
    items.append({
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': name,
            },
            'unit_amount': price,
        },
        'quantity': 1
    })

    # Create a Stripe checkout session
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
         # pass stripe session values and these value store in stripe account 
        payment_method_types=['card'],
        line_items=items,
        mode='payment',
        success_url=request.build_absolute_uri('/payment_success/'),
        cancel_url=request.build_absolute_uri('/payment_cancel/'),
    )
    # data in session stored in this var
    payment_intent = session.payment_intent

    # Create a SitePurchase object to represent the order
    order = Plan_purchase.objects.create(
        user=request.user, 
        plan_name=data['name'], 
        plan_price=data['paid_amount'],
        plan_expired=data['duration'],
        paid=False
    )
    order.save()

    return JsonResponse({'session': session, 'order': payment_intent})
def payment_success(request):
    try:
        # Retrieve the order that needs to be marked as paid
        order = get_object_or_404(Plan_purchase, user=request.user, paid=False)
        order.paid = True
        order.save()
        
        # Extract necessary data from the order
        Plan_name = order.plan_name
        price = order.plan_price
        purchaseid = order.id
        
        # Send a success email to the user
        email_subject = "Thank You for Your Purchase on Sentimental Analysis Tool"
        message = render_to_string('SendEmail.html', {
            'plan_name': Plan_name,
            'user':request.user,
            'plan_price': price,
            'purchaseid': purchaseid
        })
        email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [request.user.email])
        email_message.send()

        return render(request, 'success.html')
    except Exception as e:
        print(f"Error: {str(e)}")
        return HttpResponse(status=400)
    
     
def payment_cancel(request):
     return render(request,'cancel.html')

def limit_reached(request):
     return render(request,'limit.html')
def logoutfunction(request):
    logout(request)
    return redirect('/')
def features(request):
    if request.htmx:
        return render(request,'components/features_component.html')
    else:
        return render(request,'features.html')

 
 

def upload_files(request):
    if request.method == "POST":
        file1 = request.FILES.get("file1")
        file2 = request.FILES.get("file2")
        file4 = request.FILES.get("file4")   
        column_name = request.POST.get("column_name")
        num_topics = request.POST.get("num_topics")

        if file1 and file2 and file4:
            try:
                
                files = {
                    "file1": file1,
                    "file2": file2,
                    "file4": file4,  
                }
                data = {
                    "column_name": column_name,
                    "num_topics": num_topics,
                }

                
                response = requests.post("http://127.0.0.1:8000/upload/", files=files, data=data)
                fastapi_data = response.json()

               
                print("FastAPI Response:", fastapi_data)

               
                unique_tags_df = pd.DataFrame(fastapi_data.get("unique tags", []))
                signi_rel_df = pd.DataFrame(fastapi_data.get("significance and relevence of tags", []))
                unique_posts=pd.DataFrame(fastapi_data.get("unique posts",[]))
                total_recomendation=pd.DataFrame(fastapi_data.get("total recomendation",[]))
                post_after_preprocessing=pd.DataFrame(fastapi_data.get("extracted post",[]))
                Topics=pd.DataFrame(fastapi_data.get("Extracted Topics",[]))
                Papularity_of_topics=pd.DataFrame(fastapi_data.get("papularity of topics",[]))
                difficulty_of_topics=pd.DataFrame(fastapi_data.get("difficulty of topics",[]))
                trends_of_topics=pd.DataFrame(fastapi_data.get("trends_of_topics",[]))
                question_analysis_with_percentages=pd.DataFrame(fastapi_data.get("question_analysis_with_percentages",[]))
                # Save DataFrames to in-memory Excel files
                excel_buffer1 = BytesIO()
                unique_tags_df.to_excel(excel_buffer1, index=False, engine="xlsxwriter")
                excel_buffer1.seek(0)

                excel_buffer2 = BytesIO()
                signi_rel_df.to_excel(excel_buffer2, index=False, engine="xlsxwriter")
                excel_buffer2.seek(0)
                
                excel_buffer3 = BytesIO()
                unique_posts.to_excel(excel_buffer3, index=False, engine="xlsxwriter")
                excel_buffer3.seek(0)
                
                excel_buffer4 = BytesIO()
                total_recomendation.to_excel(excel_buffer4, index=False, engine="xlsxwriter")
                excel_buffer4.seek(0)
                
                excel_buffer5 = BytesIO()
                post_after_preprocessing.to_excel(excel_buffer5, index=False, engine="xlsxwriter")
                excel_buffer5.seek(0)
                
                excel_buffer6 = BytesIO()
                Topics.to_excel(excel_buffer6, index=False, engine="xlsxwriter")
                excel_buffer6.seek(0)
                
                excel_buffer7 = BytesIO()
                Papularity_of_topics.to_excel(excel_buffer7, index=False, engine="xlsxwriter")
                excel_buffer7.seek(0)
                
                excel_buffer8 = BytesIO()
                difficulty_of_topics.to_excel(excel_buffer8, index=False, engine="xlsxwriter")
                excel_buffer8.seek(0)
                
                excel_buffer9 = BytesIO()
                trends_of_topics.to_excel(excel_buffer9, index=False, engine="xlsxwriter")
                excel_buffer9.seek(0)
                
                excel_buffer10 = BytesIO()
                question_analysis_with_percentages.to_excel(excel_buffer10, index=False, engine="xlsxwriter")
                excel_buffer10.seek(0)

                # 🔹 Store in Django Model
                file_instance = Analysis(user=request.user)
                file_instance.unique_tags.save("unique_tags.xlsx", ContentFile(excel_buffer1.read()))
                file_instance.signi_and_rel.save("signi_and_rel.xlsx", ContentFile(excel_buffer2.read()))
                file_instance.unique_posts.save("unique_posts.xlsx", ContentFile(excel_buffer3.read()))
                file_instance.total_recomendation.save("total_recomendation.xlsx", ContentFile(excel_buffer4.read()))
                file_instance.extracted_post.save("extracted_posts.xlsx", ContentFile(excel_buffer5.read()))
                file_instance.LDA_Topic.save("LDA_Extracted_Topics.xlsx",ContentFile(excel_buffer6.read()))
                file_instance.papularity_of_topics.save("papularity_of_topics.xlsx", ContentFile(excel_buffer7.read()))
                file_instance.difficulty_of_topics.save("difficulty_of_topics.xlsx",ContentFile(excel_buffer8.read()))
                file_instance.trends_of_topics.save("trends_of_topics.xlsx", ContentFile(excel_buffer9.read()))
                file_instance.question_analysis_with_percentages.save("question_analysis_with_percentages.xlsx",ContentFile(excel_buffer10.read()))

                return redirect("analytics_dashboard")
                 
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)

        return JsonResponse({"error": "Please upload all three files "}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=405)
def uploads_dataset(request):
    return render(request,"fileupload.html")
import plotly.express as px
import pandas as pd
import plotly.express as px
from django.shortcuts import render
from .models import Analysis
from django.core.paginator import Paginator
import numpy as np
import plotly.io as pio
def Analytics_Dashboard(request):
    user = request.user
    data = Analysis.objects.filter(user=user).latest('uploaded_at')
    if data.unique_tags.name.endswith(".csv"):
            df = pd.read_csv(data.unique_tags,header=None)
    elif data.unique_tags.name.endswith(".xlsx"):
            df = pd.read_excel(data.unique_tags, engine="openpyxl",header=None)
     
    # df = df.iloc[:, 0].dropna().reset_index(drop=True)  # Ensuring it's a clean list

        # Reshape data into 4 columns
    flat_list = df[0].tolist()

    # Set how many columns you want
    num_columns = 4

    # Split the list into chunks of 4
    reshaped_data = [flat_list[i:i+num_columns] for i in range(0, len(flat_list), num_columns)]

    # Create new DataFrame
    reshaped_df = pd.DataFrame(reshaped_data).fillna("")

    
     
        
        # Convert to list of dictionaries for Django
        
    data_list = reshaped_df.to_dict(orient="records")

        # Pagination logic
    page = request.GET.get("page", 1)
    paginator = Paginator(data_list, 30)  # Show 10 records per page

    try:
        data_page = paginator.page(page)
    except:
         data_page = paginator.page(1)    
    
    
    if data.signi_and_rel.name.endswith(".csv"):
            df = pd.read_csv(data.signi_and_rel)
            
            
         
    elif data.signi_and_rel.name.endswith(".xlsx"):
            df = pd.read_excel(data.signi_and_rel, engine="openpyxl")
           
           
        

        # Ensure DataFrame has necessary columns
    required_columns = ["unique_tags", "Significance", "Relevance"]
    for col in required_columns:
            if col not in df.columns:
                return render(request, "AnalyticalDashboard.html", {"significance_chart": f"<p>Missing column: {col}</p>"})

        # Generate Plotly Line Chart for Significance
    
    fig1 = px.line(df, 
                x="unique_tags", 
                y="Significance", 
                title="Significance of Unique Tags",
                labels={"unique_tags": "Tags", "Significance": "Significance"},
                markers=True)

    fig1.update_layout(
        title_x=0.5, 
        xaxis_tickangle=-45, 
        autosize=True,
        # autosize=False, 
        # width=1000, 
        # height=600, 
        margin=dict(t=50, b=150),
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }]
    )

    # Create Frames for Animation
    frames1 = [dict(
        data=[dict(x=df["unique_tags"][:i], y=df["Significance"][:i], mode="lines+markers")]
    ) for i in range(1, len(df)+1)]
    fig1.update(frames=frames1)

    
    fig2 = px.line(df, 
                x="unique_tags", 
                y="Relevance", 
                title="Relevance of Unique Tags",
                labels={"unique_tags": "Tags", "Relevance": "Relevance"},
                markers=True)

    fig2.update_layout(
        title_x=0.5, 
        xaxis_tickangle=-45, 
        autosize=True,
        # autosize=False, 
        # width=1000, 
        # height=600, 
        margin=dict(t=50, b=150)
    )
    if data.unique_posts.name.endswith(".csv"):
            df = pd.read_csv(data.unique_posts)
    elif data.unique_posts.name.endswith(".xlsx"):
            df = pd.read_excel(data.unique_posts, engine="openpyxl")
     
    df = df.dropna().reset_index(drop=True)  # Removes NaNs but keeps all columns

# Rename the column correctly  
    df.rename(columns={"signifance": "significance"}, inplace=True)  
    unique_post_fig = px.scatter(df, 
                 x="significance",  
                 y="relevance",
                 size="count",  
                 color="count",
                 title="Significance vs Relevance (Bubble Chart)")

    unique_post_fig.update_layout(
        title_x=0.5, 
        xaxis_tickangle=-45, 
        autosize=True,
        # autosize=False, 
        # width=1000, 
        # height=600, 
        margin=dict(t=50, b=150)
    )
    if data.LDA_Topic.name.endswith(".csv"):
            df = pd.read_csv(data.LDA_Topic,index_col=0)
    elif data.LDA_Topic.name.endswith(".xlsx"):
            df = pd.read_excel(data.LDA_Topic, engine="openpyxl",index_col=0)
            print(df)
    df.reset_index(inplace=True)

    # Rename the columns
    df.rename(columns={"index": "Topic Number", df.columns[1]: "Topic Words"}, inplace=True)

    # Convert to list of tuples
    topics = list(df.itertuples(index=False, name=None))
    

    # Paginate results
    paginator_for_topics = Paginator(topics, 30)  # Show 10 topics per page
    page_number_for_topics = request.GET.get("page")
    page_obj = paginator_for_topics.get_page(page_number_for_topics)
    if data.papularity_of_topics.name.endswith(".csv"):
            df = pd.read_csv(data.papularity_of_topics,index_col=0)
    elif data.papularity_of_topics.name.endswith(".xlsx"):
            df = pd.read_excel(data.papularity_of_topics, engine="openpyxl")
            print(df)
    if df.index.name == "GeneratedTopic":
        df = df.reset_index()
    if "GeneratedTopic" in df.columns:
        df.rename(columns={"GeneratedTopic": "Topic"}, inplace=True)

    
    papularity = px.pie(
        df, 
        names="Topic",  # Now "Topic" is a proper column
        values="FusedP",
        title="Topic Popularity Distribution",
        color_discrete_sequence=px.colors.sequential.Blues_r  # Stylish Blue Color
    )
    data_list = df.to_dict(orient="records")
    print(data_list)

    
    paginator_for_papularity = Paginator(data_list, 20)  # Show 5 items per page
    page_number_for_papularity = request.GET.get("page")
    page_obj_for_papularity = paginator_for_papularity.get_page(page_number_for_papularity)
    if data.difficulty_of_topics.name.endswith(".csv"):
            df = pd.read_csv(data.difficulty_of_topics)
    elif data.difficulty_of_topics.name.endswith(".xlsx"):
            df = pd.read_excel(data.difficulty_of_topics, engine="openpyxl")
    data_list_for_difficulty= df.to_dict(orient="records")
    
    paginator_for_difficulty = Paginator(data_list_for_difficulty, 20)  # Show 5 records per page
   
    page_number_for_difficulty  = request.GET.get("page")
    page_obj_for_difficulty  = paginator_for_difficulty.get_page(page_number_for_difficulty)
    difficulty_of_topics= px.bar(
        df, x="GeneratedTopic", y=["TotalQuestions", "UnansweredQuestions"], 
        barmode="group", title="Total vs. Unanswered Questions"
    )
    difficulty_of_topics.update_layout(
        title_x=0.5, 
        xaxis_tickangle=-45, 
        autosize=True,

        # autosize=False, 
        # width=1000, 
        # height=600, 
        margin=dict(t=50, b=150)
    )
    if data.trends_of_topics.name.endswith(".csv"):
            df = pd.read_csv(data.trends_of_topics)
    elif data.trends_of_topics.name.endswith(".xlsx"):
            df = pd.read_excel(data.trends_of_topics, engine="openpyxl")
    df["YearMonth"] = pd.to_datetime(df["YearMonth"])
    topic_trends_chart = px.line(
        df, x="YearMonth", y="Count", color="GeneratedTopic",
        title="Topic Trends Over Time", markers=True
    )
    topic_trends_chart.update_layout(
        title_x=0.5, 
        xaxis_tickangle=-45, 
        autosize=True,
        # autosize=False, 
        # width=1000, 
        # height=600, 
        margin=dict(t=50, b=150))
    if data.question_analysis_with_percentages.name.endswith(".csv"):
            df = pd.read_csv(data.question_analysis_with_percentages)
    elif data.question_analysis_with_percentages.name.endswith(".xlsx"):
            df = pd.read_excel(data.question_analysis_with_percentages, engine="openpyxl")
    
    question_persentage = px.bar(
         df,
        x= df.index,
        y=['What_Percentage', 'Why_Percentage', 'How_Percentage', 'Others_Percentage'],
        title="Percentage of Each Question Category by Topic",
        labels={"GeneratedTopic": "Generated Topic", "value": "Percentage of Questions (%)"},
        barmode='stack'
    )

    # Customize the layout for the bar chart
    question_persentage.update_layout(
        xaxis_title="Generated Topic",
        yaxis_title="Percentage of Questions (%)",
        xaxis_tickangle=45,
        autosize=True,
  # Rotate x-axis labels for better readability
        # autosize=False, 
        # width=1000, 
        # height=600, 
        margin=dict(t=50, b=150)
    )
    data_list_for_questions= df.to_dict(orient="records")
    print("Debuges data",data_list_for_questions)
    
    paginator_for_question_persentage = Paginator(data_list_for_questions, 20)  # Show 5 records per page
   
    page_number_for_questions  = request.GET.get("page")
    page_obj_for_questions  = paginator_for_question_persentage.get_page(page_number_for_questions)

    significance_chart = fig1.to_html(full_html=False , config={"responsive": True})
    relevance_chart = fig2.to_html(full_html=False , config={"responsive": True})
    unique_post_chart=unique_post_fig.to_html(full_html=False , config={"responsive": True})
    papularity_chart=papularity.to_html(full_html=False , config={"responsive": True})
    difficulty_chart=difficulty_of_topics.to_html(full_html=False , config={"responsive": True})
    topic_trends_chart_html= topic_trends_chart.to_html(full_html=False , config={"responsive": True})
    question_persentage_chart=question_persentage.to_html(full_html=False , config={"responsive": True})
   

    return render(request, "AnalyticalDashboard.html", {"significance_chart": significance_chart, "relevance_chart": relevance_chart,"data_page": data_page,"unique_post_chart":unique_post_chart,"page_obj":page_obj,"papularity_chart":papularity_chart,"page_obj_for_papularity":page_obj_for_papularity,"page_obj_for_difficulty": page_obj_for_difficulty,"difficulty_of_topics":difficulty_chart,"topic_trends_chart_html":topic_trends_chart_html,"question_persentage_chart":question_persentage_chart,"page_obj_for_questions":page_obj_for_questions })
