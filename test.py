import sqlite3 as sql
import requests
import json
try:
    with sql.connect("eComDB.db") as con:
        for i in range(1,100):
            p = 'http://www.recipepuppy.com/api/?p={}' 
            p = p.format(i)
            r = requests.get(p).json()
            cur = con.cursor()
            results = r['results']
            print('request %i successfully pulled' % i)
            j = 0
            for result in results:
                if(result['thumbnail'] != ''):
                    cur.execute("INSERT INTO items (title, href, thumbnail, ingredients) VALUES (?,?,?,?)",(result['title'], result['href'], result['thumbnail'], result['ingredients']))
                    con.commit()
                msg = "Record {} from request {} successfully added"
                # print(msg.format(j, i))
                j += 1
# except:
#     con.rollback()
#     msg = "error in insert operation"
finally:
    a = con.rollback()
    con.close()