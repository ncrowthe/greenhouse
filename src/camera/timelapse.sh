# Create folder /home/ncrowther/projects/timelapse
# Create folder /home/ncrowther/projects/timelapse/log
# Move this file to /home/ncrowther/projects/timelapse
# chmod +rwx timelapse.sh
# sudo crontab -e
# @reboot sh /home/ncrowther/projects/timelapse/timelapse.sh > /home/ncrowther/projects/timelapse/timelapse.log
sleep_sec=60
while true
do
   python /home/ncrowther/projects/timelapse/timelapse.py
   echo "Sleep $sleep_sec seconds before next timelapse"
   sleep "$sleep_sec"
done