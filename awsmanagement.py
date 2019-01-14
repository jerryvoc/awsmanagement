import json
import boto3
import collections
import datetime
import time
import sys
from botocore.exceptions import ClientError

def lambda_handler(event, context):


  ec2 = boto3.client('ec2')
  response = ec2.describe_instances()
  instance_count = []
  SENDER = "jerry.vochteloo@emc.com" # MUST be registered in SES
  RECIPIENT = "jerry.vochteloo@emc.com"
  AWS_REGION = "us-east-1"   #change if sending from another region
  CHARSET = "UTF-8"
  SUBJECT = "Current Running EC2 Instances"
  
  # for non-HTML emails
  BODY_TEXT = ("Amazon SES Test (Python)\r\n"
               "Email sent using "
               "AWS SDK for Python (Boto)."
               )
  BODY_HTML = """
  <html>
  <head></head>
  <body>
    <p>AWS resources :<br>
              """
  
  today = datetime.date.today()
  today_string = today.strftime('%Y/%m/%d')
  regions = ec2.describe_regions().get('Regions',[] )
  all_regions = [region['RegionName'] for region in regions]

  for region_name in all_regions:
    BODY_HTML += ('Instances in EC2 Region {0}<br>'.format(region_name))
    ec2 = boto3.resource('ec2', region_name=region_name)
    instances = ec2.instances
    volumes = ec2.volumes
    volume_ids = []
    for i in instances.all():
      name = ''
      s ='-'
      if (i.tags):
        for tag in i.tags:  # Get the name of the instance
          if tag['Key'] == 'Name':
            name = tag['Value']
        
      BODY_HTML += ('<ul><li>Found instance \'{1}\', id: {0}, state: {2}</li>'.format(i.id, name, i.state['Name']))
  
      if (i.tags):
        for tag in i.tags:  # Get the name of the instance
          if tag['Key'][:3] == 'GTO':
              s += tag['Key']
              BODY_HTML += ('<b>GTO tags = {0} {1}</b>'.format(tag['Key'],tag['Value']))
            
      vols = i.volumes.all()  # Iterate through each instance's volumes
      BODY_HTML += "<ul>"
      for v in vols:
        BODY_HTML += ('<li>{0} is attached to volume {1} size: {2}</li>'.format(name, v.id,v.size))
      BODY_HTML += ("</ul></ul>")  
#    BODY_HTML += ("</ul>")
  
  volume_ids = []
  BODY_HTML += ("<ul>")
  for i in volumes.all():
    if not (i.attachments):
      BODY_HTML += ('<li>Found unattached volume \'{1}\', id: {0}, size {2}</li>'.format(i.id, name,i.size))

  BODY_HTML += ("</ul>")
   
  client = boto3.client('rds')
  db_instances = client.describe_db_instances()
  for database in db_instances['DBInstances']:
    print("RDS Type = %s, Instance = %s" % (database['Engine'],database['DBInstanceIdentifier']))
  # The character encoding for the email.
  CHARSET = "UTF-8"
  
  BODY_HTML += """</p>
  </body>
  </html>
              """
  # Create a new SES resource and specify a region.
  client = boto3.client('ses',region_name=AWS_REGION)
  # Try to send the email.
  try:
      #Provide the contents of the email.
      response = client.send_email(
          Destination={
              'ToAddresses': [
                  RECIPIENT,
              ],
          },
          Message={
              'Body': {
                  'Html': {
                      'Charset': CHARSET,
                      'Data': BODY_HTML,
                  },
                  'Text': {
                      'Charset': CHARSET,
                      'Data': BODY_TEXT,
                  },
              },
              'Subject': {
                  'Charset': CHARSET,
                  'Data': SUBJECT,
              },
          },
          Source=SENDER,
      )
  # Display an error if something goes wrong.	
  except ClientError as e:
      print(e.response['Error']['Message'])
  else:
      print("Email sent! Message ID:"),
      print(response['MessageId'])




v2

import json
import boto3
import collections
import datetime
import time
import sys
from botocore.exceptions import ClientError

def lambda_handler(event, context):


  ec2 = boto3.client('ec2')
  response = ec2.describe_instances()
  instance_count = []
  SENDER = "jerry.vochteloo@emc.com" # MUST be registered in SES
  RECIPIENT = "jerry.vochteloo@emc.com"
  AWS_REGION = "us-east-1"   #change if sending from another region
  CHARSET = "UTF-8"
  SUBJECT = "Current Running EC2 Instances"
  
  # for non-HTML emails
  BODY_TEXT = ("Amazon SES Test (Python)\r\n"
               "Email sent using "
               "AWS SDK for Python (Boto)."
               )
  BODY_HTML = """
  <html>
  <head></head>
  <body>
    <p>AWS resources :<br>
              """
  
  today = datetime.date.today()
  today_string = today.strftime('%Y/%m/%d')
  regions = ec2.describe_regions().get('Regions',[] )
  all_regions = [region['RegionName'] for region in regions]

  for region_name in all_regions:
    BODY_HTML += ('Instances in EC2 Region {0}<br>'.format(region_name))
    ec2 = boto3.resource('ec2', region_name=region_name)
    instances = ec2.instances
    volumes = ec2.volumes
    volume_ids = []
    for i in instances.all():
      name = ''
      s ='-'
      if (i.tags):
        for tag in i.tags:  # Get the name of the instance
          if tag['Key'] == 'Name':
            name = tag['Value']
        
      BODY_HTML += ('<ul><li>Found instance \'{1}\', id: {0}, state: {2}</li>'.format(i.id, name, i.state['Name']))
      GTO_tag = False
      creation_set = False
      GTO_time = False
      GTO_purpose = False
      
# iterate to capture all the tags
      
      if (i.tags):
        for tag in i.tags:  # Get the name of the instance
          if tag['Key'][:3] == 'GTO':
              GTO_tag = True
              if tag['Key'][4:] == 'Owner':
                GTO_Owner = tag['Value']
              elif tag['Key'][4:] == 'Purpose':
                GTO_purpose = True
              elif tag['Key'][4:] == 'Time':
                GTO_time = True
              elif tag['Key'][4:] == "Creation":
                creation_set = True
                GTO_Creation = tag['Value']
                GTO_Creation_date = datetime.date.fromisoformat(tag['Value'])
                print ('Found creation date on {0}'.format(i.id))
              BODY_HTML += ('<b>GTO tags = {0} {1}</b>'.format(tag['Key'],tag['Value']))
              
# test to see if the creation date is set, if not set it
              
      if ((not creation_set) and GTO_tag):
        ec2.create_tags(
          Resources=[
            i.id,
          ],
          Tags=[
            {
              'Key': 'GTO_Creation',
              'Value': datetime.datetime.now().strftime('%Y-%m-%d')
            },
          ]
        )
      
# if the creation date is set, check to see if it is past expiration

      if (creation_set and GTO_time):
        if (GTO_Creation_date + GTO_time < datetime.datetime.now):
          print("{1} is past date".format(i.id))
      
      vols = i.volumes.all()  # Iterate through each instance's volumes
      BODY_HTML += "<ul>"
      for v in vols:
        BODY_HTML += ('<li>{0} is attached to volume {1} size: {2}</li>'.format(name, v.id,v.size))
      BODY_HTML += ("</ul></ul>")  
#    BODY_HTML += ("</ul>")
  
  volume_ids = []
  BODY_HTML += ("<ul>")
  for i in volumes.all():
    if not (i.attachments):
      BODY_HTML += ('<li>Found unattached volume \'{1}\', id: {0}, size {2}</li>'.format(i.id, name,i.size))

  BODY_HTML += ("</ul>")
   
  client = boto3.client('rds')
  db_instances = client.describe_db_instances()
  for database in db_instances['DBInstances']:
    print("RDS Type = %s, Instance = %s" % (database['Engine'],database['DBInstanceIdentifier']))
  # The character encoding for the email.
  CHARSET = "UTF-8"
  
  BODY_HTML += """</p>
  </body>
  </html>
              """
  # Create a new SES resource and specify a region.
  client = boto3.client('ses',region_name=AWS_REGION)
  # Try to send the email.
  try:
      #Provide the contents of the email.
      response = client.send_email(
          Destination={
              'ToAddresses': [
                  RECIPIENT,
              ],
          },
          Message={
              'Body': {
                  'Html': {
                      'Charset': CHARSET,
                      'Data': BODY_HTML,
                  },
                  'Text': {
                      'Charset': CHARSET,
                      'Data': BODY_TEXT,
                  },
              },
              'Subject': {
                  'Charset': CHARSET,
                  'Data': SUBJECT,
              },
          },
          Source=SENDER,
      )
  # Display an error if something goes wrong.	
  except ClientError as e:
      print(e.response['Error']['Message'])
  else:
      print("Email sent! Message ID:"),
      print(response['MessageId'])