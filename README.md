# com-chibifire-presskit

## Generate a new presskit

```bash
# https://github.com/pixelnest/presskit.html
mkdir -p ~/.local/bin/
npm config set prefix ~/.local
CXXFLAGS="--std=c++17" npm install -g presskit
export PATH=~/.local/bin/:$PATH >> ~/.bashrc
presskit new .
```

## Build the website

```bash
# https://github.com/pixelnest/presskit.html
mkdir -p ~/.local/bin/
npm config set prefix ~/.local
CXXFLAGS="--std=c++17" npm install -g presskit
export PATH=~/.local/bin/:$PATH >> ~/.bashrc
presskit build
```

## Manuals

http://pixelnest.io/presskit.html/product/

http://pixelnest.io/presskit.html/company/
