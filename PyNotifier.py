from datetime import datetime
from plyer import notification 
from twilio.rest import Client 
import time 

##############  ENTER CREDENTIALS HERE TO RECEIVE SMS  ##############

# Create a Twilio account if you want to send notifications of events via SMS...Ignore if you want to stick to only desktop notifications instead 

account_sid = ''      # Enter your 'ACCOUNT SID' inside the quotes
auth_token = ''       # Enter your 'AUTH TOKEN' inside the quotes
twilio_from_num = ''    # Enter your twilio phone no. inside the quotes
twilio_to_num = ''      # Enter your registered twilio phone no. to which you want to send the SMS


def Notifier(reqarray1):
    print("\nNotifier Started")
    n2 = 0
    for i in reqarray1:
        schdt=reqarray1[n2]['Created']
        while(True): 
            today = datetime.now()
            nowdt = today.strftime("%d/%m/%Y %I:%M %p")
            if(schdt == nowdt):
                notification.notify( 
                    title="Reminder...", 
                    message=reqarray1[n2]['Message'],
                    app_name="PyNotifier by Ronik", 
                    timeout=10
                )
                print(f"Notification pushed for Event {n2+1}...")
                n2 = n2+1
                break     
            time.sleep(1) 
    print("\nAll Event Notifications pushed")


def send_twilioSMS(reqarray1):
    
    if (account_sid == '' or auth_token == '' or twilio_from_num == '' or twilio_to_num == ''):
        print("No account SID/auth token/twilio phone no./targeted phone number found...Please create an account on twilio and paste the required values inside the program")
        exit()

    print("\nSMS Notifier Started")
    n2 = 0
    for i in reqarray1:
        schdt=reqarray1[n2]['Created']
        while(True): 
            today = datetime.now()
            nowdt = today.strftime("%d/%m/%Y %I:%M %p")
            if(schdt == nowdt):
                client = Client(account_sid, auth_token) 
                message = client.messages.create( 
                                            from_=twilio_from_num, 
                                            body =reqarray1[n2]['Message'], 
                                            to =twilio_to_num
                                        ) 
                
                print(f"\nNotification pushed for Event {n2+1}...")
                print("SID for current SMS: ",message.sid)
                n2 = n2+1
                break     
            time.sleep(1) 
    print("\nAll Event Notifications pushed")


def takeinput():
    event_list = []
    n = 1
    while(True):
        print(f"\nEVENT {n} ----------------")
        inpdate = input("Enter date in 'dd/mm/yyyy' format (eg: 06/11/2020): ")
        inptime = input("Enter time in 'hh:mm AM/PM' format (eg: 05:40 AM): ")
        event_msg = input("Enter event message: ")
        keyjoint = inpdate+" "+inptime
        event_list.append({'Created':keyjoint,'Message':event_msg})
        choice = input("Do you want to add another event? Type 'no' to quit or anything else to proceed: ")
        n=n+1
        if(choice == 'no'):
            break

    sortedArray = sorted(
        event_list,
        key=lambda x: datetime.strptime(x['Created'], '%d/%m/%Y %I:%M %p'), reverse=False
    )

    notifchoice = int(input("\nHow do you want me to remind you ? \n1) Enter 1 for notification through your PC\n2) Enter 2 for SMS notification on your phone\nEnter choice: "))
    if (notifchoice == 1):
        Notifier(sortedArray)
    elif (notifchoice == 2):
        send_twilioSMS(sortedArray)
    else:
        print("Choice should be either 1 or 2")

if __name__ == '__main__':
    takeinput()