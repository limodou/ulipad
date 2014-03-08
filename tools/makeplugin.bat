echo d ../plugins/%1 > a.txt
python getfilelist.py a.txt
python pygettext.py -f filelist.txt -o ../plugins/%1/%1.pot -K -k tr
del a.txt
