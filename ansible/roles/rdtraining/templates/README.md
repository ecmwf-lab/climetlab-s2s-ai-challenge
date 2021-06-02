# Welcome to your ECMWF lab instance

Here are the details for your session:

* Host: {{ training_host }}
* User: {{ training_user }}
* Password: {{ training_user_password }}
* SSH key file: {{ key_name }}

## How to connect via command line

Alternatively, you can also connect to your lab on the command line, with no graphical desktop, using SSH.
On Linux or Mac, or if running on Windows using WSL, you can do:

     ssh -i {{ key_name }} -l {{ training_user }} {{ training_host }}

Note that you don't need to type the password, authentication is done through the key file provided.

On Windows, you may also use any other SSH client such as PuTTY or MobaXterm.
