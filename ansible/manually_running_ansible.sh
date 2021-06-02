# Script to run the ansible playbok in dev mode, on a given machine
# the machine should be on the .ssh/config with appropriate ssh key set up

echo "To run this script you need to change roles/s3clients/defaults/main.yml"
echo "and create files :"
echo "   pass : sudoer password of the already created machine"
echo "   s3accesskey"
echo "   s3secretkey"
# TODO get the keys from the .s3cfg file

ansible-playbook   -i florian-ansible, s2s.yml --extra-vars "ansible_become_pass=$(cat pass)" -e "s3accesskey=$(cat s3accesskey)" -e "s3secretkey=$(cat s3secretkey)"
