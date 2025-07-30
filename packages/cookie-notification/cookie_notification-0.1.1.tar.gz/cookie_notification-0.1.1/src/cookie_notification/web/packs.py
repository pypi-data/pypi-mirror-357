from m3.actions import (
    PreJsonResult,
)
from objectpack.actions import (
    BaseAction,
    BasePack,
    SimpleOneRecordPack,
)

from cookie_notification.domain import (
    DEFAULT_NOTIFICATION_TEXT,
)
from cookie_notification.models import (
    CookieNotificationsSetting,
)
from cookie_notification.utils import (
    set_agreement_to_request,
)
from cookie_notification.web.ui import (
    CookieNotificationSettingsWindow,
)


class CookieNotificationsSettingsPack(SimpleOneRecordPack):
    """
    Пак, реализующий работу с настройками уведомлений об использовании
    cookie-файлов. Следует следить за правами в конкретных реализациях
    и при их регистрации.
    """

    title = 'Уведомление об использовании файлов cookie'

    need_check_permission = True

    model = CookieNotificationsSetting

    add_window = edit_window = CookieNotificationSettingsWindow

    def extend_menu(self, menu):
        return menu.administry(menu.Item(self.title, pack=self))


class CookieNotificationPublicPack(BasePack):
    """
    Пак для экшенов, в которых реализованы функции для
    всех пользователей системы.

    Предполагается, что пак регистрируется отдельно в контроллер,
    в котором нет проверки на авторизацию пользователя.
    """

    need_check_permission = False

    def __init__(self):
        super().__init__()

        self.cookie_notification_message_action = CookieNotificationMessageAction()
        self.set_cookie_notification_agreement_action = SetCookieNotificationSettingAgreement()

        self.actions.extend((
            self.cookie_notification_message_action,
            self.set_cookie_notification_agreement_action,
        ))


class CookieNotificationMessageAction(BaseAction):
    """
    Возвращает настройки, заданные администратором системы.
    В возвращаемом значении находятся поля text с текстом
    уведомления и file с путем до файла.
    """

    need_check_permission = False

    def run(self, request, context):
        setting = CookieNotificationsSetting.objects.first()

        if setting:
            text = setting.text
            file_url = setting.file.url
        else:
            text = DEFAULT_NOTIFICATION_TEXT
            file_url = None

        return PreJsonResult({
            'text': text,
            'file': file_url,
        })


class SetCookieNotificationSettingAgreement(BaseAction):
    """
    Обработчик согласия на использование cookie.
    Основная работа происходит в middleware.
    """

    need_check_permission = False

    def run(self, request, context):
        # проставление куки будет в middleware
        set_agreement_to_request(request)

        return PreJsonResult({'ok': True})
