from django.conf import settings

from nautobot.extras.plugins import PluginTemplateExtension


class DeviceBulkConnect(PluginTemplateExtension):
    model = 'dcim.device'

    def buttons(self):
        device = self.context['object']
        white_listed_name = settings.PLUGINS_CONFIG['nautobot_bulk_connect']['device_role']
        if white_listed_name and not device.role.name == white_listed_name:
            return ""
        return self.render('nautobot_bulk_connect/inc/buttons.html', {
            'device': device
        })


template_extensions = [DeviceBulkConnect]
