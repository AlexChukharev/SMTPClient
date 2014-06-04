import base64
import getpass
from random import randint
import os
import socket
import sys

__author__ = 'Alexander.Chukharev'

port = 25


def print_help():
    path = sys.argv[0].split("/")
    name = path[len(path) - 1]
    print("{0} host port".format(name))


def get_args():
    global login, password, recipient, host
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
    else:
        host = sys.argv[1]
        if len(sys.argv) == 3:
            global port
            port = int(sys.argv[2])
    login = input("LOGIN: ")
    password = getpass.getpass('PASS: ')
    recipient = input("recipient: ".upper())


def gen_mess():
    global all_files, login, recipient
    delim = ''
    symb = 'ABCDEFGHIJKLMNOPQRSTUVWXYZqwertyuiopasdfghjklzxcvbnm1234567890+-#!^;'
    randN = randint(10, 21)
    for i in range(1, randN):
        randInd = randint(0, 64)
        delim += symb[randInd]
    result = 'FROM: {0} <{0}>\r\n' \
             'TO: {1} <{1}>\r\n' \
             'Subject: all img files in dir\r\n' \
             'Content-Type: Multipart/mixed; boundary=\"{2}\"\r\n'
    result = result.format(login, recipient, delim)
    for file, content in all_files.items():
        result += '--{2}\r\n' \
                  'Content-Type: application/octet-stream; name=\"{4}\"\r\n' \
                  'Content-transfer-encoding: base64\r\n' \
                  'Content-Disposition: attachment; filename=\"{4}\"\r\n' \
                  '\r\n' \
                  '{3}\r\n'
        result = result.format(login, recipient, delim, content.decode('utf-8'), file)
    return result


def gen_list_of_im():
    global all_files
    all_files = {}

    for file in os.listdir("./"):
        if file.lower().endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
            with open(file, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                all_files[file] = encoded_string
            image_file.close()


def send(m, sock):
    sock.send((m + '\r\n').encode('utf-8'))
    print(sock.recv(1024).decode('utf-8'))


def send_and_print(m, sock):
    print(m)
    sock.send((m + '\r\n').encode('utf-8'))
    print(sock.recv(1024).decode('utf-8'))


def to_base64(s):
    encoded_s = base64.b64encode(bytes(s, 'utf-8'))
    return encoded_s.decode('utf-8')


def create_and_send_mess(sock):
    global login, password, recipient
    print(sock.recv(1024))
    messages = [
        'helo vintik9g',
        'auth login',
        to_base64('{0}'.format(login)),
        to_base64('{0}'.format(password)),
        'mail from: <{0}>'.format(login),
        'rcpt to: <{0}>'.format(recipient),
        'data'
    ]
    for m in messages:
        send_and_print(m, sock)
    send(gen_mess() + '\r\n.', sock)


def main():
    get_args()
    print(host + ' ' + repr(port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    gen_list_of_im()

    global all_files
    print("\nyou have {0} img files\n".format(len(all_files)))

    create_and_send_mess(sock)


main()