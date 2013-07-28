# -*- coding: utf-8 -*-
import json
import os

def user(): return dict(form=auth())
def error(): return dict()
def disabled(): return dict()
'''
    Note At various times system calls are evoked using the subprocess.pOpen
         To ensure that they work on a range of systems the shell=True argument
         is used. This is a potential security issue so the use of this application
         should be restricted to trusted users.
'''
def index():
    app = request.application
    if not settings.enabled:
        redirect("/%s/default/disabled" % app)
    if not auth.user_id:
        redirect("/%s/default/user/login" % app)
    if request.ajax:
        action = request.get_vars.action
        reply = Storage()
        reply.action = action
        reply.result = True
        reply.fatal = False
        reply.dialog = False
        reply.detail = ""
        reply.advanced = ""
        if action == "start":
            reply.next = "appname"
            reply.dialog = "#app-name-form"
            return json.dumps(reply)
        elif action == "appname":
            return appname_json(reply)
        elif action == "git":
            return git_json(reply)
        elif action == "clone":
            return clone_json(reply)
        elif action == "python":
            return python_json(reply)
        elif action == "pip":
            if request.get_vars.button == "install":
                return pip_json(reply)
            elif request.get_vars.button == "skip":
                return pre_db_json(reply)
        elif action == "install":
            return install_json(reply)
        elif action == "database":
            return db_json(reply)
        elif action == "connect":
            return connect_json(reply)
        else:
            reply.next = "finished"
            return json.dumps(reply)
    else:
        try:
            # Python 2.7
            from collections import OrderedDict
        except:
            # Python 2.6
            from gluon.contrib.simplejson.ordered_dict import OrderedDict
        session.eden_release = T("Eden release 1.0")
        session.fatal = None
        response.title=T("Sahana Eden Web Setup")
        actions = OrderedDict()
        actions["appname"] = T("Getting the application name")
        actions["git"] = T("Looking for git")
        actions["clone"] = T("Cloning Sahana Eden")
        actions["python"] = T("Looking for Python libraries")
        actions["pip"] = T("Looking for pip")
        actions["install"] = T("Using pip to install missing libraries")
        actions["database"] = T("Selecting the database to use")
        actions["connect"] = T("Connecting to the database")
        actions["web_server"] = T("Type of web server")
        table = TABLE()
        for (key,value) in actions.items():
            table.append(TR(
                            TD(value, _id="%s" % key),
                            TD(IMG(_id="%s_wait" % key,
                                   _src="/%s/static/images/Waiting.png" % app),
                               IMG(_id="%s_process" % key,
                                   _src="/%s/static/images/ajax-loader.gif" % app,
                                   _class="hidden"),
                               IMG(_id="%s_pass" % key,
                                   _src="/%s/static/images/Pass.png" % app,
                                   _class="hidden"),
                               IMG(_id="%s_fail" % key,
                                   _src="/%s/static/images/Fail.png" % app,
                                   _class="hidden")
                              )
                           )
                        )
        response.basic=table
        script = """
// Check if git libraries exist
function success(_data){
    data = $.parseJSON(_data) // Global scope so that dialog events can access it
    if (data.subaction){
        $("#"+data.subaction+"_wait").hide();
        $("#"+data.subaction+"_process").hide();
    } else {
        $("#"+data.action+"_wait").hide();
        $("#"+data.action+"_process").hide();
    }
    if (data.result) {
        if (data.subaction){
            $("#"+data.subaction+"_pass").show();
        } else {
            $("#"+data.action+"_pass").show();
        }
    } else {
        if (data.subaction){
            $("#"+data.subaction+"_fail").show();
        } else {
            $("#"+data.action+"_fail").show();
        }
    }
    $("#detail").append("<p><b>"+data.action+":</b> "+data.detail+"</p>");
    if (data.advanced != "") {
        $("#advanced").append("<p><b>"+data.action+":</b> "+data.advanced+"</p>");
    }
    if (data.insert_basic){
        insert_basic(data.insert_basic_id, data.insert_basic_html); 
    }
    if (data.fatal){
        alert(data.fatal);
        return;
    }
    if (data.next != 'finished') {
        args = new Object();
        args['action'] = data.next;
        if (data.nextsubaction){
            $("#"+data.nextsubaction+"_wait").hide();
            $("#"+data.nextsubaction+"_process").show();
        }
        $("#"+data.next+"_wait").hide();
        $("#"+data.next+"_process").show();
        if (data.dialog){
            $(data.dialog).dialog("open")
        } else {
            $.get('/%s/default/index', args).done(function(data){success(data)});
        }
    }
}

function insert_basic(id, html){
    $("td#"+id).append(html);
}

var args = new Object();
args['action'] = 'start';
$("#appname_wait").hide();
$("#appname_process").show();

$.get('/%s/default/index', args)
.done(function(data){success(data)});

$("input[name='display']").change(function(){
    if ($(this).val() == "basic"){
        $("#detail").hide();
        $("#advanced").hide();
    } else if ($(this).val() == "detail"){
        $("#detail").show();
        $("#advanced").hide();
    } else if ($(this).val() == "advanced"){
        $("#detail").show();
        $("#advanced").show();
    }
});

function updateTips( t ) {
    $(".validateTips").text(t).addClass( "ui-state-highlight" );
    setTimeout(function() {
        $(".validateTips").removeClass( "ui-state-highlight", 1500 );
    }, 500 );
}
function checkLength( o, n, min, max ) {
    if ( o.val().length > max || o.val().length < min ) {
        o.addClass( "ui-state-error" );
        updateTips( "Length of " + n + " must be between " + min + " and " + max + "." );
        return false;
    } else {
        return true;
    }
}
function checkRegexp(o, regexp, n) {
    if (!(regexp.test(o.val())) ) {
        o.addClass("ui-state-error");
        updateTips(n);
        return false;
    } else {
        return true;
    }
}
""" % (app, app)
        # Add input dialogs
        response.dialogs = DIV()
        script = script + appname_dialog(app)
        script = script + appexist_dialog(app)
        script = script + pip_dialog(app)
        script = script + db_type_dialog(app)
        script = script + connect_dialog(app)
        return dict(script=script)

def appname_dialog(app):
    appName = DIV(_id="app-name-form",
                  _title=T("Enter an application name")
                 )
    appName.append(P(T("Enter the name you will call your application"),
                     _class="validateTips"))
    appName.append(FORM(LABEL(T("Application name")),
                        INPUT(_id = "appname_in",
                              _name = "appname_in",
                              value = "test"
                             )
                        )
                   )
    response.dialogs.append(appName)
    script = """
$(function() {
    var appname = $("#appname_in"),
        allFields = $([]).add(appname),
        tips = $(".validateTips");
    $("#app-name-form").dialog({
        autoOpen: false,
        height: 300,
        width: 350,
        modal: true,
        buttons: {
            "%s": function() {
                var bValid = true;
                allFields.removeClass( "ui-state-error" );
                bValid = bValid && checkLength( appname, "application name", 3, 16 );
                bValid = bValid && checkRegexp( appname, /^[a-z]([0-9a-z])+$/i, "Application name may consist of a-z, 0-9, begin with a letter.");
                if ( bValid ) {
                    args['appname'] = appname.val();
                    $( this ).dialog("close");
                    $.get('/%s/default/index', args).done(function(data){success(data)});
                }
            }
        },
        close: function() {
            allFields.val("").removeClass("ui-state-error");
        }
    });
});
""" % (T("Continue"), app)
    return script

def appexist_dialog(app):
    existsName = DIV(_id="app-exists-alert",
                     _title=T("Application exists")
                   )
    existsName.append(P(T("The application folder already exists. The setup will now work with this folder")))
    response.dialogs.append(existsName)
    script = """
$(function() {
    $("#app-exists-alert").dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            %s: function() {
                $( this ).dialog("close");
                $.get('/%s/default/index', args).done(function(data){success(data)});
            },
            %s: function() {
                $( this ).dialog("close");
            }
        },
    });
});
""" % (T("Continue"), app, T("Cancel"))
    return script

def pip_dialog(app):
    existsName = DIV(_id="missing-libs-alert",
                     _title=T("Missing Libraries")
                   )
    existsName.append(P(T("Some libraries that Eden uses are missing. Would you like the system to try and install them for you? To do this it is necessary to have pip installed.")))
    response.dialogs.append(existsName)
    script = """
$(function() {
    $("#missing-libs-alert").dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            %s: function() {
                $( this ).dialog("close");
                args['button'] = "install";
                $.get('/%s/default/index', args).done(function(data){success(data)});
            },
            %s: function() {
                $( this ).dialog("close");
                args['button'] = "skip";
                $.get('/%s/default/index', args).done(function(data){success(data)});
            }
        },
    });
});
""" % (T("Install"), app, T("Skip"), app)
    return script

def db_type_dialog(app):
    dbType = DIV(_id="db-type-form",
                  _title=T("Database type")
                 )
    dbType.append(P(T("Select the type of database that will be used.")))
    dbType.append(FORM(LABEL(T("Sqlite")),
                       INPUT(_id = "dbtype_sqlite",
                             _name = "dbtype_in",
                             _type = "radio",
                             _value = "sqlite"
                            ),
                       LABEL(T("MySql")),
                       INPUT(_id = "dbtype_mysql",
                             _name = "dbtype_in",
                             _type = "radio",
                             _value = "mysql"
                            ),
                       LABEL(T("PostgeSQL")),
                       INPUT(_id = "dbtype_postgres",
                             _name = "dbtype_in",
                             _type = "radio",
                             _value = "postgres"
                            ),
                        )
                   )
    response.dialogs.append(dbType)
    script = '''
$(function() {
    $("#db-type-form").dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            %s: function() {
                args['db_type'] = $("input:radio[name=dbtype_in]:checked").val();
                $( this ).dialog("close");
                $.get('/%s/default/index', args).done(function(data){success(data)});
            }
        },
        open: function (event, ui){
            $("input:radio[name=dbtype_in]").filter('[value="'+data.db_type+'"]').attr('checked', true); 
        }
    });
});
''' % (T("Continue"), app)
    return script

def connect_dialog(app):
    appName = DIV(_id="db-connect-form",
                  _title=T("Enter the database details")
                 )
    appName.append(P(T("Provide the details necessary to connect to the database"),
                     _class="validateTips"))
    appName.append(FORM(LABEL(T("Database host")),
                        INPUT(_id = "db_host_in",
                              _name = "db_host_in",
                              value = "localhost"
                             ),
                        LABEL(T("Database port")),
                        INPUT(_id = "db_port_in",
                              _name = "db_port_in",
                              value = ""
                             ),
                        LABEL(T("Database schema name")),
                        INPUT(_id = "db_schema_in",
                              _name = "db_schema_in",
                              value = "sahana"
                             ),
                        LABEL(T("Database username")),
                        INPUT(_id = "db_user_in",
                              _name = "db_user_in",
                              value = "sahana"
                             ),
                        LABEL(T("Database password")),
                        INPUT(_id = "db_password_in",
                              _name = "db_password_in",
                              _type = "password",
                              value = ""
                             ),
                        )
                   )
    response.dialogs.append(appName)
    script = """
$(function() {
    var dbhost = $("#db_host_in"),
        dbport = $("#db_port_in"),
        dbschema = $("#db_schema_in"),
        dbuser = $("#db_user_in"),
        dbpassword = $("#db_password_in"),
        allFields = $([]).add(dbhost).add(dbport).add(dbschema).add(dbuser).add(dbpassword),
        tips = $(".validateTips");
    $("#db-connect-form").dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            "%s": function() {
                var bValid = true;
                allFields.removeClass( "ui-state-error" );
                if ( bValid ) {
                    args['db_host'] = dbhost.val();
                    args['db_port'] = dbport.val();
                    args['db_schema'] = dbschema.val();
                    args['db_user'] = dbuser.val();
                    args['db_password'] = dbpassword.val();
                    $( this ).dialog("close");
                    $.get('/%s/default/index', args).done(function(data){success(data)});
                }
            }
        },
        open: function (event, ui){
            $("#db_port_in").val(data.db_port); 
        },
        close: function() {
            allFields.val("").removeClass("ui-state-error");
        }
    });
});
""" % (T("Continue"), app)
    return script

def appname_json(reply):
    appname = request.get_vars.appname
    reply.detail = T("Appname will be <b>%s</b>" % appname, lazy = False)
    session.appname =  appname
    path = os.path.join("applications", appname)
    if os.path.isdir(path): 
        if os.path.isdir(os.path.join(path, ".git")):
            reply.detail = reply.detail +\
                           "<br>" +\
                           T("Directory %s already exists, so %s will not be cloned" % (appname, session.eden_release),
                                            lazy = False)
            reply.dialog = "#app-exists-alert"
            reply.next = "python"
            return json.dumps(reply)
    reply.next = "git"
    return json.dumps(reply)

def git_json(reply):
    from subprocess import Popen, PIPE
    try:
        cmd = ["git", "--version"]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        (myout, myerr) = p.communicate()
        reply.detail = T("Looking for git, <b>found:</b> %s" % myout, lazy = False)
        reply.advanced = myerr
    except Exception, inst:
        reply.result = False
        reply.fatal = T("Unable to continue, please install git",
                        lazy=False)
        reply.detail = "%s<br>" %(reply.fatal)
        reply.advanced = "<b>command:</b>%s<br><b>exception:</b>%s<br>" % (" ".join(cmd), inst)
    reply.next = "clone"
    return json.dumps(reply)

def clone_json(reply):
    from subprocess import Popen, PIPE
    try:
        appname = session.appname
        eden = session.eden_release
        cmd = ["git", "clone", "https://github.com/flavour/eden.git", "applications/%s" % appname]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        (myout, myerr) = p.communicate()
        retcode = p.returncode
        if retcode != 0:
            reply.result = False
            reply.fatal = T("Unable to clone %s" % eden,
                            lazy=False)
            reply.detail = T("Cloning %s into application %s:<b> Failed</b>" % (eden, appname),
                             lazy = False)
            reply.advanced = "<b>command: </b>%s<br><b>error:</b> %s<br>" % (" ".join(cmd), myerr)
        else:
            reply.detail = T("Cloning %s into application %s: <br>%s" % (eden, appname, myout),
                             lazy = False)
            reply.advanced = "<b>command: </b>%s<br>" % (" ".join(cmd))
    except Exception, inst:
        reply.result = False
        reply.fatal = T("Unable to clone %s" % eden,
                        lazy=False)
        reply.detail = reply.fatal + "<br>"
        reply.advanced = "<b>command: </b>%s<br><b>exception:</b>%s<br>" % (" ".join(cmd), inst)
        reply.next = "finished"
    reply.next = "python"
    return json.dumps(reply)

def python_json(reply):
    result = check_python_libraries()
    reply.next = "database"
    libs_missing = False
    error_lib = []
    warning_lib = []
    if result["error_messages"]:
        for error in result["error_messages"]:
            error_lib.append(strip_lib(error))
            reply.detail = reply.detail + "<b>Error:</b> %s<br>" % error
            reply.advanced = reply.advanced + "<b>Error:</b> %s<br>" % error
            libs_missing = True
            reply.next = "pip"
    if result["warning_messages"]:
        for warning in result["warning_messages"]:
            warning_lib.append(strip_lib(warning))
            reply.advanced = reply.advanced + "<b>Warning:</b> %s<br>" % warning
            libs_missing = True
            reply.next = "pip"
    if libs_missing:
        session.error_lib = error_lib
        session.warning_lib = warning_lib
        table = TABLE()
        app = request.application
        for lib in error_lib:
            table.append(TR(
                            TD(IMG(_src="/%s/static/images/red_star.png" % app,
                                   _width=24, _height=24),
                               T("Install python library %s" % lib), _id="%s" % lib),
                            TD(IMG(_id="%s_wait" % lib,
                                   _src="/%s/static/images/Waiting.png" % app,
                                   _width=24, _height=24),
                               IMG(_id="%s_process" % lib,
                                   _src="/%s/static/images/ajax-loader.gif" % app,
                                   _width=24, _height=24,
                                   _class="hidden",
                                   _style="display: none"),
                               IMG(_id="%s_pass" % lib,
                                   _src="/%s/static/images/Pass.png" % app,
                                   _width=24, _height=24,
                                   _class="hidden",
                                   _style="display: none"),
                               IMG(_id="%s_fail" % lib,
                                   _src="/%s/static/images/Fail.png" % app,
                                   _width=24, _height=24,
                                   _class="hidden",
                                   _style="display: none")
                              )
                           )
                        )
        for lib in warning_lib:
            table.append(TR(
                            TD(IMG(_src="/%s/static/images/yellow_star.png" % app,
                                   _width=16, _height=16),
                               T("Install python library %s" % lib), _id="%s" % lib),
                            TD(IMG(_id="%s_wait" % lib,
                                   _src="/%s/static/images/Waiting.png" % app,
                                   _width=24, _height=24),
                               IMG(_id="%s_process" % lib,
                                   _src="/%s/static/images/ajax-loader.gif" % app,
                                   _width=24, _height=24,
                                   _class="hidden",
                                   _style="display: none"),
                               IMG(_id="%s_pass" % lib,
                                   _src="/%s/static/images/Pass.png" % app,
                                   _width=24, _height=24,
                                   _class="hidden",
                                   _style="display: none"),
                               IMG(_id="%s_fail" % lib,
                                   _src="/%s/static/images/Fail.png" % app,
                                   _width=24, _height=24,
                                   _class="hidden",
                                   _style="display: none")
                              )
                           )
                        )
        reply.insert_basic = True
        reply.insert_basic_html = table.xml()
        reply.insert_basic_id = "install"
        reply.dialog = "#missing-libs-alert"
    return json.dumps(reply)

def pip_json(reply):
    from subprocess import Popen, PIPE
    try:
        cmd = ["pip", "--version"]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        (myout, myerr) = p.communicate()
        reply.detail = T("Looking for pip, <b>found:</b> %s" % myout, lazy = False)
        reply.advanced = myerr
    except Exception, inst:
        reply.result = False
        reply.fatal = T("Unable to continue, please install pip",
                        lazy=False)
        reply.detail = "%s<br>" %(reply.fatal)
        reply.advanced = "<b>command:</b>%s<br><b>exception:</b>%s<br>" % (" ".join(cmd), inst)
        return json.dumps(reply)
    # Now see if the version of pip supports the --target install option
    cmd = ["pip", "install", "--target"]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    (myout, myerr) = p.communicate()
    if "no such option" in myerr:
        reply.result = False
        reply.fatal = T("The version of pip needs to be upgraded. Use 'pip install -U pip' as admin.",
                        lazy=False)
        reply.detail = reply.detail +\
                       "<br>" +\
                       "%s<br>" %(reply.fatal)
        reply.advanced = reply.advanced +\
                         "<b>command:</b>%s<br><b>error:</b>%s<br>" % (" ".join(cmd), myerr)
    else:
        reply.detail = reply.detail +\
                       "<br>" +\
                       T("Looking for pip install --target option, <b>found:</b>", lazy = False)
        reply.next = "install"
        if session.error_lib:
            reply.nextsubaction = session.error_lib[-1]
        elif session.warning_lib:
            reply.nextsubaction = session.warning_lib[-1]
    return json.dumps(reply)

def install_json(reply):
    '''
        This function will attempt to install the missing libraries
        Because of the time it takes to install each library it will
        do one at a time and then send the result back as an json string 
    '''
    from subprocess import Popen, PIPE
    target = os.path.join(request.env.web2py_path, "site-packages")
    # Install a required lib, if one exists
    lib = None
    if session.error_lib:
        lib = session.error_lib.pop()
        cmd = ["pip", "install", "--target", target, lib]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        (myout, myerr) = p.communicate()
        if p.returncode == 0:
            reply.detail = reply.detail + "<br>"+T("Installed <b>%s</b> library" % lib,
                                                   lazy = False)
            reply.advanced = reply.advanced +\
                            "<b>command:</b>%s<br>" % (" ".join(cmd))
        else:
            reply.detail = reply.detail + "<br>"+T("Failed to install <b>%s</b> library." % (lib),
                                                   lazy = False)
            reply.advanced = reply.advanced +\
                            "<b>command:</b>%s<br><b>error:</b>%s<br>" % (" ".join(cmd), myout.replace('\n', '<br />'))
            session.fatal = T("Failed to install all of the required libraries",
                            lazy=False)
            reply.result = False
    # Install a optional lib, if one exists
    elif session.warning_lib:
        lib = session.warning_lib.pop()
        cmd = ["pip", "install", "--target", target, lib]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        (myout, myerr) = p.communicate()
        if p.returncode == 0:
            reply.detail = reply.detail + "<br>"+T("Installed <b>%s</b> library" % lib,
                                                   lazy = False)
            reply.advanced = reply.advanced +\
                            "<b>command:</b>%s<br>" % (" ".join(cmd))
        else:
            reply.detail = reply.detail + "<br>"+T("Failed to install <b>%s</b> library." % (lib),
                                                   lazy = False)
            reply.advanced = reply.advanced +\
                            "<b>command:</b>%s<br><b>error:</b>%s<br>" % (" ".join(cmd), myout.replace('\n', '<br />'))
            reply.result = False
    if lib:
        reply.subaction = lib
        if session.error_lib:
            reply.nextsubaction = session.error_lib[-1]
        elif session.warning_lib:
            reply.nextsubaction = session.warning_lib[-1]
        reply.next = "install"
    else:
        if session.fatal:
            reply.fatal = session.fatal
            reply.result = False
        return pre_db_json(reply)
    return json.dumps(reply)

def pre_db_json(reply):
    reply.dialog = "#db-type-form"
    reply.next = "database"
    db_type = get_000_config("db_type", "sqlite")
    reply.db_type = db_type
    return json.dumps(reply)

def db_json(reply):
    db_type = request.get_vars.db_type
    session.db_type = db_type
    set_000_config("database.db_type",
                   '"%s"'%db_type,
                   comment=(db_type=="sqlite")
                  )
    return pre_connect_json(reply)

def pre_connect_json(reply):
    db_type = session.db_type
    if db_type == "sqlite":
        set_000_config("database.host","",True)
        set_000_config("database.port","",True)
        set_000_config("database.database","",True)
        set_000_config("database.username","",True)
        set_000_config("database.password","",True)
        reply.next = "web_server"
    elif db_type == "mysql":
        reply.dialog = "#db-connect-form"
        reply.next = "connect"
        reply.db_port = get_000_config("port", "3306")
    elif db_type == "postgres":
        reply.dialog = "#db-connect-form"
        reply.next = "connect"
        reply.db_port = get_000_config("port", "5432")
    return json.dumps(reply)

def connect_json(reply):
    db_host = request.get_vars.db_host
    db_port = request.get_vars.db_port
    db_schema = request.get_vars.db_schema
    db_user = request.get_vars.db_user
    db_password = request.get_vars.db_password
    set_000_config("database.host",
                   '"%s"'%db_host
                  )
    set_000_config("database.port",
                   db_port
                  )
    set_000_config("database.database",
                   '"%s"'%db_schema
                  )
    set_000_config("database.username",
                   '"%s"'%db_user
                  )
    set_000_config("database.password",
                   '"%s"'%db_password
                  )
    reply.next = "web_server"
    return json.dumps(reply)

def strip_lib(msg):
    needle = "unresolved dependency: "
    start = msg.find(needle) + len(needle)
    finish = msg.find(" ", start)
    lib = msg[start:finish]
    return lib

def load_000_config():
    appname = session.appname
    # Read in the 000_config file
    base_cfg_file = "applications/%s/models/000_config.py" % appname
    try:
        input = open(base_cfg_file)
        with open(base_cfg_file, "r") as file:
            data = file.readlines()
    except:
        # No file so need to copy from templates
        # NOTE this code was copied from s3_upade_check (see check_python_libraries @todo)
        template_cfg_file = "applications/%s/private/templates/000_config.py" % appname
        input = open(template_cfg_file)
        output = open(base_cfg_file, "w")
        for line in input:
            if "akeytochange" in line:
                # Generate a random hmac_key to secure the passwords in case
                # the database is compromised
                import uuid
                hmac_key = uuid.uuid4()
                line = 'deployment_settings.auth.hmac_key = "%s"' % hmac_key
            output.write(line)
        output.close()
        input.close()
        input = open(base_cfg_file)
        with open(base_cfg_file, "r") as file:
            data = file.readlines()
    return data

def get_000_config(attr, default=None):
    data = load_000_config()
    value = default
    for line in data:
        if attr in line and line[0] != "#":
            value = line[line.rfind("= ")+2:].split('"')[1]
    return value

def set_000_config(attr, value, comment=False):
    # Read in the 000_config file
    appname = session.appname
    base_cfg_file = "applications/%s/models/000_config.py" % appname
    with open(base_cfg_file, "r") as file:
        data = file.readlines()
    added = False
    attr_found = False
    cnt = 0
    for line in data:
        if attr in line:
            attr_found = True
            if value and value in line:
                while data[cnt][0] == "#":
                    data[cnt] = line[1:]
                added = True
            else:
                if line[0] != "#":
                    data[cnt] = "#%s" % line
        cnt += 1
    if not comment and not added:
        if attr_found:
            cnt = 0
            for line in data:
                if attr in line:
                    data[cnt] = "settings.%s = %s\n%s" % (attr, value, line)
                    break # so it is only added once
                cnt += 1
        else:
            # add the attr at the end of the file
            data.append("settings.%s = %s\n" % (attr, value))
    with open(base_cfg_file, 'w') as file:
        file.writelines( data )

def check_python_libraries():
    ''' 
        @todo: make this a separate function in s3_upade_check so that it can be reused

        it will be called as follows:

            from gluon.shell import exec_environment
            appname = session.appname
            module = "applications/%s/modules/s3_update_check.py" % appname
            s3check = exec_environment(module)
            result = s3check.check_python_libraries()

    ''' 
    # Fatal errors
    errors = []
    # Non-fatal warnings
    warnings = []

    # -------------------------------------------------------------------------
    # Check Python libraries
    try:
        import dateutil
    except ImportError:
        errors.append("S3 unresolved dependency: dateutil required for Sahana to run")
    try:
        import lxml
    except ImportError:
        errors.append("S3XML unresolved dependency: lxml required for Sahana to run")
    try:
        import shapely
    except ImportError:
        warnings.append("S3GIS unresolved dependency: shapely required for GIS support")
    try:
        import xlrd
    except ImportError:
        warnings.append("S3XLS unresolved dependency: xlrd required for XLS import")
    try:
        import xlwt
    except ImportError:
        warnings.append("S3XLS unresolved dependency: xlwt required for XLS export")
    try:
        from PIL import Image
    except ImportError:
        try:
            import Image
        except ImportError:
            warnings.append("S3PDF unresolved dependency: Python Imaging required for PDF export")
    try:
        import reportlab
    except ImportError:
        warnings.append("S3PDF unresolved dependency: reportlab required for PDF export")
    try:
        from osgeo import ogr
    except ImportError:
        warnings.append("S3GIS unresolved dependency: GDAL required for Shapefile support")
    try:
        import tweepy
    except ImportError:
        warnings.append("S3Msg unresolved dependency: tweepy required for non-Tropo Twitter support")
    try:
        import sunburnt
    except ImportError, inst:
        warnings.append("S3Doc unresolved dependency: sunburnt required for Full-Text Search support")
    try:
        import pyth
    except ImportError:
        warnings.append("S3Doc unresolved dependency: pyth required for RTF document support in Full-Text Search")
    try:
        import matplotlib
    except ImportError:
        msg = "S3Chart unresolved dependency: matplotlib required for charting in Survey module"
        warnings.append(msg)
    try:
        import PyRTF
    except ImportError:
        msg = "Survey unresolved dependency: PyRTF required if you want to export assessment/survey templates as a Word document"
        warnings.append(msg)
    try:
        import numpy
    except ImportError:
        warnings.append("Vulnerability unresolved dependency: numpy required for Vulnerability module support")

    return {"error_messages": errors, "warning_messages": warnings}
