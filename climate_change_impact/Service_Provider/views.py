
from django.db.models import  Count, Avg
from django.shortcuts import render, redirect,get_object_or_404
from django.db.models import Count
from django.db.models import Q
import datetime
import xlwt
from django.http import HttpResponse
import numpy as np

import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import accuracy_score

from sklearn.tree import DecisionTreeClassifier

# Create your views here.
from Remote_User.models import ClientRegister_Model,predict_climate_change_impact,detection_ratio,detection_accuracy

from django.contrib import messages

def adminhome(request):
    return render(request,'SProvider/design1.html')

def serviceproviderlogin(request):
    if request.method == "POST":
        admin = request.POST.get('username')
        password = request.POST.get('password')

        # ✅ Empty fields check
        if not admin or not password:
            messages.warning(request, "Please enter both username and password.")
            return redirect('serviceproviderlogin')

        # ✅ Correct credentials
        if admin == "admin" and password == "admin":
            detection_accuracy.objects.all().delete()
            messages.success(request, "Login successful! Welcome Admin.")
            return redirect('adminhome')

        # ❌ Wrong credentials
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'SProvider/serviceproviderlogin.html')



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
        Crop = request.POST.get('Crop')
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
        print("Selected Crop:", Crop)  # optional debug

        # 🔥 STORE IN SESSION
        request.session['prediction'] = predicted_class
        request.session['probability'] = max_prob
        request.session['crop'] = Crop   # optional (for display)

        return redirect('Find_Prediction_Of_Climate_Change_Impact_Ratio')

    # 🔥 GET
    prediction = request.session.pop('prediction', None)
    probability = request.session.pop('probability', None)
    crop = request.session.pop('crop', None)

    return render(request, 'RUser/Prediction_Of_Climate_Change_Impact.html', {
        'prediction': prediction,
        'probability': probability,
        'crop': crop,
        'objs': table_data
    })




def View_Remote_Users(request):
    obj=ClientRegister_Model.objects.all()
    return render(request,'SProvider/View_Remote_Users.html',{'objects':obj})

# ✅ Approve User → Set Active
def approve_user(request, id):
    user = get_object_or_404(ClientRegister_Model, id=id)

    if user.status == "active":
        messages.warning(request, "User is already Active.")
    else:
        user.status = "active"
        user.save()
        messages.success(request, "User Activated Successfully.")

    return redirect('View_Remote_Users')


# ✅ Optional Toggle (BEST PRACTICE 🔥)
def toggle_user_status(request, id):
    user = get_object_or_404(ClientRegister_Model, id=id)

    if user.status == "active":
        user.status = "waiting"
        messages.warning(request, "User moved to Waiting.")
    else:
        user.status = "active"
        messages.success(request, "User Activated Successfully.")

    user.save()
    return redirect('View_Remote_Users')


# ❌ Delete User
def delete_user(request, id):
    user = get_object_or_404(ClientRegister_Model, id=id)
    user.delete()
    messages.error(request, "User Deleted Successfully.")
    return redirect('View_Remote_Users')    

def ViewTrendings(request):
    topic = predict_climate_change_impact.objects.values('topics').annotate(dcount=Count('topics')).order_by('-dcount')
    return  render(request,'SProvider/ViewTrendings.html',{'objects':topic})

def charts(request,chart_type):
    chart1 = detection_ratio.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts.html", {'form':chart1, 'chart_type':chart_type})

def charts1(request,chart_type):
    chart1 = detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts1.html", {'form':chart1, 'chart_type':chart_type})

def View_Prediction_Of_Climate_Change_Impact(request):
    obj =predict_climate_change_impact.objects.all()
    return render(request, 'SProvider/View_Prediction_Of_Climate_Change_Impact.html', {'list_objects': obj})

def likeschart(request,like_chart):
    charts =detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/likeschart.html", {'form':charts, 'like_chart':like_chart})


def Download_Trained_DataSets(request):

    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="PredictedData.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # writer = csv.writer(response)
    obj = predict_climate_change_impact.objects.all()
    data = obj  # dummy method to fetch data.
    for my_row in data:
        row_num = row_num + 1

        ws.write(row_num, 0, my_row.Fid, font_style)
        ws.write(row_num, 1, my_row.CDate, font_style)
        ws.write(row_num, 2, my_row.Precipitation, font_style)
        ws.write(row_num, 3, my_row.Humidity, font_style)
        ws.write(row_num, 4, my_row.WindSpeed, font_style)
        ws.write(row_num, 5, my_row.WeatherCondition, font_style)
        ws.write(row_num, 6, my_row.AvgTemp, font_style)
        ws.write(row_num, 7, my_row.AvgTempUncertainty, font_style)
        ws.write(row_num, 8, my_row.City, font_style)
        ws.write(row_num, 9, my_row.Country, font_style)
        ws.write(row_num, 10, my_row.Latitude, font_style)
        ws.write(row_num, 11, my_row.Longitude, font_style)
        ws.write(row_num, 12, my_row.Season, font_style)
        ws.write(row_num, 13, my_row.Crop, font_style)
        ws.write(row_num, 14, my_row.Prediction, font_style)

    wb.save(response)
    return response

# def train_model(request):
#     detection_accuracy.objects.all().delete()

#     data = pd.read_csv("Datasets.csv", encoding='latin-1')

#     def apply_response(Label):
#         if (Label == 0):
#             return 0  # Good
#         elif (Label == 1):
#             return 1  # Bad

#     data['Results'] = data['Label'].apply(apply_response)

#     x = data['Fid']
#     y = data['Results']

#     cv = CountVectorizer(lowercase=False, strip_accents='unicode', ngram_range=(1, 1))
#     x = cv.fit_transform(x)

#     models = []
#     from sklearn.model_selection import train_test_split
#     X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.20, random_state=13)
#     print("Train and Test Split")
#     X_train.shape, X_test.shape, y_train.shape

#     print("MLPClassifier")
#     from sklearn.neural_network import MLPClassifier
#     mlpc = MLPClassifier().fit(X_train, y_train)
#     y_pred = mlpc.predict(X_test)
#     testscore_mlpc = accuracy_score(y_test, y_pred)
#     accuracy_score(y_test, y_pred)
#     print(accuracy_score(y_test, y_pred))
#     print(accuracy_score(y_test, y_pred) * 100)
#     print("CLASSIFICATION REPORT")
#     print(classification_report(y_test, y_pred))
#     print("CONFUSION MATRIX")
#     print(confusion_matrix(y_test, y_pred))
#     models.append(('MLPClassifier', mlpc))
#     detection_accuracy.objects.create(names="MLPClassifier", ratio=accuracy_score(y_test, y_pred) * 100)

#     # SVM Model
#     print("SVM")
#     from sklearn import svm

#     lin_clf = svm.LinearSVC()
#     lin_clf.fit(X_train, y_train)
#     predict_svm = lin_clf.predict(X_test)
#     svm_acc = accuracy_score(y_test, predict_svm) * 100
#     print(svm_acc)
#     print("CLASSIFICATION REPORT")
#     print(classification_report(y_test, predict_svm))
#     print("CONFUSION MATRIX")
#     print(confusion_matrix(y_test, predict_svm))
#     models.append(('svm', lin_clf))
#     detection_accuracy.objects.create(names="SVM", ratio=svm_acc)

#     print("Logistic Regression")

#     from sklearn.linear_model import LogisticRegression

#     reg = LogisticRegression(random_state=0, solver='lbfgs').fit(X_train, y_train)
#     y_pred = reg.predict(X_test)
#     print("ACCURACY")
#     print(accuracy_score(y_test, y_pred) * 100)
#     print("CLASSIFICATION REPORT")
#     print(classification_report(y_test, y_pred))
#     print("CONFUSION MATRIX")
#     print(confusion_matrix(y_test, y_pred))
#     models.append(('logistic', reg))
#     detection_accuracy.objects.create(names="Logistic Regression", ratio=accuracy_score(y_test, y_pred) * 100)

#     print("Gradient Boosting Classifier")

#     from sklearn.ensemble import GradientBoostingClassifier
#     clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=0).fit(
#         X_train,
#         y_train)
#     clfpredict = clf.predict(X_test)
#     print("ACCURACY")
#     print(accuracy_score(y_test, clfpredict) * 100)
#     print("CLASSIFICATION REPORT")
#     print(classification_report(y_test, clfpredict))
#     print("CONFUSION MATRIX")
#     print(confusion_matrix(y_test, clfpredict))
#     models.append(('GradientBoostingClassifier', clf))
#     detection_accuracy.objects.create(names="Gradient Boosting Classifier",
#                                       ratio=accuracy_score(y_test, clfpredict) * 100)

#     labeled = 'labeled_data.csv'
#     data.to_csv(labeled, index=False)
#     data.to_markdown

#     obj = detection_accuracy.objects.all()
#     return render(request,'SProvider/train_model.html', {'objs': obj})

def train_model(request):

    import os
    import joblib
    import pandas as pd

    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    from sklearn.preprocessing import LabelEncoder, StandardScaler

    from sklearn.neural_network import MLPClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn import svm

    print("==========================================")
    print("Climate Land Suitability Training Started")
    print("==========================================")

    # Paths
    MODEL_PATH = "best_model.pkl"
    ENCODER_PATH = "label_encoder.pkl"
    SCALER_PATH = "scaler.pkl"

    # ❌ Remove skip condition for proper retraining
    # (Important for your case)
    detection_accuracy.objects.all().delete()

    # ================= LOAD DATA =================
    data = pd.read_csv("final dataset.csv")

    X = data[[
        "Latitude",
        "Longitude",
        "Elevation",
        "Average Temperature",
        "Annual Precipitation",
        "Soil pH",
        "Soil Organic Carbon",
        "Clay Content"
    ]]

    y = data["Land Suitability Class"]

    # ================= ENCODING =================
    le = LabelEncoder()
    y = le.fit_transform(y)

    # ================= SCALING =================
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    joblib.dump(le, ENCODER_PATH)
    joblib.dump(scaler, SCALER_PATH)

    # ================= SPLIT =================
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Train Size:", len(X_train))
    print("Test Size:", len(X_test))

    # ================= MODELS =================
    models = []

    # 🔹 MLP (Improved)
    mlp = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation='relu',
        solver='adam',
        max_iter=800,
        random_state=42
    )
    models.append(("MLPClassifier", mlp))

    # 🔹 SVM (Improved)
    svm_model = svm.SVC(
        kernel='rbf',
        C=10,
        gamma='scale',
        probability=True
    )
    models.append(("SVM", svm_model))

    # 🔹 Logistic Regression (Improved)
    log_model = LogisticRegression(
        max_iter=2000,
        C=1.0,
        solver='lbfgs'
    )
    models.append(("Logistic Regression", log_model))

    # 🔹 Gradient Boosting (Strong)
    gb_model = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
    models.append(("Gradient Boosting", gb_model))

    # ================= TRAIN + EVALUATE =================
    best_accuracy = 0
    best_model = None
    best_model_name = ""

    for name, model in models:

        print(f"\n========= {name} =========")

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred) * 100

        print("Accuracy:", acc)
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        print("Classification Report:")
        print(classification_report(y_test, y_pred))

        # Save each model
        joblib.dump(model, f"{name.replace(' ', '_').lower()}.pkl")

        # Save accuracy in DB
        detection_accuracy.objects.create(
            names=name,
            ratio=acc
        )

        # Track best model
        if acc > best_accuracy:
            best_accuracy = acc
            best_model = model
            best_model_name = name

    # ================= SAVE BEST MODEL =================
    joblib.dump(best_model, MODEL_PATH)

    print("\n==========================================")
    print(f"BEST MODEL: {best_model_name} ({best_accuracy:.2f}%)")
    print("==========================================")

    print("Training Completed Successfully")

    obj = detection_accuracy.objects.all()

    return render(request, 'SProvider/train_model.html', {
        'objs': obj,
        'best_model': best_model_name,
        'best_accuracy': round(best_accuracy, 2)
    })

def model_performance(request):

    import joblib
    import pandas as pd
    import numpy as np

    from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve
    from sklearn.preprocessing import label_binarize

    print("⚡ Fast Loading Models...")

    # ================= LOAD MODELS =================
    models = {
        "MLPClassifier": joblib.load("mlpclassifier.pkl"),
        "SVM": joblib.load("svm.pkl"),
        "Logistic Regression": joblib.load("logistic_regression.pkl"),
        "Gradient Boosting": joblib.load("gradient_boosting.pkl"),
    }

    le = joblib.load("label_encoder.pkl")
    scaler = joblib.load("scaler.pkl")

    # ================= LOAD DATA =================
    data = pd.read_csv("final dataset.csv")

    X = data[[
        "Latitude", "Longitude", "Elevation",
        "Average Temperature", "Annual Precipitation",
        "Soil pH", "Soil Organic Carbon", "Clay Content"
    ]]

    y = data["Land Suitability Class"]

    y = le.transform(y)
    X = scaler.transform(X)

    # ================= INIT =================
    results = []
    accuracies = []
    roc_data = {}
    confusion_data = {}

    best_accuracy = 0
    best_model_name = ""

    # For ROC
    classes = np.unique(y)
    y_bin = label_binarize(y, classes=classes)

    # ================= SINGLE LOOP (FAST) =================
    for name, model in models.items():

        print(f"⚡ Evaluating {name}...")

        # 🔥 Predict ONCE (cached)
        y_pred = model.predict(X)

        # Accuracy
        acc = accuracy_score(y, y_pred) * 100

        results.append({
            "name": name,
            "accuracy": round(acc, 2)
        })

        accuracies.append(round(acc, 2))

        # Best model
        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name

        # 🔥 Confusion Matrix (FAST)
        confusion_data[name] = confusion_matrix(y, y_pred).tolist()

        # 🔥 ROC (only if supported)
        if hasattr(model, "predict_proba"):
            y_score = model.predict_proba(X)

            fpr, tpr, _ = roc_curve(y_bin[:, 0], y_score[:, 0])

            roc_data[name] = {
                "fpr": fpr.tolist(),
                "tpr": tpr.tolist()
            }

    print("⚡ Completed in seconds")

    return render(request, "SProvider/model_performance.html", {
        "results": results,
        "model_names": [r["name"] for r in results],
        "accuracies": accuracies,
        "best_model": best_model_name,
        "best_accuracy": round(best_accuracy, 2),
        "roc_data": roc_data,
        "confusion_data": confusion_data
    })


def view_dataset(request):
    import pandas as pd

    try:
        # Load dataset
        data = pd.read_csv("final dataset.csv")

        # Take only first 200 rows
        data = data.head(200)

        # Convert to list of dicts (for HTML table)
        columns = data.columns
        rows = data.values.tolist()

        return render(request, "SProvider/view_dataset.html", {
            "columns": columns,
            "rows": rows
        })

    except Exception as e:
        return render(request, "SProvider/view_dataset.html", {
            "error": str(e)
        })    