slshr
=====
deployment
Add a remote for our digital ocean server. You should have previously set up your ssh keys with the server
for the 'slshr' user.

    git remote add ocean ssh://slshr@192.241.131.152/home/slshr/slshr.git

Now deploying should be as simple as this:

    git push origin ocean

to get started

    sudo pip install pymongo

copy your damn ssh-keys to digital ocean

    cat .ssh/id_rsa.pub | ssh slshr@192.241.131.152 "cat >> ~/.ssh/authorized_keys"

configuring a digital ocean server
=====
install python-pip, vim, git, everything you might need.

Install pyramid in a virtual env by following these instructions
SOURCE: https://pyramid.readthedocs.org/en/latest/narr/install.html#before-you-install

    sudo easy_install virtualenv
    virtualenv --no-site-packages env
    cd env
    bin/easy_install pyramid

Install mongodb modules

    pip install pymogno

Set up an empty git repo

    mkdir slshr.git && slshr.git
    git init --bare
