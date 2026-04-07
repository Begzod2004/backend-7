from rest_framework import serializers
from .models import Estimate, EstimateItem


class EstimateItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    unit_name = serializers.CharField(source='unit.abbreviation', read_only=True)

    class Meta:
        model = EstimateItem
        fields = [
            'id', 'product', 'product_name', 'quantity',
            'unit', 'unit_name', 'price_per_unit', 'total', 'note',
        ]
        read_only_fields = ['id', 'total']


class EstimateSerializer(serializers.ModelSerializer):
    items = EstimateItemSerializer(many=True, read_only=True)
    object_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Estimate
        fields = [
            'id', 'estimate_number', 'object', 'object_name',
            'name', 'created_by', 'created_by_name', 'status',
            'approved_by', 'approved_by_name', 'total_planned',
            'note', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'estimate_number', 'created_by',
            'approved_by', 'total_planned', 'created_at', 'updated_at',
        ]

    def get_object_name(self, obj):
        if obj.object:
            return obj.object.name
        return None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}"
        return None


class EstimateCreateSerializer(serializers.ModelSerializer):
    items = EstimateItemSerializer(many=True)

    class Meta:
        model = Estimate
        fields = [
            'object', 'name', 'note', 'items',
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        estimate = Estimate.objects.create(**validated_data)

        for item_data in items_data:
            EstimateItem.objects.create(estimate=estimate, **item_data)

        estimate.calculate_total()
        return estimate

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance.name = validated_data.get('name', instance.name)
        instance.object = validated_data.get('object', instance.object)
        instance.note = validated_data.get('note', instance.note)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                EstimateItem.objects.create(estimate=instance, **item_data)
            instance.calculate_total()

        return instance
