#!/bin/sh

# # pass list from txt file to dmenu
# chosen_domain=$(cat ~/.local/share/qq/twitch-nicknames | dmenu -i -l 30)
# # Exit if none chosen.
# [ -z "${chosen_domain}" ] && exit

# pass list of videos to dmenu
chosen_video=$(piped-parser.py --domain 'https://piped.kavin.rocks' --token '108ea972-6152-41b0-87ef-7ce71dd2d636' -S | dmenu -i -l 30 | cut -d '|' -f4)
[ -z "${chosen_video}" ] && exit


#chosen_format=$(youtube-dl --list-formats ${chosen_video} | awk 'NR>=7 {print $1}' | dmenu -i -l 7)
chosen_format=$(echo -e '278+249\n243+249' | dmenu -i -l 7)
[ -z "${chosen_format}" ] && exit

# you can customize cash buffer (`--demuxer-max-bytes`) you can use `M` for megabytes and `K` for kilobytes
mpv --pause --save-position-on-quit --demuxer-max-bytes=123K --ytdl-format="${chosen_format}" ${chosen_video}