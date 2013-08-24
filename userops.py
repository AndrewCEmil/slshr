import pymongo
import logging

logger = logging.getLogger(__file__)

dbconn = pymongo.Connection()
db = dbconn['list']
usercol = db['users']
playcol = db['playlists']
followerscol = db['followers']
followingcol = db['following']



def usercheck(creds, request):
    return credcheck(creds['login'], creds['password'])

def credcheck(login, password):
    #first lookup in db and validate
    cursor = usercoll.find({"_id" : login})
    if cursor.count() == 0:
        logger.info("looked up " + login + ", found 0 users")
        return False
    if cursor.count() > 1:
        logger.warning("looked up " + login + ", found multiple users!")
        return False
    userdoc = cursor[0]
    #now generate the hash 
    wp = whirlpool.new("" + password + userdoc['salt'])
    passhash = wp.hexdigest()
    if passhash == userdoc['hash']:
        return True 
    return False

def gensalt():
    return os.urandom(512).encode('base64')#length of the hash output i think...

#confirms there is a user is usercol that has this username
def user_exists(username):
    cursor = usercol.find({'_id': username})
    if cursor.count() == 0:
        return False
    else if cursor.count() > 1:
        logger.error('BAD: there is are multiple users named: ' + username)
        #TODO do we want to throw an exception here?
        return True
    else:
        return True

def create_new_user(username, userpass):
    #TODO do I need this checks?
    #check for valid
    if username is None or userpass is None:
        return False
    if user_exists(username):
        return False

    #generate hash
    salt = gensalt()
    wp = whirlpool.new("" + newuserpass + salt)
    passhash = wp.hexdigest()
    #insert into db
    usercoll.insert({"_id": newusername, "hash": passhash, "salt": salt})
    playcoll.insert({'author' : newusername})
    followingcol.insert({'_id': newusername, 'following': []})
    return True

#NOTE: assumes that the user exists and username is not None
def get_user_articles(username):
    playlistcol = db[username]
    articles = list(playlistcol.find())

#NOTE: assumes that the user is already verified
def insert_user_article(username, headline, url):
    if headline is not None and url is not None:
        #TODO here do link validation
        ts = datetime.datetune.utcnow()
        newarticle = {'url': url, 'headline': headline, 'timestamp': ts}
        articles.append(newarticle)
        playlist_col.insert(newarticle)
        return True
    return False

#get all the follows for a user
#NOTE: assumes the user exists and is valid
def get_user_following(username)
    count = followingcol.find({'_id': username}).count()
    following = []
    if count == 0:
        logger.error('no following entry for ' + username)
    elif count == 1:
        following = followingcol.find({'_id':username})[0]['following']
    else:
        logger.error('got more than one use in followcoll in followers_view')
        #TODO is this the right behavior?
        following = followingcol.find({'_id':username})[0]['following']

#get all the follows for a user
#NOTE: assumes the user exists and is valid
def get_user_followers(username)
    cursor = followercol.find({'_id': username})
    count = cursor.count()
    followers = []
    if count == 1:
        followers = followercol.find({'_id':username})[0]['followers']
    else if count > 1:
        logger.error('got more than one use in followercol in get_user_followers')
        followers = followercol.find({'_id':username})[0]['followers']
    else: 
        logger.error('no followers entry for ' + username)
    return followers
