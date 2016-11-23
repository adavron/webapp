#!/usr/bin/python
"""
ilmnuri audio website
Api & webapp of ilmnuri
"""

from flask import Flask, render_template, jsonify, request
import memcache
import logging
from glob import glob
import os
import operator
from random import randint
import sqlite3

app = Flask(__name__)
client = memcache.Client([('127.0.0.1', 11211)])
database = '/usr/share/nginx/html/app/tokens.db'
log_dir = '/var/log/nginx'

if not os.path.exists(log_dir):
    log_dir = '/tmp'

logging.basicConfig(filename='{0}/log_ilmnuri'.format(log_dir),
                    format='%(asctime)s  %(funcName)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

log = logging.getLogger(__name__)


@app.route('/')
def index():
    log.debug('index page rendered.')
    return render_template("index.html")


@app.route('/dars/<teacher>/')
def first(teacher):
    list_items = glob('{0}/*'.format(teacher))
    new_list = []
    for item in list_items:
        s = item.split('/')
        new_list.append(s[1])

    log.debug('/dars/{0} page rendered'.format(teacher))

    return render_template('dars.html',
                           new_list=sorted(new_list),
                           teacher=teacher)


@app.route('/dars/<teacher>/<album>/')
def category(teacher, album):
    mobile = None
    user = request.headers.get('User-Agent')
    if 'Mobile' in user:
        mobile = 'mobile'

    list_items = glob('{0}/{1}/*'.format(teacher, album))
    new_list = []
    for item in list_items:
        sz = '{0} MB'.format(os.path.getsize(item) / 1024000)
        s = item.split('/')
        new_list.append((s[2], sz))

    log.debug('/dars/{0}/{1} page rendered'.format(teacher, album))

    return render_template('track.html',
                           new_list=sorted(new_list),
                           teacher=teacher,
                           album=album,
                           mobile=mobile)


def insert_token(argument):
    con = sqlite3.connect(database)
    cur = con.cursor()
    cur.execute("INSERT INTO token_table (data) VALUES (?)", (argument,))
    con.commit()
    con.close()


@app.route('/api/v1.0/albums/', methods=['GET'])
def get_tasks():
    albums = []

    if not client.get('album'):
        log.info('Dictionary empty, executing the script.')
        os.system('/usr/share/nginx/html/get_full_list.py')
        dictionary = client.get('album')
    else:
        dictionary = client.get('album')

    dictionary['Abdulloh']['0_Appni_yangi_versiyasiga_yangilang'] = [
        'Bu_appni_versiyasi_eski.mp3',
        'iltimos_yangilab_oling.mp3',
        'Play_marketda_oxirgi_3.3_verisya_bor.mp3',
        'Yaqinda_bu_versiya_ishlamay_qolishi_mumkin.mp3']
    dictionary['Abdulloh'].pop('1_Yangi_Ramazon_2016', None)

    for key, value in dictionary.items():
        i = 1
        for k, v in value.items():
            output = {
                'id': i,
                'category': key,
                'album': k,
                'items': sorted(v)
            }
            albums.append(output)
            i += 1
    log.debug('Rendering the main albums page.')
    return jsonify({'albums': sorted(albums)})


@app.route('/api/v1.0/albums/<teacher>/', methods=['GET'])
def get_teacher(teacher):
    albums = []

    if not client.get('album'):
        log.info('Dictionary empty, executing the script.')
        os.system('/usr/share/nginx/html/get_full_list.py')
        dictionary = client.get('album')
    else:
        dictionary = client.get('album')

    dictionary['Abdulloh']['0_Appni_yangi_versiyasiga_yangilang'] = [
        'Bu_appni_versiyasi_eski.mp3',
        'iltimos_yangilab_oling.mp3',
        'Play_marketda_oxirgi_3.3_verisya_bor.mp3',
        'Yaqinda_bu_versiya_ishlamay_qolishi_mumkin.mp3']
    dictionary['Abdulloh'].pop('1_Yangi_Ramazon_2016', None)

    for key, value in dictionary.items():
        if key == teacher:
            i = 1
            for k, v in value.items():
                output = {
                    'id': i,
                    'category': key,
                    'album': k,
                    'items': sorted(v)
                }
                albums.append(output)
                i += 1

    log.debug('Rendering the category {0} page.'.format(teacher))
    return jsonify({'albums': sorted(albums)})


@app.route('/api/ios/albums/<teacher>/', methods=['GET'])
def ios_teacher(teacher):
    if not client.get('album'):
        log.info('Dictionary empty, executing the script.')
        os.system('/usr/share/nginx/html/get_full_list.py')
        dictionary = client.get('album')
    else:
        dictionary = client.get('album')

    albums = []

    for key, value in dictionary.items():
        if key == teacher:
            i = 1
            for k, v in value.items():
                output = {
                    'id': i,
                    'category': key,
                    'album': k,
                    'items': sorted([{'name': x,
                                      'url': 'http://ilmnuri.net/{0}/'
                                             '{1}/{2}'.format(key, k, x)} for x
                                     in v])
                }
                albums.append(output)
                i += 1

    log.debug('Rendering the category {0} page on ios.'.format(teacher))
    return jsonify({'albums': sorted(albums)})


@app.route('/tokens/<uuid>', methods=['POST'])
def token(uuid):
    token_id = request.json
    insert_token(token_id['data'])
    log.debug(token_id['data'])
    return jsonify({'uuid': uuid})


@app.route('/api/v2.0/albums/', methods=['GET'])
def api_ver2():
    albums = []

    if not client.get('album2'):
        log.info('Dictionary empty, executing the script.')
        os.system('/usr/share/nginx/html/get_full_list.py')
        dictionary = client.get('album2')
    else:
        dictionary = client.get('album2')

    for key, value in dictionary.items():
        for k, v in value.items():
            output = {
                'category': key,
                'album': k,
                'items': sorted([{'song_atitle': x[0],
                                  'song_id': randint(10000, 99999),
                                  'song_size': x[1]} for x in v])
            }
            albums.append(output)
    log.debug('Rendering the main albums page.')
    return jsonify({'albums': sorted(albums)})


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/huquq/')
def privacy():
    return render_template('privacy.html')


@app.route('/analytics/')
def analytics():
    return render_template('analytics.html')


@app.route('/ilmnuri/<arg>/')
def pages(arg):
    return render_template('{0}.html'.format(arg))


@app.route('/sanoq/')
def sanoq():
    con = sqlite3.connect('/usr/share/nginx/html/stats.db')
    with con:
        cur = con.cursor()
        cur.execute('select * from stats;')
        raw_data = cur.fetchall()
        data = raw_data
        log.debug(data)

    date_names = []
    counts = []
    for i in data:
        date_names.append(str(i[0]))
        counts.append(i[1])

    con = sqlite3.connect('/usr/share/nginx/html/flags.db')
    with con:
        cur = con.cursor()
        cur.execute('select * from flags;')
        f = cur.fetchall()
        log.debug(f)

    clean_list = []
    for i in f:
        clean_list.append((str(i[1].rstrip()), i[2], i[3]))
    clean_list.sort(key=operator.itemgetter(2))
    clean_list.reverse()
    log.debug(clean_list)
    total = '{:,}'.format(sum(counts))

    return render_template('sanoq.html', all=reversed(data[-35:]),
                           dt=date_names[-20:], tt=counts[-20:],
                           flags=clean_list[:30], total=total)


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)
