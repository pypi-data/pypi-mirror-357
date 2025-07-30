from objectpack.ui import (
    BaseEditWindow,
    anchor100,
    model_fields_to_controls,
)

from cookie_notification.models import (
    CookieNotificationsSetting,
)


class CookieNotificationSettingsWindow(BaseEditWindow):
    def _init_components(self):
        super()._init_components()

        self.text_field, self.file_field = model_fields_to_controls(
            CookieNotificationsSetting, self,
            field_list=['text', 'file'],
        )

    def _do_layout(self):
        super()._do_layout()

        self.form.items.extend(anchor100(field) for field in (self.text_field, self.file_field))

    def set_params(self, params):
        super().set_params(params)

        self.width, self.height = 500, 600
        self.resizable = False

        self.form.file_upload = True
