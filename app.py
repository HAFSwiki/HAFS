# Init
import os
import re
import logging

from route.tool.func import *
from route import *

if platform.system() == 'Linux':
    for for_a in os.listdir(os.path.join("route_go", "bin")):
        os.system('chmod +x ./route_go/bin/' + for_a)

# Init-Version
with open('version.json', encoding = 'utf8') as file_data:
    version_list = json.loads(file_data.read())

# Init-DB
data_db_set = class_check_json()

db_data_get(data_db_set['type'])
do_db_set(data_db_set)

with get_db_connect() as conn:
    curs = conn.cursor()

    setup_tool = ''
    try:
        curs.execute(db_change('select data from other where name = "ver"'))
    except:
        setup_tool = 'init'

    if setup_tool != 'init':
        ver_set_data = curs.fetchall()
        if ver_set_data:
            if int(version_list['beta']['c_ver']) > int(ver_set_data[0][0]):
                setup_tool = 'update'
            else:
                setup_tool = 'normal'
        else:
            setup_tool = 'init'

    if data_db_set['type'] == 'mysql':
        try:
            curs.execute(db_change('create database ' + data_db_set['name'] + ' default character set utf8mb4'))
        except:
            try:
                curs.execute(db_change('alter database ' + data_db_set['name'] + ' character set utf8mb4'))
            except:
                pass

        conn.select_db(data_db_set['name'])

    if setup_tool != 'normal':
        create_data = get_db_table_list()
        for create_table in create_data:
            for create in ['test'] + create_data[create_table]:
                db_pass = 0

                try:
                    curs.execute(db_change('select ' + create + ' from ' + create_table + ' limit 1'))
                    db_pass = 1
                except:
                    pass

                if db_pass == 0:
                    try:
                        curs.execute(db_change('create table ' + create_table + '(test longtext default (""))'))
                        db_pass = 1
                    except Exception as e:
                        # print(e)
                        pass

                if db_pass == 0:
                    try:
                        curs.execute(db_change('create table ' + create_table + '(test longtext default "")'))
                        db_pass = 1
                    except Exception as e:
                        # print(e)
                        pass

                if db_pass == 0:
                    try:
                        curs.execute(db_change('create table ' + create_table + '(test longtext)'))
                        db_pass = 1
                    except Exception as e:
                        # print(e)
                        pass

                if db_pass == 0:
                    try:
                        curs.execute(db_change("alter table " + create_table + " add column " + create + " longtext default ('')"))
                        db_pass = 1
                    except Exception as e:
                        # print(e)
                        pass

                if db_pass == 0:
                    try:
                        curs.execute(db_change("alter table " + create_table + " add column " + create + " longtext default ''"))
                        db_pass = 1
                    except Exception as e:
                        # print(e)
                        pass

                if db_pass == 0:
                    try:
                        curs.execute(db_change("alter table " + create_table + " add column " + create + " longtext"))
                        db_pass = 1
                    except Exception as e:
                        # print(e)
                        pass

                if db_pass == 0:
                    raise
        try:
            curs.execute(db_change("create index history_index on history (title, ip)"))
        except:
            pass

        if setup_tool == 'update':
            update(conn, int(ver_set_data[0][0]), data_db_set)
        else:
            set_init(conn)

    set_init_always(conn, version_list['beta']['c_ver'])

    # Init-Route
    class EverythingConverter(werkzeug.routing.PathConverter):
        def __init__(self, map):
            super(EverythingConverter, self).__init__(map)
            self.regex = r'.*?'

        def to_python(self, value):
            return re.sub(r'^\\\.', '.', value)

    class RegexConverter(werkzeug.routing.BaseConverter):
        def __init__(self, url_map, *items):
            super(RegexConverter, self).__init__(url_map)
            self.regex = items[0]

    app = flask.Flask(
        __name__, 
        template_folder = './'
    )

    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600

    log = logging.getLogger('waitress')
    log.setLevel(logging.ERROR)

    app.jinja_env.filters['md5_replace'] = md5_replace
    app.jinja_env.filters['load_lang'] = load_lang
    app.jinja_env.filters['cut_100'] = cut_100

    app.url_map.converters['everything'] = EverythingConverter
    app.url_map.converters['regex'] = RegexConverter

    curs.execute(db_change('select data from other where name = "key"'))
    sql_data = curs.fetchall()
    app.secret_key = sql_data[0][0]

    # Init-DB_Data
    server_set = {}
    server_set_var = get_init_set_list()
    server_set_env = {
        'host' : os.getenv('NAMU_HOST'),
        'port' : os.getenv('NAMU_PORT'),
        'language' : os.getenv('NAMU_LANG'),
        'markup' : os.getenv('NAMU_MARKUP'),
        'encode' : os.getenv('NAMU_ENCRYPT')
    }
    for i in server_set_var:
        curs.execute(db_change('select data from other where name = ?'), [i])
        server_set_val = curs.fetchall()
        if server_set_val:
            server_set_val = server_set_val[0][0]
        elif server_set_env[i] != None:
            server_set_val = server_set_env[i]

            curs.execute(db_change('insert into other (name, data, coverage) values (?, ?, "")'), [i, server_set_env[i]])
        else:
            if 'list' in server_set_var[i]:
                print(server_set_var[i]['display'] + ' (' + server_set_var[i]['default'] + ') [' + ', '.join(server_set_var[i]['list']) + ']' + ' : ', end = '')
            else:
                print(server_set_var[i]['display'] + ' (' + server_set_var[i]['default'] + ') : ', end = '')

            server_set_val = input()
            if server_set_val == '':
                server_set_val = server_set_var[i]['default']
            elif server_set_var[i]['require'] == 'select':
                if not server_set_val in server_set_var[i]['list']:
                    server_set_val = server_set_var[i]['default']

            curs.execute(db_change('insert into other (name, data, coverage) values (?, ?, "")'), [i, server_set_val])

        print(server_set_var[i]['display'] + ' : ' + server_set_val)

        server_set[i] = server_set_val

def back_up(data_db_set):
    with get_db_connect() as conn:
        curs = conn.cursor()
    
        try:
            curs.execute(db_change('select data from other where name = "back_up"'))
            back_time = curs.fetchall()
            back_time = float(number_check(back_time[0][0], True)) if back_time and back_time[0][0] != '' else 0

            curs.execute(db_change('select data from other where name = "backup_count"'))
            back_up_count = curs.fetchall()
            back_up_count = int(number_check(back_up_count[0][0])) if back_up_count and back_up_count[0][0] != '' else 3

            if back_time != 0:
                curs.execute(db_change('select data from other where name = "backup_where"'))
                back_up_where = curs.fetchall()
                back_up_where = back_up_where[0][0] if back_up_where and back_up_where[0][0] != '' else data_db_set['name'] + '.db'

                print('Back up state : ' + str(back_time) + ' hours')
                print('Back up directory : ' + back_up_where)
                if back_up_count != 0:
                    print('Back up max number : ' + str(back_up_count))

                    file_dir = os.path.split(back_up_where)[0]
                    file_dir = '.' if file_dir == '' else file_dir
                    
                    file_name = os.path.split(back_up_where)[1]
                    file_name = re.sub(r'\.db$', '_[0-9]{14}.db', file_name)

                    backup_file = [for_a for for_a in os.listdir(file_dir) if re.search('^' + file_name + '$', for_a)]
                    backup_file = sorted(backup_file)
                    
                    if len(backup_file) >= back_up_count:
                        remove_dir = os.path.join(file_dir, backup_file[0])
                        os.remove(remove_dir)
                        print('Back up : Remove (' + remove_dir + ')')

                now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                new_file_name = re.sub(r'\.db$', '_' + now_time + '.db', back_up_where)
                shutil.copyfile(
                    data_db_set['name'] + '.db', 
                    new_file_name
                )

                print('Back up : OK (' + new_file_name + ')')
            else:
                print('Back up state : Turn off')

                back_time = 1
        except Exception as e:
            print('Back up : Error')
            print(e)

            back_time = 1

        threading.Timer(60 * 60 * back_time, back_up, [data_db_set]).start()

def do_every_day():
    with get_db_connect() as conn:
        curs = conn.cursor()
        
        # 오늘의 날짜 불러오기
        time_today = get_time().split()[0]
    
        # vote 관리
        curs.execute(db_change('select id, type from vote where type = "open" or type = "n_open"'))
        for for_a in curs.fetchall():
            curs.execute(db_change('select data from vote where id = ? and name = "end_date" and type = "option"'), [for_a[0]])
            db_data = curs.fetchall()
            if db_data:
                time_db = db_data[0][0].split()[0]
                if time_today > time_db:
                    curs.execute(db_change("update vote set type = ? where user = '' and id = ? and type = ?"), ['close' if for_a[1] == 'open' else 'n_close', for_a[0], for_a[1]])

        # ban 관리
        curs.execute(db_change("update rb set ongoing = '' where end < ? and end != '' and ongoing = '1'"), [get_time()])

        # auth 관리
        curs.execute(db_change('select id, data from user_set where name = "auth_date"'))
        db_data = curs.fetchall()
        for for_a in db_data:
            time_db = for_a[1].split()[0]
            if time_today > time_db:
                curs.execute(db_change("update user_set set data = 'user' where id = ? and name = 'acl'"), [for_a[0]])
                curs.execute(db_change('delete from user_set where name = "auth_date" and id = ?'), [for_a[0]])
                
        # acl 관리
        curs.execute(db_change("select doc_name, doc_rev, set_data from data_set where set_name = 'acl_date'"))
        db_data = curs.fetchall()
        for for_a in db_data:
            time_db = for_a[2].split()[0]
            if time_today > time_db:
                curs.execute(db_change("delete from acl where title = ? and type = ?"), [for_a[0], for_a[1]])
                curs.execute(db_change("delete from data_set where doc_name = ? and doc_rev = ? and set_name = 'acl_date'"), [for_a[0], for_a[1]])
                
        # ua 관리
        curs.execute(db_change('select data from other where name = "ua_expiration_date"'))
        db_data = curs.fetchall()
        if db_data and db_data[0][0] != '':
            time_db = int(number_check(db_data[0][0]))
            
            time_calc = datetime.date.today() - datetime.timedelta(days = time_db)
            time_calc = time_calc.strftime('%Y-%m-%d %H:%M:%S')
            
            curs.execute(db_change("delete from ua_d where today < ?"), [time_calc])
            
        # auth history 관리
        curs.execute(db_change('select data from other where name = "auth_history_expiration_date"'))
        db_data = curs.fetchall()
        if db_data and db_data[0][0] != '':
            time_db = int(number_check(db_data[0][0]))
            
            time_calc = datetime.date.today() - datetime.timedelta(days = time_db)
            time_calc = time_calc.strftime('%Y-%m-%d %H:%M:%S')
            
            curs.execute(db_change("delete from re_admin where time < ?"), [time_calc])

        # 사이트맵 생성 관리
        curs.execute(db_change('select data from other where name = "sitemap_auto_make"'))
        db_data = curs.fetchall()
        if db_data and db_data[0][0] != '':
            main_setting_sitemap(1)

            print('Make sitemap')

        threading.Timer(60 * 60 * 24, do_every_day).start()

def auto_do_something(data_db_set):
    if data_db_set['type'] == 'sqlite':
        back_up(data_db_set)

    do_every_day()

auto_do_something(data_db_set)

print('Now running... http://localhost:' + server_set['port'])
    
# Init-custom
if os.path.exists('custom.py'):
    from custom import custom_run
    custom_run('error', app)

db_set_str = json.dumps(data_db_set)

# Func
# Func-inter_wiki
app.route('/filter/inter_wiki', defaults = { 'tool' : 'inter_wiki' })(filter_all)
app.route('/filter/inter_wiki/add', methods = ['POST', 'GET'], defaults = { 'tool' : 'inter_wiki' })(filter_all_add)
app.route('/filter/inter_wiki/add/<everything:name>', methods = ['POST', 'GET'], defaults = { 'tool' : 'inter_wiki' })(filter_all_add)
app.route('/filter/inter_wiki/del/<everything:name>', defaults = { 'tool' : 'inter_wiki' })(filter_all_delete)

app.route('/filter/outer_link', defaults = { 'tool' : 'outer_link' })(filter_all)
app.route('/filter/outer_link/add', methods = ['POST', 'GET'], defaults = { 'tool' : 'outer_link' })(filter_all_add)
app.route('/filter/outer_link/add/<everything:name>', methods = ['POST', 'GET'], defaults = { 'tool' : 'outer_link' })(filter_all_add)
app.route('/filter/outer_link/del/<everything:name>', defaults = { 'tool' : 'outer_link' })(filter_all_delete)

app.route('/filter/document', defaults = { 'tool' : 'document' })(filter_all)
app.route('/filter/document/add', methods = ['POST', 'GET'], defaults = { 'tool' : 'document' })(filter_all_add)
app.route('/filter/document/add/<everything:name>', methods = ['POST', 'GET'], defaults = { 'tool' : 'document' })(filter_all_add)
app.route('/filter/document/del/<everything:name>', defaults = { 'tool' : 'document' })(filter_all_delete)

app.route('/filter/edit_top', defaults = { 'tool' : 'edit_top' })(filter_all)
app.route('/filter/edit_top/add', methods = ['POST', 'GET'], defaults = { 'tool' : 'edit_top' })(filter_all_add)
app.route('/filter/edit_top/add/<everything:name>', methods = ['POST', 'GET'], defaults = { 'tool' : 'edit_top' })(filter_all_add)
app.route('/filter/edit_top/del/<everything:name>', defaults = { 'tool' : 'edit_top' })(filter_all_delete)

app.route('/filter/image_license', defaults = { 'tool' : 'image_license' })(filter_all)
app.route('/filter/image_license/add', methods = ['POST', 'GET'], defaults = { 'tool' : 'image_license' })(filter_all_add)
app.route('/filter/image_license/del/<everything:name>', defaults = { 'tool' : 'image_license' })(filter_all_delete)

app.route('/filter/template', defaults = { 'tool' : 'template' })(filter_all)
app.route('/filter/template/add', methods = ['POST', 'GET'], defaults = { 'tool' : 'template' })(filter_all_add)
app.route('/filter/template/add/<everything:name>', methods = ['POST', 'GET'], defaults = { 'tool' : 'template' })(filter_all_add)
app.route('/filter/template/del/<everything:name>', defaults = { 'tool' : 'template' })(filter_all_delete)

app.route('/filter/edit_filter', defaults = { 'tool' : 'edit_filter' })(filter_all)
app.route('/filter/edit_filter/add', methods = ['POST', 'GET'], defaults = { 'tool' : 'edit_filter' })(filter_all_add)
app.route('/filter/edit_filter/add/<everything:name>', methods = ['POST', 'GET'], defaults = { 'tool' : 'edit_filter' })(filter_all_add)
app.route('/filter/edit_filter/del/<everything:name>', defaults = { 'tool' : 'edit_filter' })(filter_all_delete)

app.route('/filter/email_filter', defaults = { 'tool' : 'email_filter' })(filter_all)
app.route('/filter/email_filter/add', methods = ['POST', 'GET'], defaults = { 'tool' : 'email_filter' })(filter_all_add)
app.route('/filter/email_filter/del/<everything:name>', defaults = { 'tool' : 'email_filter' })(filter_all_delete)

app.route('/filter/file_filter', defaults = { 'tool' : 'file_filter' })(filter_all)
app.route('/filter/file_filter/add', methods = ['POST', 'GET'], defaults = { 'tool' : 'file_filter' })(filter_all_add)
app.route('/filter/file_filter/del/<everything:name>', defaults = { 'tool' : 'file_filter' })(filter_all_delete)

app.route('/filter/name_filter', defaults = { 'tool' : 'name_filter' })(filter_all)
app.route('/filter/name_filter/add', methods = ['POST', 'GET'], defaults = { 'tool' : 'name_filter' })(filter_all_add)
app.route('/filter/name_filter/del/<everything:name>', defaults = { 'tool' : 'name_filter' })(filter_all_delete)

app.route('/filter/extension_filter', defaults = { 'tool' : 'extension_filter' })(filter_all)
app.route('/filter/extension_filter/add', methods = ['POST', 'GET'], defaults = { 'tool' : 'extension_filter' })(filter_all_add)
app.route('/filter/extension_filter/del/<everything:name>', defaults = { 'tool' : 'extension_filter' })(filter_all_delete)

# Func-list
app.route('/list/document/old', defaults = { 'set_type' : 'old' })(list_old_page)
app.route('/list/document/old/<int:num>', defaults = { 'set_type' : 'old' })(list_old_page)

app.route('/list/document/new', defaults = { 'set_type' : 'new' })(list_old_page)
app.route('/list/document/new/<int:num>', defaults = { 'set_type' : 'new' })(list_old_page)

app.route('/list/document/no_link')(list_no_link)
app.route('/list/document/no_link/<int:num>')(list_no_link)

app.route('/list/document/acl')(list_acl)
app.route('/list/document/acl/<int:arg_num>')(list_acl)

app.route('/list/document/need')(list_please)
app.route('/list/document/need/<int:arg_num>')(list_please)

app.route('/list/document/all')(list_title_index)
app.route('/list/document/all/<int:num>')(list_title_index)

app.route('/list/document/long')(list_long_page)
app.route('/list/document/long/<int:arg_num>')(list_long_page)

app.route('/list/document/short', defaults = { 'tool' : 'short_page' })(list_long_page)
app.route('/list/document/short/<int:arg_num>', defaults = { 'tool' : 'short_page' })(list_long_page)

app.route('/list/file')(list_image_file)
app.route('/list/file/<int:arg_num>')(list_image_file)
app.route('/list/image', defaults = { 'do_type' : 1 })(list_image_file)
app.route('/list/image/<int:arg_num>', defaults = { 'do_type' : 1 })(list_image_file)

app.route('/list/admin')(list_admin)

app.route('/list/admin/auth_use', methods = ['POST', 'GET'])(list_admin_auth_use)
app.route('/list/admin/auth_use_page/<int:arg_num>/<everything:arg_search>', methods = ['POST', 'GET'])(list_admin_auth_use)

app.route('/list/user')(list_user)
app.route('/list/user/<int:arg_num>')(list_user)

app.route('/list/user/check/<name>')(list_user_check)
app.route('/list/user/check/<name>/<do_type>')(list_user_check)
app.route('/list/user/check/<name>/<do_type>/<int:arg_num>')(list_user_check)
app.route('/list/user/check/<name>/<do_type>/<int:arg_num>/<plus_name>')(list_user_check)
app.route('/list/user/check/delete/<name>/<ip>/<time>/<do_type>', methods = ['POST', 'GET'])(list_user_check_delete)

# Func-auth
app.route('/auth/give', methods = ['POST', 'GET'])(give_auth)
app.route('/auth/give/<name>', methods = ['POST', 'GET'])(give_auth)

app.route('/auth/give/ban', methods = ['POST', 'GET'])(give_user_ban)
app.route('/auth/give/ban/<everything:name>', methods = ['POST', 'GET'])(give_user_ban)
app.route('/auth/give/ban_cidr/<everything:name>', methods = ['POST', 'GET'], defaults = { 'ban_type' : 'cidr' })(give_user_ban)
app.route('/auth/give/ban_regex/<everything:name>', methods = ['POST', 'GET'], defaults = { 'ban_type' : 'regex' })(give_user_ban)
app.route('/auth/give/ban_multiple', methods = ['POST', 'GET'], defaults = { 'ban_type' : 'multiple' })(give_user_ban)

# /auth/list
# /auth/list/add/<name>
# /auth/list/delete/<name>
app.route('/auth/list')(list_admin_group_2)
app.route('/auth/list/add/<name>', methods = ['POST', 'GET'])(give_admin_groups_2)
app.route('/auth/list/delete/<name>', methods = ['POST', 'GET'])(give_delete_admin_group_2)

app.route('/auth/give/fix/<user_name>', methods = ['POST', 'GET'])(give_user_fix)

app.route('/app_submit', methods = ['POST', 'GET'])(recent_app_submit_2)

# /auth/history
app.route('/recent_block')(list_recent_block)
app.route('/recent_block/all')(list_recent_block)
app.route('/recent_block/all/<int:num>')(list_recent_block)
app.route('/recent_block/user/<user_name>', defaults = { 'tool' : 'user' })(list_recent_block)
app.route('/recent_block/user/<user_name>/<int:num>', defaults = { 'tool' : 'user' })(list_recent_block)
app.route('/recent_block/admin/<user_name>', defaults = { 'tool' : 'admin' })(list_recent_block)
app.route('/recent_block/admin/<user_name>/<int:num>', defaults = { 'tool' : 'admin' })(list_recent_block)
app.route('/recent_block/regex', defaults = { 'tool' : 'regex' })(list_recent_block)
app.route('/recent_block/regex/<int:num>', defaults = { 'tool' : 'regex' })(list_recent_block)
app.route('/recent_block/cidr', defaults = { 'tool' : 'cidr' })(list_recent_block)
app.route('/recent_block/cidr/<int:num>', defaults = { 'tool' : 'cidr' })(list_recent_block)
app.route('/recent_block/ongoing', defaults = { 'tool' : 'ongoing' })(list_recent_block)
app.route('/recent_block/ongoing/<int:num>', defaults = { 'tool' : 'ongoing' })(list_recent_block)

app.route('/recent_change')(list_recent_change)
app.route('/recent_changes')(list_recent_change)
app.route('/recent_change/<int:num>/<set_type>')(list_recent_change)

app.route('/recent_discuss', defaults = { 'tool' : 'normal' })(list_recent_discuss)
app.route('/recent_discuss/<int:num>/<tool>')(list_recent_discuss)

# Func-history
app.route('/recent_edit_request', defaults = { 'db_set' : db_set_str })(recent_edit_request)

app.route('/record/<name>', defaults = { 'tool' : 'record' })(recent_change)
app.route('/record/<int:num>/<set_type>/<name>', defaults = { 'tool' : 'record' })(recent_change)

app.route('/record/reset/<name>', methods = ['POST', 'GET'])(recent_record_reset)
app.route('/record/topic/<name>')(recent_record_topic)

app.route('/record/bbs/<name>', defaults = { 'tool' : 'record' })(bbs_w)
app.route('/record/bbs_comment/<name>', defaults = { 'tool' : 'comment_record' })(bbs_w)

app.route('/history/<everything:name>', defaults = { 'tool' : 'history' }, methods = ['POST', 'GET'])(recent_change)
app.route('/history_page/<int:num>/<set_type>/<everything:name>', defaults = { 'tool' : 'history' }, methods = ['POST', 'GET'])(recent_change)

app.route('/history_tool/<int(signed = True):rev>/<everything:name>')(recent_history_tool)
app.route('/history_delete/<int(signed = True):rev>/<everything:name>', methods = ['POST', 'GET'])(recent_history_delete)
app.route('/history_hidden/<int(signed = True):rev>/<everything:name>')(recent_history_hidden)
app.route('/history_send/<int(signed = True):rev>/<everything:name>', methods = ['POST', 'GET'])(recent_history_send)
app.route('/history_reset/<everything:name>', methods = ['POST', 'GET'])(recent_history_reset)
app.route('/history_add/<everything:name>', methods = ['POST', 'GET'])(recent_history_add)

# Func-view
app.route('/xref/<everything:name>')(view_xref)
app.route('/xref_page/<int:num>/<everything:name>')(view_xref)
app.route('/xref_this/<everything:name>', defaults = { 'xref_type' : 2 })(view_xref)
app.route('/xref_this_page/<int:num>/<everything:name>', defaults = { 'xref_type' : 2 })(view_xref)

app.route('/doc_watch_list/<int:num>/<everything:name>')(w_watch_list)
app.route('/doc_star_doc/<int:num>/<everything:name>', defaults = { 'do_type' : 'star_doc' })(w_watch_list)

app.route('/raw/<everything:name>')(view_w_raw)
app.route('/raw_acl/<everything:name>', defaults = { 'doc_acl' : 'on' })(view_w_raw)
app.route('/raw_rev/<int(signed = True):rev>/<everything:name>')(view_w_raw)

app.route('/diff/<int(signed = True):num_a>/<int(signed = True):num_b>/<everything:name>')(view_diff)

app.route('/down/<everything:name>')(view_down)

app.route('/acl/<everything:name>', methods = ['POST', 'GET'])(view_set)

app.route('/w_from/<everything:name>', defaults = { 'do_type' : 'from' })(view_w)
app.route('/w/<everything:name>')(view_w)

app.route('/random', defaults = { 'db_set' : db_set_str })(view_random)

# Func-edit
app.route('/edit/<everything:name>', methods = ['POST', 'GET'])(edit)
app.route('/edit_from/<everything:name>', methods = ['POST', 'GET'], defaults = { 'do_type' : 'load' })(edit)
app.route('/edit_section/<int:section>/<everything:name>', methods = ['POST', 'GET'])(edit)

app.route('/edit_request/<everything:name>', methods = ['POST', 'GET'])(edit_request)
app.route('/edit_request_from/<everything:name>', defaults = { 'do_type' : 'from' }, methods = ['POST', 'GET'])(edit_request)

# app.route('/edit_request_rev/<int:rev>/<everything:name>', methods = ['POST', 'GET'])(edit_request)

app.route('/upload', methods = ['POST', 'GET'])(edit_upload)

# 개편 예정
app.route('/xref_reset/<everything:name>')(edit_backlink_reset)

app.route('/delete/<everything:name>', methods = ['POST', 'GET'])(edit_delete)
app.route('/delete_file/<everything:name>', methods = ['POST', 'GET'])(edit_delete_file)
app.route('/delete_multiple', methods = ['POST', 'GET'])(edit_delete_multiple)

app.route('/revert/<int:num>/<everything:name>', methods = ['POST', 'GET'])(edit_revert)

app.route('/move/<everything:name>', methods = ['POST', 'GET'])(edit_move)

# Func-topic
app.route('/topic/<everything:name>', methods = ['POST', 'GET'])(topic_list)
app.route('/topic_page/<int:page>/<everything:name>', methods = ['POST', 'GET'])(topic_list)

app.route('/thread/<int:topic_num>', methods = ['POST', 'GET'])(topic)
app.route('/thread/0/<everything:doc_name>', defaults = { 'topic_num' : '0' }, methods = ['POST', 'GET'])(topic)

app.route('/thread/<int:topic_num>/tool')(topic_tool)
app.route('/thread/<int:topic_num>/setting', methods = ['POST', 'GET'])(topic_tool_setting)
app.route('/thread/<int:topic_num>/acl', methods = ['POST', 'GET'])(topic_tool_acl)
app.route('/thread/<int:topic_num>/delete', methods = ['POST', 'GET'])(topic_tool_delete)
app.route('/thread/<int:topic_num>/change', methods = ['POST', 'GET'])(topic_tool_change)

app.route('/thread/<int:topic_num>/comment/<int:num>/tool')(topic_comment_tool)
app.route('/thread/<int:topic_num>/comment/<int:num>/notice')(topic_comment_notice)
app.route('/thread/<int:topic_num>/comment/<int:num>/blind')(topic_comment_blind)
app.route('/thread/<int:topic_num>/comment/<int:num>/raw')(view_raw)
app.route('/thread/<int:topic_num>/comment/<int:num>/delete', methods = ['POST', 'GET'])(topic_comment_delete)

# Func-user
app.route('/change', methods = ['POST', 'GET'])(user_setting)
app.route('/change/key')(user_setting_key)
app.route('/change/key/delete')(user_setting_key_delete)
app.route('/change/pw', methods = ['POST', 'GET'])(user_setting_pw)
app.route('/change/head', methods = ['GET', 'POST'], defaults = { 'skin_name' : '' })(user_setting_head)
app.route('/change/head/<skin_name>', methods = ['GET', 'POST'])(user_setting_head)
app.route('/change/head_reset', methods = ['GET', 'POST'])(user_setting_head_reset)
app.route('/change/skin_set')(user_setting_skin_set)
app.route('/change/top_menu', methods = ['GET', 'POST'])(user_setting_top_menu)
app.route('/change/user_name', methods = ['GET', 'POST'])(user_setting_user_name)
app.route('/change/user_name/<user_name>', methods = ['GET', 'POST'])(user_setting_user_name)
# 하위 호환용 S
app.route('/skin_set')(user_setting_skin_set)
# 하위 호환용 E
app.route('/change/skin_set/main', methods = ['POST', 'GET'])(user_setting_skin_set_main)

app.route('/user')(user_info)
app.route('/user/<name>')(user_info)

app.route('/challenge', methods = ['GET', 'POST'])(user_challenge)

app.route('/edit_filter/<name>', methods = ['GET', 'POST'])(user_edit_filter)

app.route('/count')(user_count)
app.route('/count/<name>')(user_count)

app.route('/alarm')(user_alarm)
app.route('/alarm/delete')(user_alarm_delete)
app.route('/alarm/delete/<int:id>')(user_alarm_delete)

app.route('/watch_list', defaults = { 'tool' : 'watch_list' })(user_watch_list)
app.route('/watch_list/<everything:name>', defaults = { 'tool' : 'watch_list' })(user_watch_list_name)
app.route('/watch_list_from/<everything:name>', defaults = { 'tool' : 'watch_list_from' })(user_watch_list_name)

app.route('/star_doc', defaults = { 'tool' : 'star_doc' })(user_watch_list)
app.route('/star_doc/<everything:name>', defaults = { 'tool' : 'star_doc' })(user_watch_list_name)
app.route('/star_doc_from/<everything:name>', defaults = { 'tool' : 'star_doc_from' })(user_watch_list_name)

# 개편 보류중 S
app.route('/change/email', methods = ['POST', 'GET'])(user_setting_email_2)
app.route('/change/email/delete')(user_setting_email_delete)
app.route('/change/email/check', methods = ['POST', 'GET'])(user_setting_email_check_2)
# 개편 보류중 E

# Func-login
# 개편 예정

# login -> login/2fa -> login/2fa/email with login_id
# register -> register/email -> regiter/email/check with reg_id
# pass_find -> pass_find/email with find_id

app.route('/login', methods = ['POST', 'GET'])(login_login_2)
app.route('/login/2fa', methods = ['POST', 'GET'])(login_login_2fa_2)
app.route('/register', methods = ['POST', 'GET'])(login_register_2)
app.route('/register/email', methods = ['POST', 'GET'])(login_register_email_2)
app.route('/register/email/check', methods = ['POST', 'GET'])(login_register_email_check_2)
app.route('/register/submit', methods = ['POST', 'GET'])(login_register_submit_2)

app.route('/login/find')(login_find)
app.route('/login/find/key', methods = ['POST', 'GET'])(login_find_key)
app.route('/login/find/email', methods = ['POST', 'GET'], defaults = { 'tool' : 'pass_find' })(login_find_email)
app.route('/login/find/email/check', methods = ['POST', 'GET'], defaults = { 'tool' : 'check_key' })(login_find_email_check)
app.route('/logout')(login_logout)

# Func-vote
app.route('/vote/<int:num>', methods = ['POST', 'GET'])(vote_select)
app.route('/vote/end/<int:num>')(vote_end)
app.route('/vote/close/<int:num>')(vote_close)
app.route('/vote', defaults = { 'list_type' : 'normal' })(vote_list)
app.route('/vote/list', defaults = { 'list_type' : 'normal' })(vote_list)
app.route('/vote/list/<int:num>', defaults = { 'list_type' : 'normal' })(vote_list)
app.route('/vote/list/close', defaults = { 'list_type' : 'close' })(vote_list)
app.route('/vote/list/close/<int:num>', defaults = { 'list_type' : 'close' })(vote_list)
app.route('/vote/add', methods = ['POST', 'GET'])(vote_add)

# Func-bbs
app.route('/bbs/main')(bbs_main)
app.route('/bbs/make', methods = ['POST', 'GET'])(bbs_make)
# app.route('/bbs/main/set')
app.route('/bbs/in/<int:bbs_num>')(bbs_in)
app.route('/bbs/in/<int:bbs_num>/<int:page>')(bbs_in)
# app.route('/bbs/blind/<int:bbs_num>', methods = ['POST', 'GET'])(bbs_hide)
app.route('/bbs/delete/<int:bbs_num>', methods = ['POST', 'GET'])(bbs_delete)
app.route('/bbs/set/<int:bbs_num>', methods = ['POST', 'GET'])(bbs_w_set)
app.route('/bbs/edit/<int:bbs_num>', methods = ['POST', 'GET'])(bbs_w_edit)
app.route('/bbs/w/<int:bbs_num>/<int:post_num>', methods = ['POST', 'GET'])(bbs_w_post)
# app.route('/bbs/blind/<int:bbs_num>/<int:post_num>', methods = ['POST', 'GET'])(bbs_w_hide)
app.route('/bbs/pinned/<int:bbs_num>/<int:post_num>', methods = ['POST', 'GET'])(bbs_w_pinned)
app.route('/bbs/delete/<int:bbs_num>/<int:post_num>', methods = ['POST', 'GET'])(bbs_w_delete)
app.route('/bbs/raw/<int:bbs_num>/<int:post_num>')(view_raw)
app.route('/bbs/tool/<int:bbs_num>/<int:post_num>')(bbs_w_tool)
app.route('/bbs/edit/<int:bbs_num>/<int:post_num>', methods = ['POST', 'GET'])(bbs_w_edit)
app.route('/bbs/tool/<int:bbs_num>/<int:post_num>/<comment_num>')(bbs_w_comment_tool)
app.route('/bbs/raw/<int:bbs_num>/<int:post_num>/<comment_num>')(view_raw)
app.route('/bbs/edit/<int:bbs_num>/<int:post_num>/<comment_num>', methods = ['POST', 'GET'])(bbs_w_edit)
app.route('/bbs/delete/<int:bbs_num>/<int:post_num>/<comment_num>', methods = ['POST', 'GET'])(bbs_w_delete)

# Func-api
## v1 API
app.route('/api/render', methods = ['POST'], defaults = { 'db_set' : db_set_str })(api_w_render)
app.route('/api/render/<tool>', methods = ['POST'], defaults = { 'db_set' : db_set_str })(api_w_render)

app.route('/api/raw_exist/<everything:name>', defaults = { 'exist_check' : 'on', 'db_set' : db_set_str })(api_w_raw)
app.route('/api/raw_rev/<int(signed = True):rev>/<everything:name>', defaults = { 'db_set' : db_set_str })(api_w_raw)
app.route('/api/raw/<everything:name>', defaults = { 'db_set' : db_set_str })(api_w_raw)

app.route('/api/xref/<int:num>/<everything:name>', defaults = { 'db_set' : db_set_str })(api_w_xref)
app.route('/api/xref_this/<int:num>/<everything:name>', defaults = { 'xref_type' : '2', 'db_set' : db_set_str })(api_w_xref)

app.route('/api/random', defaults = { 'db_set' : db_set_str })(api_w_random)

app.route('/api/bbs/w/<sub_code>')(api_bbs_w_post)
app.route('/api/bbs/w/comment/<sub_code>')(api_bbs_w_comment)
app.route('/api/bbs/w/comment_one/<sub_code>')(api_bbs_w_comment)

app.route('/api/version', defaults = { 'version_list' : version_list })(api_version)
app.route('/api/skin_info')(api_skin_info)
app.route('/api/skin_info/<name>')(api_skin_info)
app.route('/api/user_info/<user_name>')(api_user_info)
app.route('/api/setting/<name>')(api_setting)

app.route('/api/auth_list', defaults = { 'db_set' : db_set_str })(api_func_auth_list)
app.route('/api/auth_list/<user_name>', defaults = { 'db_set' : db_set_str })(api_func_auth_list)

app.route('/api/thread/<int:topic_num>/<int:s_num>/<int:e_num>', defaults = { 'db_set' : db_set_str })(api_topic)
app.route('/api/thread/<int:topic_num>/<tool>', defaults = { 'db_set' : db_set_str })(api_topic)
app.route('/api/thread/<int:topic_num>', defaults = { 'db_set' : db_set_str })(api_topic)

app.route('/api/search/<everything:name>', defaults = { 'db_set' : db_set_str })(api_search)
app.route('/api/search_page/<int:num>/<everything:name>', defaults = { 'db_set' : db_set_str })(api_search)
app.route('/api/search_data/<everything:name>', defaults = { 'search_type' : 'data', 'db_set' : db_set_str })(api_search)
app.route('/api/search_data_page/<int:num>/<everything:name>', defaults = { 'search_type' : 'data', 'db_set' : db_set_str })(api_search)

app.route('/api/recent_change', defaults = { 'db_set' : db_set_str })(api_list_recent_change)
app.route('/api/recent_changes', defaults = { 'db_set' : db_set_str })(api_list_recent_change)
app.route('/api/recent_change/<int:limit>', defaults = { 'db_set' : db_set_str })(api_list_recent_change)
app.route('/api/recent_change/<int:limit>/<set_type>/<int:num>', defaults = { 'db_set' : db_set_str })(api_list_recent_change)

app.route('/api/recent_edit_request', defaults = { 'db_set' : db_set_str })(api_list_recent_edit_request)
app.route('/api/recent_edit_request/<int:limit>/<set_type>/<int:num>', defaults = { 'db_set' : db_set_str })(api_list_recent_edit_request)

app.route('/api/recent_discuss/<set_type>/<int:limit>', defaults = { 'db_set' : db_set_str })(api_list_recent_discuss)
app.route('/api/recent_discuss/<int:limit>', defaults = { 'db_set' : db_set_str })(api_list_recent_discuss)
app.route('/api/recent_discuss', defaults = { 'db_set' : db_set_str })(api_list_recent_discuss)

app.route('/api/lang', methods = ['POST'], defaults = { 'db_set' : db_set_str })(api_func_language)
app.route('/api/lang/<data>', defaults = { 'db_set' : db_set_str })(api_func_language)
app.route('/api/sha224/<everything:data>')(api_func_sha224)
app.route('/api/ip/<everything:data>', defaults = { 'db_set' : db_set_str })(api_func_ip)

app.route('/api/image/<everything:name>')(api_image_view)

## v2 API
app.route('/api/v2/recent_edit_request/<set_type>/<int:num>', defaults = { 'db_set' : db_set_str, 'limit' : 50 })(api_list_recent_edit_request)
app.route('/api/v2/recent_change/<set_type>/<int:num>', defaults = { 'db_set' : db_set_str, 'legacy' : '', 'limit' : 50 })(api_list_recent_change)
app.route('/api/v2/recent_discuss/<set_type>/<int:num>', defaults = { 'db_set' : db_set_str, 'legacy' : '', 'limit' : 50 })(api_list_recent_discuss)
app.route('/api/v2/recent_block/<set_type>/<int:num>', defaults = { 'db_set' : db_set_str })(api_list_recent_block)
app.route('/api/v2/recent_block/<set_type>/<int:num>/<user_name>', defaults = { 'db_set' : db_set_str })(api_list_recent_block)
app.route('/api/v2/list/document/old/<int:num>', defaults = { 'db_set' : db_set_str, 'set_type' : 'old' })(api_list_old_page)
app.route('/api/v2/list/document/new/<int:num>', defaults = { 'db_set' : db_set_str, 'set_type' : 'new' })(api_list_old_page)
app.route('/api/v2/list/document/<int:num>', defaults = { 'db_set' : db_set_str })(api_list_title_index)

app.route('/api/v2/topic/<int:num>/<set_type>/<everything:name>', defaults = { 'db_set' : db_set_str })(api_topic_list)

app.route('/api/v2/bbs', defaults = { 'db_set' : db_set_str })(api_bbs_list)
app.route('/api/v2/bbs/main', defaults = { 'db_set' : db_set_str })(api_bbs)
app.route('/api/v2/bbs/in/<int:bbs_num>/<int:page>', defaults = { 'db_set' : db_set_str })(api_bbs)
app.route('/api/v2/bbs/w/comment/<int:bbs_num>/<int:post_num>/<tool>', defaults = { 'db_set' : db_set_str })(api_bbs_w_comment_n)

app.route('/api/v2/doc_star_doc/<int:num>/<everything:name>', defaults = { 'db_set' : db_set_str, 'do_type' : 'star_doc' })(api_w_watch_list)
app.route('/api/v2/doc_watch_list/<int:num>/<everything:name>', defaults = { 'db_set' : db_set_str })(api_w_watch_list)
app.route('/api/v2/set_reset/<everything:name>', defaults = { 'db_set' : db_set_str })(api_w_set_reset)

app.route('/api/v2/setting/<name>', methods = ['GET', 'PUT'], defaults = { 'db_set' : db_set_str })(api_setting)

app.route('/api/v2/user/setting/editor', methods = ['GET', 'POST', 'DELETE'], defaults = { 'db_set' : db_set_str })(api_user_setting_editor)

app.route('/api/v2/ip/<everything:data>', defaults = { 'db_set' : db_set_str })(api_func_ip)
app.route('/api/v2/ip_menu/<everything:ip>', defaults = { 'db_set' : db_set_str, 'option' : 'user' })(api_func_ip_menu)
app.route('/api/v2/user_menu/<everything:ip>', defaults = { 'db_set' : db_set_str })(api_func_ip_menu)

# Func-main
# 여기도 전반적인 조정 시행 예정
app.route('/other')(main_tool_other)
app.route('/manager', methods = ['POST', 'GET'])(main_tool_admin)
app.route('/manager/<int:num>', methods = ['POST', 'GET'])(main_tool_redirect)
app.route('/manager/<int:num>/<everything:add_2>', methods = ['POST', 'GET'])(main_tool_redirect)

app.route('/search', methods=['POST'])(main_search)
app.route('/search/<everything:name>', defaults = { 'db_set' : db_set_str }, methods = ['POST', 'GET'])(main_search_deep)
app.route('/search_page/<int:num>/<everything:name>', defaults = { 'db_set' : db_set_str }, methods = ['POST', 'GET'])(main_search_deep)
app.route('/search_data/<everything:name>', defaults = { 'search_type' : 'data', 'db_set' : db_set_str }, methods = ['POST', 'GET'])(main_search_deep)
app.route('/search_data_page/<int:num>/<everything:name>', defaults = { 'search_type' : 'data', 'db_set' : db_set_str }, methods = ['POST', 'GET'])(main_search_deep)
app.route('/goto', methods=['POST'])(main_search_goto)
app.route('/goto/<everything:name>', methods=['GET', 'POST'])(main_search_goto)

app.route('/setting')(main_setting)
app.route('/setting/main', defaults = { 'db_set' : data_db_set['type'] }, methods = ['POST', 'GET'])(main_setting_main)
app.route('/setting/main/logo', methods = ['POST', 'GET'])(main_setting_main_logo)
app.route('/setting/top_menu', methods = ['POST', 'GET'])(main_setting_top_menu)
app.route('/setting/phrase', methods = ['POST', 'GET'])(main_setting_phrase)
app.route('/setting/head', defaults = { 'num' : 3 }, methods = ['POST', 'GET'])(main_setting_head)
app.route('/setting/head/<skin_name>', defaults = { 'num' : 3 }, methods = ['POST', 'GET'])(main_setting_head)
app.route('/setting/body/top', defaults = { 'num' : 4 }, methods = ['POST', 'GET'])(main_setting_head)
app.route('/setting_preview/body/top', defaults = { 'num' : 4, 'set_preview' : 1 }, methods = ['POST'])(main_setting_head)
app.route('/setting/body/bottom', defaults = { 'num' : 7 }, methods = ['POST', 'GET'])(main_setting_head)
app.route('/setting_preview/body/bottom', defaults = { 'num' : 7, 'set_preview' : 1 }, methods = ['POST'])(main_setting_head)
app.route('/setting/robot', methods = ['POST', 'GET'])(main_setting_robot)
app.route('/setting/external', methods = ['POST', 'GET'])(main_setting_external)
app.route('/setting/acl', methods = ['POST', 'GET'])(main_setting_acl)
app.route('/setting/sitemap', methods = ['POST', 'GET'])(main_setting_sitemap)
app.route('/setting/sitemap_set', methods = ['POST', 'GET'])(main_setting_sitemap_set)
app.route('/setting/skin_set', methods = ['POST', 'GET'])(main_setting_skin_set)
app.route('/setting/404_page', methods = ['POST', 'GET'])(setting_404_page)

app.route('/easter_egg')(main_func_easter_egg)

# views -> view
app.route('/view/<path:name>')(main_view)
app.route('/views/<path:name>')(main_view)
app.route('/image/<path:name>')(main_view_image)
# 조정 계획 중
app.route('/<regex("[^.]+\\.(?:txt|xml|ico)"):data>')(main_view_file)

app.route('/shutdown', methods = ['POST', 'GET'])(main_sys_shutdown)
app.route('/restart', methods = ['POST', 'GET'])(main_sys_restart)
app.route('/update', methods = ['POST', 'GET'])(main_sys_update)

app.errorhandler(404)(main_func_error_404)

if __name__ == "__main__":
    waitress.serve(
        app,
        host = server_set['host'],
        port = int(server_set['port']),
        clear_untrusted_proxy_headers = True,
        threads = os.cpu_count()
    )
