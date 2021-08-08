import http.client
import httplib2
import os
import random
import time

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

from oauth2client import client # Added
from oauth2client import tools # Added
from oauth2client.file import Storage # Added

class Fake_args:
  keywords = None


prepare_for_post = []

for x in os.walk('TEST'): #name folder month
    if (('.mp4') or ('.txt') or ('.jpg')) in str(x):
        data_post = (x[0].split('/')[2].replace(' ','-'))
        if '.jpg' in str(x[-1]):
            for j in x[-1]:
                if '.txt' in j:
                    with open(x[0] + '/' + j) as f:
                        contents = f.read()
                        description = (contents.split('DESCRIPTION:')[-1].strip())
                        for i in contents.split('\n'):
                            if 'Track:' in i:
                                track = (i.split(':')[-1].strip())
                            if 'Artist:' in i:
                                artist = (i.split(':')[-1].strip())
                            if 'Label:' in i:
                                label = (i.split(':')[-1].strip())
                            if 'LABEL:' in i:
                                label = (i.split(':')[-1].strip())
                            if 'Style:' in i:
                                tags_video = (i.split(':')[-1].strip())
                        title_music = f'{artist} - {track}[{label}]'
                if '.mp4' in j:
                    way_video = (x[0] + '/' + j)
                if '.jpg' in j:
                    way_picture = (x[0] + '/' + j)
        elif '.jpg' not in str(x[-1]):
            for j in x[-1]:
                if '.txt' in j:
                    with open(x[0] + '/' + j) as f:
                        contents = f.read()
                        description = (contents.split('DESCRIPTION:')[-1].strip())
                        for i in contents.split('\n'):
                            if 'Track:' in i:
                                track = (i.split(':')[-1].strip())
                            if 'Artist:' in i:
                                artist = (i.split(':')[-1].strip())
                            if 'Label:' in i:
                                label = (i.split(':')[-1].strip())
                            if 'LABEL:' in i:
                                label = (i.split(':')[-1].strip())
                            if 'Style:' in i:
                                tags_video = (i.split(':')[-1].strip())
                        title_music = f'{artist} - {track}[{label}]'
                if '.mp4' in j:
                    way_video = (x[0] + '/' + j)

                way_picture = ''

        prepare_for_post.append([data_post, title_music, tags_video, description, way_video, way_picture])



# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
  http.client.IncompleteRead, http.client.ImproperConnectionState,
  http.client.CannotSendRequest, http.client.CannotSendHeader,
  http.client.ResponseNotReady, http.client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = 'client_secret_25.json'

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')



def get_authenticated_service(): # Modified
    credential_path = os.path.join('./', 'credentials.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)
        credentials = tools.run_flow(flow, store)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def initialize_upload(youtube, options):

  body=dict(
    snippet=dict(
      title=TITLE,
      description=DESCRIPTIONS,
      tags=TAGS.split(','),
      categoryId='22'
    ),
    status=dict(
      privacyStatus='private',
      publishAt = f'{DATA_PUBLIC}T00:01:00'
    )
  )


  # Call the API's videos.insert method to create and upload the video.
  videoPath = PATH_VIDEO
  insert_request = youtube.videos().insert(
    part=','.join(body.keys()),
    body=body,
    media_body=MediaFileUpload(videoPath, chunksize=-1, resumable=True)
  )
  resumable_upload(insert_request, options)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(request, options):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print('Uploading file...')
      status, response = request.next_chunk()
      if response is not None:
        if 'id' in response:
          print ('The video with the id %s was successfully uploaded!' % response['id'])
          # upload thumbnail for Video
          if PATH_IMAGE != '':
            youtube.thumbnails().set(
              videoId=response['id'],
              media_body=MediaFileUpload(PATH_IMAGE)
            ).execute()

        else:
          exit('The upload failed with an unexpected response: %s' % response)
    except HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = 'A retriable error occurred: %s' % e

    if error is not None:
      print (error)
      retry += 1
      if retry > MAX_RETRIES:
        exit('No longer attempting to retry.')

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print (f'Sleeping {sleep_seconds} seconds and then retrying...')
      time.sleep(sleep_seconds)


for i in prepare_for_post:
    print(i)
    args = Fake_args()
    DATA_PUBLIC = i[0]
    TITLE = i[1]
    TAGS = i[2]
    DESCRIPTIONS = i[3]
    PATH_VIDEO = i[4]
    PATH_IMAGE = i[5]

    youtube = get_authenticated_service()

    try:
      initialize_upload(youtube, args)
    except HttpError as e:
      print(f'An HTTP error {(e.resp.status, e.content)} ')

    print('wait 120 sec. for uplouding next video ...')
    for i in range(120, 0, -1):
      print(i)
      time.sleep(1)

