from audit.models import AuditLog

def serialize_data(data):
    if isinstance(data, dict):
        return {str(k): serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(v) for v in data]
    elif hasattr(data, 'pk'):
        # Usually a Django model instance for ForeignKey fields
        return str(data.pk)
    elif isinstance(data, (int, float, bool, type(None), str)):
        return data
    else:
        return str(data)

def diff_instance(old, new, fields):
    changes = {}
    for f in fields:
        oldv = getattr(old, f, None)
        newv = getattr(new, f, None)
        if oldv != newv:
            # We use serialize_data for both to ensure consistency and serializability
            changes[f] = {"from": serialize_data(oldv), "to": serialize_data(newv)}
    return changes

class AuditMixin:
    audit_model_name = None
    audit_fields = None  # list of fields to track

    def _audit_name(self):
        return self.audit_model_name or self.get_queryset().model.__name__

    def perform_create(self, serializer):
        obj = serializer.save()
        fields = self.audit_fields or list(serializer.validated_data.keys())
        # Filter and serialize data
        changes = {f: serialize_data(serializer.validated_data[f]) 
                  for f in fields if f in serializer.validated_data}
        actor = self.request.user if self.request.user.is_authenticated else None
        AuditLog.objects.create(
            actor=actor,
            action="CREATE",
            model=self._audit_name(),
            object_id=str(obj.pk),
            changes=changes,
        )

    def perform_update(self, serializer):
        obj = self.get_object()
        old = obj.__class__.objects.get(pk=obj.pk)
        obj = serializer.save()
        fields = self.audit_fields or list(serializer.validated_data.keys())
        changes = diff_instance(old, obj, fields)
        actor = self.request.user if self.request.user.is_authenticated else None
        AuditLog.objects.create(
            actor=actor,
            action="UPDATE",
            model=self._audit_name(),
            object_id=str(obj.pk),
            changes=changes,
        )

    def perform_destroy(self, instance):
        pk = instance.pk
        instance.delete()
        actor = self.request.user if self.request.user.is_authenticated else None
        AuditLog.objects.create(
            actor=actor,
            action="DELETE",
            model=self._audit_name(),
            object_id=str(pk),
            changes={},
        )

    def audit_log(self, action, obj=None, changes=None):
        actor = self.request.user if self.request.user.is_authenticated else None
        AuditLog.objects.create(
            actor=actor,
            action=action,
            model=obj.__class__.__name__ if obj else self._audit_name(),
            object_id=str(obj.pk) if obj else "0",
            changes=changes or {},
        )
