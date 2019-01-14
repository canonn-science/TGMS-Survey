from config import config
import myNotebook as nb
from urllib import quote_plus
import webbrowser
import threading
import requests
from canonn import codex
import os

import ttk
import Tkinter as tk
import sys
    
this = sys.modules[__name__]
this.body_name=None


this.nearloc = {
   'Latitude' : None,
   'Longitude' : None,
   'Altitude' : None,
   'Heading' : None,
   'Time' : None
}
this.systemCache={ "Sol": (0,0,0) }
    
def plugin_prefs(parent, cmdr, is_beta):
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    this.anon = tk.IntVar(value=config.getint("Anonymous")) # Retrieve saved value from config
    frame = nb.Frame(parent)
    frame.columnconfigure(3, weight=1)
    nb.Checkbutton(frame, text="I want to be anonymous", variable=this.anon).grid(row = 1, column = 0,sticky=tk.W)

    
def prefs_changed(cmdr, is_beta):
    """
    Save settings.
    """
    config.set('Anonymous', this.anon.get())       
   
def plugin_start(plugin_dir):
    """
    Load Template plugin into EDMC
    """
    
    #print this.patrol
    return 'TGMS'
    
def submitTCMS():
    url="https://docs.google.com/forms/d/e/1FAIpQLSfXfnQ9AqxTEfjoucyjQQHWbMg3T4ClnMUlJszC7Ll0rVFzUg/viewform?usp=pp_url"
    url+="&entry.2011446833="+quote_plus(this.cmdr);
    url+="&entry.350770152="+quote_plus(this.system)
    webbrowser.open(url)
    
def plugin_app(parent):

    this.parent = parent
    #create a new frame as a containier for the status
    this.frame = tk.Frame(parent)
    
    
    this.buttonbar = tk.Frame(this.frame)
    
    #We want three columns, label, text, button
    this.frame.columnconfigure(1, weight=1)
    
    #this.label = tk.Label(parent, text="TCMS:")
    this.status = tk.Button(this.frame, anchor=tk.W, text="Submit TGMS Report", command=submitTCMS)
    this.status.grid(row = 0, column = 1)
    #this.label.grid_remove()
    this.status.grid_remove()
    
    return (this.frame)
    

    

    
   
def journal_entry(cmdr, is_beta, system, station, entry, state):
    '''
    Commanders may want to be anonymous so we we have a journal entry anonymiser
    that passes the journale entry to the one that does all the real work
    '''
    # capture some stats when we launch not read for that yet
    # startup_stats(cmdr)

    #this.label.grid()
    this.status.grid()
    
    if ('Body' in entry):
        this.body_name = entry['Body']    
    
    if config.getint("Anonymous") >0:
        commander="Anonymous"
        if cmdr in str(entry):
            #entry["cmdrName"]="Anonymous"
            s = str(entry).replace(cmdr,"Anonymous")
            entry=eval(s)
    else:
        commander=cmdr
        
    x,y,z=edsmGetSystem(system)
    
    return journal_entry_wrapper(commander, is_beta, system, station, entry, state,x,y,z,this.body_name,this.nearloc['Latitude'],this.nearloc['Longitude'])       
  
class Reporter(threading.Thread):
    def __init__(self, payload):
        threading.Thread.__init__(self)
        self.payload = payload

    def run(self):
        try:
            requests.get(self.payload)
            
        except:
            print("["+myPlugin+"] Issue posting message " + str(sys.exc_info()[0]))
              

    
    
def CodexEntry(cmdr, is_beta, system, station, entry, state):
    #{ "timestamp":"2018-12-30T00:48:12Z", "event":"CodexEntry", "EntryID":2100301, "Name":"$Codex_Ent_Cone_Name;", "Name_Localised":"Bark Mounds", "SubCategory":"$Codex_SubCategory_Organic_Structures;", "SubCategory_Localised":"Organic structures", "Category":"$Codex_Category_Biology;", "Category_Localised":"Biological and Geological", "Region":"$Codex_RegionName_18;", "Region_Localised":"Inner Orion Spur", "System":"HIP 16378", "SystemAddress":1, "VoucherAmount":2500 }
    if entry['event'] == "CodexEntry":
        
        x,y,z=edsmGetSystem(system)
        url="https://docs.google.com/forms/d/e/1FAIpQLSfdr7GFj6JJ1ubeRXP_uZu3Xx9HPYT6507lRLqqC0oUZyj-Jg/formResponse?usp=pp_url"
        
        url+="&entry.1415400073="+quote_plus(cmdr);
        url+="&entry.1860059185="+quote_plus(system)
        url+="&entry.810133478="+str(x)
        url+="&entry.226558470="+str(y)
        url+="&entry.1643947574="+str(z)
        if this.body_name:
            url+="&entry.1432569164="+quote_plus(this.body_name)
        if this.nearloc['Latitude']:
            url+="&entry.1891952962="+str(this.nearloc['Latitude'])
            url+="&entry.405491858="+str(this.nearloc['Longitude'])
        url+="&entry.1531581549="+quote_plus(str(entry["EntryID"]))
        url+="&entry.1911890028="+quote_plus(entry["Name"])
        url+="&entry.1057995915="+quote_plus(entry["Name_Localised"])
        url+="&entry.598514572="+quote_plus(entry["SubCategory"])
        url+="&entry.222515268="+quote_plus(entry["SubCategory_Localised"])
        url+="&entry.198049318="+quote_plus(entry["Category"])
        url+="&entry.348683576="+quote_plus(entry["Category_Localised"])
        url+="&entry.761612585="+quote_plus(entry["Region"])
        url+="&entry.216399442="+quote_plus(entry["Region_Localised"])
        url+="&entry.1236018468="+quote_plus(str(entry["SystemAddress"]))
        if('VoucherAmount' in entry):
            url+="&entry.1250864566="+quote_plus(str(entry["VoucherAmount"]))
                
            
        
        Reporter(url).start()    
    
# Detect journal events
def journal_entry_wrapper(cmdr, is_beta, system, station, entry, state,x,y,z,body,lat,lon):
    #Google sheet codex entry
    CodexEntry(cmdr, is_beta, system, station, entry, state)
    #Strapi Codex Entry
    codex.submit( cmdr, is_beta, system, x,y,z, entry, body,lat,lon)
    
    if system and cmdr:
        this.system=system
        this.cmdr=cmdr
    

    
def dashboard_entry(cmdr, is_beta, entry):
    
      
    
    this.landed = entry['Flags'] & 1<<1 and True or False
    this.SCmode = entry['Flags'] & 1<<4 and True or False
    this.SRVmode = entry['Flags'] & 1<<26 and True or False
    this.landed = this.landed or this.SRVmode
      #print "LatLon = {}".format(entry['Flags'] & 1<<21 and True or False)
      #print entry
    if(entry['Flags'] & 1<<21 and True or False):
        if('Latitude' in entry):
            this.nearloc['Latitude'] = entry['Latitude']
            this.nearloc['Longitude'] = entry['Longitude']
    else:
        this.body_name = None
        this.nearloc['Latitude'] = None
        this.nearloc['Longitude'] = None    
    
    
def edsmGetSystem(system):
    
    if this.systemCache.has_key(system):
    
        return this.systemCache[system]
        
    else:
        url = 'https://www.edsm.net/api-v1/system?systemName='+quote_plus(system)+'&showCoordinates=1'      
        #print url
        r = requests.get(url)
        s =  r.json()
        #print s
        
        this.systemCache[system]=(s["coords"]["x"],s["coords"]["y"],s["coords"]["z"])
        return s["coords"]["x"],s["coords"]["y"],s["coords"]["z"]    