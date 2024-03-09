# bitespeed-submission

API submission for bitespeed
Access apis using /docs or curl

## App Hosted on Render

https://bitespeed-identify-api.onrender.com

## Test with Swagger using

https://bitespeed-identify-api.onrender.com/docs

## OR

## Using CURL

```bash
curl -X POST -H "Content-Type: application/json" -d '{"email": "xyz@xyz.com", "phoneNumber": "123456789"}' https://bitespeed-identify-api.onrender.com/identify
```

## Install Dependencies and Run

### Create Virtual Enviornment (Optional)

```bash
python -m venv venv
```

### Activate Virtual Enviornemnt
#### For Linux
```bash
source venv/bin/activate
```
#### For Windows
```bash
venv/Scripts/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start App

```bash
uvicorn main:app --reload
```
