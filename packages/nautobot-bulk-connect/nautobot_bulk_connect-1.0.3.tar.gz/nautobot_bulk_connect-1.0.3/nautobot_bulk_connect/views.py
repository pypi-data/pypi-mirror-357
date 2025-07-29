from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe
from django.shortcuts import redirect, render
from django.views.generic import View

from nautobot.dcim.models import Cable, Device
from nautobot.core.views.mixins import GetReturnURLMixin
from .forms import ConnectCablesToRearPortsForm


class ConnectView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = 'dcim.add_cable'
    template_name = 'nautobot_bulk_connect/cable_connect.html'

    def dispatch(self, request, *args, **kwargs):
        self.termination_type = ContentType.objects.get(model="rearport")

        self.obj = Cable(
            termination_a_type=self.termination_type,
            termination_b_type=self.termination_type
        )
        self.form_class = ConnectCablesToRearPortsForm

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, pk=None, **kwargs):

        # Parse initial data manually to avoid setting field values as lists
        initial_data = {k: request.GET[k] for k in request.GET}

        form = self.form_class(instance=self.obj, initial=initial_data)

        return render(request, self.template_name, {
            'device': Device.objects.get(pk=pk),
            'obj': self.obj,
            'obj_type': Cable._meta.verbose_name,
            'termination_b_type': self.termination_type.name,
            'form': form,
            'return_url': self.get_return_url(request, self.obj),
        })

    def post(self, request, *args, pk=None, **kwargs):

        form = self.form_class(request.POST, request.FILES, instance=self.obj)

        if form.is_valid():
            objs = form.save()

            msg = 'Created cables {}'.format(
                ", ".join('<a href="{}">{}</a>'.format(
                    obj.get_absolute_url(),
                    escape(obj)
                ) for obj in objs)
            )
            messages.success(request, mark_safe(msg))

            if '_addanother' in request.POST:
                return redirect(request.get_full_path())

            return_url = form.cleaned_data.get('return_url')
            if return_url is not None and url_has_allowed_host_and_scheme(url=return_url, allowed_hosts=request.get_host()):
                return redirect(return_url)
            else:
                if len(objs):
                    return redirect(self.get_return_url(request, objs[0].termination_a.device))
                return redirect('home')

        return render(request, self.template_name, {
            'device': Device.objects.get(pk=pk),
            'obj': self.obj,
            'obj_type': Cable._meta.verbose_name,
            'termination_b_type': self.termination_type.name,
            'form': form,
            'return_url': self.get_return_url(request, self.obj),
        })
