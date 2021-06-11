# Script to run the ansible playbok in dev mode, on a given machine
# the machine should be on the .ssh/config with appropriate ssh key set up

echo "To run this script you need to change roles/s3clients/defaults/main.yml and roles/rdtraining/defaults/main.yml (search for DEVMODE)"
echo "and create files :"
echo "   pass : sudoer password of the already created machine"
# not used: echo "   s2sadminpassword : password you want to give to the s2sadmin user"
echo "   s3accesskey" # TODO get the key from the .s3cfg file
echo "   s3secretkey" # TODO get the key from the .s3cfg file

# Install ansible with yum instead of conda.
# conda deactivate

ansible-playbook   -i florian-ansible, s2s.yml --extra-vars "ansible_become_pass=$(cat pass)" -e "s3accesskey=$(cat s3accesskey)" -e "s3secretkey=$(cat s3secretkey)" --private-key ~/.ssh/id_rsa_s2s # -e "s2sadminpassword=$(cat s2sadminpassword)" 
