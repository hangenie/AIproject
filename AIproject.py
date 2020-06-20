#!/usr/bin/env python
# coding: utf-8

# # 공공 데이터 포털로부터 날씨 정보 가져오기

# In[1]:


import requests
import json
import datetime

vilage_weather_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst?"

# 공공 데이터 포털에서 발급받은 인증키
service_key = "6ClTIhHLgyLqzpIO1EsI54T%2BD02t9STimsteXUUqMaqDJ17G5ylnSlE%2BJ7AsCtqWCyV2H9aOtmDpVGgRwzatoA%3D%3D"

today = datetime.datetime.today()
base_date = today.strftime("%Y%m%d") # 현재 날짜의 날씨를 받아오기 위한 변수 설정
base_time = "0500" # 5시에 발표된 자료를 받아오기 위한 변수 설정

nx = "68" # 예보 지점의 위치(x, y) 설정, 청주시 서원구 사창동
ny = "107"

payload = "serviceKey=" + service_key + "&" +    "dataType=json" + "&" +    "base_date=" + base_date + "&" +    "base_time=" + base_time + "&" +    "nx=" + nx + "&" +    "ny=" + ny

# 자료를 요청하기 위해 JSON 형식으로 요청
res = requests.get(vilage_weather_url + payload)

items = res.json().get('response').get('body').get('items').get('item')


# In[2]:


# 요청에 의해 반환된 값
items

# fcstTime : 예보 시각
# category : 예보 구분 코드
#            PTY - 강수형태, T3H - 3시간 기온
# fcstValue : 예보 값


# In[3]:


# 자료의 여러 category 중 T3H, PTY 값만 따로 저장
# 값을 저장하기 위해 dictionary 형태의 data 변수 선언
data = dict()
data['date'] = base_date

weather_data = dict()

for item in items:
    # 기온 category 해당하는 값을 저장
    if item['category'] == 'T3H':
        weather_data['tmp'] = item['fcstValue']
    
    # 강수 형태 에 해당하는 값을 저장
    if item['category'] == 'PTY':
        
        weather_code = item['fcstValue']
        
        if weather_code == '1':
            weather_state = '비'
        elif weather_code == '2':
            weather_state = '비/눈'
        elif weather_code == '3':
            weather_state = '눈'
        elif weather_code == '4':
            weather_state = '소나기'
        else:
            weather_state = '없음'
        
        weather_data['code'] = weather_code
        weather_data['state'] = weather_state

# category 별로 구분한 weather_data를 data 변수에 저장
data['weather'] = weather_data
data['weather']


# # 날씨에 따른 음식 데이터 저장

# In[4]:


# 비 오는 날 추천 음식을 저장하는 변수 선언
rain_foods = "부대찌개,아구찜,해물탕,칼국수,수제비,짬뽕,우동,치킨,국밥,김치부침개,두부김치,파전".split(',')


# # 네이버 검색 API를 통해 음식점 검색
# # 인증, 음식리스트 저장, 맛집 검색

# In[5]:


# 네이버 인증
# https://developers.naver.com/apps
# 해당 사이트에서 로그인 후 얻어 온 "Cliend ID"와 "Client Secret"을 저장
ncreds = {
    "client_id": "P9pgwk4i5fibPN3TWG5V",      
    "client_secret" : "Ul2LM3vZtt"
}
nheaders = {
    "X-Naver-Client-Id" : ncreds.get('client_id'),
    "X-Naver-Client-Secret" : ncreds.get('client_secret')
}


# In[6]:


# 경우 1 : 비/눈/소나기           => 비 오는 날 음식 3개 추천
# 경우 2 : 정상                   => 블로그 리뷰 순 맛집 추천

# 저장한 data에서 weather_code 값이 0이 아니면 경우 1
if data.get('weather').get('code') != '0':
    weather_state = '1'
else:  # weather_code 값이 0이면 경우 2
    weather_state = '2'


# In[7]:


import random
# random.sample(x, k=len(x)) 함수를 사용하여 무작위로 리스트 섞기

foods_list = None

# 경우 1이면 비 오는 날 음식 리스트를 무작위로 섞기
if weather_state == '1':
    foods_list = random.sample(rain_foods, k=len(rain_foods))
else:  # 경우 2
    foods_list = ['']

foods_list


# In[8]:


import urllib
# urllib.parse.quote(query) URL에서 검색어를 인코딩하기 위한 라이브러리
import json

# 네이버 지역 검색 주소
naver_local_url = "https://openapi.naver.com/v1/search/local.json?"

# 검색에 필요한 요청 변수
# 정렬 sort - comment (카페/블로그 리뷰 개수 순)
# 검색어 query : 검색을 원하는 문자열, UTF-8로 인코딩된 문자열
params_format = "sort=comment&query="

# 청주 지역으로 위치 설정
location = "청주"

# 추천된 맛집을 담을 리스트
recommands = []
for food in foods_list:
    # 검색어 지정
    query = location + " " + food + " 맛집"
    enc_query = urllib.parse.quote(query) # 검색어 문자열 인코딩
    params = params_format + enc_query
    
    # 검색 요청
    # headers : 네이버 인증 정보
    res = requests.get(naver_local_url + params, headers=nheaders)
    
    # 맛집 검색 결과
    result_list = res.json().get('items')

    # 경우 2 처리
    # 맛집 검색 결과에서 가장 상위 3개를 가져옴
    if weather_state == '2':
        for i in range(0,3):
            recommands.append(result_list[i])
        break
    
    # 경우 1 처리
    # 해당 음식 검색 결과에서 가장 상위를 가져옴
    elif len(result_list) > 0:
        recommands.append(result_list[0])
        
        # 3개를 찾았다면 검색 중단
        if len(recommands) >= 3:
            break
            
recommands


# # 카카오톡 메시지 전송

# # 카카오톡 API Access Token

# In[9]:


# 카카오 서버에 요청하여 받은 인증 코드
app_key = "839749e32911063e0a8f51fce3c9a2bf" # 앱 생성 시 발급 받은 REST API 키
code = "0qNn3MNy5dsIsBy8N0OXysVob9tm_kYBd5vMjvrSr-2k4aSs7LrMs1wp0d_ICYkgSL931AopcSEAAAFyrOxa7w"


# In[10]:


# 인증 코드를 이용하여 카카오 서버에 Access Token 요청
url = "https://kauth.kakao.com/oauth/token"

data2 = {
    "grant_type" : "authorization_code",
    "client_id" : app_key, 
    "redirect_uri" : "https://localhost.com",
    "code"         : code
    
}
response = requests.post(url, data=data2)

tokens = response.json()

print(tokens)


# In[11]:


# 받은 Access Token은 유효기간이 6시간이므로
# 일정 기간 동안 다시 인증 절차를 거치지 않고도 액세스 토큰을 발급 받을 수 있게 하는
# Refresh Token 요청
url = "https://kauth.kakao.com/oauth/token"
data3 = {
    "grant_type" : "refresh_token",
    "client_id"  : app_key,
    "refresh_token" : "LR2JqA6PXecQJK2VBnU8sC9evim2W5jnoK3dSwo9dNsAAAFyhJLrig"
}
response = requests.post(url, data=data3)
tokens = response.json()

print(tokens)


# In[12]:


# kakao_token.json 파일을 생성하여 받은 토큰 저장하기
with open("kakao_token.json", "w") as fp:
    json.dump(tokens, fp)


# In[13]:


# kakao_token.json 파일로 부터 저장한 토큰 불러오기
with open("kakao_token.json", "r") as fp:
    tokens = json.load(fp)


# In[14]:


tokens


# # 카카오톡 인증

# In[15]:


# 카카오톡 인증
# https://developers.kakao.com/docs/restapi/tool
# 받은 'Access token'을 저장
kcreds = {
    "access_token" : tokens['access_token']
}
kheaders = {
    "Authorization": "Bearer " + kcreds.get('access_token')
}


# # 날씨 정보 카카오톡으로 전송

# In[16]:


import json
import requests

# 카카오톡 URL 주소
kakaotalk_template_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

# 날씨 상세 정보 URL
weather_url = "https://search.naver.com/search.naver?sm=top_hty&fbm=0&ie=utf8&query=%EB%82%A0%EC%94%A8"

# 날씨 정보 만들기 
text = f"""#날씨 정보 ({data['date']}) 
기온 : {data['weather']['tmp']} 
기우  : {data['weather']['state']} 
"""

# 텍스트 템플릿 형식 만들기
template = {
  "object_type": "text",
  "text": text,
  "link": {
    "web_url": weather_url,
    "mobile_web_url": weather_url
  },
  "button_title": "날씨 상세보기"
}

# JSON 형식 -> 문자열 변환
payload = {
    "template_object" : json.dumps(template)
}

# 카카오톡 보내기
res = requests.request("POST", kakaotalk_template_url, data =payload, headers=kheaders)

if res.json().get('result_code') == 0:
    print('메시지를 성공적으로 보냈습니다.')
else:
    print('메시지를 성공적으로 보내지 못했습니다. 오류메시지 : ' + str(res.json()))


# # 추천 맛집 카카오톡으로 전송

# In[17]:


# 리스트 템플릿 형식 만들기
contents = []
template = {
    "object_type" : "list",
    "header_title" : "현재 날씨에 따른 음식 추천",
    "header_link" : {
        "web_url": weather_url,
        "mobile_web_url" : weather_url
    },
    "contents" : contents,
    "buttons" : [
        {
            "title" : "날씨 정보 상세보기",
            "link" : {
                "web_url": weather_url,
                "mobile_web_url" : weather_url
            }
        }
    ],
}

# contents 만들기
for place in recommands:
    title = place.get('title')  # 장소 이름
    # title : 태극쿵푸<b>마라탕</b>
    # html 태그 제거
    title = title.replace('<b>','').replace('</b>','')
    
    category = place.get('category')  # 장소 카테고리
    telephone = place.get('telephone')  # 장소 전화번호
    address = place.get('address')  # 장소 지번 주소

    # 각 장소를 클릭할 때 네이버 검색으로 연결해주기 위해 작성된 코드
    enc_address = urllib.parse.quote(address + ' ' + title)
    query = "query=" + enc_address

    # 장소 카테고리가 카페이면 카페 이미지
    # 이외에는 음식 이미지
    if '카페' in category:
        image_url = "https://freesvg.org/img/pitr_Coffee_cup_icon.png"
    elif '치킨' in category:
        image_url = "http://www.momstouch.co.kr/data/shopimages/xboard/menu/20170622893503.jpg"
    elif '전' in category:
        image_url = "http://www.sk5.co.kr/img_src/s600/a918/a9180025.jpg"
    elif '부침' in category:
        image_url = "http://www.sk5.co.kr/img_src/s600/a918/a9180025.jpg"
    elif '칼국수' in category:
        image_url = "http://www.sk5.co.kr/img_src/s600/1209/12091443.jpg"
    elif '찜' in category:
        image_url = "https://t1.daumcdn.net/cfile/tistory/26590D3C577B13FB30"
    elif '부대찌개' in category:
        image_url = "https://t1.daumcdn.net/cfile/tistory/235B103C577B13FB2F"
    elif '일식' in category:
        image_url = "http://www.simbata.co.kr/img_src/s600/1227/12273259.jpg"
    elif '고기' in category:
        image_url = "https://t1.daumcdn.net/liveboard/dailylife/8f41a57e8e0f4ce7878ffad0eda9e5bc.JPG"    
    else:
        image_url = "https://pgnqdrjultom1827145.cdn.ntruss.com/img/0e/fe/0efeb7320298d35eb99b02e2af0cc0a6cdb87174cfd2f85e36f501a87efd6448_v1.jpg"
        

    # 전화번호가 있다면 제목과 함께 넣어줍니다.
    if telephone:
        title = title + "\ntel) " + telephone

    # 카카오톡 리스트 템플릿 형식에 맞춰줍니다.
    content = {
        "title": "[" + category + "] " + title,
        "description": ' '.join(address.split()[1:]),
        "image_url": image_url,
        "image_width": 50, "image_height": 50,
        "link": {
            "web_url": "https://search.naver.com/search.naver?" + query,
            "mobile_web_url": "https://search.naver.com/search.naver?" + query
        }
    }
    
    contents.append(content)

# JSON 형식 -> 문자열 변환
payload = {
    "template_object" : json.dumps(template)
}

# 카카오톡 보내기
res = requests.post(kakaotalk_template_url, data=payload, headers=kheaders)

if res.json().get('result_code') == 0:
    print('메시지를 성공적으로 보냈습니다.')
else:
    print('메시지를 성공적으로 보내지 못했습니다. 오류메시지 : ' + str(res.json()))


# # 맛집 위치를 카카오맵을 통해 카카오톡으로 전송

# In[18]:


naver_search_url = "https://search.naver.com/search.naver?"

# 위치 템플릿 형식 만들기

# contents 만들기
for place in recommands:
    title = place.get('title')  # 장소 이름
    # title : 태극쿵푸<b>마라탕</b>
    # html 태그 제거
    title = title.replace('<b>','').replace('</b>','')
    
    category = place.get('category')  # 장소 카테고리
    telephone = place.get('telephone')  # 장소 전화번호
    address = place.get('address')  # 장소 지번 주소

    # 각 장소를 클릭할 때 카카오맵으로 연결해주기 위해 작성된 코드
    enc_address = urllib.parse.quote(address)
    query = "query=" + enc_address

    # 장소 카테고리가 카페이면 카페 이미지
    # 이외에는 음식 이미지
    if '카페' in category:
        image_url = "https://freesvg.org/img/pitr_Coffee_cup_icon.png"
    elif '치킨' in category:
        image_url = "http://www.momstouch.co.kr/data/shopimages/xboard/menu/20170622893503.jpg"
    elif '전' in category:
        image_url = "http://www.sk5.co.kr/img_src/s600/a918/a9180025.jpg"
    elif '부침' in category:
        image_url = "http://www.sk5.co.kr/img_src/s600/a918/a9180025.jpg"
    elif '칼국수' in category:
        image_url = "http://www.sk5.co.kr/img_src/s600/1209/12091443.jpg"
    elif '찜' in category:
        image_url = "https://t1.daumcdn.net/cfile/tistory/26590D3C577B13FB30"
    elif '부대찌개' in category:
        image_url = "https://t1.daumcdn.net/cfile/tistory/235B103C577B13FB2F"
    elif '일식' in category:
        image_url = "http://www.simbata.co.kr/img_src/s600/1227/12273259.jpg"
    elif '고기' in category:
        image_url = "https://t1.daumcdn.net/liveboard/dailylife/8f41a57e8e0f4ce7878ffad0eda9e5bc.JPG"    
    else:
        image_url = "https://pgnqdrjultom1827145.cdn.ntruss.com/img/0e/fe/0efeb7320298d35eb99b02e2af0cc0a6cdb87174cfd2f85e36f501a87efd6448_v1.jpg"
    
    # 전화번호가 있다면 제목과 함께 넣어줍니다.
    if telephone:
        category = category + "\ntel) " + telephone

    # 카카오톡 리스트 템플릿 형식에 맞춰줍니다.
    content = {
        "title": title,
        "description": category,
        "image_url": image_url,
        "image_width": 50, "image_height": 50,
        "link": {
            "web_url": naver_search_url + query,
            "mobile_web_url": naver_search_url + query
        }
    }
    
    template = {
        "object_type" : "location",
        "address" : address,
        "address_title" : title,
        "content" : content
    }   

    # JSON 형식 -> 문자열 변환
    payload = {
        "template_object" : json.dumps(template)
    }

    # 카카오톡 보내기
    res = requests.post(kakaotalk_template_url, data=payload, headers=kheaders)

    if res.json().get('result_code') == 0:
        print('메시지를 성공적으로 보냈습니다.')
    else:
        print('메시지를 성공적으로 보내지 못했습니다. 오류메시지 : ' + str(res.json()))


# In[ ]:




