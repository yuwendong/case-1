ssh root@219.224.135.46

ping 192.168.1.6 (sugon ds600 G10)

ping 192.168.1.7 (sugon ds200 G10)

登陆ds600
用户名：administrator
密码：password

iscsiadm -m node -p 192.168.1.6 -u

iscsiadm -m node -p 192.168.1.6 -l

fdisk -l

mkdir -p /mnt/ds600
mount /dev/sdb /mnt/ds600

