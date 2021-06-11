# Welcome to your ECMWF S2S instance

Here are the details for your session:

* Host: {{ training_host }}
* User: {{ training_user }}
* Password: {{ training_user_password }}
* SSH key file: {{ key_name }}

## How to connect via command line

Alternatively, you can also connect to your lab on the command line, with no graphical desktop, using SSH.
On Linux or Mac, or if running on Windows using WSL, you can do:

     ssh -i {{ key_name }} -l {{ training_user }} {{ training_host_ip }}
     ssh -i {{ key_name }} -l {{ training_user }} {{ training_host }}

On Windows, you may also use any other SSH client such as PuTTY or MobaXterm.

Note that you don't need to type the password, authentication is done through the key file provided.

## Environment

The /home disk is small and will be easily filled up.
There is a larger disk on /data: you should use /data/{{ training_user }} to store your data.

Conda and CliMetLab are pre-installed, as root, with some default packages.
You can create your own conda environment as the "{{ training_user }}" user.
CliMetLab is preinstalled for the user "{{ training_user }}", its cache directory has been set to /data/{{ training_user }}/tmp-climetlab/.

This setup is experimental, it is expected to fit your needs, but has not been extensively tested. Do not hesitate to adapt it.
For instance, you may want to setup a Jupyter lab instance and use SSH tunnel to access it.

This setup is intented for a single user "{{ training_user }}". Feel free to create more users if needed. Please do not remove the already existing users: mafp and s2sadmin.

## Support

This virtual machine is provided on a best effort basis.
When using these resources, feedback is very welcome (on https://renkulab.io/gitlab/aaron.spring/s2s-ai-challenge/-/issues) but no support is provided to maintain the system.
That is the reason why you have sudo permissions on the machine.

## Terms and conditions

The credentials have been provided to you for the sole purpose of participating to the "S2S challenge" as described in https://s2s-ai-challenge.github.io/ to improve subseasonal-to-seasonal precipitation and temperature forecasts with Machine Learning/Artificial Intelligence.
To use the EWC, you must agree with the terms and conditions (https://confluence.ecmwf.int/display/EWCLOUDKB/Terms+and+Conditions). If you do not agree with them, do not use these credentials.
Unless otherwise notified, the credentials will be disabled and the virtual machines deleted (including the data) upon termination of the "S2S challenge".
