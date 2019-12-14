if [ `whoami` = "root" ];then
	docker run \
	-p 6379:6379 \
	-v $PWD/urldata:/data \
	--privileged=true \
	--name urlQueue \
	-d redis redis-server
	docker run \
	-p 6380:6379 \
	-v $PWD/savedata:/data \
	--privileged=true \
	--name saveQueue \
	-d redis redis-server
else
  echo "你不是root用户，请登录后执行脚本"
fi
