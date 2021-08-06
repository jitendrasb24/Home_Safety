import cv2
import numpy
import os
from twilio.rest import Client
import smtplib
import imghdr
from email.message import EmailMessage

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
fire_cascade = cv2.CascadeClassifier('fire.xml')

account_sid = 'XYZ' #twilio account sid
auth_token = 'ABC'  #twilio account token
client = Client(account_sid, auth_token)

Sender_Email = "XYZ@gmail.com" #mail id that will be use to send mails.
Reciever_Email = "ABC@gmail.com"  #mail in which you want to recieve Alert.
f = open("password.txt", "r")   #opening password text file to read password
Password= f.read()  #sender's mail id password.


count = 0
flag = 0

coun = 1

while True:
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    [_, img] = cap.read()
    diff = cv2.absdiff(frame1, frame2)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(diff_gray, (5, 5), 0)
    [_, thresh] = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 900:
            continue
        cv2.putText(frame1, "STATUS: {}".format('MOTION DETECTED'), (10, 90), cv2.FONT_HERSHEY_SIMPLEX,1, (25, 130, 12), 2)


    gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    fire = fire_cascade.detectMultiScale(frame1, 1.9, 50)

    if count >= 30:
        flag = 1


    for(x,y,w,h) in fire:
        count+=1

        if flag:
            flag = 0

            count = 0
            cv2.rectangle(frame1, (x-20, y-20), (x + w + 20, y + h + 20), (0, 0, 255), 2)
            cv2.putText(frame1,"ALERT: {}".format("FIRE DETECTED "), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (217, 10, 10), 2)
            print("Sending Alert Message...........")

            message = client.messages.create(
                body='ALERT: FIRE FIRE FIRE',   #body of the message
                from_='123',    #twilio account generated number
                to='1234'    #person phone number whom to send the message
            )
            print(message.sid)

        else:
            cv2.rectangle(frame1, (x-20, y-20), (x + w + 20, y + h + 20), (0, 0, 255), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame1[y:y+h, x:x+w]
            cv2.putText(frame1,"ALERT: {}".format("FIRE DETECTED "), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 170, 0), 2)
            print("Fire Detected")


    gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (124, 255, 0), 2)
        roi_color = gray[y:y+h, x:x+w]
        path = r'C:\Users\Lenovo\Desktop\Training\Home_safety_data'  #path where the image will be saved.
        full_name = 'person.jpg'  #name by which the image will be saved.
        os.chdir(path)
        cv2.imwrite(full_name, roi_color)
        print('Face Detected & Saved with filename person')
        coun+=1

        if coun>=50:
            coun = 0
            newMessage = EmailMessage()
            newMessage['Subject'] = "ALERT ALERT ALERT"
            newMessage['From'] = Sender_Email
            newMessage['To'] = Reciever_Email
            newMessage.set_content('SOMEONE IS ON THE DOOR.'
                                   'PLEASE VERIFY THE PERSON.'
                                   'STRANGER IMAGE ATTACHED!')

            with open('person.jpg', 'rb') as f:  #saved image of stranger
                image_data = f.read()
                image_type = imghdr.what(f.name)
                image_name = f.name

            newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:

                smtp.login(Sender_Email, Password)
                smtp.send_message(newMessage)

            print('WARNING MAIL SENT..........')

            print("Sending Alert Message...........")
            message = client.messages.create(
                body='ALERT: SOMEONE IS ON THE DOOR. '    #body of the message
                     'THE PICTURE HAS BEEN SENT AS AN ATTACHMENT TO YOUR MAIL. '
                     'PLEASE CHECK YOUR MAIL AND VERIFY THE PERSON.',
                from_='123',    #twilio account generated number
                to='1234'    #person phone number whom to send the message
            )
            print(message.sid)


    cv2.imshow("Video", frame1)
    frame1 = frame2
    ret, frame2 = cap.read()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()