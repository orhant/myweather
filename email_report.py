#!/usr/bin/python
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email_credentials import email_credentials
from sqlite3 import connect
from os.path import dirname, abspath
from dateutil.parser import parse

def send_mail(data):
    mailhost, fromaddr, toaddrs, subject, credentials = email_credentials()
    username, password = credentials
    subject = 'seanweather weekly report'
    body = 'Here are some interesting results, my good-looking friend:\n\n' + data
    msg = MIMEText(body, _charset="UTF-8")
    msg['Subject'] = Header(subject, "utf-8")
    server = smtplib.SMTP(mailhost)
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    server.quit()

def gather_data(cur):
    data = "Last week's lookups\n"
    query = 'select zipcode, count(*) as c from lookup group by zipcode order by c desc'
    data += '\n'.join('{}{:>3}'.format(*result) for result in cur.execute(query))
    data += '\n\nComments\n'
    query = 'select date, text from comment'
    results = ((parse(date), text) for date, text in cur.execute(query))
    data += u'\n'.join(u'{:>12} -- {}'.format(date.strftime('%m/%d %H:%M'), text) for date, text in results)
    return data

def clean_up(cur):
    cur.execute('delete from lookup')
    cur.execute('delete from comment')
    cur.execute('update location set cache="" where julianday(last_updated) < julianday()-1')

if __name__ == '__main__':
    directory = dirname(abspath(__file__))
    conn = connect(directory + '/db.db')
    cur = conn.cursor()
    send_mail(gather_data(cur))
    clean_up(cur)
    conn.commit()
    conn.close()
