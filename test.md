1. xapian + moosefs

配置：219.224.135.46是mfs master，45、47、48、60、126是chunkserver, mfssetgoal -r 3 /mnt/mfs/csv_weibo_201309

a. rsync写速度: 11MB/s

rsync -r /mnt/ds600/csv_weibo_201309/* --progress /mnt/mfs/csv_weibo_201309/

2. elasticsearch

配置：219.224.135.45、46、47、48、60、126

a. 24637609用户：平均速度：970.1498022470337 条/秒 最大速度2300条/秒, 耗时 24571.06 sec

3. cobar


