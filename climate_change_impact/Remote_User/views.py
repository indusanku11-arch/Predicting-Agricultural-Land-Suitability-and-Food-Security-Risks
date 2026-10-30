from django.db.models import Count, Q
from django.shortcuts import render, redirect

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier, VotingClassifier

from Remote_User.models import (
    ClientRegister_Model,
    predict_climate_change_impact,
    detection_ratio,
    detection_accuracy
)


def base(request):
    return render(request, 'RUser/base.html')

def userhome(request):
    return render(request,'RUser/userhome.html')    

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ClientRegister_Model
from django.contrib import messages

def login(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        try:
            user = ClientRegister_Model.objects.get(username=username)

            if user.password != password:
                messages.error(request, "Wrong Password ❌")
                return redirect('login')

            # 🔥 STATUS CHECK
            if user.status != "active":
                messages.warning(request, "Account not approved by admin yet ⏳")
                return redirect('login')

            request.session["userid"] = user.id
            messages.success(request, "Login Successful ✅")
            return redirect('userhome')

        except ClientRegister_Model.DoesNotExist:
            messages.error(request, "User not found ❌")
            return redirect('login')

    return render(request, 'RUser/login.html')


from django.contrib import messages

def Register1(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()

        # Check duplicate user
        if ClientRegister_Model.objects.filter(username=username).exists():
            messages.error(request, "Username already exists ❌")
            return redirect('Register1')

        ClientRegister_Model.objects.create(
            username=username,
            email=request.POST.get('email'),
            password=request.POST.get('password'),
            phoneno=request.POST.get('phoneno'),
            country=request.POST.get('country'),
            state=request.POST.get('state'),
            city=request.POST.get('city'),
            status='waiting'   # IMPORTANT
        )

        messages.success(request, "Registered Successfully! Waiting for Admin Approval ⏳")
        return redirect('Register1')

    return render(request, 'RUser/Register1.html')

def ViewYourProfile(request):
    userid = request.session['userid']
    obj = ClientRegister_Model.objects.get(id=userid)
    return render(request, 'RUser/ViewYourProfile.html', {'object': obj})



from django.shortcuts import render, redirect

def Prediction_Of_Climate_Change_Impact(request):

    import os
    import pandas as pd
    import joblib
    import numpy as np

    MODEL_PATH = "best_model.pkl"
    SCALER_PATH = "scaler.pkl"
    ENCODER_PATH = "label_encoder.pkl"

    table_data = detection_accuracy.objects.all()

    if not os.path.exists(MODEL_PATH):
        return render(request, 'RUser/Prediction_Of_Climate_Change_Impact.html', {
            'error': "Model Not Trained Yet",
            'objs': table_data
        })

    if request.method == "POST":

        Latitude = float(request.POST.get('Latitude'))
        Longitude = float(request.POST.get('Longitude'))
        Elevation = float(request.POST.get('Elevation'))
        AvgTemp = float(request.POST.get('AverageTemperature'))
        Precipitation = float(request.POST.get('AnnualPrecipitation'))
        SoilPH = float(request.POST.get('SoilPH'))
        SoilOrganicCarbon = float(request.POST.get('SoilOrganicCarbon'))
        ClayContent = float(request.POST.get('ClayContent'))

        input_data = pd.DataFrame([[ 
            Latitude, Longitude, Elevation,
            AvgTemp, Precipitation, SoilPH,
            SoilOrganicCarbon, ClayContent
        ]], columns=[
            "Latitude", "Longitude", "Elevation",
            "Average Temperature", "Annual Precipitation",
            "Soil pH", "Soil Organic Carbon", "Clay Content"
        ])

        scaler = joblib.load(SCALER_PATH)
        model = joblib.load(MODEL_PATH)
        le = joblib.load(ENCODER_PATH)

        input_scaled = scaler.transform(input_data)

        prediction = model.predict(input_scaled)
        probability = model.predict_proba(input_scaled)

        predicted_class = le.inverse_transform(prediction)[0]
        max_prob = round(np.max(probability) * 100, 2)

        print("Prediction:", predicted_class)

        # 🔥 STORE IN SESSION
        request.session['prediction'] = predicted_class
        request.session['probability'] = max_prob

        return redirect('Find_Prediction_Of_Climate_Change_Impact_Ratio')

    # 🔥 GET
    prediction = request.session.pop('prediction', None)
    probability = request.session.pop('probability', None)

    return render(request, 'RUser/Prediction_Of_Climate_Change_Impact.html', {
        'prediction': prediction,
        'probability': probability,
        'objs': table_data
    })