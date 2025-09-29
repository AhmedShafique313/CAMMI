# CAMMI
Chat Agent Marketing Manager Interface

Working on Scrapping Feature on CAMMI
https://53zbaogrfrggc2flsihl2hnc240hjaku.lambda-url.ap-southeast-2.on.aws/?website=https://kavtech.net/

How to create the Linux packages of Python in windows using the docker
- `mkdir python`
- `cd path_with_folder`
- `docker run --rm -it --entrypoint /bin/sh -v "C:\Users\Kavtech AI Engineer\Desktop\foldename:/var/task" public.ecr.aws/lambda/python3.13 -c "python3.13 -m pip install --upgrade pip && python3.13 -m pip install groq -t /var/task/python"` 

Then Zip the python folder and rename it according to the your layer name which should be added to the lambda function.

How to open any WordPress Website: http://localhost:5000/register-site

application password: 8x8t Vxvm yT5S 2gw0 EUWq iWPv
application password name: cammi-testing-app

Register site: http://localhost:5000/register-site

Create post: http://localhost:5000/schedule-post

{
  "body": "{\n  \"sitename\": \"Cammi Kavtech\",\n  \"title\": \"My First Text Only Post\",\n  \"content_html\": \"<p>This is a text-only post created via AWS Lambda without an image.</p>\",\n  \"embed\": false\n}"
}


cammi-service@product-471907.iam.gserviceaccount.com

## Docker
CMD
`docker run --rm -v "%cd%:/var/task" --entrypoint /bin/bash public.ecr.aws/lambda/python:3.13 -c "pip3 install python-docx reportlab -t python/"`
Powershell
`docker run --rm -v "C:\Users\Kavtech AI Engineer\OneDrive\Desktop\New folder\lambda_layer":/var/task --entrypoint /bin/bash public.ecr.aws/lambda/python:3.13 -c "pip3 install requests cachecontrol google-auth google-auth-oauthlib -t python/"`


Updated Pricing file:
- `https://onedrive.live.com/:x:/g/personal/FFC3AB340811657C/EeMkZoeTbDdNoOwCybdVgDgBwzxspoTaLQqYSzG4R1n7OA?resid=FFC3AB340811657C!s876624e36c934d37a0ec02c9b7558038&ithint=file%2Cxlsx&wdOrigin=TEAMS-MAGLEV.p2p_ns.rwc&wdExp=TEAMS-CONTROL&wdhostclicktime=1758708250298&web=1&migratedtospo=true&redeem=aHR0cHM6Ly8xZHJ2Lm1zL3gvYy9mZmMzYWIzNDA4MTE2NTdjL0VlTWtab2VUYkRkTm9Pd0N5YmRWZ0RnQnd6eHNwb1RhTFFxWVN6RzRSMW43T0E_d2RPcmlnaW49VEVBTVMtTUFHTEVWLnAycF9ucy5yd2Mmd2RFeHA9VEVBTVMtQ09OVFJPTCZ3ZGhvc3RjbGlja3RpbWU9MTc1ODcwODI1MDI5OCZ3ZWI9MQ`


## Payment Gateway
In product catalog the product is created by code using the create_payment.py file present in the practices folder fo the Payment Gateway folder.

