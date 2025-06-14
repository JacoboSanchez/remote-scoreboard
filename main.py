import logging
import os
import sys
from oid_dialog import OidDialog
from gui import GUI
from fastapi.responses import RedirectResponse
from authentication import AuthMiddleware, PasswordAuthenticator
from nicegui import ui, app
from customization import Customization
from customization_page import CustomizationPage
from conf import Conf
from backend import Backend
from app_storage import AppStorage
from messages import Messages
from typing import Optional


logging.addLevelName( logging.DEBUG, "\033[39m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
logging.addLevelName( logging.INFO, "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.INFO))
logging.addLevelName( logging.WARNING, "\033[1;43m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName( logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName( logging.FATAL, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.FATAL))
root = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter( "\033[1;36m%s\033[1;0m" % '%(asctime)s'+' %(levelname)s '+"\033[32m%s\033[1;0m" % '[%(name)s]'+':  %(message)s'))
root.addHandler(handler)
root.setLevel(os.environ.get('LOGGING_LEVEL', 'warning').upper())
logger = logging.getLogger("Main")
scoreboardTab = ui.tab(Customization.SCOREBOARD_TAB)
configurationTab = ui.tab(Customization.CONFIG_TAB)

if (PasswordAuthenticator.do_authenticate_users()):
    logger.info("User authentication enabled")
    app.add_middleware(AuthMiddleware)

def reset_links_storage():
    logger.info("resetting links")
    AppStorage.save(AppStorage.Category.CONFIGURED_OID, None)
    AppStorage.save(AppStorage.Category.CONFIGURED_OUTPUT, None)

def reset_all():
    logger.info("Clearing storage")
    AppStorage.clear_user_storage()

def process_parameters(refresh=None, logout=None):
    if logout == "true":
        reset_all()
        ui.navigate.to('./')
    elif refresh == "true":
        reset_links_storage()
        ui.navigate.to('./')

@ui.page("/indoor")
async def beach(control=None, output=None, refresh=None, logout=None):
    process_parameters(refresh=refresh, logout=logout)
    await run_page(custom_points_limit=25, custom_points_limit_last_set=15, custom_sets_limit=5, oid=control, output=output)

@ui.page("/beach")
async def beach(control=None, output=None, refresh=None, logout=None):
    process_parameters(refresh=refresh, logout=logout)
    await run_page(custom_points_limit=21, custom_points_limit_last_set=15, custom_sets_limit=3, oid=control, output=output)

@ui.page("/")
async def main(control=None, output=None, refresh=None, logout=None):
    process_parameters(refresh=refresh, logout=logout)
    await run_page(oid=control, output=output)


@ui.page('/login', response_timeout = 5)
async def login(redirect_to: str = '/') -> Optional[RedirectResponse]:
    if app.storage.user.get(AppStorage.Category.AUTHENTICATED, False):
        return RedirectResponse('/')
    logger.debug("Authenticating")
    authenticator =  PasswordAuthenticator(redirect_to=redirect_to)
    await authenticator.open()
    logger.debug("Authentication finished")
    return ui.navigate.to(redirect_to)

async def run_page(custom_points_limit=None, custom_points_limit_last_set=None, custom_sets_limit=None, oid=None, output=None):
    ui.add_head_html('''
        <script>
        function emitSize() {
            window.emitEvent('resize', {
                width: document.body.offsetWidth,
                height: document.body.offsetHeight,
            });
            }
            window.onload = emitSize;
            window.onresize = emitSize;
        </script>
    ''')
    notification = ui.notification(Messages.get(Messages.LOADING), timeout=None, spinner=True)
    tabs = ui.tabs().props('horizontal').classes("w-full")
    conf = Conf()
    backend = Backend(conf)
    scoreboard_page = GUI(tabs, conf, backend)
    ui.on('resize', lambda e: scoreboard_page.set_page_size(e.args['width'], e.args['height']))
    await ui.context.client.connected()
    if custom_points_limit == None:
        custom_points_limit = conf.points
    if custom_points_limit_last_set == None:
        custom_points_limit_last_set = conf.points_last_set
    if custom_sets_limit == None:
        custom_sets_limit = conf.sets
    if oid != None:
        conf.oid = oid
        conf.output = None
    if output != None:
        conf.output = OidDialog.UNO_OUTPUT_BASE_URL+output
    
    storageOid = AppStorage.load(AppStorage.Category.CONFIGURED_OID, default=None)
    storageOutput = AppStorage.load(AppStorage.Category.CONFIGURED_OUTPUT, default=None)
    if oid == None and backend.validate_and_store_model_for_oid(storageOid) == Backend.ValidationResult.VALID:
        logger.info("Loading session oid: %s and output %s", storageOid, storageOutput)
        conf.oid = storageOid
        conf.output = storageOutput
    else:
        validationResult = backend.validate_and_store_model_for_oid(conf.oid)
        if validationResult != Backend.ValidationResult.VALID:
            notification.dismiss()
            logger.info("Current oid is not valid [%s]: %s", validationResult, conf.oid)
            dialog = OidDialog(backend=backend)
            result = await dialog.open()
            if result != None:
                conf.oid = result[OidDialog.CONTROL_TOKEN_KEY]
                outputCustom = result.get(OidDialog.OUTPUT_URL_KEY, None )
                if outputCustom != None:
                    conf.output = outputCustom
                    AppStorage.save(AppStorage.Category.CONFIGURED_OUTPUT, conf.output)
                logger.debug("Received oid %s", conf.oid)
                AppStorage.save(AppStorage.Category.CONFIGURED_OID, conf.oid)

    customization_page = CustomizationPage(tabs, conf, backend, scoreboard_page)
    with ui.tab_panels(tabs, value=scoreboardTab).classes("w-full"):
        scoreboardTabPanel = ui.tab_panel(scoreboardTab)
        with scoreboardTabPanel:
            scoreboard_page.init(custom_points_limit=custom_points_limit, custom_points_limit_last_set=custom_points_limit_last_set, custom_sets_limit=custom_sets_limit)
        configurationTabPanel = ui.tab_panel(configurationTab)
        with configurationTabPanel:
            customization_page.init(configurationTabPanel)
    with tabs:
        scoreboardTab
        configurationTab
    notification.dismiss()

onair = os.environ.get('UNO_OVERLAY_AIR_ID', None)
if onair == '':
    onair = None
port = int(os.environ.get('APP_PORT', 8080))
title = os.environ.get('APP_TITLE', 'Scoreboard')
secret = os.environ.get('STORAGE_SECRET', title+str(port))
custom_favicon='<svg xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="24px" viewBox="0 0 24 24" width="24px" fill="#5f6368"><g><rect fill="none" height="24" width="24"/></g><g><g><path d="M12,2C6.48,2,2,6.48,2,12c0,5.52,4.48,10,10,10s10-4.48,10-10C22,6.48,17.52,2,12,2z M13,4.07 c3.07,0.38,5.57,2.52,6.54,5.36L13,5.65V4.07z M8,5.08c1.18-0.69,3.33-1.06,3-1.02v7.35l-3,1.73V5.08z M4.63,15.1 C4.23,14.14,4,13.1,4,12c0-2.02,0.76-3.86,2-5.27v7.58L4.63,15.1z M5.64,16.83L12,13.15l3,1.73l-6.98,4.03 C7.09,18.38,6.28,17.68,5.64,16.83z M10.42,19.84 M12,20c-0.54,0-1.07-0.06-1.58-0.16l6.58-3.8l1.36,0.78 C16.9,18.75,14.6,20,12,20z M13,11.42V7.96l7,4.05c0,1.1-0.23,2.14-0.63,3.09L13,11.42z"/></g></g></svg>'
ui.run(title=title, favicon=custom_favicon, on_air=onair, port=port, storage_secret=secret)