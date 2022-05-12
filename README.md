# car_scraper

![alt text](data/pipeline_image.png)

## Installing dependencies
This code allows you to quickly scrape all available car data on cars.com. Before running this code, run 

```
pip install -r requirements.txt
```

to install all of the python dependencies.

## **Setting up PostGreSQL and secret.py file**

On AWS, set up an RDS PostGreSQL instance and add your personal IP to the VPC groups. Then set your environment
variables to the appropriate fields listed in the secret.py file.


## **Extracting the data**

Run 

```
python async_scraper.py
```

to scrape all of the data off of cars.com. Make to create a folder called "data" before running this script. 

## **Transforming and Loading the data**

Run 

```
pyton transform_load.py
```

to aggregate and clean all of the scraped data. This script will also populate your RDS instance.


## **Updating the database with new records**

Deploy **update_extract.py** on heroku, or any scheduling service to update the database with new records.