#!/usr/bin/env python
# coding: utf-8

# In[33]:


import requests
import json
import datetime

vilage_weather_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst?"

service_key = "6ClTIhHLgyLqzpIO1EsI54T%2BD02t9STimsteXUUqMaqDJ17G5ylnSlE%2BJ7AsCtqWCyV2H9aOtmDpVGgRwzatoA%3D%3D"

today = datetime.datetime.today()
base_date = today.strftime("%Y%m%d") # "20200214" == 기준 날짜
base_time = "0500" # 날씨 값

nx = "68"     # 위치 청주시 서원구 사창동
ny = "107"

payload = "serviceKey=" + service_key + "&" +    "dataType=json" + "&" +    "base_date=" + base_date + "&" +    "base_time=" + base_time + "&" +    "nx=" + nx + "&" +    "ny=" + ny

# 값 요청
res = requests.get(vilage_weather_url + payload)

items = res.json().get('response').get('body').get('items').get('item')


# In[34]:


items


# In[35]:


data = dict()
data['date'] = base_date

weather_data = dict()

for item in items:
    # 기온
    if item['category'] == 'T3H':
        weather_data['tmp'] = item['fcstValue']
    
    # 기상상태
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

data['weather'] = weather_data
data['weather']
# {'code': '0', 'state': '없음', 'tmp': '9'} # 9도 / 기상 이상 없음


# In[36]:


rain_foods = "부대찌개,아구찜,해물탕,칼국수,수제비,짬뽕,우동,치킨,국밥,김치부침개,두부김치,파전".split(',')


# In[37]:


# 네이버 인증
# https://developers.naver.com/apps
# 해당 사이트에서 로그인 후 "Cliend ID"와 "Client Secret"을 얻어오세요
ncreds = {
    "client_id": "P9pgwk4i5fibPN3TWG5V",      
    "client_secret" : "P9pgwk4i5fibPN3TWG5V"
}
nheaders = {
    "X-Naver-Client-Id" : ncreds.get('client_id'),
    "X-Naver-Client-Secret" : ncreds.get('client_secret')
}


# In[38]:


# 경우 1 : 비/눈/소나기           => 비오는날 음식 3개 추천
# 경우 2 : 정상                   => 블로그 리뷰 순 맛집 추천

# weather_state
if data.get('weather').get('code') != '0':
    weather_state = '1'
else:
    weather_state = '2'


# In[61]:


import random
# random.sample(x, k=len(x)) 무작위로 리스트 섞기

foods_list = None

# 경우 1, 2
if weather_state == '1':
    foods_list = random.sample(rain_foods, k=len(rain_foods))
else:
    foods_list = ['']

foods_list
# ['쌀국수', '굴', '콩나물국밥', '마라탕', '고등어']


# In[62]:


food_list = ['쌀국수', '굴', '콩나물국밥', '마라탕', '고등어']


# In[63]:


import urllib
# urllib.parse.quote(query) URL에서 검색어를 인코딩하기 위한 라이브러리

# 네이버 지역 검색 주소
naver_local_url = "https://openapi.naver.com/v1/search/local.json?"

# 검색에 사용될 파라미터
# 정렬 sort : 리뷰순(comment)
# 검색어 query : 인코딩된 문자열
params_format = "sort=comment&query="

# 위치는 사용자가 사용할 지역으로 변경가능
location = "청주"

# 추천된 맛집을 담을 리스트
recommands = []
for food in foods_list:
    # 검색어 지정
    query = location + " " + food + " 맛집"
    enc_query = urllib.parse.quote(query)
    params = params_format + enc_query
    
    # 검색
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
    elif result_list:
        recommands.append(result_list[0])
        # 3개를 찾았다면 검색 중단
        if len(recommands) >= 3:
            break
            
recommands


# In[54]:


url = "https://kauth.kakao.com/oauth/token"

data = {
    "grant_type" : "authorization_code",
    "client_id" : "839749e32911063e0a8f51fce3c9a2bf",
    "redirect_uri" : "https://localhost.com",
    "code"         : "Leh34YC5o7MX2dxGNVQT6MFNKZkuXnkpMuVRlVVremyPnZXtkIg4i7JYtHMww_rDhkdWkwopcJ8AAAFyhJJZKQ"
    
}
response = requests.post(url, data=data)

tokens = response.json()

print(tokens)


# In[14]:


with open("kakao_token.json", "w") as fp:
    json.dump(tokens, fp)


# In[ ]:


url = "https://kauth.kakao.com/oauth/token"
data = {
    "grant_type" : "refresh_token",
    "client_id"  : "c41274663b2adca6f0866cb814c0163a",
    "refresh_token" : "LR2JqA6PXecQJK2VBnU8sC9evim2W5jnoK3dSwo9dNsAAAFyhJLrig"
}
response = requests.post(url, data=data)

print(response.json())


# In[52]:


# 카카오톡 인증
# https://developers.kakao.com/docs/restapi/tool
# 해당 사이트에서 로그인 후 'Access token'을 얻어오세요
kcreds = {
    "access_token" : "L1Gqs-jvNg8rot3l7Iyoc9Dicky9TSlCSjF4AAo9dNsAAAFyhJLrjA"
}
kheaders = {
    "Authorization": "Bearer " + kcreds.get('access_token')
}


# In[53]:


import json

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
res = requests.post(kakaotalk_template_url, data=payload, headers=kheaders)

if res.json().get('result_code') == 0:
    print('메시지를 성공적으로 보냈습니다.')
else:
    print('메시지를 성공적으로 보내지 못했습니다. 오류메시지 : ' + str(res.json()))


# In[ ]:


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
    else:
        image_url = "https://freesvg.org/img/bentolunch.png?w=150&h=150&fit=fill"

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

