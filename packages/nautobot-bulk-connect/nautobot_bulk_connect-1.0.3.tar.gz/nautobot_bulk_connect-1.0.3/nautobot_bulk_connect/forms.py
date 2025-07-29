from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Q

from nautobot.dcim.models import Cable, RearPort
from nautobot.dcim.forms import ConnectCableToRearPortForm
from nautobot.core.forms import DynamicModelChoiceField


class ConnectCablesToRearPortsForm(ConnectCableToRearPortForm):
    termination_a_id = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        label='Name',
        disabled_indicator='cable',
        query_params={
            'device': '$termination_a_device'
        }
    )
    count = forms.IntegerField()

    class Meta(ConnectCableToRearPortForm.Meta):
        fields = ConnectCableToRearPortForm.Meta.fields + [
            "termination_a_id",
            "count",
        ]

    def clean_ports(self, start, count):
        ports = []
        started = False
        typ = ContentType.objects.get(model="rearport")

        for port in RearPort.objects.filter(device=start.device).order_by('_name'):
            if not started and port != start:
                continue
            started = True

            if Cable.objects.filter(Q(termination_a_id=port.pk, termination_a_type=typ) | Q(termination_b_id=port.pk,
                                                                                            termination_b_type=typ)).exists():
                raise ValidationError(
                    'Port {} already has a cable in it (would be cable {})!'.format(port.name, len(ports) + 1))

            ports.append(port)
            if len(ports) == count:
                break

        if not len(ports) == count:
            raise ValidationError(
                'Cannot find {} rear ports after {} in {}'.format(count, start.name, start.device.name))

        return ports

    def clean_count(self):
        count = self.cleaned_data['count']
        termination_a_id = self.cleaned_data['termination_a_id']
        termination_b_id = self.cleaned_data['termination_b_id']
        from_port = RearPort.objects.get(pk=termination_a_id)
        to_port = RearPort.objects.get(pk=termination_b_id)
        self.from_ports = self.clean_ports(from_port, count)
        self.to_ports = self.clean_ports(to_port, count)

    def clean_termination_a_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data['termination_a_id'], 'pk', None)

    def save(self):
        instances = []
        for from_, to in zip(self.from_ports, self.to_ports):
            self.instance.pk = None
            self.instance.termination_a = from_
            self.instance.termination_b = to
            self.instance._state.adding = True
            self.instance.save()
            instances.append(Cable.objects.get(pk=self.instance.pk))
        return instances
