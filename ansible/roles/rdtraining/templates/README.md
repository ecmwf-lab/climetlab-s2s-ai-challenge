# Welcome to your ECMWF lab instance

Here are the details for your session:

* Host: {{ training_host }}
* User: {{ training_user }}
* Password: {{ training_user_password }}
* SSH key file: {{ key_name }}

## How to connect with Jupyter lab

You can connect to the Lab platform using Jupyterlab in your browser. 

1. Open your browser and go to https://{{ training_host }}
   
2. Sign in with the user and password provided:
   * Username: {{ training_user }}
   * Password: {{ training_user_password }}

Note that connecting with this method will not let you open any graphical tools such as Metview.

## How to connect with a graphical desktop

You can open an XFCE graphical desktop on your lab instance following these steps:

1. Download and install X2go client on your computer. Follow the instructions here:
https://wiki.x2go.org/doku.php/start

2. Open X2go client, and create a new session with the following parameters, leaving the rest with its default values:
    * Session name: {{ ansible_facts.hostname }}
    * Host: {{ training_host }}
    * Login: {{ training_user }}
    * Use RSA/DSA key for ssh connection: path to {{ key_name }}
    * Session type: XFCE
   
3. Click on the session box to initiate your remote connection.

Note that you don't need to type the password, authentication is done through the key file provided.

If the Desktop does not resize automatically when you maximise your X2Go window, Select "Maximum availble" under Session preferences - Input/Output - Display.

## How to connect via command line

Alternatively, you can also connect to your lab on the command line, with no graphical desktop, using SSH.
On Linux or Mac, or if running on Windows using WSL, you can do:

     ssh -i {{ key_name }} -l {{ training_user }} {{ training_host }}

Note that you don't need to type the password, authentication is done through the key file provided.

On Windows, you may also use any other SSH client such as PuTTY or MobaXterm.
