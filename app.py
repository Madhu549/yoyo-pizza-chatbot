from flask import Flask,render_template,request
from flask_mysqldb import MySQL
import yaml
from datetime import datetime

#Flask app
app = Flask(__name__)


#configuration of db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']
mysql = MySQL(app)

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/webhook',methods=['POST'])
def webhook():
    print("started")
    req=request.get_json(silent=True , force=True)
    print(req)
    fulfillment=''
    query_result = req.get('queryResult')
    if (query_result.get('action') == 'pizzaorder'):
        quantity = query_result.get('parameters').get('quantity')
        toppings = query_result.get('parameters').get('toppings')
        size = query_result.get('parameters').get('size')
        print(quantity)
        print(size)
        print(toppings)
        print(datetime.now())
        ordered_items=""
        if(quantity==[]):
            for i in size:
                ordered_items+="1 "+i

        else:
            if(len(quantity)==len(size)):
                for i in range(len(size)):
                    ordered_items+=str(quantity[i])+" "+size[i]+" "
            else:
                l1,l2=len(quantity),len(size)
                for i in range(min(l1,l2)):
                    ordered_items+=str(quantity[i])+" "+size[i]+" "
        ordered_items += " ".join(toppings)
        print(ordered_items)
        formatted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(formatted_date)
        #global ordernumber
        cur = mysql.connection.cursor()
        cur.execute("SELECT MAX(order_number) from YMn71bbWVg.orders ")
        ordernumber =cur.fetchone()
        order_no=ordernumber[0]+1
        print(ordernumber[0])
        cur.execute("INSERT INTO YMn71bbWVg.orders VALUES(%s,%s,%s)", (int(order_no), formatted_date, ordered_items))
        mysql.connection.commit()
        cur.close()
        #fulfillment = 'Your order is placed sucessfully.Your order number is ' + str(ordernumber) + '.'
        fulfillment = 'Your order number is ' + str(order_no) + '.'
        order="Your order: "+ordered_items+" pizza is successfully placed."
        """
        return {
            "fulfillmentText":fulfillment,
            "displayText":'25',
            "source":"webhookdata"
        }
        """
        return {
                "fulfillmentMessages": [
                {
                    "text": {
                    "text": [
                        order,
                        fulfillment,
                        'Thank you for ordering.',
                        'Have a nice day'

                            ]
                            }
                 }
                ]
            }
    if(query_result.get('action') == 'status'):
        ordernumber = int(query_result.get('parameters').get('ordernumber'))
        print(ordernumber)
        cur = mysql.connection.cursor()
        cur.execute("SELECT ordered_time from YMn71bbWVg.orders where order_number = %s",(ordernumber,))
        time=cur.fetchone()
        if(time==None):
            text="This "+str(ordernumber)+" order number does not exist."
            return {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [

                                text,
                                'Once again check the order number that you have entered'
                            ]
                        }
                    }
                ]
            }

        diff_time=datetime.now()-time[0]
        diff_time=int(diff_time.total_seconds()//60)
        print(diff_time)
        mysql.connection.commit()
        cur.close()
        if(diff_time>=0 and diff_time<=8):
            return {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [

                                'Your Request has been processing.',
                                ''

                            ]
                        }
                    }
                ]
            }
        elif(diff_time>8 and diff_time<=50):
            return {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [

                                'Your order is on the way.',
                                'At any time you can recieve your order'

                            ]
                        }
                    }
                ]
            }
        else:
            return {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [

                                'We are sorry you did not recieve your order on time.',
                                'We experienced an unusually large number orders,which disrupted our normal delivery schedule.',
                                'To serve you better and faster , we are busy expanding our staff.',


                            ]
                        }
                    }
                ]
            }



""""{
  "fulfillmentMessages": [
    {
      "text": {
        "text": [
            fulfillment
        ]
      }
    }
  ]
}
"""



if(__name__ == '__main__'):
    app.run(debug=True,port=80)