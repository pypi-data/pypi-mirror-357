# CloudHands SDK

CloudHands SDK is a Python library for interacting with the CloudHands API. It provides tools for authentication, charging events, and retrieving transaction details.

## Installation

```bash
pip install cloudhands
```

## Usage

```python
# CloudHands is your more general interface with cloudhands.ai and its apis
ch = CloudHands(api_key=YOUR_API_KEY)
ch.text_post(title="Posting Sample Usage", content="This shows how you can use the SDK to make a post on cloudhands.ai")

# CloudHandsPayment is used for dealing with a particular transaction/auth flow for a user to pay you
chPay = CloudHandsPayment(author_key=YOUR_AUTHOR_KEY)
auth_url = chPay.get_authorization_url()
# you must give this auth url to the user you want to pay you
# they will visit and be prompted to confirm the auth, then will be given a code to return to you with
chPay.exchange_code_for_token(code)
# Now authenticated, can charge cloudhands credits for the user
result = chPay.charge(charge=1.0, event_name="Sample cloudhands charge")
```

## Publish on pypi
pip install setuptools wheel twine
rm -rf src/cloudhands.egg-info/ dist
python -m build
twine upload dist/*
