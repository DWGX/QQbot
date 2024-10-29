import pymysql

# 连接到 MySQL 数据库
try:
    connection = pymysql.connect(
        host="localhost",      # 替换为您的主机地址（可以是 IP）
        user="dv4fplzie",      # 数据库用户名
        password="dwgx0705",    # 数据库密码
        database="dv4fplzie"   # 要访问的数据库名称
    )

    with connection.cursor() as cursor:
        # 测试查询
        cursor.execute("SHOW TABLES;")
        result = cursor.fetchall()
        print("数据库中的表：", result)

    connection.close()
except pymysql.MySQLError as e:
    print("连接失败：", e)
