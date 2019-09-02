# frp client ui
## frp客户端ui 通过网页配置frp 客户端代理
## 目前(2019-09)还在完善中

# 如何使用？
    1 修改 config.ini中相关配置
        将[frp] config_file_path 改成运行frpc服务的主机上的frpc.ini文件的真实位置

        [admin] 中为登录本系统的用户名和密码
        
    2 pip3 install requirement.txt
    
    3 运行 python3 Server.py 默认端口 9800 可以加 --port=端口号 自定义端口
        访问 http://youhost:9800

