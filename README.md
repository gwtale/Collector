# Collector

--- SETUP ---

#1 - Add cron jobs:
    0 5 * * * `cd /var/Collector && python cron_retrieveVpnServiceConfig.py`
    0,5,10,15,20,25,30,35,40,45,50,55 * * * * `cd /var/Collector && python cron_checkVpnStatus.py`
    * * * * * `cd /var/Collector && python cron_uploadCache.py`

#2 - Install dependencies:
    # yum/apt install python-pip
    # pip install python-paramiko
    # pip install scp

#3 - Exchange SSH keys with server running Sherlock project
    NOTE: the same instructiosn below are also in README.md on Sherlock. Please remember to update both.

    If there is already 1 collector node deployed, replicate the file [collector]/home/cloudbr/.ssh/id_rsa to
     all other collectors, then run "ssh-copy id <new collector ip>" on Sherlock.

    If this is the first setup, create the key-pairs as following:
    - On collector node:
        If .ssh folder does not exist:
            cloudbr@colbrf1:~/$ mkdir ~/.ssh
            cloudbr@colbrf1:~/$ chmod 700 ~/.ssh
        EndIf :)

        cloudbr@colbrf1:~/$ cd .ssh
        cloudbr@colbrf1:~/.ssh$ ssh-keygen
        -----------------------------
        Generating public/private rsa key pair.
            Enter file in which to save the key (/home/cloudbr/.ssh/id_rsa):
        Enter passphrase (empty for no passphrase):
        Enter same passphrase again:
        Your identification has been saved in /home/cloudbr/.ssh/id_rsa
        Your public key has been saved in /home/cloudbr/.ssh/id_rsa.pub
        -----------------------------
        cloudbr@colbrf1:~/.ssh$ ssh-copy-id <Sherlock IP>
        -----------------------------
        The authenticity of host '192.168.10.49 (192.168.10.49)' can't be established.
        ECDSA key fingerprint is a6:f7:ea:75:57:58:a9:f6:c4:ee:90:f8:50:9c:45:1d.
        Are you sure you want to continue connecting (yes/no)? yes
        /usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
        /usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
        cloudbr@192.168.10.49's password:

        Number of key(s) added: 1

        Now try logging into the machine, with:   "ssh '192.168.10.49'"
        and check to make sure that only the key(s) you wanted were added.
        -----------------------------

    - On Sherlock node:
        cloudbr@shrelock1:~/ cd .ssh
        cloudbr@shrelock1:~/.ssh$ cat cloudbr.collectors.ssh_id.pub  >> authorized_keys

    Repeat the steps above, inverting the servers, so cross login without password can be used.
    NOTE: If Sherlock node