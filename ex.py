import pymysql

# MySQL Connection 연결
conn = pymysql.connect(
    host="localhost", user="root", password="As731585!", db="developer", charset="utf8"
)

cursor = conn.cursor()

sql = """INSERT INTO user (email, department) VALUES (%s, %s)"""

cursor.execute(sql, ("developer_lim@limsee.com", "AI"))
cursor.execute(sql, ("developer_kim@limsee.com", "AI"))
cursor.execute(sql, ("developer_song@limsee.com", "AI"))

conn.commit()
conn.close()

