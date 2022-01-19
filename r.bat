@echo off
cd "C:\Users\mariu\OneDrive - BG Perchtoldsdorf\Schule\helloworld\"
if not exist %1 (
    mkdir %1
    cd %1
    echo Created Directory in \Projects
    echo # %1>"README.md"
    echo Added README
    git init
    gh repo create %1 --private=true --confirm=true --enable-wiki=false
    git add .
    git commit -m "init"
    echo Made init commit
    git push -u origin master
    echo Pushed init commit
    code .
    echo Starting VS Code...
    cd ..
    echo Finished!
) else (
    @echo on
    echo Folder already exists
)