# text-piped-cli

pipedcli was created to enable viewing videos from Piped without visiting the actual website. pipedcli parses Piped (currently only watch.whatever.social and piped.kavin.rocks) and provides the obtained data to stdout, allowing it to be used in a sequence of tools.

## Installation
```
git clone https://github.com/lumpsoid/text-piped-cli.git
cd text-piped-cli
chmod +x pipedcli.py
```

## Usage
you can use this tool with dmenu and mpv to selecting and viewing videos from your terminal
for example bash script:
```
#!/bin/bash

# pass list of videos to dmenu
chosen_video=$(pipedcli.py --domain 'piped.kavin.rocks' --token '<token>' -S | dmenu -i -l 30 | cut -d '|' -f4)
[ -z "${chosen_video}" ] && exit


#chosen_format=$(youtube-dl --list-formats ${chosen_video} | awk 'NR>=7 {print $1}' | dmenu -i -l 7)
chosen_format=$(echo -e '278+249\n243+249' | dmenu -i -l 7)
if [ -z "${chosen_format}" ]; then
    mpv --pause --save-position-on-quit --demuxer-max-bytes=123K ${chosen_video} &&
    exit
fi

# you can customize chache buffer (`--demuxer-max-bytes`) you can use `M` for megabytes and `K` for kilobytes
mpv --pause --save-position-on-quit --demuxer-max-bytes=123K --ytdl-format="${chosen_format}" ${chosen_video}
```
to get your token you need to log in into piped and then
- in firefox: open Developer Tools -> Inspect -> Storage -> Local Storage -> piped -> authToken
- in vivaldi: open Developer Tools -> Inspect -> Application -> Local Storage -> piped -> authToken
