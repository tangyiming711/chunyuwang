import json
from tweepy import OAuthHandler, API, Stream
import os
import wget
import sys
import requests
import subprocess
import io
from google.cloud import vision
from google.cloud.vision import types
from google.auth import app_engine

##add your twitter app credentials here
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""

os.environ['GOOGLE_APPLICATION_CREDENTIALS']= ""##add your google credential json file path here

def main():
	#Authentication
	api = authenticate()
	print ('\n\nTwitter Image Downloader and Analyzer:\n======================================\n')
	username = input("\nEnter the twitter handle of the Account to download media from: ")
	max_tweets = int(input("\nEnter Max. number of tweets to search (0 for all tweets): "))
	
	all_tweets = getTweetsFromUser(username,max_tweets,api)
	media_URLs = getTweetMediaURL(all_tweets)
	
	downloadFiles(media_URLs,username)
	print ('\n\nFinished Downloading.\n')

def getTweetsFromUser(username,max_tweets,api):
	# Fetches Tweets from user with the handle 'username' upto max of 'max_tweets' tweets
	last_tweet_id, num_images = 0,0
	try:
	    raw_tweets = api.user_timeline(screen_name=username,include_rts=False,exclude_replies=True)
	except Exception as e:
		print (e)
		sys.exit()

	last_tweet_id = int(raw_tweets[-1].id-1)
	
	print ('\nFetching tweets.....')

	if max_tweets == 0:
		max_tweets = 3500

	while len(raw_tweets)<max_tweets:
		sys.stdout.write("\rTweets fetched: %d" % len(raw_tweets))
		sys.stdout.flush()
		temp_raw_tweets = api.user_timeline(screen_name=username, max_id=last_tweet_id, include_rts=False, exclude_replies=True)

		if len(temp_raw_tweets) == 0:
			break
		else:
			last_tweet_id = int(temp_raw_tweets[-1].id-1)
			raw_tweets = raw_tweets + temp_raw_tweets

	print ('\nFinished fetching ' + str(min(len(raw_tweets),max_tweets)) + ' Tweets.')
	return raw_tweets

def getTweetMediaURL(all_tweets):
	print ('\nCollecting Media URLs.....')
	tweets_with_media = set()
	for tweet in all_tweets:
		media = tweet.entities.get('media',[])
		if (len(media)>0):
			tweets_with_media.add(media[0]['media_url'])
			sys.stdout.write("\rMedia Links fetched: %d" % len(tweets_with_media))
			sys.stdout.flush()
	print ('\nFinished fetching ' + str(len(tweets_with_media)) + ' Links.')

	return tweets_with_media

def downloadFiles(media_url,username):

	print ('\nDownloading Images.....')
	try:
	    os.mkdir('twitter_images')
	    os.chdir('twitter_images')
	except:
		os.chdir('twitter_images')

	for url in media_url:
		wget.download(url)


def authenticate():
	# Authenticate the use of twitter API 
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key,access_secret)
	api = API(auth)
	return api

class BatchRename():
   # Rename all the jpg file in the directory
    def __init__(self):
        self.path = os.getcwd() #local path

    def rename(self):
        filelist = os.listdir(self.path) #get the path of files
        total_num = len(filelist) #get the length of the files(quantities)
        i = 1  #the files name come from 1
        for item in filelist:
            if item.endswith('.jpg'):  #the initial files are jpg
                src = os.path.join(os.path.abspath(self.path), item)
                dst = os.path.join(os.path.abspath(self.path), ''+str(i) + '.jpg')#the files after are jpg as well

                try:
                    os.rename(src, dst)
                    print ('converting %s to %s ...' % (src, dst))
                    i = i + 1
                except:
                    continue
        print ('total %d to rename & converted %d jpgs' % (total_num, i))
    
def video():
    subprocess.call('ffmpeg -f image2 -r 1 -i %d.jpg -vcodec mpeg4 test.mp4', shell=True)
    print('\n\nVideo created.')

def createLabels():
    client = vision.ImageAnnotatorClient()

    print('\nCreating Labels of images, please wait......\n')

    # create file 
    f1 = open('labels.txt','w+') 
    f1.write('Labels:')

    # The name of the image file to annotate
    directory =  os.getcwd()  # change to local path
    #for i in range(1,n):
    for filename in os.listdir(directory): 
            if filename.endswith(".jpg"):
                file_name = filename 
                # Loads the image into memory 
                with io.open(file_name, 'rb') as image_file:
                    content = image_file.read()

                image = types.Image(content=content)

                # Performs label detection on the image file
                response = client.label_detection(image=image)
                labels = response.label_annotations

                
                for label in labels:
                    f1.write('\n')  
                    f1.write(label.description)
                    #labels created in labels.txt
                

    f1.close()
    print('labels.txt created.')
if __name__ == '__main__':
	main()
demo = BatchRename()
demo.rename()
video()
createLabels()

print('\nPlease check the twitter_images document for info\n')