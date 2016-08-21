from rest_framework import serializers


class SearchIndexSerializer(serializers.Serializer):
    source_id = serializers.CharField(max_length=20)
    source_type = serializers.CharField(max_length=20)
    title = serializers.CharField(max_length=160)
    summary = serializers.CharField(max_length=255)
    postcode = serializers.CharField(max_length=20)
    alt_title = serializers.CharField(max_length=160)
    alt_postcode = serializers.CharField(max_length=20)
