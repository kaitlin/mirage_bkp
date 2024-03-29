from rest_framework import serializers
from vendor.models import Vendor, Pool, Naics, SetAside
from contract.models import Contract

class SetAsideSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetAside
        fields = ('code', 'description')


class NaicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Naics
        fields = ('code', 'description', 'short_code')


class PoolSerializer(serializers.ModelSerializer):
    naics = NaicsSerializer(many=True)
    class Meta:
        model = Pool
        fields = ('id', 'number', 'vehicle', 'naics', 'threshold')


class ShortPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pool
        fields = ('id', 'number', 'vehicle')


class VendorSerializer(serializers.ModelSerializer):
    setasides = SetAsideSerializer(many=True)
    pools = ShortPoolSerializer(many=True)
    
    class Meta:
        model = Vendor
        fields = ('name', 'duns', 'duns_4', 'cage', 'sam_address', 'sam_citystate', 'cm_name', 'cm_email', 'cm_phone', 'pools', 'setasides', 'sam_status', 'sam_expiration_date', 'sam_activation_date', 'sam_exclusion', 'sam_url', 'annual_revenue', 'number_of_employees')


class ShortVendorSerializer(serializers.ModelSerializer):
    setasides = SetAsideSerializer(many=True)

    class Meta:
        model = Vendor
        fields = ('name', 'duns', 'duns_4', 'sam_address', 'sam_citystate',
            'setasides', 'sam_status', 'sam_exclusion', 'sam_url')

class ContractSerializer(serializers.ModelSerializer):
    
    pricing_type = serializers.Field(source='get_pricing_type_display')
    piid = serializers.SerializerMethodField('split_piid')
    class Meta:
        model = Contract
        fields = ('piid', 'agency_name', 'NAICS', 'date_signed', 'status', 'obligated_amount', 'point_of_contact', 'pricing_type')
        
    def split_piid(self, obj):
        if '_' in obj.piid:
            return obj.piid.split('_')[1]
        return obj.piid


