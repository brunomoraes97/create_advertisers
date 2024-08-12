import requests
import csv

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
    }
CSV_FILE = "./advertisers.csv"

class Advertiser:
    def __init__(self,
                 address,
                 confirm_password,
                 password,
                 country,
                 description,
                 email,
                 first_name,
                 last_name,
                 name,
                 phone,
                 skype,
                 telegram,
                 brand_id=None,
                 integration_id=None,
                 provider_id=None,
                 reference=None,
                 settings=None,
                 status=1,
                 system_role="0",
                 archived="0"):
        self.address = address
        self.confirm_password = confirm_password
        self.password = password
        self.country = country
        self.description = description
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.name = name
        self.phone = phone
        self.skype = skype
        self.telegram = telegram
        self.brand_id = brand_id
        self.integration_id = integration_id
        self.provider_id = provider_id
        self.reference = reference
        self.settings = settings
        self.status = status
        self.system_role = system_role
        self.archived = archived

    def __repr__(self):
        return (f"Advertiser(name={self.name}, brand_id={self.brand_id}, "
                f"first_name={self.first_name}, last_name={self.last_name}, "
                f"email={self.email}, system_role={self.system_role}, "
                f"reference={self.reference}, country={self.country}, "
                f"address={self.address}, phone={self.phone}, skype={self.skype}, "
                f"telegram={self.telegram}, description={self.description}, "
                f"status={self.status}, archived={self.archived})")
    
    def create_advertisers(self, session):
        HEADERS.update(
            {"Authorization": f"Bearer {session.main_token}"}
        )
        url = f"https://{session.crm}/backend/api/v1/crm/action/process"
        body = {
        "action": "Advertiser\\Insert",
        "repository": "Eloquent\\AdvertiserRepository",
        "arguments": {
            "integration_id": self.integration_id,
            "provider_id": self.provider_id,
            "name": self.name,
            "brand_id": self.brand_id,
            "first_name": self.first_name,
            "last_name": self.first_name,
            "email": self.email,
            "system_role": self.system_role,
            "reference": self.reference,
            "country": self.country,
            "address": self.address,
            "phone": self.phone,
            "skype": self.skype,
            "telegram": self.telegram,
            "description": self.description,
            "status": self.status,
            "archived": self.archived,
            "password": self.password,
            "confirm_password": self.confirm_password,
            "settings": self.settings
        }
    }
        response = requests.post(url=url,
                     headers=HEADERS,
                     json=body)
        return response
             
class Session:

    def __init__(
            self,
            crm,
            username,
            password):
        
        self.crm = crm
        self.username = username
        self.password = password

    def get_login_token(self, token="null"):
    
        url = "https://id.irev.com/master/backend/api/wizard/v1/login"
        body = {
        "login": self.username,
        "password": self.password,
        "token_2fa": token,
        "redirect":f"https:%2F%2F{self.crm}%2Fpt%2Fauth%2Fsignin"
    }
        response = requests.post(url=url,
                                headers=HEADERS,
                                json=body).json()
        try:
            if response['error']['otp'] == "telegram":
                otp_code = input("What is the OTP code? ")
                body.update({
                    "token_2fa": otp_code
                })
                response = requests.post(url=url,
                                    headers=HEADERS,
                                    json=body).json()
        except KeyError:
            pass

        self.login_token = response['data']['access_token']
        return self.login_token
    
    def start_session(self):
        self.get_login_token()
        url = f"https://{self.crm}/backend/api/v1/crm/sign/callback"
        HEADERS.update({
            "Authorization": f"Bearer {self.login_token}"
        })
        response = requests.post(url=url,headers=HEADERS).json()
        self.main_token = response['data']['token']
        return self

def create_session() -> Session:
    crm = input("What is the CRM? ")
    if "https://" in crm:
        crm = crm.split("https://")[1]
        if "/" in crm:
            crm = crm.split("/")[0]

    username = input("What is your email address? ")
    password = input("What is your password? ")

    session = Session(crm,username,password)
    return session

def instantiate_advertisers(CSV_FILE):

    advertisers_list = []
    advertiser_objects = []

    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                advertisers_list.append(dict(row))
    except IOError as e:
        print(f"I/O error: {e}")

    for adv in advertisers_list:
        advertiser = Advertiser(
            address=adv['address'],
            confirm_password=adv['confirm_password'],
            password=adv['password'],
            country=adv['country'],
            description=adv['description'],
            email=adv['email'],
            first_name=adv['first_name'],
            last_name=adv['last_name'],
            name=adv['name'],
            phone=adv['phone'],
            skype=adv['skype'],
            telegram=adv['telegram']
        )
        advertiser_objects.append(advertiser)
    return advertiser_objects


def main():
    session = create_session().start_session()
    advertisers = instantiate_advertisers(CSV_FILE)
    for advertiser in advertisers:
        advertiser.create_advertisers(session)
    
if __name__ == "__main__":
    main()
