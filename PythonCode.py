#!/usr/bin/env python
# coding: utf-8

# # .........................................................................................   جمع آوری داده های مورد نیاز     

#  برای انجام این تحقیق به قیمت های 10 سال گذشته چند کالا (نفت ، طلا ، مس ،شاخص دلار، نقره) احتیاج داشتیم . برای استخراج این داده های مالی منابع مختلف و معتبری مانند : رویترز ، بلومبرگ ، ابزارهای مالی شرکت یاهو و همینطور شرکت گوگل و ..... وجود دارند که می توان از آنها استفاده کرد . ما دراین تحقیق با توجه به اینکه اپ شرکت یاهو  
# هماهنگی مناسبی با زبان پایتون دارد ، استفاده از آن را برای استخراج و بارگیری داده ها مفید ارزیابی کرده ایم  

# (https://pypi.org/project/yahoofinancials/)

# In[1]:


import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from yahoofinancials import YahooFinancials


# بسته یاهو فایننشیالز به نمادهای تیکر یاهو احتیاج دارد که در قالب یک فایل اکسل آنها را وارد می کنیم و نمادها و نامها را به عنوان لیست های جداگانه استخراج می کنیم 

# In[2]:


ticker_details = pd.read_excel("Ticker List.xlsx")
ticker_details.head(20)


# In[3]:


ticker = ticker_details['Ticker'].to_list()
names = ticker_details["Description"].to_list()


# حالا که لیست را در اختیار داریم باید مشخص کنیم که داده ها برای چه محدوده تاریخی وارد شوند.در اینجا محدوده بین سالهای 2010 تا 2021 را انتخاب می کنیم و آن را در یک قاب داده خالی می نویسیم ومقادیری که از یاهو استخراج می کنیم در این قاب داده قرار می دهیم  

# In[4]:



end_date= "2021-03-01"
start_date = "2010-01-01"
date_range = pd.bdate_range(start=start_date,end=end_date)
values = pd.DataFrame({ 'Date': date_range})
values['Date']= pd.to_datetime(values['Date'])


# با استفاده از یک لوپ قیمت نهایی تاریخها را استخراج کرده و به صورت افقی به قاب داده اضافه می کنیم . با توجه به وجود تعطیلات متفاوت ممکن است فیلدهایی خالی بماند که در نهایت آنها را پر می کنیم

# In[5]:



for i in ticker:
    raw_data = YahooFinancials(i)
    raw_data = raw_data.get_historical_price_data(start_date, end_date,"daily")
    df = pd.DataFrame(raw_data[i]["prices"])[['formatted_date','adjclose']]
    df.columns = ['Date1',i]
    df['Date1']= pd.to_datetime(df['Date1'])
    values = values.merge(df,how='left',left_on='Date',right_on='Date1')
    values = values.drop(labels='Date1',axis=1)


names.insert(0,'Date')
values.columns = names
print(values.shape)
print(values.isna().sum())
values.tail()


# In[6]:


#Front filling the NaN values in the data set
values = values.fillna(method="ffill",axis=0)
values = values.fillna(method="bfill",axis=0)
values.isna().sum()


# In[7]:


# Co-ercing numeric type to all columns except Date
cols=values.columns.drop('Date')
values[cols] = values[cols].apply(pd.to_numeric,errors='coerce').round(decimals=1)
values.tail()


# In[8]:


values.to_csv("Training Data_Values.csv")


# در اینجا بازده کوتاه مدت همه ابزارها و بازده بلندمدت آنها را محاسبه می کنیم

# In[9]:


imp = ["Gold","Silver", "Crude Oil", "Copper","Dollar Index"]

# Calculating Short term -Historical Returns

change_days = [1,3,5,14,21]

data = pd.DataFrame(data=values['Date'])
for i in change_days:
    print(data.shape)
    x= values[cols].pct_change(periods=i).add_suffix("-T-"+str(i))
    data=pd.concat(objs=(data,x),axis=1)
    x=[]
print(data.shape)

# Calculating Long term Historical Returns
change_days = [60,90,180,250]

for i in change_days:
    print(data.shape)
    x= values[imp].pct_change(periods=i).add_suffix("-T-"+str(i))
    data=pd.concat(objs=(data,x),axis=1)
    x=[]
print(data.shape)


# میانگین های متحرک یک معیار بسیار متداول تکنیکال در محاسبه نقاط حمایت و مقاومت یک دارایی می باشند .ترکیبی از میانگین های متحرک ساده ونمایی را محاسبه می کنیم و به فضای ویژگی های موجود اضافه می کنیم

# In[10]:


moving_avg = pd.DataFrame(values["Date"],columns=["Date"])
moving_avg["Date"]=pd.to_datetime(moving_avg["Date"],format="%Y-%b-%d")
moving_avg["Gold/15SMA"] = (values["Gold"]/(values["Gold"].rolling(window=15).mean()))-1
moving_avg["Gold/30SMA"] = (values["Gold"]/(values["Gold"].rolling(window=30).mean()))-1
moving_avg["Gold/60SMA"] = (values["Gold"]/(values["Gold"].rolling(window=60).mean()))-1
moving_avg["Gold/90SMA"] = (values["Gold"]/(values["Gold"].rolling(window=90).mean()))-1
moving_avg["Gold/180SMA"] = (values["Gold"]/(values["Gold"].rolling(window=180).mean()))-1
moving_avg["Gold/90EMA"] = (values["Gold"]/(values["Gold"].ewm(span=90,adjust=True,ignore_na=True).mean()))-1
moving_avg["Gold/180EMA"] = (values["Gold"]/(values["Gold"].ewm(span=180,adjust=True,ignore_na=True).mean()))-1
moving_avg = moving_avg.dropna(axis=0)
print(moving_avg.shape)
moving_avg.head()


# In[11]:


#Merging Moving Average values to the feature space

print(data.shape)
data["Date"]=pd.to_datetime(data["Date"],format='%Y-%b-%d')
data = pd.merge(left=data,right=moving_avg,how='left',on='Date')
print(data.shape)
data.isna().sum()


# اکنون ما باید اهداف ایجاد کنیم ، یعنی آنچه می خواهیم پیش بینی کنیم. افق های 14 روزه و 22 روزه را انتخاب کردم زیرا سایر افق های کوچکتر بسیار ناپایدارو فاقد قدرت پیش بینی هستند. با این حال ، می توان افق های دیگر را نیز آزمایش کرد

# In[12]:


y = pd.DataFrame(data=values['Date'])
print(y.shape)
y["Gold-T+14"]=values["Gold"].pct_change(periods=-14)
y["Gold-T+22"]=values["Gold"].pct_change(periods=-22)
print(y.shape)
y.isna().sum()


# In[13]:


# Removing NAs

print(data.shape)
data = data[data["Gold-T-250"].notna()]
y = y[y["Gold-T+22"].notna()]
print(data.shape)
print(y.shape)


# اکنون ما متغیرهای هدف را با فضای ویژگی ادغام می کنیم تا داده ای دریافت کنیم که در نهایت بتوانیم مدل سازی را شروع کنیم

# In[14]:


data = pd.merge(left=data,right=y,how='inner',on='Date',suffixes=(False,False))
print(data.shape)
data.isna().sum()


# In[15]:


data.to_csv("Training Data.csv",index=False)


# In[16]:


corr = data.corr().iloc[:,-2:].drop(labels=["Gold-T+14","Gold-T+22"],axis=0)


# In[17]:


import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


# In[18]:


sns.distplot(corr.iloc[:,0])


# In[19]:


pd.set_option('display.max_rows', None)
corr_data = data.tail(2000).corr()
corr_data = pd.DataFrame(corr_data['Gold-T+14'])
corr_data = corr_data.sort_values('Gold-T+14',ascending=False)


# In[20]:


sns.distplot(corr_data)


# # Pycaret کتابخانه کارآمد

# این کتابخانه یک کتابخانه یادگیری ماشین منبع باز در پایتون است که می تواند در هر محیط نوت بوک مورد استفاده قرار گیرد و مشکلات برنامه نویسی را به شدت کاهش می دهد و این فرآیند را بسیار کارآمد و پربار کند.اکنون مجموعه داده ها برای مدلسازی آماده شده است ، حال با استفاده از این کتابخانه مبتکرانه و کارآمد الگوریتم های مختلف را آزمایش خواهیم کرد

# In[21]:


data = pd.read_csv("Training Data.csv")


# In[22]:


from pycaret.regression import *


# افق 22 روزه را به عنوان هدف در نظر می گیریم. این بدان معناست که با توجه به داده های تاریخی ، ما سعی خواهیم کرد بازده طلا را در سه هفته آینده پیش بینی کنیم

# In[23]:


data_22= data.drop(["Gold-T+14"],axis=1)
data_22.head()


# برای شروع هرگونه تمرین مدل سازی در این کتابخانه ، اولین قدم تابع "راه اندازی" است.  تمام دگرگونی های اولیه و ضروری داده ها مانند رها کردن شناسه ها ، عوامل طبقه بندی شده و محاسبه ارزش از دست رفته به طور خودکار در پشت صحنه اتفاق می افتد.  همچنین بیش از 20 گزینه پیش پردازش را ارائه می دهد

# In[24]:


a=setup(data_22,target='Gold-T+22',
        ignore_features=['Date'],session_id=11,
        silent=True,profile=False,remove_outliers=False);


# در مرحله بعد ، یکی از ویژگی های جادویی این کتابخانه را به کار می گیریم ، که صدها خط کد را اساساً به 2 کلمه کاهش می دهد . این تابع از همه الگوریتم ها (25 الگوریتم فعلی) استفاده می کند و آنها را با داده ها مطابقت می دهد ، 10 بار اعتبار متقابل را اجرا می کند و 6 معیار ارزیابی را برای هر مدل تفسیر می کند

# In[25]:


compare_models(turbo=False)


# دو الگوریتم نزدیکترین همسایگی و درختان خیلی تصادفی (:  بهترین ضریب تشخیص را دارند ،که چیزی حدود 87% است . حال این دومدل را ایجاد می کنیم (تمرین و تست) 

# In[27]:


et = create_model('et')


# In[30]:


plot_model(et)


# In[31]:


knn = create_model('knn')


# In[32]:


tuned_knn = tune_model(knn, n_iter = 150)


# In[34]:


plot_model(tuned_knn)


# همانطور که در بالا می بینید الگوریتم نزدیکترین همسایگی پس از تیونینگ به میزان قابل توجهی(90.9%) بهبود یافت

# انجام برخی ازفرایندهای تشخیص بر روی مدلهای آموزش دیده بسیار مهم است. ما فرایند تشخیص و مشاهده مجموعه نمودارها  را در هر دو مدل برتر خود انجام می دهیم

# In[44]:


evaluate_model(et)


# In[45]:


evaluate_model(tuned_knn)


# حال با استفاده از ترکیب این دو مدل سعی می کنیم عملکرد مدل را ارتقا دهیم

# In[46]:


blend_knn_et = blend_models(estimator_list=[tuned_knn,et])


# In[47]:


plot_model(blend_knn_et)


# In[48]:


evaluate_model(blend_knn_et)


# In[49]:


save_model(model=blend_knn_et, model_name='22 Rooze Ayande')


# In[50]:


data_14= data.drop(['Gold-T+22'],axis=1)
data_14.head()


# In[51]:


c=setup(data_14,target='Gold-T+14',
        ignore_features=['Date'],session_id=11,
        silent=True,profile=False,remove_outliers=True);


# In[52]:


compare_models(turbo=False)


# In[53]:


knn = create_model('knn')
tuned_knn = tune_model(knn,n_iter=150)
et = create_model('et')
blend_knn_et = blend_models(estimator_list=[tuned_knn,et])


# In[54]:


save_model(model=blend_knn_et, model_name='14 Rooze Ayande')


# In[ ]:





# In[ ]:





# هنگامی که مدل های خود را ذخیره کردیم ، می خواهیم پیش از آنکه داده های جدید وارد شوند ، پیش بینی کنیم. ما می توانیم به بسته مالی یاهو اعتماد کنیم تا قیمت نهایی همه ابزارها را به ما ارائه دهد ، با این حال ، ما باید داده های جدید را دوباره آماده کنیم تا بتوانیم از مدل استفاده کنیم

# In[55]:


#Importing Libraries

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from yahoofinancials import YahooFinancials
ticker_details = pd.read_excel("Ticker List.xlsx")
ticker = ticker_details['Ticker'].to_list()
names = ticker_details["Description"].to_list()

#Preparing Date Range

end_date= datetime.strftime(datetime.today(),'%Y-%m-%d')
start_date = "2019-01-01"
date_range = pd.bdate_range(start=start_date,end=end_date)
values = pd.DataFrame({ 'Date': date_range})
values['Date']= pd.to_datetime(values['Date'])

#Extracting Data from Yahoo Finance and Adding them to Values table using date as key

for i in ticker:
    raw_data = YahooFinancials(i)
    raw_data = raw_data.get_historical_price_data(start_date, end_date, "daily")
    df = pd.DataFrame(raw_data[i]["prices"])[['formatted_date','adjclose']]
    df.columns = ['Date1',i]
    df['Date1']= pd.to_datetime(df['Date1'])
    values = values.merge(df,how='left',left_on='Date',right_on='Date1')
    values = values.drop(labels='Date1',axis=1)
    
#Renaming columns to represent instrument names rather than their ticker codes for ease of readability

names.insert(0,'Date')
values.columns = names

#Front filling the NaN values in the data set

values = values.fillna(method="ffill",axis=0)
values = values.fillna(method="bfill",axis=0)

# Co-ercing numeric type to all columns except Date

cols=values.columns.drop('Date')
values[cols] = values[cols].apply(pd.to_numeric,errors='coerce').round(decimals=1)
imp = ["Gold","Silver", "Crude Oil", "Copper","Dollar Index"]

# Calculating Short term -Historical Returns

change_days = [1,3,5,14,21]
data = pd.DataFrame(data=values['Date'])
for i in change_days:
    x= values[cols].pct_change(periods=i).add_suffix("-T-"+str(i))
    data=pd.concat(objs=(data,x),axis=1)
    x=[]
    
# Calculating Long term Historical Returns

change_days = [60,90,180,250]
for i in change_days:
    x= values[imp].pct_change(periods=i).add_suffix("-T-"+str(i))
    data=pd.concat(objs=(data,x),axis=1)
    x=[]
#Calculating Moving averages for Gold

moving_avg = pd.DataFrame(values['Date'],columns=['Date'])
moving_avg['Date']=pd.to_datetime(moving_avg['Date'],format='%Y-%b-%d')
moving_avg['Gold/15SMA'] = (values['Gold']/(values['Gold'].rolling(window=15).mean()))-1
moving_avg['Gold/30SMA'] = (values['Gold']/(values['Gold'].rolling(window=30).mean()))-1
moving_avg['Gold/60SMA'] = (values['Gold']/(values['Gold'].rolling(window=60).mean()))-1
moving_avg['Gold/90SMA'] = (values['Gold']/(values['Gold'].rolling(window=90).mean()))-1
moving_avg['Gold/180SMA'] = (values['Gold']/(values['Gold'].rolling(window=180).mean()))-1
moving_avg['Gold/90EMA'] = (values['Gold']/(values['Gold'].ewm(span=90,adjust=True,ignore_na=True).mean()))-1
moving_avg['Gold/180EMA'] = (values['Gold']/(values['Gold'].ewm(span=180,adjust=True,ignore_na=True).mean()))-1
moving_avg = moving_avg.dropna(axis=0)

#Merging Moving Average values to the feature space

data['Date']=pd.to_datetime(data['Date'],format='%Y-%b-%d')
data = pd.merge(left=data,right=moving_avg,how='left',on='Date')
data = data[data['Gold-T-250'].notna()]
prediction_data = data.copy()


# پس از آماده سازی داده ها ، باید مدل را بارگذاری کرده و پیش بینی کنیم.کدهای زیر مدل را بارگذاری می کند و داده های جدید را پیش بینی می کند  

# In[56]:


from pycaret.regression import *

#Loading the stored model

regressor_22 = load_model("22 Rooze Ayande");

#Making Predictions

predicted_return_22 = predict_model(regressor_22,data=prediction_data)
predicted_return_22=predicted_return_22[['Date','Label']]
predicted_return_22.columns = ['Date','Return_22']

#Adding return Predictions to Gold Values

predicted_values = values[['Date','Gold']]
predicted_values = predicted_values.tail(len(predicted_return_22))
predicted_values = pd.merge(left=predicted_values,right=predicted_return_22,on=['Date'],how='inner')
predicted_values['Gold-T+22']=(predicted_values['Gold']*(1+predicted_values['Return_22'])).round(decimals =1)

#Adding T+22 Date

from datetime import datetime, timedelta
predicted_values['Date-T+22'] = predicted_values['Date']+timedelta(days = 22)
predicted_values.tail()


# In[57]:


from pycaret.regression import *

#Loading the stored model

regressor_14 = load_model("14 Rooze Ayande");

#Making Predictions

predicted_return_14 = predict_model(regressor_14,data=prediction_data)
predicted_return_14=predicted_return_14[['Date','Label']]
predicted_return_14.columns = ['Date','Return_14']

#Adding return Predictions to Gold Values

predicted_values = values[['Date','Gold']]
predicted_values = predicted_values.tail(len(predicted_return_14))
predicted_values = pd.merge(left=predicted_values,right=predicted_return_14,on=['Date'],how='inner')
predicted_values['Gold-T+14']=(predicted_values['Gold']*(1+predicted_values['Return_14'])).round(decimals =1)

#Adding T+14 Date

from datetime import datetime, timedelta
predicted_values['Date-T+14'] = predicted_values['Date']+timedelta(days = 14)
predicted_values.tail()


# لطفاً توجه داشته باشید که بازار طلا یک بازار بسیار رقابتی است. کسب درآمد مداوم از هر استراتژی برای مدت طولانی اگر غیرممکن نباشد ، بسیار دشوار است. این مقاله فقط برای  انجام پروژه پایانی دوره کارشناسی فناوری اطلاعات است و نه ایده ای برای سرمایه گذاری یا تجارت. با این حال ، برای دانشجویانی مانند من ، این ایده را می توان توسعه داد و با تلاش های فردی به الگوریتم های تجاری تبدیل کرد

# In[ ]:




