from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json,random,string,requests,sys,os,time,traceback,urllib

ua = UserAgent(verify_ssl=False)

def getCompanyFromName(company,JSESSIONID,li_at):

    cookies = {'JSESSIONID':JSESSIONID}
    cookies['li_at'] =  li_at
    headers = {'Csrf-Token': JSESSIONID,
               'User-Agent': ua.firefox}

    params = (
        ('keywords', company),
        ('origin', 'GLOBAL_SEARCH_HEADER'),
        ('q', 'blended'),
    )

    response = requests.get('https://www.linkedin.com/voyager/api/typeahead/hitsV2', headers=headers, params=params, cookies=cookies)
    result=[]
    for i in response.json()["elements"]:
        if i["type"]=="COMPANY":
            if "miniCompany" in i["image"]["attributes"][0].keys():
                if i["image"]["attributes"][0]["miniCompany"]["logo"]==None:
                    logo=""
                else:
                    logo=i["image"]["attributes"][0]["miniCompany"]["logo"]["com.linkedin.common.VectorImage"]["rootUrl"]+i["image"]["attributes"][0]["miniCompany"]["logo"]["com.linkedin.common.VectorImage"]["artifacts"][0]["fileIdentifyingUrlPathSegment"]
                result.append({"name":i["image"]["attributes"][0]["miniCompany"]["name"],"urlCompany":"https://www.linkedin.com/company/"+i["image"]["attributes"][0]["miniCompany"]["universalName"],"logo":logo})
    return(result)
def getProfileFromName(search_string,JSESSIONID,li_at,pages_to_scrape=5,results_per_page=20):
    search_results = []


    cookies = {'JSESSIONID':JSESSIONID}
    cookies['li_at'] =  li_at
    headers = {'Csrf-Token': JSESSIONID,
               'User-Agent': ua.firefox}

    search_url = "https://www.linkedin.com/voyager/api/search/cluster?" \
                   "count=%i&guides=List(v-%%3EPEOPLE,facetGeoRegion-%%3Ear" \
                   "%%3A0)&keywords=%s&origin=FACETED_SEARCH&q=guided&start=0"

    page_url = "https://www.linkedin.com/voyager/api/search/cluster?" \
               "count=%i&guides=List(v-%%3EPEOPLE,facetGeoRegion-%%3Ear" \
               "%%3A0)&keywords=%s&origin=FACETED_SEARCH&q=guided&start=%i"


    url = search_url % (results_per_page,
                        search_string)
    try:
        r = requests.get(url, cookies=cookies, headers=headers)
    except Exception:
        exit()
    try:
        content = json.loads(r.text)
    except:
        return(r.text)

    data_total = content['paging']['total']

    pages = data_total / results_per_page
    if data_total % results_per_page == 0:
        pages = pages - 1
    if pages == 0:
        pages = 1

    if data_total > 1000:
        pages = pages_to_scrape

    pages=int(pages)+1
    for p in range(pages):
        # Request results for each page using the start offset

        url = page_url % (results_per_page,
                          search_string,
                          p*results_per_page)

        r = requests.get(url, cookies=cookies, headers=headers)

        content = r.text.encode('UTF-8')
        content = json.loads(content.decode("utf-8"))

        #print"Fetching page %i (contains %i results)" %
              #(p+1, len(content['elements'][0]['elements'])))

        profiles_skipped = False
        for c in content['elements'][0]['elements']:
            try:
                # Using these lookup strings to shorten query lines below
                lookup = 'com.linkedin.voyager.search.SearchProfile'
                h = 'hitInfo'
                m = 'miniProfile'

                # Doesn't work anymore
                pic_url = "https://media.licdn.com/mpr/mpr/shrinknp_400_400"+"%s"
                pic_query = "com.linkedin.voyager.common.MediaProcessorImage"

                if not c[h][lookup]['headless']:
                    try:
                        data_industry = c[h][lookup]['industry']
                    except Exception:
                        data_industry = ""

                    data_firstname = c[h][lookup][m]['firstName']
                    data_lastname = c[h][lookup][m]['lastName']
                    data_url = "https://www.linkedin.com/in/%s" % \
                               c[h][lookup][m]['publicIdentifier']
                    data_occupation = c[h][lookup][m]['occupation']
                    data_location = c[h][lookup]['location']
                    # This section doesn't work
                    try:
                        data_picture = c[h][lookup][m]["picture"]["com.linkedin.common.VectorImage"]["rootUrl"]+c[h][lookup][m]["picture"]["com.linkedin.common.VectorImage"]["artifacts"][0]["fileIdentifyingUrlPathSegment"]
                    except Exception:
                        # No pic found for (data_firstn, data_lastn, d_occ)
                        data_picture = ""
                    search_results.append({"firstname":data_firstname,"lastname":data_lastname,"occupation":data_occupation,"profile-url":data_url,"location":data_location,"industry":data_industry,"picture-url":data_picture})
                else:
                    pass
            except Exception:
                profiles_skipped = True
                continue
        if profiles_skipped:
            pass
    return(search_results)
def getCompanyFromProfile(profile_url,JSESSIONID,li_at):
    def scraping_dict():
        items = {
            "fs_course": ["name"],

            "fs_education":
                ['schoolName', 'description', 'degreeName', 'activities', 'grade',
                 'fieldOfStudy', 'projects', 'entityLocale', 'recommendations'],

            "fs_honor": ['title', 'description', 'issuer'],

            "fs_language": ['name'],

            "fs_position":
                ['companyName', 'description', 'title', {"company": "industries"},
                 'courses', 'locationName', 'projects', 'entityLocale',
                 'organizations', 'region', 'recommendations', 'honors',
                 'promotion'],

            "fs_profile": ["headline", "summary", "industryName", "locationName"],

            "fs_project": ['title', 'occupation', 'description'],

            "fs_publication": ['name', 'publisher', 'description'],

            "fs_skill": ["name"]
        }

        return items


    cookies = {'JSESSIONID':JSESSIONID}
    cookies['li_at'] = li_at
    headers = {'Csrf-Token': JSESSIONID,
               'User-Agent': ua.firefox}

    fields_to_scrape = scraping_dict().keys()
    empty_dict = dict.fromkeys(fields_to_scrape, None)

    data_dict = {}
    try:
        r = requests.get(profile_url, cookies=cookies, headers=headers)
    except Exception:
        print(traceback.format_exc())
        exit()


    soup = BeautifulSoup(r.text, "html.parser")
    found = soup.find(
        lambda tag: tag.name == "code" and "*profile" in tag.text)
    extract = found.contents[0].strip()

    data = json.loads(extract)
    results=[]
    for i in data["included"]:
        if "url" in i.keys() and i["url"]!=None:
            if "https://www.linkedin.com/company/" in i["url"]:

                if i["logo"]!=None:
                    logo=str(i["logo"]["vectorImage"]["rootUrl"]+i["logo"]["vectorImage"]["artifacts"][0]["fileIdentifyingUrlPathSegment"])
                else:
                    logo=""
                results.append({"name":i["name"].replace('Ã©','é'),"linkedin_url":i["url"],"logo":logo})

    return(results)
def getAllEmployees(company,JSESSIONID,li_at):

    headers={'Accept-Language': 'en,en-US;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive', 'Accept': 'application/vnd.linkedin.normalized+json+2.1',
    'User-Agent': ua.firefox,
    'csrf-token': JSESSIONID, 'Host': 'www.linkedin.com',
    'TE': 'Trailers',
    'x-restli-protocol-version': '2.0.0'}

    cookies = {'JSESSIONID':JSESSIONID}
    cookies['li_at'] = li_at
    result = []
    params = (
    ('companyIdOrUniversalName', company),
    ('count', '3'),
    ('moduleKey', 'ORGANIZATION_MEMBER_FEED_DESKTOP'),
    ('numComments', '0'),
    ('numLikes', '0'),
    ('q', 'companyRelevanceFeed'),
    )
    response = requests.get('https://www.linkedin.com/voyager/api/organization/updatesV2', headers=headers, params=params, cookies=cookies)
    idcompany=response.text.split("urn:li:company:")[1].split('"')[0]
    response = requests.get('https://www.linkedin.com/voyager/api/search/hits?count=49&educationEndYear=List()&educationStartYear=List()&facetCurrentCompany=List('+idcompany+')&facetCurrentFunction=List()&facetFieldOfStudy=List()&facetGeoRegion=List()&facetNetwork=List()&facetSchool=List()&facetSkillExplicit=List()&keywords=List()&maxFacetValues=49&origin=organization&q=people&start=0&supportedFacets=List(GEO_REGION,SCHOOL,CURRENT_COMPANY,CURRENT_FUNCTION,FIELD_OF_STUDY,SKILL_EXPLICIT,NETWORK)',headers=headers,cookies=cookies)
    max=int(response.json()["data"]["metadata"]["totalResultCount"])-49
    result.append(response.json()["included"])
    c=0
    while max >0:
        c+=49
        response = requests.get('https://www.linkedin.com/voyager/api/search/hits?count=49&educationEndYear=List()&educationStartYear=List()&facetCurrentCompany=List('+idcompany+')&facetCurrentFunction=List()&facetFieldOfStudy=List()&facetGeoRegion=List()&facetNetwork=List()&facetSchool=List()&facetSkillExplicit=List()&keywords=List()&maxFacetValues=49&origin=organization&q=people&start='+str(c)+'&supportedFacets=List(GEO_REGION,SCHOOL,CURRENT_COMPANY,CURRENT_FUNCTION,FIELD_OF_STUDY,SKILL_EXPLICIT,NETWORK)',headers=headers,cookies=cookies)
        max=max-49
        result.append(response.json()["included"])
    results=[]
    for profile in result:
        for pro in profile:
            if "occupation" in pro.keys():
                name = pro["firstName"] + " " + pro["lastName"]
                if name == " ":
                    pro["firstName"]="Linkedin"
                    pro["lastName"]="User"
                if pro["picture"]==None:
                    propicture=""
                else:
                    propicture=pro["picture"]["rootUrl"]+pro["picture"]["artifacts"][2]["fileIdentifyingUrlPathSegment"]
                results.append({"firstname":pro["firstName"],"lastname":pro["lastName"],'occupation':pro["occupation"],"profile-url":"https://www.linkedin.com/in/"+str(pro["publicIdentifier"]),"picture-url":propicture})
    return(results)
def GetContactInformations(profile_url,JSESSIONID,li_at):
    profile_url=profile_url+"/detail/contact-info/"

    headers = {
        'authority': 'www.linkedin.com',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': ua.firefox,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9,fr;q=0.8,fr-FR;q=0.7',
        'cookie': 'JSESSIONID="'+JSESSIONID+'";li_at='+li_at+';',
    }



    try:
        r = requests.get(profile_url, headers=headers)
    except Exception:
        print(traceback.format_exc())
        exit()


    soup = BeautifulSoup(r.text, "html.parser")
    data =json.loads('{"data":{"birthDateOn"'+str(soup).split('"data":{"birthDateOn"')[1].split('},"included":[')[0]+'}}')
    months = {"1":"January",
              "2":"Febuary",
              "3":"March",
              "4":"April",
              "5":"May",
              "6":"June",
              "7":"July",
              "8":"August",
              "9":"September",
              "10":"October",
              "11":"November",
              "12":"December"}
    data=data["data"]
    if data['birthDateOn']!=None:
        birthDate=str(data['birthDateOn']["day"])+" "+months[str(data['birthDateOn']["month"])]
    else:
        birthDate=None
    twittersAccount=[]
    if data["twitterHandles"]!=None:
        for twitter in data["twitterHandles"]:
            twittersAccount.append(twitter["name"])

    emailAddress=data["emailAddress"]
    address=data["address"]
    websites=[]
    if data["websites"]!=None:
        for website in data["websites"]:
            websites.append(website["url"])
    phoneNumbers=[]
    if data["phoneNumbers"]!=None:
        for phoneNumber in data["phoneNumbers"]:
            phoneNumbers.append(phoneNumber["number"])
    return({"birthDate":birthDate,"twittersAccount":twittersAccount,"emailAddress":emailAddress,"address":address,"websites":websites,"phoneNumbers":phoneNumbers})
