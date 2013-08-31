import pymongo
import whirlpool
import logging
import datetime

logger = logging.getLogger(__file__)

dbconn = pymongo.Connection()
db = dbconn['list']
#schema: _id: default, author:string
playlistcol = db['playlists']
#schema: _id: username, hash: string, salt: string
usercol = db['users']
#stupid col, probably should not even exist...
playcol = db['playlists']
#schema: _id: username, followts = timestamp followers = [{ username: username, followts: timestamp }] #TODO check this schema
followerscol = db['followers']
#schema: _id: username, following = [{ username: username, followts: timestamp }]
followingcol = db['following']
#schema: _id default, url: string, headline: string, insertts: timestamp
#thats schema for the playlist where the collection name is the curator

def usercheck(creds, request):
    return credcheck(creds['login'], creds['password'])

def credcheck(login, password):
    #first lookup in db and validate
    cursor = usercol.find({"_id" : login})
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
    if cursor.count() == 0:
        return False
    elif cursor.count() > 1:
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
    usercol.insert({"_id": newusername, "hash": passhash, "salt": salt})
    playcol.insert({'author' : newusername})
    followingcol.insert({'_id': newusername, 'following': []})
    followerscol.insert({'_id': newusername, 'followers': []})
    return True

def get_all_playlists():
    playlists = []
    for playlist in playlistcol.find():
        playlists.append(playlist)
    return playlists


#NOTE: assumes that the user exists and username is not None
def get_user_articles(username):
    playlistcol = db[username]
    articles = list(playlistcol.find())
    return articles

#NOTE: assumes that the user is already verified
def insert_user_article(username, headline, url):
    if headline is not None and url is not None:
        playlist_col = db[username]
        #TODO here do link validation
        ts = datetime.datetime.utcnow()
        newarticle = {'url': url, 'headline': headline, 'timestamp': ts}
        playlist_col.insert(newarticle)
        return newarticle
    return None

#NOTE: assumes these are valid users
def follows(follower, followee):
    #first get following and followers
    following = get_user_following(follower)
    followers = get_user_followers(followee)
    alreadyfollowing = False
    alreadyfollowed = False
    for user in following:
        if user['username'] == followee:
            alreadyfollowing = True
            break
    for user in followers:
        if user['username'] == follower:
            alreadyfollowed = True

    #if alreadyfollowing != alreadyfollowed
    if alreadyfollowing != alreadyfollowed:
        logger.error('users are not in same following/followed state: ' + follower + ' and ' + followee)
        return False
    
    if alreadyfollowing:
        return True
    return False

#get all the follows for a user
#NOTE: assumes the user exists and is valid
def get_user_following(username):
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
    return following

#get all the follows for a user
#NOTE: assumes the user exists and is valid
def get_user_followers(username):
    cursor = followerscol.find({'_id': username})
    count = cursor.count()
    followers = []
    if count == 1:
        followers = followerscol.find({'_id':username})[0]['followers']
    elif count > 1:
        logger.error('got more than one use in followercol in get_user_followers')
        followers = followercol.find({'_id':username})[0]['followers']
    else: 
        logger.error('no followers entry for ' + username)
    return followers

#NOTE: assumes both users exist are are valid
def new_follow(follower, followee):
    followcursor = followerscol.find({'_id': followee})
    followcount = followcursor.count()
    if followcount == 0:
        #TODO should this be an exception?
        logger.error('no entry in followers for user ' + followee)
        return False
    if followcount > 1:
        looger.error('followcol has multiple users with name ' + followee)
        return False

    followingcursor = followingcol.find({'_id': follower})
    followingcount = followingcursor.count()
    if followingcount == 0:
        logger.error('no entry in followers for user ' + username)
        return False
    if followcount > 1:
        looger.error('followcol has multiple users with name ' + followee)
        return False

    #return false if already follows
    if follows(follower, followee):
        return False

    #both are the right count
    ts = datetime.datetime.utcnow()
    followerscol.update({'_id': followee}, {"$push" : { "followers": { "username": follower, "followts": ts}}})
    followingcol.update({'_id': follower}, {"$push": { "following": { "username": followee, "followts": ts}}})

#NOTE: assumes that both users exist and are valid
def unfollow(follower, followee):
    followcursor = followerscol.find({'_id': followee})
    followcount = followcursor.count()
    if followcount == 0:
        #TODO should this be an exception?
        logger.error('no entry in followers for user ' + followee)
        return False
    if followcount > 1:
        logger.error('followcol has multiple users with name ' + followee)
        return False

    followingcursor = followingcol.find({'_id': follower})
    followingcount = followingcursor.count()
    if followingcount == 0:
        logger.error('no entry in followers for user ' + username)
        return False
    if followcount > 1:
        logger.error('followcol has multiple users with name ' + followee)
        return False

    if not follows(follower, followee):
        logger.info(follower + " does not follow " + followee)
        return False

    followerscol.update({'_id': followee}, {"$pull" : { "followers": { "username": follower}}})
    followingcol.update({'_id': follower}, {"$pull": { "following": { "username": followee}}})
    return True



