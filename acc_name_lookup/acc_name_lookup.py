''' A script which looks up account names from account numbers and bank names or codes using the Flutterwave API. '''

# Helpful resource on bank codes: https://sandbox.interswitchng.com/docbase/docs/autogatebatchgate/appendix/bank-cbn-codes/

import os
import requests
import dotenv
import pathlib

# You need to have a .env file in the root directory with your FLW_CLIENT_ID and FLW_CLIENT_SECRET keys
base_dir = pathlib.Path(__file__).parent.parent
dotenv.load_dotenv(f'{base_dir}/keys.env')

# BASE_URL = "https://api.flutterwave.cloud/f4bexperience"
BASE_URL = "https://f4bexperience.flutterwave.com"
token_url = "https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token"
acc_lookup_url = f"{BASE_URL}/banks/account-resolve"


def get_access_token():
	headers = {
		"content-type": "application/x-www-form-urlencoded",
	}
	data = {
		"client_secret": os.getenv("FLW_CLIENT_SECRET"),
		"client_id": os.getenv("FLW_CLIENT_ID"),
		"grant_type": "client_credentials"
	}
	token_response = requests.post(token_url, headers=headers, data=data).json()
	# print(token_response)
	access_token = token_response['access_token']

	return access_token

access_token = get_access_token()

def get_bank_codes():
	
	headers = {
		"content-type": "application/json",
		"Authorization": f"BEARER {access_token}"
	}
	response_data = requests.get(f'{BASE_URL}/banks', headers=headers, params={"country": "NG"})
	# Alternatively...
	# response_data = requests.get(f'{BASE_URL}/banks?country=NG', headers=headers)
	
	bank_codes = response_data.json()['data']
	return bank_codes

def get_account_name(account_number, bank_name_or_code):
	bank_codes = get_bank_codes()
	# Just an inline function to get specific bank names from a provided bank code
	get_code_from_name = lambda name: next((bank['code'] for bank in bank_codes if bank['name'].lower().lstrip().rstrip() == name.lower()), None)
	
	bank_code = bank_name_or_code

	# If this raises a ValueError, then the argument provided is most likely a bank name.
	try: int(bank_name_or_code)
	except ValueError:
		bank_code = get_code_from_name(bank_name_or_code)

	if not bank_code:
		raise ValueError('''
Bank name not found. Try another name or perhaps check your spelling.
You could also try the following: 
	1. Try alternative names: For example, "Guaranty Trust Bank" instead of "GT Bank", or vice-versa.
	2. Use the bank CBN code instead.
''')
	

	# Okay, so we've gotten past the hurdle of getting the bank code if not supplied directly.
	# I guess we can get the account name now
	request_body = {
		"account": {
			"code": bank_code,
			"number": account_number,
		},
		"currency": "NGN"
	}
	response = requests.post(acc_lookup_url, headers={
		"content-type": "application/json",
		"accept": "application/json",
		"authorization": f"Bearer {access_token}"
	}
	, json=request_body).json()
	print(response)

	if response["status"] == "success":
		return response['data']['account_name']
	elif response["status"] == "failed":
		return response['error']['message']
	

	
print(get_account_name("2411193506", "057")) #Zenith Bank
print(get_account_name("7011477728", "Opay")) #Let's see if this works