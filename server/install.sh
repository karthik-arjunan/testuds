sudo pip install --upgrade setuptools
sudo apt-get install -y libffi-dev libssl-dev
sudo apt-get install -y libmysqlclient-dev
sudo apt-get install -y libcurl4-gnutls-dev
sudo apt-get install -y libpq-dev python-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev
easy_install pillow
wget https://pypi.python.org/packages/38/87/d387b8c912410b690da161143368c7582a6f1b4db1c72ab6658ce20455dc/ovirt-engine-sdk-python-4.2.2.tar.gz
tar -xvf ovirt-engine-sdk-python-4.2.2.tar.gz
cd ovirt-engine-sdk-python-4.2.2
python setup.py  install
sudo apt-get install -y mysql-server
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install coffee-script -g