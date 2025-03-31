# How to install the game

## install prerequisites

### install build essentials

```bash
sudo apt update
sudo apt install build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```
### install [pyenv](https://github.com/pyenv/pyenv)

```bash
curl -fsSL https://pyenv.run | bash

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
```

### install python (3.12) via pyenv

```bash
pyenv install 3.12
```

## install evennia and `mygame`

### create installation folder (e.g. `~/mud`)

```bash
mkdir ~/mud
cd ~/mud
```

### download game files

```bash
git clone https://github.com/JohniFi/evennia.git
git clone https://github.com/JohniFi/mygame.git
```

### create and activate python virtual environment

```bash
pyenv local 3.12
python3 -m venv evenv
source evenv/bin/activate
```

### install evennia

```bash
pip install --upgrade pip
pip install -e evennia
```

### create `secret_settings.py`

```bash
evennia --init tempgame
mv tempgame/server/conf/secret_settings.py mygame/server/conf/secret_settings.py
rm -r tempgame
```

### start game

```bash
cd mygame
evennia migrate
evennia start
```

Enter new **superuser** credentials.

## Start on boot

### Edit the crontab to start evennia on boot:

`crontab -e`

### Add this line to the end of the file:
`@reboot /bin/bash -c 'cd ~/mud/mygame && source ../evenv/bin/activate && evennia start'`

## Upgrade

### stop evennia

```bash
cd ~/mud # your installation folder
source evenv/bin/activate
cd mygame
evennia stop
```

### upgrade `mygame` and evennia core
```bash
# upgrade mygame
git pull

# upgrade evennia core
cd ../evennia
git pull

cd ..
pip install --upgrade evennia
```

### migrate and restart evennia
```bash
cd mygame
evennia migrate
evennia start
```