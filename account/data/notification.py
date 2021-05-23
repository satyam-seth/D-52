import smtplib
from .models import Record,Water

receivers=['satyam1998.1998@gmail.com','ankitgupta6564@gmail.com','harshitdixit65@gmail.com']

def notify_record(reg_id):
    data=Record.objects.get(pk=reg_id)
    s=smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls() 
    try:
        s.login("astered.info@gmail.com", "password")
    except:
        return 
    SUBJECT=f'D-52 Record Entry Alert {data.id}'
    TEXT=f'''!!     D-52 Record Entry Notification      !!
        Purchase Date - {data.date.strftime("%d-%m-%Y")}
        Item Name - {data.item}
        Item Price - {data.price}
        Purchase By - {data.name}
        Entry ID - {data.id}
        Entry Date - {data.datetime.strftime("%d-%m-%Y")}
        Enter By - {data.added_by}
        Detailed View - http://satyam1998.pythonanywhere.com/admin/data/record/{data.id}/change/
        Visit D-52 Website - http://satyam1998.pythonanywhere.com/'''
    message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
    for receiver in receivers:
        s.sendmail("astered.info@gmail.com", receiver, message) 
    s.quit()

def notify_water(reg_id):
    data=Water.objects.get(pk=reg_id)
    s=smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    try:
        s.login("astered.info@gmail.com", "password")
    except:
        return
    SUBJECT=f'D-52 Water Entry Alert {data.id}'
    TEXT=f'''!!     D-52 Water Entry Notification       !!
        Receiving Date - {data.date.strftime("%d-%m-%Y")}
        Quantity - {data.quantity}
        Entry ID - {data.id}
        Entry Date - {data.datetime.strftime("%d-%m-%Y")}
        Enter By - {data.added_by}
        Detailed View - http://satyam1998.pythonanywhere.com/admin/data/water/{data.id}/change/
        Visit D-52 Website - http://satyam1998.pythonanywhere.com/'''
    message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
    for receiver in receivers:
        s.sendmail("astered.info@gmail.com", receiver, message) 
    s.quit()
