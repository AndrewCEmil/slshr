slshr
=====
deployment
first add a new remote
    git remote add ocean ssh://slshr@192.241.131.152/home/slshr/slshr-app
then click deploy
    git push origin ocean

to get started

    sudo pip install pymongo

copy your damn ssh-keys to digital ocean

    cat .ssh/id_rsa.pub | ssh slshr@192.241.131.152 "cat >> ~/.ssh/authorized_keys"
