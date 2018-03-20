# encoding:utf-8

from SETTINGS import MYSQL_HOST,MYSQL_USER,MYSQL_DATABASE,MYSQL_PASSWORD
import pymysql

class ExtractInfo():

    def __init__(self):
        self.conn = pymysql.connect(
            host= MYSQL_HOST,
            user= MYSQL_USER,
            password= MYSQL_PASSWORD,
            db=MYSQL_DATABASE,
            charset='utf8mb4',
        )
        self.cursor = self.conn.cursor()
    
    def main(self):
        result= self.content()
        for i in result:
            id=i[0]
            new_content=self.remove(i[1])
            self.update_content(id,new_content)
            print('id:',i[0],',',i[2]+':has been updated!')
        self.conn.commit()


    
    def content(self):
        # sql='SELECT id,content,title FROM laws LIMIT 3'#just for test
        sql='SELECT id,content,title FROM laws'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    def remove(self,content):
        new_content= content.replace('\u3000','').replace('\n','\r\n').replace('\t','\r\n').replace('\xa0','').replace('\r\n\r\n','\r\n').replace(' ','')
        return new_content

    def update_content(self,id,new_content):
        sql='UPDATE laws SET content= %(new_content)s WHERE id=%(id)s'
        value={
            'new_content':new_content,
            'id':id
        }
        self.cursor.execute(sql,value)
    


if __name__ == "__main__":
    obj= ExtractInfo()
    obj.main()
    # for i in obj.content():
    #     print(i[1])