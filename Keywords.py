import sqlite3, random, urllib2, json, time

cursor = None
connection = None


class Client:

    def __init__(self, id, balance):
        self.client_id=id
        self.balance=balance


def connect_to_db():
    global cursor, connection
    connection = sqlite3.connect('/home/nurgaliev/test/testing/web/clients.db',)
    cursor = connection.cursor()


def get_active_client():
    query = "select CLIENT_ID, BALANCE from CLIENTS inner join BALANCES on clients.CLIENT_ID = BALANCES.CLIENTS_CLIENT_ID where BALANCES.BALANCE > 0"
    cursor.execute(query)
    client_ids = cursor.fetchall()
    if len(client_ids) == 0:
        print 'There are no client in database with positive balance'
        cursor.execute('select max(client_id) from clients')
        max_existing_client_id = cursor.fetchone()[0]
        new_client_id = max_existing_client_id + 1
        cursor.execute('insert into clients values(%s, \'new_client\')' % new_client_id)
        cursor.execute('insert into balances values(%s, 5)' % new_client_id)
        connection.commit()
        return 0
    client = random.choice(client_ids)
    return Client(client[0], client[1])

def get_services(client_id=None):
    if client_id:
        data = {"client_id":client_id}
        services =__send_request('http://localhost:5000/client/services', data)
    else:
        services =__send_request('http://localhost:5000/services')

    return json.loads(services[1])['items']


def get_random_off_service(all_services, current_client_services):
    all_service_ids = [item['id'] for item in all_services]
    current_client_service_ids = [item['id'] for item in current_client_services]
    service_id = random.choice(list(set(all_service_ids) - set(current_client_service_ids)))
    for item in all_services:
        if item['id'] == service_id:
            return [service_id,item['cost']]


def activate_new_service_and_check_it(client_id, service_id):
    data = {"client_id": client_id, "service_id":service_id}
    answer =__send_request('http://localhost:5000/client/add_service', data)
    assert(answer[0]==202), 'Wrong answer code on activate new service'
    start_time = time.time()
    while True:
        services = get_services(client_id)
        service_ids = [item['id'] for item in services]
        if service_id in service_ids:
            return 1
        time.sleep(1)
        if time.time() - start_time>60:
            print 'Activation service time is expired'
            return 0

def check_balance(client, service_cost):
    query = "select BALANCE from BALANCES where BALANCES.CLIENTS_CLIENT_ID= %s" % client.client_id
    cursor.execute(query)
    end_balance = cursor.fetchone()[0]
    assert(end_balance==(client.balance-service_cost)), 'Wrong balance for client %s after activate service' % client.client_id
    return 1


def __send_request( url, data=None):
    request = urllib2.Request(url)
    if data:
        request.add_data(json.dumps(data))
    request.add_header('Content-Type', 'application/json')
    try:
        f = urllib2.urlopen(request)
        response = [f.code,f.read()]
        f.close()
    except urllib2.HTTPError as e:
        response = e.read()
    return response
