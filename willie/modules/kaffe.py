# -*- coding: utf-8 -*-
"""
Created on Mon Sep  1 21:36:31 2014

@author: jsve
"""



import willie
import datetime
import pickle
DATA_FILE = 'botdata.p'

#def setup(bot):
    #Having a db means pref's exists. Later, we can just use `if bot.db`.
    #if bot.db and not bot.db.preferences.has_columns('coffeecount'):
        #bot.db.preferences.add_columns(['coffeecount'])
        
        
def configure(config):
    if config.option('Configure coffee module', False):
        config.interactive_add('kaffe', 'caffeine_per_cup', 'Caffeine per mg', 0.095)
        config.interactive_add('kaffe', 'coffee_delta', 'Minimum time in minutes between coffees', 30)
    

@willie.module.commands('kaffe')
def kaffe(bot, trigger):
    caller_nick, channel, nicks = decompose_info(bot,trigger)
    
    if not hasattr(bot,'LAST_COFFEE_CALL'):
        bot.LAST_COFFEE_CALL = datetime.datetime.min
    
    print(bot.LAST_COFFEE_CALL)
    
    # Check whether time enough has been spent
    kaffedelta = datetime.timedelta(0,0,0,0,float(bot.config.kaffe.coffee_delta))
    ddiff = datetime.datetime.now()-bot.LAST_COFFEE_CALL
    if (ddiff < kaffedelta):
        bot.say('\00303Ikke kaffe igen allerede, {}. Der er kun gået {} siden sidst.'.format(caller_nick,ddiff))
    else:   # Allow coffee call
        bot.LAST_COFFEE_CALL = datetime.datetime.now()
        
        count = increase_coffee_count(trigger.nick)
        s = ' ({}. kald)'.format(count)

        bot.say('\037\00304{} indkalder til kaffe.{}'.format(caller_nick,s))
        bot.say('\00303{}'.format(' '.join(nicks)))

@willie.module.commands('tally')
def tally(bot,trigger):
    
    count = total_count()
    caffeine_per_cup = float(bot.config.kaffe.caffeine_per_cup)
    bot.say('\037\00304{} fælleskopper nået (cirka {:.4f}g ren koffein).'.format(count,count*caffeine_per_cup))
        
@willie.module.commands('top5')
def top5(bot,trigger):

    # Get a sorted list of tuples (descending)
    x = individual_counts()
    sorted_x = sorted(x, key=lambda tup: tup[1],reverse=True)
    
    # Cut to 5
    if len(sorted_x)>5:
        sorted_x = sorted_x[:5]
    
    s = []
    for usr, count in sorted_x:
        s.append('{} ({} kald)'.format(usr,count))
    s = ', '.join(s)    # Concat to sentence separated by ,
    
    bot.say('Top {} kaffeelskere er {}'.format(len(sorted_x),s))
    
@willie.module.commands('frokost')
def frokost(bot,trigger):
    caller_nick, channel, nicks = decompose_info(bot,trigger)

    bot.say('ommenommenommenom frokost, {}.'.format(caller_nick))
    bot.say('\00303{0}'.format(' '.join(nicks)))
    

def coffee_count(nick):
    return get_value(nick,'coffeecount',0)
    

def total_count():
    total = 0
    for usr, count in individual_counts():
        total += count
    return total


def individual_counts():
    userlist = read_userlist()

    counts = []
    for usr in userlist:
        print(usr)
        counts.append( (usr,userlist[usr]['coffeecount']))
        
    return counts

    
def increase_coffee_count(nick):
    old_count = get_value(nick,'coffeecount',0)
    new_count = old_count+1
    #db.preferences.update(nick, {'coffeecount': '{}'.format(new_count)})
    set_value(nick,'coffeecount',new_count)

    return new_count
    
def decompose_info(bot,trigger):
    channel = trigger.sender
    caller = trigger.nick
    nicks = privs2nicks(bot,channel)
    return caller, channel, nicks
    
def privs2nicks(bot,channel):
    return ['{}'.format(key) for key in bot.privileges[channel].keys()]
    

#### Data I/O
    
def get_value(nick,key,default_value=None):
    # Read a value of a given variable for a given user
    userlist = read_userlist()
    if nick in userlist:
        if key in userlist[nick]:
            return userlist[nick][key]
    return default_value

def set_value(nick,key,value):
    userlist = read_userlist()
    if not nick in userlist:
        userlist[nick] = {}
    userlist[nick][key] = value
    write_userlist(userlist)

def read_userlist():
    import os
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE,'rb') as f:
            usrlist = pickle.load(f)
        return usrlist
    else:
        return {}
    
def write_userlist(userlist):    
    with open(DATA_FILE,'wb') as f:
        pickle.dump(userlist,f)
